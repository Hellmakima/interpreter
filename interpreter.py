## Reference: [YT @CoreDumpped](https://www.youtube.com/watch?v=0c8b7YfsBKs)

from typing import Union

variables = {}

class Token:
    def __init__(self, arg: str = ''):
        self.arg = arg
    def __repr__(self):
        return f"Token '{self.arg}'"

class Eof(Token):
    def __init__(self):
        super().__init__()
    def __repr__(self):
        return f'Eof'

class Atom(Token):
    def __repr__(self):
        # return f"Atom '{self.arg}'"
        return self.arg

class Operator(Token):
    def __repr__(self):
        # return f"Op '{self.arg}'"
        return self.arg

class Operation:
    def __init__(self, op: Operator, lhs: 'Expression', rhs: 'Expression'):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self):
        # return f"({str(self.lhs)} {str(self.op)} {str(self.rhs)})"
        return f"({str(self.op)} {str(self.lhs)} {str(self.rhs)})"
    def draw(self, level=0, prefix=""):
        """
        Draws the parse tree in a hierarchical, readable format.
        """
        pass

Expression = Union[Atom, Operation]

class Lexer:
    def __init__(self, exp: str = None):
        if exp is None:
            exp = input('> ')
        if not isinstance(exp, str) or len(exp.strip()) == 0:
            raise ValueError("Empty expression")

        self.tokens = []
        i = 0
        while i < len(exp):
            c = exp[i]
            if c in ' \t\n':
                i += 1
                continue
            if c.isalnum():
                # Handle multi-character numbers and identifiers
                start = i
                while i < len(exp) and (exp[i].isalnum() or exp[i] in '_.'):
                    i += 1
                self.tokens.append(Atom(exp[start:i]))
                continue
            else:
                self.tokens.append(Operator(c))
            i += 1
        self.tokens.reverse() # to use it as a stack, but backwards

    def __repr__(self):
        return ', '.join([str(token) for token in self.tokens])
    def next(self):
        if self.tokens:
            return self.tokens.pop()
        return Eof()
    def peek(self):
        if self.tokens:
            return self.tokens[-1]
        return Eof()

def parse_expression(lexer: Lexer, min_bp: float = 0.0) -> Expression:
    '''
    ## Parsing Expressions

    The following is a recursive descent parser for expressions.
    It is based on the following grammar:

        expr -> atom | expr op expr
        atom -> number | identifier
        op -> '+' | '-' | '*' | '/' | '^'

    The function `parse_expression` takes a `Lexer` object and `min_bp` (minimum binding power)
    returns an `Expression` object.

    For example, 2+3*4 -> (2 + (3 * 4))
    '''
    lhs_token = lexer.next()

    if isinstance(lhs_token, Operator) and lhs_token.arg == '(':
        # fold (solve) the expression inside braces completely
        lhs = parse_expression(lexer)
        bracket_token = lexer.next()
        if not (isinstance(bracket_token, Operator) and bracket_token.arg == ')'):
            raise ValueError("Unmatched parenthesis")
    elif isinstance(lhs_token, Operator) and lhs_token.arg == '-':
        # handle unary operator '-'
        lhs = parse_expression(lexer)
        lhs = Operation(Operator('-'), Atom('0'), lhs)
    elif isinstance(lhs_token, Atom):
        lhs = lhs_token
    else:
        raise ValueError('Expected atom or opening parenthesis')

    while True:
        op_token = lexer.peek()

        if isinstance(op_token, Atom):
            raise SyntaxError(f"Unexpected token '{op_token.arg}'. Expected an operator or end of expression.")

        if not isinstance(op_token, Operator) or isinstance(op_token, Eof):
            # also breaks on ')'
            break

        # Get operator precedence
        try:
            l_bp, r_bp = infix_binding_power(op_token.arg)
        except ValueError:
            break  # not a binary operator

        if l_bp < min_bp:
            break

        # Consume the operator
        op = lexer.next()

        # Parse right-hand side with higher precedence
        rhs = parse_expression(lexer, r_bp)

        # Combine into operation
        lhs = Operation(op, lhs, rhs)

    return lhs

def infix_binding_power(op: str) -> tuple:
    if op == '=':
        return (0.2, 0.1)
    if op in ['+', '-']:
        return (1.0, 1.1)
    if op in ['*', '/']:
        return (2.0, 2.1)
    if op == '^':
        return (3.1, 3.0)
    raise ValueError(f"invalid operator {op}")

def evaluate(expression: Expression):
    """
    Evaluates the given parsed expression.
    """
    if isinstance(expression, Atom):
        # Try to convert to float if it's a number, otherwise treat as variable
        try:
            return float(expression.arg)
        except ValueError:
            if expression.arg in variables:
                return variables[expression.arg]
            else:
                raise NameError(f"name '{expression.arg}' is not defined")
    if isinstance(expression, Operation):
        op_arg = expression.op.arg
        if op_arg == '=':
            # Handle assignment
            try:
                var_name = expression.lhs.arg
            except AttributeError:
                # You are either assigning to a literal or have assignment operators in unwanted places.
                raise SyntaxError('try adding more parenthesis.')
            if var_name.isnumeric():
                raise SyntaxError('cannot assign to literal')
            value = evaluate(expression.rhs)
            variables[var_name] = value
            return value
        else:
            # Handle binary operations
            lhs_val = evaluate(expression.lhs)
            rhs_val = evaluate(expression.rhs)

            if op_arg == '+':
                return lhs_val + rhs_val
            elif op_arg == '-':
                return lhs_val - rhs_val
            elif op_arg == '*':
                return lhs_val * rhs_val
            elif op_arg == '/':
                if rhs_val == 0:
                    raise ZeroDivisionError("division by zero")
                return lhs_val / rhs_val
            elif op_arg == '^':
                return lhs_val ** rhs_val
            else:
                raise ValueError(f"Unknown operator: {op_arg}")
    else:
        raise TypeError("Invalid expression type for evaluation")

def interactive():
    print("Welcome to the expression evaluator! Type 'quit' or 'exit' to stop.")
    while True:
        try:
            expr_str = input("> ").strip()
            if expr_str.lower() in ('quit', 'exit'):
                break
            if not expr_str:
                continue

            lexer = Lexer(expr_str)
            print(lexer)
            parsed_expression = parse_expression(lexer)

            print("Parsed AST:", parsed_expression)

            # After parsing, check if there are any remaining tokens that weren't consumed
            # This catches cases like '2 3' where 3 is left unparsed
            if not isinstance(lexer.peek(), Eof):
                raise SyntaxError(f"Unexpected token(s) at end of expression: {', '.join(str(t) for t in lexer.tokens[::-1])}")

            result = evaluate(parsed_expression)
            
            # Only print the result if it wasn't an assignment (assignments already return the value)
            if not (isinstance(parsed_expression, Operation) and parsed_expression.op.arg == '='):
                print("Result:", result)
            else:
                print(f"{parsed_expression.lhs.arg} = {result}")

        except Exception as e:
            print("Error:", e)
        print("Variables:", variables) # Show current variable state for debugging/user info

def test1():
    """Test single atom"""
    parsed_expression = parse_expression(Lexer('1'))
    result = str(parsed_expression).replace(' ', '')
    expected = '1'
    assert result == expected, f"Expected {expected}, got {result}"
    print("test1 passed")

def test2():
    """Test operator precedence"""
    parsed_expression = parse_expression(Lexer('1 + 2 * 3'))
    result = str(parsed_expression).replace(' ', '')
    expected = '(+1(*23))'
    assert result == expected, f"Expected {expected}, got {result}"
    print("test2 passed")

def test3():
    """Test variables and complex expression"""
    parsed_expression = parse_expression(Lexer('a + b * 2 - c'))
    result = str(parsed_expression).replace(' ', '')
    expected = '(-(+a(*b2))c)'
    assert result == expected, f"Expected {expected}, got {result}"
    print("test3 passed")

def test4():
    """Test parentheses"""
    parsed_expression = parse_expression(Lexer('(a + b) * 2'))
    result = str(parsed_expression).replace(' ', '')
    expected = '(*(+ab)2)'
    assert result == expected, f"Expected {expected}, got {result}"
    print("test4 passed")

def test5():
    """Test exponentiation"""
    parsed_expression = parse_expression(Lexer('a ^ b * c'))
    result = str(parsed_expression).replace(' ', '')
    expected = '(*(^ab)c)'
    assert result == expected, f"Expected {expected}, got {result}"
    print("test5 passed")

def parse_file(file_path):
    code = ''
    with open(file_path, 'r') as f:
        code = f.read()
    code = code.split('\n')
    for line_no, line in enumerate(code):
        try:
            line = line.split('#')[0]
            if line.lower() in ('quit', 'exit'):
                print('... exiting')
                break
            if line == 'vars':
                print(variables)
                continue
            if not line.replace(' ','').replace('\t',''):
                continue
            lexer = Lexer(line)
            parsed_expression = parse_expression(lexer)

            # After parsing, check if there are any remaining tokens that weren't consumed
            # This catches cases like '2 3' where 3 is left unparsed
            if not isinstance(lexer.peek(), Eof):
                raise SyntaxError(f"Unexpected token(s) at end of expression: {', '.join(str(t) for t in lexer.tokens[::-1])}")

            result = evaluate(parsed_expression)
            
            # Only print the result if it wasn't an assignment (assignments already return the value)
            if not (isinstance(parsed_expression, Operation) and parsed_expression.op.arg == '='):
                print(result)

        except Exception as e:
            print("Error:", e)
    print("Variables:", variables)

if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    print("Uncomment 'parse_file(file_path)' in main to run script")
    # file_path = 'main.alya'
    # parse_file(file_path)
    interactive()
    
