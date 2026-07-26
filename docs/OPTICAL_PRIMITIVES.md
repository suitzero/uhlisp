# Optical Primitives in uhlisp

This document describes the foundational optical primitives provided by the `uhlisp` standard library. These primitives act as the basic building blocks for defining optical tensor cores and related hardware architectures.

## Motivation

To synthesize hardware directly from S-expressions, we need minimal core forms that map to physical optical components. These components are implemented using standard Lisp `lambda` closures that generate abstract nodes (data representing the component).

## Core Primitives

The initial primitives are defined in `src/stdlib/optical.uhl`.

### 1. Splitter (`splitter`)
- **Purpose**: Represents a 1x2 optical splitter (like a Y-branch or 50/50 directional coupler) that takes one input signal and divides it into two output signals.
- **Syntax**: `(splitter in_signal)`
- **Node Output**: Evaluates to `(node "splitter" in_signal)` representing the physical branching point.

### 2. Phase Shifter (`phase-shifter`)
- **Purpose**: Represents a phase shifting element (like a thermo-optic or electro-optic phase shifter). It modifies the phase of the input signal by a given angle `theta`.
- **Syntax**: `(phase-shifter in_signal theta)`
- **Node Output**: Evaluates to `(node "phase-shifter" in_signal theta)`.

### 3. Combiner (`combiner`)
- **Purpose**: Represents a 2x1 optical combiner (e.g., merging two signals and causing interference based on their phases and amplitudes).
- **Syntax**: `(combiner in_signal1 in_signal2)`
- **Node Output**: Evaluates to `(node "combiner" in_signal1 in_signal2)`.

## Integration with the AST

These primitive definitions use the `quote` special form. For example, `(quote (node "splitter" in_signal))` tells the evaluator not to evaluate the `node` list, but to return it as a structured data representation (an AST list node). Later compiler passes (macro expansion, IR lowering) will interpret these `node` structures and synthesize the final netlist/IR for photonic simulation.
