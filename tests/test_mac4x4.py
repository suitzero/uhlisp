import unittest
import os
from src.compiler import compile_source
from src.ir import Netlist
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all
from src.frontend.macro import MacroExpander

class TestMac4x4(unittest.TestCase):
    def test_mac4x4_compilation(self):
        # Load the source code
        filepath = os.path.join(os.path.dirname(__file__), '..', 'src', 'mac4x4.uhl')
        with open(filepath, 'r') as f:
            mac_source = f.read()
        
        netlist = compile_source(mac_source)
        
        self.assertEqual(len(netlist.components), 48, "Should have exactly 48 components")
        
        types = [c.type for c in netlist.components]
        self.assertEqual(types.count('splitter'), 16)
        self.assertEqual(types.count('phase-shifter'), 16)
        self.assertEqual(types.count('combiner'), 16)
        
        # 4x4 cell has:
        # 16 splitters * 3 ports = 48
        # 16 phase-shifters * 2 ports = 32
        # 16 combiners * 3 ports = 48
        # Total ports = 128
        # Expected internal connections:
        # mid1 nets: 16 (splitter -> phase-shifter)
        # mid2 nets: 16 (phase-shifter -> combiner)
        # x_i routing nets: 12 (splitter -> splitter)
        # y_i routing nets: 12 (combiner -> combiner)
        # Total internal connections = 56
        self.assertEqual(len(netlist.connections), 56, "Should have 56 internal connections")
        
        # Validate that all ports are accounted for (no dangling nets)
        # We manually check since `netlist.validate()` fails on external boundary nets.
        
        # Determine the module ports from the source
        # Collect internally connected ports
        internally_connected = set()
        for conn in netlist.connections:
            internally_connected.add((conn.source_comp, conn.source_port))
            internally_connected.add((conn.sink_comp, conn.sink_port))
            
        # Re-parse body elements to see what is mapped to module ports
        # (Alternatively, simply ensure that every unconnected port is intended to be external)
        # Actually, in the FDTD hooks or netlist there's no explicit list of external nets,
        # but we know that 128 - (56 * 2) = 16 ports should be external.
        # Wait, 56 connections means 112 connected ports.
        # 128 total ports - 112 internally connected = 16 unconnected (external) ports.
        # Let's count them!
        
        external_count = 0
        for comp in netlist.components:
            for port in comp.ports:
                if (comp.name, port.name) not in internally_connected:
                    external_count += 1
                    
        self.assertEqual(external_count, 128 - 112, "Exactly 16 ports should connect to the boundary")

if __name__ == '__main__':
    unittest.main()
