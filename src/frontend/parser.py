from typing import List as TList
from src.frontend.ast import ASTNode, Symbol, Number, String, Boolean, List

class ParserError(Exception):
    pass

class Parser:
    """
    Recursive descent parser for uhlisp.
    Converts a list of tokens into an AST.
    """
    def __init__(self, tokens: TList[str]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        if self.pos >= len(self.tokens):
            raise ParserError("Unexpected end of input")

        token = self.tokens[self.pos]
        self.pos += 1

        if token == '(':
            return self._parse_list()
        elif token == ')':
            raise ParserError("Unexpected ')'")
        else:
            return self._parse_atom(token)

    def _parse_list(self) -> List:
        elements = []
        while self.pos < len(self.tokens) and self.tokens[self.pos] != ')':
            elements.append(self.parse())

        if self.pos >= len(self.tokens):
            raise ParserError("Unexpected end of input, missing ')'")

        self.pos += 1  # Skip the closing ')'
        return List(elements)

    def _parse_atom(self, token: str) -> ASTNode:
        if token == 'true':
            return Boolean(True)
        elif token == 'false':
            return Boolean(False)

        if token.startswith('"') and token.endswith('"'):
            return String(token[1:-1])

        # Try to parse as an integer
        try:
            return Number(int(token))
        except ValueError:
            pass

        # Try to parse as a float
        try:
            return Number(float(token))
        except ValueError:
            pass

        # Otherwise, it's a symbol
        return Symbol(token)

def parse(tokens: TList[str]) -> ASTNode:
    """Helper function to parse a list of tokens into an AST."""
    if not tokens:
        raise ParserError("Empty token list")

    parser = Parser(tokens)
    return parser.parse()

def parse_all(tokens: TList[str]) -> TList[ASTNode]:
    """Parses multiple expressions from a token list."""
    parser = Parser(tokens)
    nodes = []
    while parser.pos < len(parser.tokens):
        nodes.append(parser.parse())
    return nodes
