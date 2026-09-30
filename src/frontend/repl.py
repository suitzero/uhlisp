import sys
import traceback
from src.frontend.lexer import tokenize, LexerError
from src.frontend.parser import parse_all, ParserError
from src.frontend.macro import MacroExpander, MacroError

def repl():
    print("Welcome to the uhlisp REPL.")
    print("Type 'exit' or 'quit' to exit, or press Ctrl+C / Ctrl+D.")
    
    macro_expander = MacroExpander()

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

            # Extract macros
            remaining_asts = macro_expander.extract_macros(asts)

            # Expand macros and "Eval" (Print AST for now)
            for ast in remaining_asts:
                expanded_ast = macro_expander.expand(ast)
                print(repr(expanded_ast))

        except (EOFError, KeyboardInterrupt):
            print("\nExiting uhlisp REPL.")
            break
        except LexerError as e:
            print(f"LexerError: {e}")
        except ParserError as e:
            print(f"ParserError: {e}")
        except MacroError as e:
            print(f"MacroError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    repl()
