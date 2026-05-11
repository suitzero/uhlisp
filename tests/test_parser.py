import unittest
from src.frontend.lexer import tokenize, LexerError
from src.frontend.parser import parse, ParserError, parse_all
from src.frontend.ast import Symbol, Number, String, Boolean, List

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        source = "(defmodule splitter (in out1 out2))"
        tokens = tokenize(source)
        self.assertEqual(tokens, ['(', 'defmodule', 'splitter', '(', 'in', 'out1', 'out2', ')', ')'])

    def test_strings(self):
        source = '(print "hello world")'
        tokens = tokenize(source)
        self.assertEqual(tokens, ['(', 'print', '"hello world"', ')'])

    def test_comments_and_whitespace(self):
        source = "\n; This is a comment\n(def x 10) ; another comment\n"
        tokens = tokenize(source)
        self.assertEqual(tokens, ['(', 'def', 'x', '10', ')'])

    def test_unterminated_string(self):
        with self.assertRaises(LexerError):
            tokenize('(print "unterminated)')

class TestParser(unittest.TestCase):
    def test_parse_atom_symbol(self):
        tokens = ['x']
        ast = parse(tokens)
        self.assertEqual(ast, Symbol('x'))

    def test_parse_atom_number(self):
        tokens = ['42']
        ast = parse(tokens)
        self.assertEqual(ast, Number(42))

        tokens = ['3.14']
        ast = parse(tokens)
        self.assertEqual(ast, Number(3.14))

    def test_parse_atom_string(self):
        tokens = ['"hello"']
        ast = parse(tokens)
        self.assertEqual(ast, String('hello'))

    def test_parse_atom_boolean(self):
        tokens = ['true']
        ast = parse(tokens)
        self.assertEqual(ast, Boolean(True))

        tokens = ['false']
        ast = parse(tokens)
        self.assertEqual(ast, Boolean(False))

    def test_parse_list(self):
        tokens = ['(', '+', '1', '2', ')']
        ast = parse(tokens)
        self.assertEqual(ast, List([Symbol('+'), Number(1), Number(2)]))

    def test_parse_nested_list(self):
        tokens = tokenize("(defmodule splitter (in out1 out2))")
        ast = parse(tokens)
        self.assertEqual(ast, List([
            Symbol('defmodule'),
            Symbol('splitter'),
            List([Symbol('in'), Symbol('out1'), Symbol('out2')])
        ]))

    def test_unexpected_paren(self):
        with self.assertRaises(ParserError):
            parse([')'])

    def test_unexpected_eof(self):
        with self.assertRaises(ParserError):
            parse(['(', 'x'])

    def test_parse_all(self):
        tokens = tokenize("(def x 1) (def y 2)")
        asts = parse_all(tokens)
        self.assertEqual(len(asts), 2)
        self.assertEqual(asts[0], List([Symbol('def'), Symbol('x'), Number(1)]))
        self.assertEqual(asts[1], List([Symbol('def'), Symbol('y'), Number(2)]))

if __name__ == '__main__':
    unittest.main()
