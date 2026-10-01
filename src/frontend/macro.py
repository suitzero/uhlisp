from typing import List as TList, Dict, Tuple
import copy
from src.frontend.ast import ASTNode, Symbol, List

class MacroError(Exception):
    pass

class MacroExpander:
    """
    Handles extraction and expansion of defmacro definitions.
    """
    def __init__(self):
        # Maps macro name -> (parameters, body)
        self.macros: Dict[str, Tuple[TList[str], ASTNode]] = {}
        # Maps module name -> (ports, body_elements)
        self.modules: Dict[str, Tuple[TList[str], TList[ASTNode]]] = {}

    def extract_macros(self, asts: TList[ASTNode]) -> TList[ASTNode]:
        """
        Iterates over ASTs, extracts (defmacro ...) definitions, 
        registers them, and returns the remaining ASTs.
        """
        remaining_asts = []
        for ast in asts:
            if self._is_macro_def(ast):
                self._register_macro(ast)
            elif self._is_module_def(ast):
                self._register_module(ast)
            else:
                remaining_asts.append(ast)
        return remaining_asts

    def _is_macro_def(self, ast: ASTNode) -> bool:
        if isinstance(ast, List) and len(ast.elements) >= 3:
            first = ast.elements[0]
            if isinstance(first, Symbol) and first.name == 'defmacro':
                return True
        return False

    def _is_module_def(self, ast: ASTNode) -> bool:
        if isinstance(ast, List) and len(ast.elements) >= 3:
            first = ast.elements[0]
            if isinstance(first, Symbol) and first.name == 'defmodule':
                return True
        return False

    def _register_macro(self, ast: List):
        # Format: (defmacro name (params...) body)
        if len(ast.elements) != 4:
            raise MacroError(f"Invalid defmacro syntax: {ast}")
        
        name_node = ast.elements[1]
        if not isinstance(name_node, Symbol):
            raise MacroError("Macro name must be a symbol")
        macro_name = name_node.name
        
        params_node = ast.elements[2]
        if not isinstance(params_node, List):
            raise MacroError("Macro parameters must be a list")
        
        params = []
        for p in params_node.elements:
            if not isinstance(p, Symbol):
                raise MacroError("Macro parameters must be symbols")
            params.append(p.name)
            
        body = ast.elements[3]
        self.macros[macro_name] = (params, body)

    def _register_module(self, ast: List):
        # Format: (defmodule name (ports...) body...)
        if len(ast.elements) < 4:
            raise MacroError(f"Invalid defmodule syntax: {ast}")
        
        name_node = ast.elements[1]
        if not isinstance(name_node, Symbol):
            raise MacroError("Module name must be a symbol")
        module_name = name_node.name
        
        ports_node = ast.elements[2]
        if not isinstance(ports_node, List):
            raise MacroError("Module ports must be a list")
        
        ports = []
        for p in ports_node.elements:
            if not isinstance(p, Symbol):
                raise MacroError("Module ports must be symbols")
            ports.append(p.name)
            
        body_elements = ast.elements[3:]
        self.modules[module_name] = (ports, body_elements)

    def expand(self, ast: ASTNode) -> ASTNode:
        """Recursively expands macros in the AST."""
        if not isinstance(ast, List):
            return ast

        if not ast.elements:
            return ast

        first = ast.elements[0]
        
        # If it's a macro invocation
        if isinstance(first, Symbol) and first.name in self.macros:
            macro_name = first.name
            args = ast.elements[1:]
            params, body = self.macros[macro_name]
            
            if len(args) != len(params):
                raise MacroError(f"Macro '{macro_name}' expects {len(params)} arguments, got {len(args)}")
            
            # Map parameters to arguments
            bindings = {param: arg for param, arg in zip(params, args)}
            
            # Substitute parameters with arguments in the body
            substituted = self._substitute(body, bindings)
            
            # Recursively expand the result (to support nested macros)
            return self.expand(substituted)
            
        # If it's a module invocation
        if isinstance(first, Symbol) and first.name in self.modules:
            module_name = first.name
            args = ast.elements[1:]
            ports, body_elements = self.modules[module_name]
            
            if len(args) != len(ports):
                raise MacroError(f"Module '{module_name}' expects {len(ports)} arguments, got {len(args)}")
            
            # Map ports to arguments
            bindings = {port: arg for port, arg in zip(ports, args)}
            
            # Substitute ports with arguments in all body elements
            substituted_body = [self._substitute(elem, bindings) for elem in body_elements]
            
            # Recursively expand the result, wrapped in a List
            # This turns the body elements into an S-expression sequence
            expanded_elements = [self.expand(elem) for elem in substituted_body]
            return List(expanded_elements)
        
        # Otherwise, expand all elements in the list recursively
        expanded_elements = [self.expand(elem) for elem in ast.elements]
        return List(expanded_elements)

    def _substitute(self, ast: ASTNode, bindings: Dict[str, ASTNode]) -> ASTNode:
        """AST-to-AST parameter substitution."""
        if isinstance(ast, Symbol):
            if ast.name in bindings:
                return copy.deepcopy(bindings[ast.name])
            return ast
        elif isinstance(ast, List):
            substituted_elements = [self._substitute(elem, bindings) for elem in ast.elements]
            return List(substituted_elements)
        else:
            return ast
