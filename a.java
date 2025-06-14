import java.util.*;

class Token {
    String arg;

    Token(String arg) {
        this.arg = arg;
    }

    @Override
    public String toString() {
        return this.arg;
    }
}

class Eof extends Token{
    Eof() {
        super("");
    }

    @Override
    public String toString() {
        return "Eof";
    }
}

interface Expression{}

class Atom extends Token implements Expression {
    Atom(String arg) { super(arg); }
}

class Operator extends Token {
    Operator(String arg) {
        super(arg);
    }
}

class Operation implements Expression {
	Operator op;
	Expression lhs;
	Expression rhs;
	Operation(Operator op, Expression lhs, Expression rhs){
		this.op = op;
		this.lhs = lhs;
		this.rhs = rhs;
	}
	@Override
    public String toString() {
        return "(" + op.toString() + " " + lhs.toString() + " " + rhs.toString() + ")";
    }
}

class Lexer{
	public Deque<Token> tokens = new ArrayDeque<>();

	Lexer(String exp){
		if (exp == null || exp.trim().isEmpty()) {
            throw new IllegalArgumentException("Empty expression");
        }
		int i = 0;
		while (i < exp.length()){
			char c = exp.charAt(i);
			if (Character.isWhitespace(c)){
				i++;
				continue;
			}
			if (Character.isLetterOrDigit(c)) {
				int start = i;
				while (i < exp.length() && Character.isLetterOrDigit(exp.charAt(i))){
					i++;
				}
				tokens.addFirst(new Atom(exp.substring(start,i)));
				continue;
			}
			tokens.addFirst(new Operator(String.valueOf(c)));
			i++;
		}
	}

	@Override
    public String toString() {
        List<Token> list = new ArrayList<>(tokens);
        Collections.reverse(list);
        StringBuilder sb = new StringBuilder();
        for (Token t : list) {
            sb.append(t.toString()).append(", ");
        }
        return sb.length() > 2 ? sb.substring(0, sb.length()-2) : sb.toString();
    }

	public Token next(){
		return tokens.isEmpty() ? new Eof() : tokens.removeLast();
	}

	public Token peek(){
		return tokens.isEmpty() ? new Eof() : tokens.peekLast();
	}
}

class a{
	private static HashMap<String, Double> variables = new HashMap<>();
	public static double[] infixBindingPower(String op) {
	    switch (op) {
	        case "=":
	            return new double[]{0.2, 0.1};
	        case "+":
	        case "-":
	            return new double[]{1.0, 1.1};
	        case "*":
	        case "/":
	            return new double[]{2.0, 2.1};
	        case "^":
	            return new double[]{3.1, 3.0};
	        default:
	            throw new IllegalArgumentException("invalid operator " + op);
	    }
	}
	public static Object evaluate(Expression expression) {
	    if (expression instanceof Atom) {
	        String arg = ((Atom) expression).arg;

	        // Check if it's a number using regex
	        if (arg.matches("-?\\d+(\\.\\d+)?")) {
	            return Double.parseDouble(arg);
	        }

	        // Else it's a variable
	        if (variables.containsKey(arg)) {
	            return variables.get(arg);
	        }

	        throw new RuntimeException("name '" + arg + "' is not defined");
	    }

	    if (expression instanceof Operation) {
	        Operation op = (Operation) expression;
	        String opArg = op.op.arg;

	        if (opArg.equals("=")) {
	            // Handle assignment
	            if (!(op.lhs instanceof Atom)) {
	                throw new RuntimeException("Try adding more parenthesis.");
	            }

	            String varName = ((Atom) op.lhs).arg;

	            if (varName.matches("\\d+")) {
	                throw new RuntimeException("Cannot assign to literal");
	            }

	            Object value = evaluate(op.rhs);
	            variables.put(varName, toDouble(value));
	            return value;
	        } else {
	            // Binary operations
	            Object lhsObj = evaluate(op.lhs);
	            Object rhsObj = evaluate(op.rhs);

	            double lhs = toDouble(lhsObj);
	            double rhs = toDouble(rhsObj);

	            switch (opArg) {
	                case "+":
	                    return lhs + rhs;
	                case "-":
	                    return lhs - rhs;
	                case "*":
	                    return lhs * rhs;
	                case "/":
	                    if (rhs == 0) {
	                        throw new ArithmeticException("division by zero");
	                    }
	                    return lhs / rhs;
	                case "^":
	                    return Math.pow(lhs, rhs);
	                default:
	                    throw new RuntimeException("Unknown operator: " + opArg);
	            }
	        }
	    }

	    throw new RuntimeException("Invalid expression type for evaluation");
	}

	private static double toDouble(Object obj) {
	    if (obj instanceof Number) {
	        return ((Number) obj).doubleValue();
	    }
	    throw new RuntimeException("Cannot convert to number: " + obj);
	}
	public static Expression parseExpression(Lexer lexer, double minBp) {
	    Token lhsToken = lexer.next();
	    Expression lhs;

	    if (lhsToken instanceof Operator && ((Operator) lhsToken).arg.equals("(")) {
	        lhs = parseExpression(lexer, 0.0);
	        Token bracketToken = lexer.next();
	        if (!(bracketToken instanceof Operator) || !((Operator) bracketToken).arg.equals(")")) {
	            throw new RuntimeException("Unmatched parenthesis");
	        }
	    } else if (lhsToken instanceof Operator && ((Operator) lhsToken).arg.equals("-")) {
	        // Unary minus becomes: 0 - expr
	        Expression inner = parseExpression(lexer, 0.0);
	        lhs = new Operation(new Operator("-"), new Atom("0"), inner);
	    } else if (lhsToken instanceof Atom) {
	        lhs = (Atom) lhsToken;
	    } else {
	        throw new RuntimeException("Expected atom or opening parenthesis");
	    }

	    while (true) {
	        Token opToken = lexer.peek();

	        if (opToken instanceof Atom) {
	            throw new RuntimeException("Unexpected token '" + ((Atom) opToken).arg + "'. Expected an operator or end of expression.");
	        }

	        if (opToken instanceof Eof || !(opToken instanceof Operator)) {
	            break;
	        }

	        double[] bp;
	        try {
	            bp = infixBindingPower(opToken.arg);
	        } catch (IllegalArgumentException e) {
	            break;
	        }

	        double lBp = bp[0];
	        double rBp = bp[1];

	        if (lBp < minBp) {
	            break;
	        }

	        lexer.next();
	        Expression rhs = parseExpression(lexer, rBp);
	        lhs = new Operation((Operator) opToken, lhs, rhs);

	    }

	    return lhs;
	}

	public static Expression parseExpression(Lexer lexer) {
	    return parseExpression(lexer, 0.0);
	}

	public static void interactive() {
		System.out.println("Welcome to the expression evaluator! Type 'quit' or 'exit' to stop.");
		Scanner sc = new Scanner(System.in);
		while (true){
			try {
				System.out.print("> ");
				String exprStr = sc.nextLine().trim();
				if (exprStr.equalsIgnoreCase("quit") || exprStr.equalsIgnoreCase("exit")){
					break;
				}
				if (exprStr.length() == 0){
					continue;
				}
				Lexer lexer = new Lexer(exprStr);
				// System.out.println(lexer);
				Expression parsedExpression = parseExpression(lexer);
				// System.out.println("Parsed AST: " + parsedExpression);
				
				if (!(lexer.peek() instanceof Eof)) {
				    StringBuilder message = new StringBuilder("Unexpected token(s) at end of expression: ");
				    List<Token> reversed = new ArrayList<>(lexer.tokens);
				    Collections.reverse(reversed);
				    for (int i = 0; i < reversed.size(); i++) {
				        message.append(reversed.get(i).toString());
				        if (i != reversed.size() - 1) {
				            message.append(", ");
				        }
				    }
				    throw new RuntimeException(message.toString());
				}
				Object result = evaluate(parsedExpression);

				if (!(parsedExpression instanceof Operation) || !((Operation)parsedExpression).op.arg.equals("=")) {
					System.out.println("Result: " + result);
				} else {
					System.out.println(((Atom)((Operation)parsedExpression).lhs).arg + " = " + result);
				}
			} catch (Exception e){
				System.out.println("Error: " + e);
			}
			System.out.println("Variables: " + variables);
		}
	}

	public static void main(String[] args) {
		interactive();
	}
}
