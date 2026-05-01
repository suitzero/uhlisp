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
class List(ASTNode):
    """Represents a Lisp list (S-expression)."""
    elements: TList[ASTNode]

    def __repr__(self) -> str:
        return f"List([{', '.join(repr(e) for e in self.elements)}])"
