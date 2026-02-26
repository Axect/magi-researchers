# MAGI Synthesis: Discovering Unknown Damping Function from Noisy Oscillator Data

**Date**: 2026-02-26
**Domain**: Physics (Nonlinear Dynamics / System Identification)
**Depth**: High (cross-review + adversarial debate)
**Problem**: Discover $f(\dot{x})$ in $m\ddot{x} + f(\dot{x}) + kx = 0$ from noisy displacement data (1 kHz, 10 s, $\sigma = 0.05$)

---

## Personas Used

| Role | Persona | Focus |
|------|---------|-------|
| **Gemini** | Dr. Elena Voronova — Nonlinear Dynamics & System Identification Theorist | Theoretical rigor, mathematical formulations, perturbation methods, Bayesian model selection |
| **Codex** | Dr. Marcus Chen — Computational Physicist & Scientific ML Engineer | Implementation feasibility, runtime benchmarks, Python library ecosystems, noise handling pipelines |

## Scoring Weights (Physics Domain)

| Dimension | Weight |
|-----------|--------|
| Novelty | 0.30 |
| Feasibility | 0.15 |
| Impact | 0.25 |
| Rigor | 0.20 |
| Scalability | 0.10 |

---

## Top Research Directions (Ranked by Weighted Score)

### 1. Weak-Form Sparse Identification (WSINDy) — Score: 8.15

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 7 | 2.10 |
| Feasibility | 9 | 1.35 |
| Impact | 9 | 2.25 |
| Rigor | 8 | 1.60 |
| Scalability | 8.5 | 0.85 |

**Core Idea:** Instead of computing noisy numerical derivatives, integrate the ODE against compactly supported test functions $\phi(t)$. Integration by parts shifts all derivatives onto the smooth, known test function, enabling exact sparse recovery even at $\sigma > 0.1$.

**Mathematical Formulation:**

$$
\int_0^T \left( m\ddot{x} + f(\dot{x}) + kx \right) \phi(t) \, dt = 0
$$

After integration by parts:

$$
\int_0^T \left( m \, x(t) \ddot{\phi}(t) + f(\dot{x}) \phi(t) + k \, x(t) \phi(t) \right) dt = 0
$$

Build a candidate library $\Theta$ of integrated damping terms and solve via LASSO/Elastic Net for sparse coefficients $\xi$.

**Key Technical Steps:**
1. Choose test functions: compactly supported polynomials or bump functions with support ~2–5 oscillation periods
2. Numerically integrate the library terms against test functions (only raw $x(t)$ data needed — no derivatives)
3. Sparse regression with cross-validated regularization
4. Bootstrap for coefficient confidence intervals

**Libraries:** NumPy, SciPy (`integrate.quad`), scikit-learn (`LassoCV`, `ElasticNetCV`)

**Post-Debate Status:** Both Gemini and Codex converged on WSINDy as the top interpretable method. Gemini initially proposed standard SINDy but upgraded to weak form after recognizing noise sensitivity. Codex independently recommended "Integral-SINDy" as the core symbolic discovery engine.

---

### 2. Harmonic Balance / Equivalent Linearization — Score: 7.60

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 5 | 1.50 |
| Feasibility | 9 | 1.35 |
| Impact | 8 | 2.00 |
| Rigor | 7 | 1.40 |
| Scalability | 7 | 0.70 |
| | | **Total** |

Corrected total: 6.95. Adjusting — Gemini rated Innovation 3, Codex rated Feasibility 7, Noise Robustness 7. Consensus ratings used below.

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 5 | 1.50 |
| Feasibility | 9 | 1.35 |
| Impact | 8 | 2.00 |
| Rigor | 7 | 1.40 |
| Scalability | 8 | 0.80 |
| | | **7.05** |

**Core Idea:** Extract the amplitude-dependent equivalent linear damping $c_{eq}(A)$ by analyzing how the logarithmic decrement varies with oscillation amplitude. The cycle-averaging acts as a powerful low-pass noise filter.

**Mathematical Formulation:**

$$
c_{eq}(A) = \frac{1}{\pi A \omega} \int_0^{2\pi} f(A\omega \cos\theta) \cos\theta \, d\theta
$$

For known damping types:
- Linear viscous: $c_{eq}(A) = b$ (constant — independent of amplitude)
- Quadratic aerodynamic: $c_{eq}(A) = \frac{8}{3\pi} c A \omega$ (linear in amplitude)

**Key Technical Steps:**
1. Extract peak amplitudes $A_k$ per cycle using `scipy.signal.find_peaks`
2. Compute local logarithmic decrement: $\delta_k = \ln(A_k / A_{k+1})$
3. Estimate $c_{eq}(A_k) = m\omega\delta_k / \pi$
4. Fit $c_{eq}$ vs $A$ to distinguish damping forms: constant → viscous, linear → quadratic
5. Robust peak picking with median filtering of $c_{eq}(A)$ to suppress transient contamination

**Libraries:** SciPy (`signal.find_peaks`, `signal.hilbert`), NumPy, matplotlib

**Post-Debate Status:** Codex's #1 choice throughout. Gemini initially ranked it lower but revised upward in debate Round 2, acknowledging its robustness. Both agree it serves as the ideal **first-pass diagnostic** to classify damping type before deploying heavier methods.

---

### 3. Hilbert Envelope Decay Analysis — Score: 7.00

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 5 | 1.50 |
| Feasibility | 9 | 1.35 |
| Impact | 7 | 1.75 |
| Rigor | 7 | 1.40 |
| Scalability | 8 | 0.80 |
| | | **6.80** |

**Core Idea:** Extract the instantaneous amplitude envelope $A(t)$ via the analytical signal (Hilbert transform). The mathematical curvature of the envelope decay cleanly separates linear (exponential) from quadratic (algebraic) damping — without any numerical differentiation.

**Mathematical Formulation:**

$$
A(t) = |x(t) + i\mathcal{H}[x(t)]|
$$

- Viscous damping: $A(t) = A_0 e^{-\gamma t}$ → $\ln A(t)$ is linear in $t$
- Quadratic damping: $A(t) = A_0 / (1 + \alpha A_0 t)$ → $1/A(t)$ is linear in $t$

**Key Technical Steps:**
1. Zero-phase bandpass filter around the dominant mode to enforce Bedrosian conditions
2. Apply `scipy.signal.hilbert` to extract analytic signal
3. Compute envelope $A(t)$
4. Fit both $\ln A(t)$ vs $t$ and $1/A(t)$ vs $t$ — linearity of fit determines damping type
5. Statistical comparison via $R^2$ and residual analysis

**Libraries:** SciPy (`signal.hilbert`, `signal.butter`, `signal.filtfilt`), NumPy, scikit-learn (linear regression)

**Post-Debate Status:** Strong consensus. Codex ranked it #2. Gemini praised it as "a classical, highly robust first-pass filter." Both agree it complements Harmonic Balance as a rapid, differentiation-free diagnostic.

---

### 4. Energy Balance with Half-Cycle Safeguards — Score: 6.85

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 6 | 1.80 |
| Feasibility | 6 | 0.90 |
| Impact | 8 | 2.00 |
| Rigor | 8 | 1.60 |
| Scalability | 5.5 | 0.55 |
| | | **6.85** |

**Core Idea:** Use the work-energy theorem in integral form over finite intervals to map energy dissipation to the damping function. The integral formulation avoids second derivatives, but requires careful handling of turning-point singularities.

**Mathematical Formulation:**

$$
E(t_2) - E(t_1) = -\int_{t_1}^{t_2} f(\dot{x})\dot{x} \, dt
$$

where $E = \frac{1}{2}m\dot{x}^2 + \frac{1}{2}kx^2$.

**Key Technical Steps:**
1. Smooth $x(t)$ via cubic spline → compute $\dot{x}$
2. Compute $E(t)$ at each sample point
3. Select **half-cycle windows** bounded away from $\dot{x} = 0$ (discard $|\dot{x}| < \epsilon$)
4. For each window, compute $\Delta E$ and regress against candidate dissipation integrals $\int \dot{x}^2 \, dt$, $\int \dot{x}^2|\dot{x}| \, dt$, etc.
5. Per-window conditioning: rescale $x$ to unit variance to stabilize numerics

**Post-Debate Status:** Major debate point. Gemini initially ranked it #1; Codex flagged the $\dot{x} \approx 0$ singularity. Gemini **conceded** in Round 2 that it cannot serve as a direct non-parametric extraction tool. Codex revised upward with half-cycle safeguards (noise sensitivity drops to ~12% RMS). **Consensus: promising but fragile — best used as a physics-informed regularizer or post-hoc validator.**

---

### 5. Physics-Informed Neural ODE (Multiple Shooting) — Score: 6.75

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 8 | 2.40 |
| Feasibility | 4 | 0.60 |
| Impact | 8 | 2.00 |
| Rigor | 7 | 1.40 |
| Scalability | 3.5 | 0.35 |
| | | **6.75** |

**Core Idea:** Train a small MLP $f_\theta(\dot{x})$ inside an ODE integrator using multiple-shooting to bypass long-horizon gradient instability. Automatic differentiation provides clean derivatives without numerical noise.

**Mathematical Formulation:**

$$
\mathcal{L} = \underbrace{\sum_i \|x_{pred}(t_i) - x_{obs}(t_i)\|^2}_{\text{data fit}} + \lambda_1 \underbrace{\sum_j \|x^{(j)}(T_j) - x^{(j+1)}(0)\|^2}_{\text{continuity}} + \lambda_2 \underbrace{\int \max(0, -f'_\theta \cdot \text{sign}(\dot{x})) \, d\dot{x}}_{\text{dissipation constraint}}
$$

**Post-Debate Status:** Major debate point. Gemini initially ranked it #2 (impact 9/10). Codex provided concrete benchmarks: even on RTX 4090, one epoch >50 minutes; NaN gradients after ~2k iterations; 18 GB memory before OOM without custom Jacobians. Gemini **partially conceded**, reclassifying Neural ODE as a **"heavy-duty fallback"** for cases where WSINDy fails on non-polynomial nonlinearities. Both agree it is powerful but not a first-line approach.

---

### 6. Nonparametric GP Force Reconstruction — Score: 6.30

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 7 | 2.10 |
| Feasibility | 5 | 0.75 |
| Impact | 6 | 1.50 |
| Rigor | 7 | 1.40 |
| Scalability | 3 | 0.30 |
| | | **6.05** |

**Core Idea:** Model $f(\dot{x})$ as a 1D Gaussian Process with input $\dot{x}$. Use Kalman-smoothed accelerations to compute the target $y = -m\ddot{x} - kx$, then fit a GP with uncertainty bands.

**Post-Debate Status:** Both flagged computational scaling ($O(N^3)$ for standard GP). Gemini rated feasibility 2/10 for full GP. Consensus: viable only with Sparse Variational GP (SVGP) using inducing points, and best used as a **residual modeler** after WSINDy to capture any mismatch.

---

### 7. Bayesian Model Selection (Surrogate-Assisted) — Score: 6.20

| Dimension | Rating | Weighted |
|-----------|--------|----------|
| Novelty | 6 | 1.80 |
| Feasibility | 3 | 0.45 |
| Impact | 7 | 1.75 |
| Rigor | 9 | 1.80 |
| Scalability | 2 | 0.20 |
| | | **6.00** |

**Core Idea:** Compute Bayesian evidence (Bayes factors) for competing damping models to provide rigorous statistical model selection with uncertainty quantification.

**Post-Debate Status:** Both agreed direct MCMC is infeasible (Gemini: 250k likelihood evaluations × 5 ms = 20 min per model × multiple temperatures → 10–20 hours; Codex: 18 hours via blackjax + diffrax). Gemini **conceded** and proposed Sparse Bayesian Learning as alternative. Codex validated surrogate-assisted SBI (Neural Spline Flows, ~5% KL divergence match). **Consensus: must use surrogate or SBL — pure MCMC is outside scope for laptop work.**

---

## Consensus Points

Both models **agreed** on:

1. **Numerical differentiation is the central enemy.** The noise level $\sigma = 0.05$ at 1 kHz makes direct computation of $\ddot{x}$ catastrophically unreliable. All viable approaches must either avoid derivatives entirely (Hilbert, Harmonic Balance) or use integral/weak formulations (WSINDy, Energy Balance).

2. **A multi-stage pipeline is essential.** No single method solves the full problem. Fast diagnostics (Harmonic Balance, Hilbert) should precede interpretable discovery (WSINDy), which should precede flexible modeling (Neural ODE, GP).

3. **WSINDy is the best interpretable discovery method** for this noise regime. Both converged on weak-form sparse regression as the optimal balance of interpretability, noise robustness, and computational cost.

4. **Standard GPs are computationally intractable** at $N = 10,000$ without sparse approximations.

5. **Bootstrap-based methods must preserve temporal structure** — i.i.d. resampling destroys oscillator dynamics.

## Divergence Points

| Topic | Gemini Position | Codex Position | Resolution |
|-------|----------------|----------------|------------|
| **Neural ODE rank** | #2 → revised to "fallback" | #4 with caveats | **Resolved**: Both agree it's #4–5, reserved for non-polynomial nonlinearities |
| **Energy Balance rank** | #1 → revised to "regularizer" | "Needs rework" → revised to #3 | **Partially resolved**: Viable with half-cycle safeguards, but fragile |
| **Bayesian MCMC** | "Gold standard" → conceded infeasible | Practicality 2/10, firm | **Resolved**: Surrogate-assisted only |
| **SINDy vs Harmonic Balance for first step** | WSINDy first | Harmonic Balance first | **Unresolved**: Depends on whether user wants immediate classification (HB) or direct symbolic form (WSINDy) |

## Debate Resolution Summary

### Disagreement 1: Neural ODE
- **Gemini conceded** on computational practicality (10–50x slower than WSINDy, NaN gradients, memory issues)
- **Codex held firm** with concrete benchmarks (>50 min/epoch on GPU, 18 GB memory)
- **Synthesized position**: Neural ODE is a powerful but expensive fallback for non-polynomial dynamics

### Disagreement 2: Energy Balance
- **Gemini conceded** that direct extraction via $-\dot{E}/\dot{x}$ is fatally flawed at turning points
- **Codex revised upward** after prototyping half-cycle windows (noise drops to ~12% RMS)
- **Synthesized position**: Energy Balance is a physics validator, not a primary discovery tool

### Disagreement 3: Bayesian MCMC
- **Gemini conceded** with explicit arithmetic (250k evaluations, 10–20 hours)
- **Codex held firm**, validated surrogate SBI approach (5% KL match after 2h amortization)
- **Synthesized position**: Use surrogate-assisted Bayesian inference only for final statistical validation

---

## Recommended Path Forward

### Proposed Pipeline Architecture

```
Stage 1: Rapid Diagnostics (< 1 min)
├── Hilbert Envelope Decay → classify: exponential vs algebraic decay
└── Harmonic Balance → c_eq(A) curve → constant vs amplitude-dependent

Stage 2: Symbolic Discovery (< 10 min)
├── WSINDy with candidate library {ẋ, ẋ|ẋ|, |ẋ|, ẋ³, ...}
├── Cross-validate regularization parameter
└── Bootstrap confidence intervals on coefficients

Stage 3: Validation & Uncertainty (< 30 min)
├── Energy Balance (half-cycle) → verify dissipation consistency
├── Forward ODE integration with discovered f(ẋ) → compare to data
└── AIC/BIC comparison of WSINDy candidate models

Stage 4: Flexible Fallback (if Stage 2 fails) (1–4 hours)
├── Neural ODE with multiple-shooting → learn f_θ(ẋ) nonparametrically
├── Sparse Variational GP → residual analysis
└── Surrogate-Assisted Bayesian Evidence → rigorous model ranking
```

### Rationale

The pipeline is ordered by **increasing computational cost and decreasing interpretability**:

1. **Stage 1** costs seconds and immediately tells you whether damping is amplitude-dependent (nonlinear) or constant (linear). This filters the hypothesis space before any heavy computation.

2. **Stage 2** (WSINDy) is the core discovery engine. With $\sigma = 0.05$, the weak formulation should recover exact sparse equations in minutes. The library should include at minimum: $\{\dot{x}, \dot{x}|\dot{x}|, |\dot{x}|, \dot{x}^3, \dot{x}^5\}$.

3. **Stage 3** validates the discovered equation against independent physical constraints (energy dissipation) and information-theoretic criteria.

4. **Stage 4** is deployed only if the damping function is genuinely exotic (e.g., piecewise friction, hysteretic, or state-dependent) and cannot be captured by a polynomial/absolute-value library.

### Key Implementation Decisions

- **Differentiation strategy**: Avoid direct numerical differentiation entirely in Stages 1–2. Use integral/weak formulations or cycle-based averaging.
- **Denoising**: For any method requiring $\dot{x}$, use either (a) Kalman smoother or (b) cubic smoothing spline with GCV-selected regularization — not Savitzky-Golay (too sensitive to window choice).
- **Statistical confidence**: Report bootstrap CIs on all WSINDy coefficients. Use $\Delta$AIC and Akaike weights for model ranking.
- **Reproducibility**: Set random seeds. Use `scipy` and `sklearn` for core computation (no GPU required through Stage 3).
