# uhlisp Core Language Specification

## 1. Context & Philosophy

`uhlisp` is designed to be a minimal Lisp-dialect for hardware description and execution on tensor backends with actor-model concurrency support.
**Core Philosophy:** "Less is more." This specification defines ONLY the absolute minimum primitives necessary to bootstrap the language. All other features (math, logic, tensor operations, standard library) are implemented in `uhlisp` itself as standard library functions or macros. The core handles lazy evaluation (AST building) and actor-model concurrency.

## 2. Data Types & S-Expression Structure

The internal representation (IR) in `uhlisp` is designed for building computation graphs (AST nodes).

### Atoms
- **Symbol**: Represents variables and identifiers.
- **Number**: Numeric literals (integers, floats).
- **String**: String literals.
- **Boolean**: `true` and `false`.

### S-expressions (Lists)
- **List**: An ordered sequence of elements, representing either data or unevaluated function applications.

### Specialized Types for Laziness & Actors
- **Thunk**: Represents an unevaluated computation graph node. Instead of eagerly computing results, `uhlisp` constructs a Thunk.
- **PID**: A unique identifier for a spawned actor/process.

### Python Internal Representation (AST)

```python
from dataclasses import dataclass
from typing import Any, List as TList, Union

class ASTNode:
    pass

@dataclass
class Symbol(ASTNode):
    name: str

@dataclass
class Number(ASTNode):
    value: Union[int, float]

@dataclass
class String(ASTNode):
    value: str

@dataclass
class Boolean(ASTNode):
    value: bool

@dataclass
class List(ASTNode):
    elements: TList[ASTNode]

@dataclass
class Thunk(ASTNode):
    """Represents an unevaluated computation graph node (delayed expression)."""
    env: dict          # Lexical environment at the time of creation
    expr: ASTNode      # The expression to be evaluated when forced

@dataclass
class PID(ASTNode):
    """Process Identifier for an isolated actor."""
    id: int
```

## 3. The Minimal Primitives (Axioms)

These are the core primitives. Any other language feature must be built upon them.

### Core Lisp Forms
1. **`quote`**
   - **Syntax**: `(quote expr)` or `'expr`
   - **Behavior**: Returns `expr` exactly as-is without evaluating it.

2. **`lambda`**
   - **Syntax**: `(lambda (args...) body)`
   - **Behavior**: Creates a lexical closure. Captures the current environment and returns a callable function.

3. **`define`**
   - **Syntax**: `(define symbol expr)`
   - **Behavior**: Evaluates `expr` (or creates a Thunk based on evaluation rules) and binds it to `symbol` in the current environment.

4. **`if`**
   - **Syntax**: `(if condition true_branch false_branch)`
   - **Behavior**: Evaluates `condition`. If true, evaluates and returns `true_branch`; otherwise evaluates and returns `false_branch`.

### Lazy Evaluation Forms
5. **`delay`**
   - **Syntax**: `(delay expr)`
   - **Behavior**: Wraps `expr` in a `Thunk` capturing the current environment, preventing immediate evaluation.

6. **`force`**
   - **Syntax**: `(force thunk_expr)`
   - **Behavior**: Evaluates `thunk_expr` to yield a `Thunk`, then recursively evaluates the expression inside the `Thunk` in its captured environment to produce a value (or a deeper Thunk graph).

### Actor Model Forms
7. **`spawn`**
   - **Syntax**: `(spawn (lambda () body))`
   - **Behavior**: Spawns a new isolated worker/process with a copy of the current environment (or a fresh environment with specified closures) to execute the given function asynchronously. Returns a new `PID`.

8. **`send`**
   - **Syntax**: `(send pid message)`
   - **Behavior**: Asynchronously sends `message` (an evaluated expression) to the mailbox of the actor identified by `pid`. Returns immediately.

9. **`receive`**
   - **Syntax**: `(receive (pattern1 action1) (pattern2 action2) ...)`
   - **Behavior**: Blocks the current actor until a message matching one of the patterns arrives in its mailbox, then evaluates the corresponding action.

## 4. The Evaluation Strategy (eval / apply)

The evaluator recursively processes AST nodes within a given Environment (a mapping of Symbols to values/Thunks).

### Rule 1: Handling Forms vs. Application
When the evaluator encounters a List `(op arg1 arg2 ...)`:
- If `op` is a **Core Lisp Form** or **Primitive** (e.g., `if`, `define`, `quote`, `delay`), it applies the special evaluation rules associated with that form.
- If `op` evaluates to a closure (from `lambda`), it evaluates the arguments (depending on Rule 2) and applies the closure to the arguments.

### Rule 2: Thunk-by-Default (Lazy Application)
Unlike standard strict Lisps, application of non-primitive functions in `uhlisp` is lazy by default to support the generation of computation graphs.
- When applying a user-defined function (a closure) to arguments, the arguments are NOT fully evaluated to primitive values.
- Instead, applying a function naturally returns a `Thunk` (AST node representing the computation) rather than computing the result eagerly.
- This means executing `(f x)` yields a graph node representing the operation `f` over `x`.
- The actual execution of the graph happens ONLY when `(force ...)` is explicitly called, pushing the computation down to the tensor backend or optical simulator.

### Rule 3: Actor Environments
- **Isolation**: When `spawn` creates an actor, it does not share mutable state with its parent. The spawned closure captures the lexical environment (closures) strictly by value/reference in an immutable way.
- **Message Passing**: State mutation and coordination across different parts of the computation graph only occur via explicit message passing (`send` and `receive`), enforcing strict Actor-model semantics.
