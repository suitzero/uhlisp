import unittest
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all
from src.frontend.macro import MacroExpander, MacroError
from src.frontend.ast import List, Symbol, Number, String

class TestMacroSystem(unittest.TestCase):
    def setUp(self):
        self.expander = MacroExpander()

    def test_macro_definition(self):
        source = "(defmacro my-mac (a b) (+ a b))"
        tokens = tokenize(source)
        asts = parse_all(tokens)

        remaining = self.expander.extract_macros(asts)

        self.assertEqual(len(remaining), 0)
        self.assertIn("my-mac", self.expander.macros)

        params, body = self.expander.macros["my-mac"]
        self.assertEqual(params, ["a", "b"])

        expected_body = List([Symbol("+"), Symbol("a"), Symbol("b")])
        self.assertEqual(body, expected_body)

    def test_basic_expansion(self):
        source = "(defmacro inc (x) (+ x 1)) (inc 5)"
        tokens = tokenize(source)
        asts = parse_all(tokens)

        remaining = self.expander.extract_macros(asts)
        self.assertEqual(len(remaining), 1)

        expanded = self.expander.expand(remaining[0])

        expected = List([Symbol("+"), Number(5), Number(1)])
        self.assertEqual(expanded, expected)

    def test_recursive_expansion(self):
        source = """
        (defmacro inc (x) (+ x 1))
        (defmacro double-inc (y) (inc (inc y)))
        (double-inc 10)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)

        remaining = self.expander.extract_macros(asts)
        self.assertEqual(len(remaining), 1)

        expanded = self.expander.expand(remaining[0])

        # (double-inc 10)
        # -> (inc (inc 10))
        # -> (inc (+ 10 1))
        # -> (+ (+ 10 1) 1)
        expected = List([
            Symbol("+"),
            List([Symbol("+"), Number(10), Number(1)]),
            Number(1)
        ])

        self.assertEqual(expanded, expected)

    def test_macro_error_wrong_args(self):
        source = "(defmacro my-mac (a) (print a)) (my-mac 1 2)"
        tokens = tokenize(source)
        asts = parse_all(tokens)

        remaining = self.expander.extract_macros(asts)
        with self.assertRaises(MacroError):
            self.expander.expand(remaining[0])

if __name__ == '__main__':
    unittest.main()
