# Expression Parser & Evaluator

This is a recursive descent expression parser and evaluator written in Python. It supports variable assignment, arithmetic operations, and correct operator precedence, with an interactive mode and file-based execution.

## Reference: [YT @CoreDumpped video](https://www.youtube.com/watch?v=0c8b7YfsBKs)

## Features

* Supports basic arithmetic: `+`, `-`, `*`, `/`, `^`
* Correct operator precedence and associativity
* Variable assignment (e.g. `x = 3 + 2`)
* Nested parentheses and unary minus
* Syntax error detection and helpful messages
* Interactive REPL and `.alya` file execution
* Includes simple tests for correctness
* example `a = (9*8^2)-4^(b=-9)`

## Run

The code has some test cases
and runs interactive mode

U can run a script by uncommenting
```python
    # file_path = 'main.alya'
    # parse_file(file_path)
```

Additionally I have included `a.java` a java version of the same code.

## License

This project is open-source and free to use for learning and experimentation.
