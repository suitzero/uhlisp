from typing import List as TList, Dict, Tuple, Any
from src.frontend.ast import List, Symbol, Number
from src.frontend.lexer import tokenize
from src.frontend.parser import parse_all
from src.frontend.macro import MacroExpander
from src.ir import Netlist, Component, Port, Connection

class CompilerError(Exception):
    pass

PORT_SPECS = {
    "splitter": [("in", "input"), ("out1", "output"), ("out2", "output")],
    "phase-shifter": [("in", "input"), ("out", "output")],
    "combiner": [("in1", "input"), ("in2", "input"), ("out", "output")]
}

PARAM_NAMES = {
    "phase-shifter": ["theta"]
}

def compile_netlist(module_name: str, ports: TList[str], body_elements: TList[List]) -> Netlist:
    components: TList[Component] = []
    # Dictionary tracking which instance port is connected to which net.
    # Maps net_name -> list of (instance_name, port_name, direction)
    nets: Dict[str, TList[Tuple[str, str, str]]] = {}
    
    type_counts: Dict[str, int] = {}
    
    for element in body_elements:
        if not element.elements:
            continue
            
        head = element.elements[0]
        if not isinstance(head, Symbol):
            raise CompilerError(f"Expected symbol at head of component definition, got {head}")
            
        comp_type = head.name
        if comp_type not in PORT_SPECS:
            raise CompilerError(f"Unknown component type: {comp_type}")
            
        type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        instance_name = f"{comp_type}_{type_counts[comp_type]}"
        
        args = element.elements[1:]
        
        port_spec = PORT_SPECS[comp_type]
        param_names = PARAM_NAMES.get(comp_type, [])
        
        comp_ports = []
        comp_params = {}
        
        for i, arg in enumerate(args):
            if i < len(port_spec):
                if not isinstance(arg, Symbol):
                    raise CompilerError(f"Expected symbol for port connection, got {arg}")
                
                port_name, direction = port_spec[i]
                comp_ports.append(Port(name=port_name, direction=direction))
                
                net_name = arg.name
                if net_name not in nets:
                    nets[net_name] = []
                nets[net_name].append((instance_name, port_name, direction))
            else:
                param_idx = i - len(port_spec)
                if param_idx < len(param_names):
                    param_name = param_names[param_idx]
                    if isinstance(arg, Number):
                        comp_params[param_name] = arg.value
                    elif isinstance(arg, Symbol):
                        # We might allow symbols as parameters? The test asks for numeric theta arg.
                        comp_params[param_name] = arg.name
                    else:
                        raise CompilerError(f"Unexpected parameter type: {arg}")
                else:
                    # Surplus positional arg with no mapped name
                    pass
        
        # Check if we got enough args for the ports?
        # A simple implementation can just be flexible for now, or we can check length.
        components.append(Component(
            name=instance_name,
            type=comp_type,
            ports=comp_ports,
            params=comp_params
        ))
        
    connections: TList[Connection] = []
    external_nets = set(ports)
    
    for net_name, endpoints in nets.items():
        if net_name in external_nets:
            continue
            
        sources = [ep for ep in endpoints if ep[2] == "output"]
        sinks = [ep for ep in endpoints if ep[2] == "input"]
        
        # A net might be connected to one source and multiple sinks
        for src_inst, src_port, _ in sources:
            for sink_inst, sink_port, _ in sinks:
                connections.append(Connection(
                    source_comp=src_inst,
                    source_port=src_port,
                    sink_comp=sink_inst,
                    sink_port=sink_port
                ))
                
    return Netlist(components=components, connections=connections)


def flatten_ast(node: List) -> TList[List]:
    if not isinstance(node, List) or not node.elements:
        return []
    head = node.elements[0]
    if not isinstance(head, List):
        return [node]
    flat = []
    for elem in node.elements:
        if isinstance(elem, List):
            flat.extend(flatten_ast(elem))
    return flat

def compile_source(source: str) -> Netlist:
    tokens = tokenize(source)
    asts = parse_all(tokens)
    
    expander = MacroExpander()
    expander.extract_macros(asts)
    
    if not expander.modules:
        raise CompilerError("No defmodule found in source")
        
    # Get the last module defined as the top-level module
    module_name = list(expander.modules.keys())[-1]
    ports, body_elements = expander.modules[module_name]
    
    # Expand nested modules in body elements
    expanded_body = [expander.expand(elem) for elem in body_elements]
    
    # Flatten the expanded ASTs to a simple list of primitives
    flat_body = []
    for elem in expanded_body:
        if isinstance(elem, List):
            flat_body.extend(flatten_ast(elem))
    
    return compile_netlist(module_name, ports, flat_body)
