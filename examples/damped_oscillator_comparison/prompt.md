# Experiment Prompt: Equation Discovery for Damped Oscillator

> This prompt is given identically to all models (Claude, Gemini, Codex, MAGI) for fair comparison.

---

## Prompt

You are a researcher brainstorming approaches to a scientific computing problem. Provide concrete, actionable research ideas with technical depth.

### Problem

We have noisy time-series data from a damped mechanical oscillator. The displacement $x(t)$ was recorded at 1000 Hz for 10 seconds, with Gaussian measurement noise ($\sigma = 0.05$). The system is known to follow:

$$
m\ddot{x} + f(\dot{x}) + kx = 0
$$

where $m$ and $k$ are known, but the **damping function $f(\dot{x})$ is unknown**. It could be:

- Linear (viscous) damping: $f(\dot{x}) = b\dot{x}$
- Quadratic (aerodynamic) damping: $f(\dot{x}) = c\dot{x}|\dot{x}|$
- A hybrid or other nonlinear form

### Task

Brainstorm research approaches to **discover the correct form of $f(\dot{x})$ directly from the noisy data**. For each approach, provide:

1. **Method name and core idea** (1-2 sentences)
2. **Mathematical formulation** — key equations, loss functions, or objective functions
3. **Implementation sketch** — libraries, algorithms, key steps
4. **Strengths** — when/why this approach works well
5. **Weaknesses** — failure modes, limitations, assumptions
6. **Expected output** — what the result looks like (plots, equations, metrics)

### Constraints

- Assume Python with standard scientific computing stack (NumPy, SciPy, scikit-learn, PyTorch)
- The solution should be reproducible and runnable on a laptop (no GPU required)
- Prioritize approaches that can distinguish between damping models with statistical confidence
- Consider both data-driven and physics-informed strategies

Generate 5-7 diverse approaches, ranging from classical methods to modern ML techniques.
