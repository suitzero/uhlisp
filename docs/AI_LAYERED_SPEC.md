# uhlisp: AI-Driven Layered Specification

## 1. Context & Philosophy

The design of the `uhlisp` language and its compiler relies heavily on two guiding principles:
1. **Less is More:** The frontend S-expression syntax must be kept absolutely minimal.
2. **AI-Driven Compilation:** The compiler takes on the heavy lifting. Through the use of AI (inference, auto-sharding, ML-based optimizations), it infers intent, optimizes graphs, and handles the low-level complexities that the user leaves unspecified.

This layered specification outlines the core primitives available to the user and clearly defines the compiler's AI responsibilities at each stage of computation.

---

## 2. Layer 1: Pure Math & Intent

At the highest level, the user expresses pure mathematical intent and logic without specifying shapes, hardware targets, or derivatives.

- **Primitives:** `lambda`, `define`, `if`, `delay`

### AI Task: Lazy AST & Inference
The compiler evaluates user code to construct a Lazy Abstract Syntax Tree (AST) (using Thunks). It leverages AI to:
- **Infer Missing Tensor Dimensions:** The user does not specify matrix shapes; the compiler analyzes the data flow and dynamically resolves dimensions.
- **Algebraic Optimization:** AI simplifies algebraic expressions, cancelling out redundant operations before the graph is ever executed.
- **Auto-Differentiation:** The compiler automatically generates backward passes for gradients without requiring explicit user annotations.

### Code Comparison

**What the user writes (Minimal):**
```lisp
(define relu
  (lambda (x)
    (if (> x 0) x 0)))

(define model
  (lambda (weights inputs)
    (relu (matmul weights inputs))))
```

**What the AI compiler infers and executes (Optimized):**
```lisp
;; The compiler infers shapes, optimizes the graph, and auto-differentiates.
(define model_optimized
  (lambda (weights inputs)
    ;; Compiler inferred: weights is [128x256], inputs is [256x64]
    ;; Compiler inserted: optimized fused-relu-matmul
    (fused-relu-matmul weights inputs)))

;; Compiler automatically generates the backward pass
(define model_grad
  (lambda (weights inputs grad_output)
    (auto-diff-backward (fused-relu-matmul weights inputs) grad_output)))
```

---

## 3. Layer 2: Virtual Actor Topology

`uhlisp` inherently supports actor-model concurrency to model distributed tensor operations. Users simply define asynchronous processes and message passing.

- **Primitives:** `spawn`, `send`, `receive`

### AI Task: AI Scheduler & Dynamic Placement
The AI Scheduler manages the virtual actor topology. It is responsible for:
- **Dynamic Actor Placement:** Placing spawned actors on physical or virtual nodes to minimize network hops.
- **Latency Balancing:** Observing communication patterns (`send`/`receive`) and dynamically re-balancing the workload or migrating actors to optimize throughput and reduce bottlenecks across the distributed network.

### Code Comparison

**What the user writes (Minimal):**
```lisp
(define worker
  (lambda ()
    (receive
      ((data) (process data)))))

(define main
  (lambda (data-chunks)
    (define pid (spawn worker))
    (send pid data-chunks)))
```

**What the AI compiler infers and executes (Optimized):**
```lisp
;; The compiler maps actors to optimal nodes based on latency profiles.
(define main_optimized
  (lambda (data-chunks)
    ;; Compiler evaluates topology and spawns actors on Node 0 and Node 1
    (define pid_node0 (spawn-on-node worker 'node-0))
    (define pid_node1 (spawn-on-node worker 'node-1))

    ;; Compiler load-balances communication automatically
    (smart-route-send (list pid_node0 pid_node1) data-chunks)))
```

---

## 4. Layer 3: Physical Mapping & Sharding

This layer maps the virtual topology and tensor operations to physical hardware. Under normal circumstances, the user writes absolutely no code for this layer.

- **Primitives:** `with-mesh`, `with-sharding` *(Used ONLY for manual overrides)*

### AI Task: Auto-Sharding
The compiler utilizes an Auto-Sharding engine that evaluates the Lazy AST alongside physical memory constraints and cluster topology. It automatically shards massive tensors and distributes computations across multiple optical tensor cores or devices. The user does not need to write Layer 3 code unless they require a strict manual override.

### Code Comparison

**What the user writes (Minimal):**
```lisp
;; The user writes nothing for mapping/sharding.
;; They rely entirely on Layer 1 & 2 definitions.
```

**What the AI compiler infers and executes (Optimized):**
```lisp
;; The compiler automatically wraps the operations in optimal sharding strategies
;; based on memory limits and cluster size.
(with-mesh '([4 4] optical-tpu-mesh)
  (with-sharding '(weights (shard-x) inputs (shard-y))
    (fused-relu-matmul weights inputs)))
```

---

## 5. Layer 4: Execution & IR Lowering

The final layer forces the execution of the lazily built computation graph, lowering it to a hardware-specific representation.

- **Primitives:** `force`

### AI Task: Intelligent Lowering & Kernel Fusion
When the user explicitly calls `force`, the compiler's backend uses Reinforcement Learning or LLM-based translation to lower the highly-optimized Lisp AST into target intermediate representations like MLIR or XLA. The AI aggressively performs kernel fusion and instruction scheduling to maximize hardware utilization before final execution.

### Code Comparison

**What the user writes (Minimal):**
```lisp
;; The user triggers evaluation of the lazy graph
(force (model weights inputs))
```

**What the AI compiler infers and executes (Optimized):**
```lisp
;; The AI backend translates the AST to MLIR/XLA and executes it.
;; RL-agent selects the optimal lowered IR pass pipeline.
(execute-mlir
  (rl-optimize-pass
    (lower-to-mlir (model_optimized weights inputs))))
```
