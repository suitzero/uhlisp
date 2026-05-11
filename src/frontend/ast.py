from typing import Any, List as TList, Union
from dataclasses import dataclass

class ASTNode:
    """Base class for all AST nodes."""
    pass

@dataclass
class Symbol(ASTNode):
    """Represents a Lisp symbol (e.g., variables, function names)."""
    name: str

    def __repr__(self) -> str:
        return f"Symbol({self.name})"

@dataclass
class Number(ASTNode):
    """Represents a numeric literal."""
    value: Union[int, float]

    def __repr__(self) -> str:
        return f"Number({self.value})"

@dataclass
class String(ASTNode):
    """Represents a string literal."""
    value: str

    def __repr__(self) -> str:
        return f"String('{self.value}')"

@dataclass
class Boolean(ASTNode):
    """Represents a boolean literal."""
    value: bool

    def __repr__(self) -> str:
        return f"Boolean({self.value})"

@dataclass
class List(ASTNode):
    """Represents a Lisp list (S-expression)."""
    elements: TList[ASTNode]

    def __repr__(self) -> str:
        return f"List([{', '.join(repr(e) for e in self.elements)}])"

@dataclass
class Thunk(ASTNode):
    """Represents an unevaluated computation graph node (delayed expression)."""
    env: dict
    expr: ASTNode

    def __repr__(self) -> str:
        return f"Thunk({self.expr})"

@dataclass
class PID(ASTNode):
    """Process Identifier for an isolated actor."""
    id: int

    def __repr__(self) -> str:
        return f"PID({self.id})"
