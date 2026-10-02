import unittest
import json
import yaml
from src.ir import Port, Component, Connection, Netlist

class TestIR(unittest.TestCase):
    def setUp(self):
        # Build a small two-stage optical block:
        # source -> splitter -> phase_shifter (top branch) -> combiner -> sink
        # bottom branch goes directly from splitter to combiner
        self.netlist = Netlist(
            components=[
                Component(
                    name="source1", 
                    type="source", 
                    ports=[Port("out", "output")]
                ),
                Component(
                    name="split1",
                    type="splitter",
                    ports=[Port("in", "input"), Port("out1", "output"), Port("out2", "output")]
                ),
                Component(
                    name="ps1",
                    type="phase_shifter",
                    ports=[Port("in", "input"), Port("out", "output")],
                    params={"phase": 1.57}
                ),
                Component(
                    name="comb1",
                    type="combiner",
                    ports=[Port("in1", "input"), Port("in2", "input"), Port("out", "output")]
                ),
                Component(
                    name="sink1",
                    type="sink",
                    ports=[Port("in", "input")]
                )
            ],
            connections=[
                Connection("source1", "out", "split1", "in"),
                Connection("split1", "out1", "ps1", "in"),
                Connection("split1", "out2", "comb1", "in2"),
                Connection("ps1", "out", "comb1", "in1"),
                Connection("comb1", "out", "sink1", "in")
            ]
        )

    def test_validation_success(self):
        # Should not raise any exceptions
        self.netlist.validate()

    def test_duplicate_component(self):
        netlist = Netlist(
            components=[
                Component("c1", "source", [Port("out", "output")]),
                Component("c1", "sink", [Port("in", "input")])
            ],
            connections=[Connection("c1", "out", "c1", "in")]
        )
        with self.assertRaisesRegex(ValueError, "Duplicate component name: c1"):
            netlist.validate()

    def test_dangling_connection_comp_not_found(self):
        netlist = Netlist(
            components=[
                Component("c1", "source", [Port("out", "output")])
            ],
            connections=[Connection("c1", "out", "c2", "in")]
        )
        with self.assertRaisesRegex(ValueError, "Dangling connection: sink component c2 not found"):
            netlist.validate()

    def test_dangling_connection_port_not_found(self):
        netlist = Netlist(
            components=[
                Component("c1", "source", [Port("out", "output")]),
                Component("c2", "sink", [Port("in", "input")])
            ],
            connections=[Connection("c1", "wrong_port", "c2", "in")]
        )
        with self.assertRaisesRegex(ValueError, "Dangling connection: port wrong_port not found on component c1"):
            netlist.validate()

    def test_unconnected_port(self):
        netlist = Netlist(
            components=[
                Component("c1", "source", [Port("out", "output"), Port("unused", "output")]),
                Component("c2", "sink", [Port("in", "input")])
            ],
            connections=[Connection("c1", "out", "c2", "in")]
        )
        with self.assertRaisesRegex(ValueError, "Unconnected port: unused on component c1"):
            netlist.validate()

    def test_json_serialization(self):
        json_str = self.netlist.to_json()
        loaded_netlist = Netlist.from_json(json_str)
        self.assertEqual(self.netlist, loaded_netlist)

    def test_yaml_serialization(self):
        yaml_str = self.netlist.to_yaml()
        loaded_netlist = Netlist.from_yaml(yaml_str)
        self.assertEqual(self.netlist, loaded_netlist)

if __name__ == '__main__':
    unittest.main()
