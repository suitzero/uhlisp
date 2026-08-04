import unittest
import os
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all

class TestStdlib(unittest.TestCase):
    def test_optical_primitives_parsing(self):
        # Resolve path to the optical.uhl file
        filepath = os.path.join(os.path.dirname(__file__), '..', 'src', 'stdlib', 'optical.uhl')
        with open(filepath, 'r') as f:
            source_code = f.read()

        # Tokenize and parse the file
        tokens = tokenize(source_code)
        asts = parse_all(tokens)

        # Ensure that 3 expressions were parsed (splitter, phase-shifter, combiner)
        self.assertEqual(len(asts), 3)

        # Ensure the definitions have the correct names
        self.assertEqual(asts[0].elements[1].name, "splitter")
        self.assertEqual(asts[1].elements[1].name, "phase-shifter")
        self.assertEqual(asts[2].elements[1].name, "combiner")

if __name__ == '__main__':
    unittest.main()
