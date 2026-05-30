import sys
import traceback
from src.frontend.lexer import tokenize, LexerError
from src.frontend.parser import parse_all, ParserError

def repl():
    print("Welcome to the uhlisp REPL.")
    print("Type 'exit' or 'quit' to exit, or press Ctrl+C / Ctrl+D.")

    while True:
        try:
            # Read
            user_input = input("uhlisp> ")

            # Check for exit commands
            if user_input.strip() in ("exit", "quit"):
                break

            if not user_input.strip():
                continue

            # Lex & Parse
            tokens = tokenize(user_input)
            if not tokens:
                continue

            asts = parse_all(tokens)

            # "Eval" (Print AST for now)
            for ast in asts:
                print(repr(ast))

        except (EOFError, KeyboardInterrupt):
            print("\nExiting uhlisp REPL.")
            break
        except LexerError as e:
            print(f"LexerError: {e}")
        except ParserError as e:
            print(f"ParserError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    repl()
