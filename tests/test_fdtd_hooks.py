import unittest
from src.compiler import compile_source
from src.ir import Netlist, Component
from src.fdtd_hooks import (
    generate_fdtd_spec,
    DEFAULT_GRID_SHAPE,
    DEFAULT_DX,
    DEFAULT_DY,
    DEFAULT_DT,
    DEFAULT_EPS_BG,
    DEFAULT_EPS_WG,
    DEFAULT_FREQ
)

class TestFDTDHooks(unittest.TestCase):
    def test_mzi_end_to_end(self):
        source = """
        (defmodule mzi (in out)
            (splitter in mid1 mid2)
            (combiner mid1 mid2 out))
        """
        netlist = compile_source(source)
        spec = generate_fdtd_spec(netlist)
        
        self.assertEqual(spec["grid_shape"], DEFAULT_GRID_SHAPE)
        self.assertEqual(spec["grid_params"]["dx"], DEFAULT_DX)
        self.assertEqual(spec["grid_params"]["dy"], DEFAULT_DY)
        self.assertEqual(spec["grid_params"]["dt"], DEFAULT_DT)
        
        self.assertEqual(spec["materials"]["eps_bg"], DEFAULT_EPS_BG)
        self.assertEqual(spec["materials"]["eps_wg"], DEFAULT_EPS_WG)
        
        self.assertEqual(spec["source"]["frequency"], DEFAULT_FREQ)
        
        self.assertEqual(len(spec["components"]), 2)
        comp_types = {c["type"] for c in spec["components"]}
        self.assertEqual(comp_types, {"splitter", "combiner"})
        
        self.assertEqual(len(spec["connections"]), 2)
        
    def test_unsupported_primitive(self):
        # We manually construct a netlist with an unsupported primitive
        netlist = Netlist(
            components=[Component(name="bad_comp_1", type="magic_box", ports=[])],
            connections=[]
        )
        with self.assertRaises(ValueError) as context:
            generate_fdtd_spec(netlist)
            
        self.assertIn("Unsupported primitive for FDTD simulation: 'magic_box'", str(context.exception))

    def test_defaults(self):
        netlist = Netlist(components=[], connections=[])
        spec = generate_fdtd_spec(netlist)
        
        self.assertEqual(spec["grid_shape"], (100, 100))
        self.assertEqual(spec["grid_params"]["dx"], 0.1)
        self.assertEqual(spec["grid_params"]["dy"], 0.1)
        self.assertEqual(spec["grid_params"]["dt"], 0.05)
        self.assertEqual(spec["materials"]["eps_bg"], 1.0)
        self.assertEqual(spec["materials"]["eps_wg"], 4.0)
        self.assertEqual(spec["source"]["frequency"], 2.0)

if __name__ == '__main__':
    unittest.main()
