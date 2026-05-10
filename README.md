# uhlisp

**A Lisp-Dialect Hardware Description Language for Optical Tensor Cores**

`uhlisp` is a minimalist Hardware Description Language (HDL) rooted in the Lisp paradigm, specifically designed for synthesizing and defining optical tensor cores. By leveraging Lisp's homoiconicity (code-as-data), `uhlisp` utilizes powerful macros to abstract complex low-level physical interactions and logic gates into scalable optical architectures.

Author: Hagyoon Choi

## Core Philosophy
* **Homoiconicity for Hardware:** Hardware modules are S-expressions. Meta-programming directly generates circuit netlists.
* **Von Neumann to Photonic:** Bridging traditional low-level hardware design concepts with continuous-wave optical logic.
* **Minimalist Syntax:** Driven by `def` paradigms and first-principles logic structuring.

## Architecture
1. **Parser & Lexer:** A lightweight frontend to parse S-expressions into Abstract Syntax Trees (AST).
2. **Macro Expander:** The core engine translating high-level tensor abstractions into low-level optical gate netlists.
3. **Netlist Emitter:** Compiles the AST into an intermediate representation (IR) compatible with photonic simulation tools (like `uh-fdtd`).

## Planning & Roadmap

### Phase 1: Lisp Frontend Foundation
- [ ] Define the core language specification (S-expressions, primitives).
- [x] Implement the Lexer and Parser to construct the AST.
- [ ] Build the REPL environment for real-time hardware component definitions.

### Phase 2: Hardware Primitives & Macro System
- [ ] Define basic optical logic primitives (Splitters, Phase Shifters, Combiners) as foundational Lisp functions.
- [ ] Implement the Macro system (`defmacro`) to allow recursive hardware generation.
- [ ] Construct the `defmodule` syntax for encapsulating optical circuit blocks.

### Phase 3: Synthesis & Netlist Generation
- [ ] Develop the intermediate representation (IR) for optical routing.
- [ ] Implement the compiler pass that lowers AST S-expressions into a structured netlist (JSON/YAML).
- [ ] Write integration hooks to pipe the netlist directly into FDTD simulators.

### Phase 4: Tensor Core Architecture Implementation
- [ ] Write the `uhlisp` code to synthesize a 4x4 Optical MAC (Multiply-Accumulate) unit.
- [ ] Scale up to define a fully integrated Optical Tensor Core layout.