import unittest
import os
from src.compiler import compile_source

class TestTensorCoreLayout(unittest.TestCase):
    def test_tensor_core_compilation(self):
        filepath = os.path.join(os.path.dirname(__file__), '..', 'src', 'tensor_core_layout.uhl')
        with open(filepath, 'r') as f:
            source = f.read()
            
        netlist = compile_source(source)
        
        # A 2x2 grid of mac4x4 components = 4 * 48 = 192 components
        self.assertEqual(len(netlist.components), 192, "Should have exactly 192 components (4x48)")
        
        types = [c.type for c in netlist.components]
        self.assertEqual(types.count('splitter'), 64)
        self.assertEqual(types.count('phase-shifter'), 64)
        self.assertEqual(types.count('combiner'), 64)
        
        # Internal connections:
        # Each mac4x4 has 56 internal connections. 4 * 56 = 224
        # Tiling connections:
        # 2x2 grid has 4 mac4x4 blocks.
        # X outputs of MAC(r, c) go to X inputs of MAC(r, c+1)
        # There are 2 rows, each has 1 boundary between c=0 and c=1.
        # Boundary size = 4 wires. Total X tiling wires = 2 * 4 = 8
        # Y outputs of MAC(r, c) go to Y inputs of MAC(r+1, c)
        # There are 2 cols, each has 1 boundary between r=0 and r=1.
        # Boundary size = 4 wires. Total Y tiling wires = 2 * 4 = 8
        # Total tiling wires = 16.
        # But wait, does Netlist emit these as connections? Yes, because they are internal nets.
        # Wait, the wires are named int_x_... and int_y_...
        # Let's count total nets.
        # In a MAC block, each internal connection is 1 source -> 1 sink.
        # Tiling connections are also 1 source -> 1 sink.
        # So we should have 224 + 16 = 240 connections.
        
        self.assertEqual(len(netlist.connections), 240, "Should have 240 internal connections")

if __name__ == '__main__':
    unittest.main()
