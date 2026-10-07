import unittest
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all
from src.frontend.macro import MacroExpander, MacroError
from src.frontend.ast import List, Symbol, Number

class TestDefmodule(unittest.TestCase):
    def setUp(self):
        self.expander = MacroExpander()

    def test_defmodule_parsing(self):
        source = "(defmodule mzi (in1 in2 out1 out2) (splitter in1 in2 mid1 mid2) (combiner mid1 mid2 out1 out2))"
        tokens = tokenize(source)
        asts = parse_all(tokens)
        
        remaining = self.expander.extract_macros(asts)
        
        self.assertEqual(len(remaining), 0)
        self.assertIn("mzi", self.expander.modules)
        
        ports, body_elements = self.expander.modules["mzi"]
        self.assertEqual(ports, ["in1", "in2", "out1", "out2"])
        
        self.assertEqual(len(body_elements), 2)
        
        expected_body_1 = List([Symbol("splitter"), Symbol("in1"), Symbol("in2"), Symbol("mid1"), Symbol("mid2")])
        expected_body_2 = List([Symbol("combiner"), Symbol("mid1"), Symbol("mid2"), Symbol("out1"), Symbol("out2")])
        
        self.assertEqual(body_elements[0], expected_body_1)
        self.assertEqual(body_elements[1], expected_body_2)

    def test_module_instantiation(self):
        source = """
        (defmodule mzi (in1 in2 out1 out2) 
            (splitter in1 in2 mid1 mid2) 
            (combiner mid1 mid2 out1 out2))
        (mzi portA portB portC portD)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)
        
        remaining = self.expander.extract_macros(asts)
        self.assertEqual(len(remaining), 1)
        
        expanded = self.expander.expand(remaining[0])
        
        # Expected expansion:
        # ( (splitter portA portB mid1_mzi_1 mid2_mzi_1) (combiner mid1_mzi_1 mid2_mzi_1 portC portD) )
        expected = List([
            List([Symbol("splitter"), Symbol("portA"), Symbol("portB"), Symbol("mid1_mzi_1"), Symbol("mid2_mzi_1")]),
            List([Symbol("combiner"), Symbol("mid1_mzi_1"), Symbol("mid2_mzi_1"), Symbol("portC"), Symbol("portD")])
        ])
        
        self.assertEqual(expanded, expected)

    def test_nested_defmodule(self):
        source = """
        (defmodule simple-split (in-port out1 out2)
            (splitter in-port none out1 out2))
            
        (defmodule double-split (in-port final1 final2 final3 final4)
            (simple-split in-port mid1 mid2)
            (simple-split mid1 final1 final2)
            (simple-split mid2 final3 final4))
            
        (double-split start p1 p2 p3 p4)
        """
        tokens = tokenize(source)
        asts = parse_all(tokens)
        
        remaining = self.expander.extract_macros(asts)
        self.assertEqual(len(remaining), 1)
        
        expanded = self.expander.expand(remaining[0])
        
        # Expected expansion:
        expected = List([
            List([ List([Symbol("splitter"), Symbol("start"), Symbol("none_simple-split_2"), Symbol("mid1_double-split_1"), Symbol("mid2_double-split_1")]) ]),
            List([ List([Symbol("splitter"), Symbol("mid1_double-split_1"), Symbol("none_simple-split_3"), Symbol("p1"), Symbol("p2")]) ]),
            List([ List([Symbol("splitter"), Symbol("mid2_double-split_1"), Symbol("none_simple-split_4"), Symbol("p3"), Symbol("p4")]) ])
        ])
        
        self.assertEqual(expanded, expected)

    def test_module_error_wrong_args(self):
        source = "(defmodule my-mod (a) (print a)) (my-mod 1 2)"
        tokens = tokenize(source)
        asts = parse_all(tokens)
        
        remaining = self.expander.extract_macros(asts)
        with self.assertRaises(MacroError):
            self.expander.expand(remaining[0])

if __name__ == '__main__':
    unittest.main()
