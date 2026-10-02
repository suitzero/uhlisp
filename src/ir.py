import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class Port:
    name: str
    direction: str  # 'input' or 'output'

@dataclass
class Component:
    name: str
    type: str
    ports: List[Port] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Connection:
    source_comp: str
    source_port: str
    sink_comp: str
    sink_port: str

@dataclass
class Netlist:
    components: List[Component] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)

    def validate(self):
        # check for duplicate component names
        comp_names = set()
        for comp in self.components:
            if comp.name in comp_names:
                raise ValueError(f"Duplicate component name: {comp.name}")
            comp_names.add(comp.name)
        
        # dangling connections & track connected ports
        connected_ports = {comp.name: set() for comp in self.components}
        
        for conn in self.connections:
            if conn.source_comp not in comp_names:
                raise ValueError(f"Dangling connection: source component {conn.source_comp} not found")
            if conn.sink_comp not in comp_names:
                raise ValueError(f"Dangling connection: sink component {conn.sink_comp} not found")
            
            # ensure ports exist on components
            source_comp = next(c for c in self.components if c.name == conn.source_comp)
            sink_comp = next(c for c in self.components if c.name == conn.sink_comp)
            
            source_port_names = [p.name for p in source_comp.ports]
            if conn.source_port not in source_port_names:
                raise ValueError(f"Dangling connection: port {conn.source_port} not found on component {conn.source_comp}")
                
            sink_port_names = [p.name for p in sink_comp.ports]
            if conn.sink_port not in sink_port_names:
                raise ValueError(f"Dangling connection: port {conn.sink_port} not found on component {conn.sink_comp}")
                
            connected_ports[conn.source_comp].add(conn.source_port)
            connected_ports[conn.sink_comp].add(conn.sink_port)
            
        # check for unconnected ports
        for comp in self.components:
            for port in comp.ports:
                if port.name not in connected_ports[comp.name]:
                    raise ValueError(f"Unconnected port: {port.name} on component {comp.name}")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        components = []
        for comp_data in data.get('components', []):
            ports = [Port(**p) for p in comp_data.get('ports', [])]
            components.append(Component(
                name=comp_data['name'],
                type=comp_data['type'],
                ports=ports,
                params=comp_data.get('params', {})
            ))
            
        connections = [Connection(**c) for c in data.get('connections', [])]
        return cls(components=components, connections=connections)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str):
        return cls.from_dict(yaml.safe_load(yaml_str))
