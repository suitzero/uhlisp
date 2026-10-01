import copy
from typing import List as TList, Dict, Any
from src.frontend.ast import ASTNode, Symbol, List

class MacroExpanderError(Exception):
    pass

class MacroExpander:
    def __init__(self):
        # Maps macro name to a tuple of (parameters, body_nodes)
        self.macros: Dict[str, tuple[TList[str], TList[ASTNode]]] = {}

    def expand_all(self, nodes: TList[ASTNode]) -> TList[ASTNode]:
        """Expands all macros in a list of top-level AST nodes."""
        expanded_nodes = []
        for node in nodes:
            expanded = self.expand(node)
            if expanded is not None:
                expanded_nodes.append(expanded)
        return expanded_nodes

    def expand(self, node: ASTNode) -> ASTNode | None:
        """
        Expands a single AST node recursively.
        Returns None if the node was a macro definition (which is removed from output).
        """
        if not isinstance(node, List):
            return node

        if not node.elements:
            return node

        first = node.elements[0]

        # Check for defmacro
        if isinstance(first, Symbol) and first.name == 'defmacro':
            self._define_macro(node)
            return None

        # Check for macro call
        if isinstance(first, Symbol) and first.name in self.macros:
            return self._expand_macro_call(first.name, node.elements[1:])

        # Otherwise recursively expand list elements
        expanded_elements = []
        for elem in node.elements:
            expanded_elem = self.expand(elem)
            if expanded_elem is not None:
                expanded_elements.append(expanded_elem)
        return List(expanded_elements)

    def _define_macro(self, node: List):
        if len(node.elements) < 4:
            raise MacroExpanderError("Invalid defmacro: requires name, params, and body")

        name_node = node.elements[1]
        if not isinstance(name_node, Symbol):
            raise MacroExpanderError(f"Invalid defmacro: name must be a symbol, got {type(name_node)}")

        params_node = node.elements[2]
        if not isinstance(params_node, List):
            raise MacroExpanderError("Invalid defmacro: parameters must be a list")

        params = []
        for p in params_node.elements:
            if not isinstance(p, Symbol):
                raise MacroExpanderError(f"Invalid defmacro: parameter must be a symbol, got {type(p)}")
            params.append(p.name)

        body = node.elements[3:]
        self.macros[name_node.name] = (params, body)

    def _expand_macro_call(self, macro_name: str, args: TList[ASTNode]) -> ASTNode:
        params, body = self.macros[macro_name]

        if len(args) != len(params):
            raise MacroExpanderError(f"Macro {macro_name} expects {len(params)} arguments, got {len(args)}")

        # Bind parameters to arguments
        bindings = dict(zip(params, args))

        # Substitute in body
        substituted_body = [self._substitute(n, bindings) for n in body]

        # The body is a sequence of expressions. Usually macros evaluate to a single form.
        # If there are multiple, we might wrap in a 'progn' or just expand the last.
        # But commonly in Lisp S-exprs without 'progn' we assume the macro body evaluates to a single list element,
        # or we wrap it in a 'begin'. For a simplistic HDL AST, let's assume body contains exactly 1 expression
        # representing the expanded hardware node, or we wrap it.
        # Actually, let's just return a List if there are multiple, or just the single item.
        if len(substituted_body) == 1:
            expanded_node = substituted_body[0]
        else:
            expanded_node = List([Symbol('begin')] + substituted_body)

        # Recursively expand the result (to handle nested/recursive macros)
        return self.expand(expanded_node)

    def _substitute(self, node: ASTNode, bindings: Dict[str, ASTNode]) -> ASTNode:
        if isinstance(node, Symbol):
            if node.name in bindings:
                # Deep copy to avoid mutating the original arguments if they are substituted multiple times
                return copy.deepcopy(bindings[node.name])
            return node

        if isinstance(node, List):
            return List([self._substitute(elem, bindings) for elem in node.elements])

        # Numbers, Strings, Booleans, etc.
        return node
