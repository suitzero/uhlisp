import unittest
from src.compiler import compile_source, CompilerError
from src.ir import Netlist

class TestCompiler(unittest.TestCase):
    def test_mzi_example(self):
        # We use a 1x1 MZI to match the 3-port specs for splitter/combiner
        # and to yield exactly 2 internal connections (mid1, mid2).
        source = """
        (defmodule mzi (in out)
            (splitter in mid1 mid2)
            (combiner mid1 mid2 out))
        """
        netlist = compile_source(source)
        
        # exactly 2 components with types splitter/combiner and correct instance names
        self.assertEqual(len(netlist.components), 2)
        comp_types = {c.type for c in netlist.components}
        self.assertEqual(comp_types, {"splitter", "combiner"})
        comp_names = {c.name for c in netlist.components}
        self.assertEqual(comp_names, {"splitter_1", "combiner_1"})
        
        # exactly 2 internal Connections (nets mid1, mid2)
        self.assertEqual(len(netlist.connections), 2)
        
        # Verify connections map mid1 and mid2 correctly
        # In our mapping, splitter outputs are out1, out2 connected to mid1, mid2
        # combiner inputs are in1, in2 connected to mid1, mid2
        sources = {(c.source_comp, c.source_port) for c in netlist.connections}
        sinks = {(c.sink_comp, c.sink_port) for c in netlist.connections}
        
        self.assertEqual(sources, {("splitter_1", "out1"), ("splitter_1", "out2")})
        self.assertEqual(sinks, {("combiner_1", "in1"), ("combiner_1", "in2")})

    def test_phase_shifter_numeric_theta(self):
        source = """
        (defmodule ps_mod (in_port out_port)
            (phase-shifter in_port out_port 3.14))
        """
        netlist = compile_source(source)
        self.assertEqual(len(netlist.components), 1)
        comp = netlist.components[0]
        self.assertEqual(comp.type, "phase-shifter")
        self.assertEqual(comp.params.get("theta"), 3.14)
        
    def test_json_round_trip(self):
        source = """
        (defmodule mzi (in out)
            (splitter in mid1 mid2)
            (combiner mid1 mid2 out))
        """
        netlist = compile_source(source)
        json_str = netlist.to_json()
        restored = Netlist.from_json(json_str)
        self.assertEqual(netlist, restored)
        
    def test_unknown_component_type(self):
        source = """
        (defmodule bad_mod (in out)
            (magic_box in out))
        """
        with self.assertRaises(CompilerError):
            compile_source(source)

if __name__ == '__main__':
    unittest.main()
