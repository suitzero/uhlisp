import unittest
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all
from src.frontend.ast import Symbol, Number, List
from src.frontend.macro_expander import MacroExpander, MacroExpanderError

class TestMacroExpander(unittest.TestCase):
    def setUp(self):
        self.expander = MacroExpander()

    def test_basic_macro_definition_and_expansion(self):
        source = """
        (defmacro identity (x) x)
        (identity 42)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)

        expanded = self.expander.expand_all(asts)

        # The defmacro should be removed, leaving only the expanded call
        self.assertEqual(len(expanded), 1)
        self.assertEqual(expanded[0], Number(42))

    def test_macro_with_multiple_parameters(self):
        source = """
        (defmacro add-nodes (a b) (+ a b))
        (add-nodes 10 20)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)

        expanded = self.expander.expand_all(asts)

        self.assertEqual(len(expanded), 1)
        self.assertEqual(expanded[0], List([Symbol('+'), Number(10), Number(20)]))

    def test_recursive_macro_expansion(self):
        source = """
        (defmacro inner-mac (y) (* y 2))
        (defmacro outer-mac (x) (inner-mac (+ x 1)))
        (outer-mac 5)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)

        expanded = self.expander.expand_all(asts)

        self.assertEqual(len(expanded), 1)
        # Should expand to (* (+ 5 1) 2)
        expected = List([Symbol('*'), List([Symbol('+'), Number(5), Number(1)]), Number(2)])
        self.assertEqual(expanded[0], expected)

    def test_macro_error_invalid_args(self):
        source = """
        (defmacro foo (x) x)
        (foo 1 2)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)

        with self.assertRaises(MacroExpanderError):
            self.expander.expand_all(asts)

if __name__ == '__main__':
    unittest.main()
