import re
from typing import List, Tuple

class LexerError(Exception):
    pass

class Lexer:
    """
    A minimal lexer for uhlisp.
    Tokenizes input strings into a list of string tokens.
    """
    def __init__(self, source: str):
        self.source = source
        self.pos = 0

    def tokenize(self) -> List[str]:
        tokens = []
        while self.pos < len(self.source):
            char = self.source[self.pos]

            if char.isspace():
                self.pos += 1
                continue

            if char == ';':
                # Skip comments to end of line
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            if char in ('(', ')'):
                tokens.append(char)
                self.pos += 1
                continue

            if char == '"':
                tokens.append(self._read_string())
                continue

            # Read a symbol or number
            tokens.append(self._read_symbol_or_number())

        return tokens

    def _read_string(self) -> str:
        # Start of string
        start_pos = self.pos
        self.pos += 1 # skip opening quote

        while self.pos < len(self.source) and self.source[self.pos] != '"':
            # rudimentary escape character support could go here
            self.pos += 1

        if self.pos >= len(self.source):
            raise LexerError("Unterminated string literal")

        self.pos += 1 # skip closing quote
        return self.source[start_pos:self.pos]

    def _read_symbol_or_number(self) -> str:
        start_pos = self.pos
        # Read until space, parenthesis, or end of file
        while self.pos < len(self.source) and not self.source[self.pos].isspace() and self.source[self.pos] not in ('(', ')'):
            self.pos += 1
        return self.source[start_pos:self.pos]

def tokenize(source: str) -> List[str]:
    """Helper function to tokenize a string directly."""
    lexer = Lexer(source)
    return lexer.tokenize()
