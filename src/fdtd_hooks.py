from typing import Dict, Any
from src.ir import Netlist

DEFAULT_GRID_SHAPE = (100, 100)
DEFAULT_DX = 0.1
DEFAULT_DY = 0.1
DEFAULT_DT = 0.05
DEFAULT_EPS_BG = 1.0
DEFAULT_EPS_WG = 4.0
DEFAULT_FREQ = 2.0
DEFAULT_SOURCE_LOC = (10, 50)
DEFAULT_TARGET_LOC = (90, 50)

SUPPORTED_PRIMITIVES = {"splitter", "phase-shifter", "combiner"}

def generate_fdtd_spec(netlist: Netlist) -> Dict[str, Any]:
    """
    Converts a compiler Netlist into a uh-fdtd input specification dictionary.
    """
    for comp in netlist.components:
        if comp.type not in SUPPORTED_PRIMITIVES:
            raise ValueError(f"Unsupported primitive for FDTD simulation: '{comp.type}'")

    # Serialize components and connections directly from the netlist
    netlist_dict = netlist.to_dict()
    components = netlist_dict.get("components", [])
    connections = netlist_dict.get("connections", [])

    spec = {
        "grid_shape": DEFAULT_GRID_SHAPE,
        "grid_params": {
            "dx": DEFAULT_DX,
            "dy": DEFAULT_DY,
            "dt": DEFAULT_DT
        },
        "materials": {
            "eps_bg": DEFAULT_EPS_BG,
            "eps_wg": DEFAULT_EPS_WG
        },
        "source": {
            "location": DEFAULT_SOURCE_LOC,
            "frequency": DEFAULT_FREQ
        },
        "target": {
            "location": DEFAULT_TARGET_LOC
        },
        "components": components,
        "connections": connections
    }
    
    return spec
