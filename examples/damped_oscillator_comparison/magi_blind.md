# Discovering Unknown Damping Functions from Noisy Oscillator Data

## Problem Statement

We have noisy time-series data from a damped mechanical oscillator. The displacement $x(t)$ was recorded at 1000 Hz for 10 seconds, with Gaussian measurement noise ($\sigma = 0.05$). The system is known to follow:

$$
m\ddot{x} + f(\dot{x}) + kx = 0
$$

where $m$ and $k$ are known, but the **damping function $f(\dot{x})$ is unknown**. It could be:

- Linear (viscous) damping: $f(\dot{x}) = b\dot{x}$
- Quadratic (aerodynamic) damping: $f(\dot{x}) = c\dot{x}|\dot{x}|$
- A hybrid or other nonlinear form

**Goal:** Discover the correct form of $f(\dot{x})$ directly from the noisy data.

---

## Approach 1: Weak-Form Sparse Identification (WSINDy)

**Core idea:** Instead of computing noisy numerical derivatives, integrate the ODE against compactly supported test functions $\phi(t)$. Integration by parts shifts all derivatives onto the smooth, known test function, enabling exact sparse recovery even at $\sigma > 0.1$.

### Mathematical Formulation

$$
\int_0^T \left( m\ddot{x} + f(\dot{x}) + kx \right) \phi(t) \, dt = 0
$$

After integration by parts:

$$
\int_0^T \left( m \, x(t) \ddot{\phi}(t) + f(\dot{x}) \phi(t) + k \, x(t) \phi(t) \right) dt = 0
$$

Build a candidate library $\Theta$ of integrated damping terms and solve via LASSO/Elastic Net for sparse coefficients $\xi$.

### Implementation Sketch

1. Choose test functions: compactly supported polynomials or bump functions with support ~2–5 oscillation periods
2. Numerically integrate the library terms against test functions (only raw $x(t)$ data needed — no derivatives)
3. Sparse regression with cross-validated regularization
4. Bootstrap for coefficient confidence intervals

**Libraries:** NumPy, SciPy (`integrate.quad`), scikit-learn (`LassoCV`, `ElasticNetCV`)

### Strengths

- Dramatically more noise-robust than pointwise derivative methods — integration is a smoothing operation
- Produces interpretable symbolic expressions directly
- Only needs raw $x(t)$ data, no numerical differentiation at all
- Fast, no GPU needed

### Weaknesses

- Requires choosing test function parameters (widths, centers) — some tuning needed
- More complex implementation than standard SINDy
- Still requires a candidate library of basis functions

### Expected Output

A sparse coefficient vector $\xi$ with 1-2 nonzero entries, with bootstrap confidence intervals. Significantly lower variance in estimated coefficients compared to direct differentiation approaches.

---

## Approach 2: Harmonic Balance / Equivalent Linearization

**Core idea:** Extract the amplitude-dependent equivalent linear damping $c_{eq}(A)$ by analyzing how the logarithmic decrement varies with oscillation amplitude. The cycle-averaging acts as a powerful low-pass noise filter.

### Mathematical Formulation

$$
c_{eq}(A) = \frac{1}{\pi A \omega} \int_0^{2\pi} f(A\omega \cos\theta) \cos\theta \, d\theta
$$

For known damping types:
- Linear viscous: $c_{eq}(A) = b$ (constant — independent of amplitude)
- Quadratic aerodynamic: $c_{eq}(A) = \frac{8}{3\pi} c A \omega$ (linear in amplitude)

### Implementation Sketch

1. Extract peak amplitudes $A_k$ per cycle using `scipy.signal.find_peaks`
2. Compute local logarithmic decrement: $\delta_k = \ln(A_k / A_{k+1})$
3. Estimate $c_{eq}(A_k) = m\omega\delta_k / \pi$
4. Fit $c_{eq}$ vs $A$ to distinguish damping forms: constant → viscous, linear → quadratic
5. Robust peak picking with median filtering of $c_{eq}(A)$ to suppress transient contamination

**Libraries:** SciPy (`signal.find_peaks`, `signal.hilbert`), NumPy, matplotlib

### Strengths

- Extremely fast and intuitive first-pass diagnostic
- Cycle-averaging provides excellent noise rejection
- No numerical differentiation required
- Result is immediately interpretable: constant $c_{eq}$ = linear damping, amplitude-dependent $c_{eq}$ = nonlinear

### Weaknesses

- Only classifies damping type — does not directly give the full functional form
- Assumes slowly varying amplitude (quasi-harmonic approximation)
- Struggles with very strong nonlinearity or multi-modal oscillations

### Expected Output

A plot of $c_{eq}(A)$ vs $A$. A flat line indicates viscous damping; a linear trend indicates quadratic damping. The slope directly gives the damping coefficient.

---

## Approach 3: Hilbert Envelope Decay Analysis

**Core idea:** Extract the instantaneous amplitude envelope $A(t)$ via the analytical signal (Hilbert transform). The mathematical curvature of the envelope decay cleanly separates linear (exponential) from quadratic (algebraic) damping — without any numerical differentiation.

### Mathematical Formulation

$$
A(t) = |x(t) + i\mathcal{H}[x(t)]|
$$

- Viscous damping: $A(t) = A_0 e^{-\gamma t}$ → $\ln A(t)$ is linear in $t$
- Quadratic damping: $A(t) = A_0 / (1 + \alpha A_0 t)$ → $1/A(t)$ is linear in $t$

### Implementation Sketch

1. Zero-phase bandpass filter around the dominant mode to enforce Bedrosian conditions
2. Apply `scipy.signal.hilbert` to extract analytic signal
3. Compute envelope $A(t)$
4. Fit both $\ln A(t)$ vs $t$ and $1/A(t)$ vs $t$ — linearity of fit determines damping type
5. Statistical comparison via $R^2$ and residual analysis

**Libraries:** SciPy (`signal.hilbert`, `signal.butter`, `signal.filtfilt`), NumPy, scikit-learn (linear regression)

### Strengths

- No numerical differentiation required at all
- Extremely fast (seconds)
- Robust diagnostic — the two decay shapes are qualitatively distinct
- Complements Harmonic Balance as a rapid first-pass filter

### Weaknesses

- Requires accurate envelope extraction (bandpass filtering critical)
- Works best for underdamped systems with many oscillation cycles
- Only classifies damping type; does not yield parametric coefficients directly

### Expected Output

Two side-by-side plots: $\ln A(t)$ vs $t$ and $1/A(t)$ vs $t$. The one that is more linear determines the damping type. $R^2$ values quantify the distinction.

---

## Approach 4: Energy Balance with Half-Cycle Safeguards

**Core idea:** Use the work-energy theorem in integral form over finite intervals to map energy dissipation to the damping function. The integral formulation avoids second derivatives, but requires careful handling of turning-point singularities.

### Mathematical Formulation

$$
E(t_2) - E(t_1) = -\int_{t_1}^{t_2} f(\dot{x})\dot{x} \, dt
$$

where $E = \frac{1}{2}m\dot{x}^2 + \frac{1}{2}kx^2$.

### Implementation Sketch

1. Smooth $x(t)$ via cubic spline → compute $\dot{x}$
2. Compute $E(t)$ at each sample point
3. Select **half-cycle windows** bounded away from $\dot{x} = 0$ (discard $|\dot{x}| < \epsilon$)
4. For each window, compute $\Delta E$ and regress against candidate dissipation integrals $\int \dot{x}^2 \, dt$, $\int \dot{x}^2|\dot{x}| \, dt$, etc.
5. Per-window conditioning: rescale $x$ to unit variance to stabilize numerics

**Libraries:** SciPy (`interpolate.CubicSpline`, `integrate.trapezoid`), NumPy, scikit-learn

### Strengths

- Grounded in fundamental physics (work-energy theorem)
- Provides direct physical insight into energy dissipation pathways
- Can serve as independent validation for other methods

### Weaknesses

- Fragile near turning points where $\dot{x} \approx 0$ — singularity in $f(\dot{x})/\dot{x}$
- Requires first-derivative estimation (noise sensitive)
- Half-cycle windowing discards data, reducing statistical power
- Best used as a physics-informed validator rather than primary discovery tool

### Expected Output

Per-half-cycle energy dissipation values plotted against amplitude, with regression lines for candidate damping models. Error bars from window-to-window variation.

---

## Approach 5: Physics-Informed Neural ODE (Multiple Shooting)

**Core idea:** Train a small MLP $f_\theta(\dot{x})$ inside an ODE integrator using multiple-shooting to bypass long-horizon gradient instability. Automatic differentiation provides clean derivatives without numerical noise.

### Mathematical Formulation

$$
\mathcal{L} = \underbrace{\sum_i \|x_{pred}(t_i) - x_{obs}(t_i)\|^2}_{\text{data fit}} + \lambda_1 \underbrace{\sum_j \|x^{(j)}(T_j) - x^{(j+1)}(0)\|^2}_{\text{continuity}} + \lambda_2 \underbrace{\int \max(0, -f'_\theta \cdot \text{sign}(\dot{x})) \, d\dot{x}}_{\text{dissipation constraint}}
$$

### Implementation Sketch

1. Define $f_\theta$ as a 2-hidden-layer MLP: $\mathbb{R} \to \mathbb{R}$ (e.g., [1, 32, 32, 1] with `tanh` activations)
2. Split the time series into overlapping windows (multiple shooting segments)
3. Use `torchdiffeq.odeint_adjoint` for memory-efficient backpropagation through the ODE solver
4. Train with Adam, learning rate scheduling; continuity loss forces segments to stitch together
5. Post-hoc: evaluate the learned $f_\theta(v)$ over a grid of $v$ values and fit symbolic candidates

**Libraries:** PyTorch, torchdiffeq, NumPy

### Strengths

- Makes no assumption about the functional form — can discover arbitrary damping functions
- Leverages known physics ($m$, $k$, ODE structure) while learning only the unknown part
- Multiple shooting stabilizes training for long time series

### Weaknesses

- Computationally expensive — even on GPU, can require significant training time
- The learned $f_\theta$ is a black box; requires post-hoc symbolic distillation
- Risk of NaN gradients and memory issues without custom Jacobians
- Non-convex optimization with local minima — not a first-line approach

### Expected Output

A plot of $f_\theta(v)$ vs $v$ revealing the functional shape. Overlay of predicted vs observed trajectories. The plot shape guides subsequent symbolic identification.

---

## Approach 6: Nonparametric GP Force Reconstruction

**Core idea:** Model $f(\dot{x})$ as a 1D Gaussian Process with input $\dot{x}$. Use Kalman-smoothed accelerations to compute the target $y = -m\ddot{x} - kx$, then fit a GP with uncertainty bands.

### Mathematical Formulation

From the ODE: $f(\dot{x}) = -m\ddot{x} - kx$. Place a GP prior:

$$
f \sim \mathcal{GP}(0, k_{\text{RBF}}(\dot{x}, \dot{x}'))
$$

Posterior mean and variance give a nonparametric estimate of the damping function with confidence bands.

### Implementation Sketch

1. Apply Kalman smoother on $x(t)$ to get smooth $\dot{x}(t)$, $\ddot{x}(t)$
2. Compute residuals $r_j = -m\ddot{x}_j - kx_j$
3. Fit GP: $r \sim \mathcal{GP}(\dot{x})$ using sparse variational GP (SVGP) with inducing points
4. Evaluate posterior mean on a dense $\dot{x}$-grid, inspect shape

**Libraries:** GPy or GPyTorch (for SVGP), SciPy (`KalmanFilter` via `simdkalman` or `filterpy`), NumPy

### Strengths

- Fully nonparametric — no candidate library needed
- Provides uncertainty quantification (credible intervals)
- The GP posterior mean can be visually inspected to distinguish linear from quadratic behavior

### Weaknesses

- Computationally heavy at $N = 10,000$ — standard GP is $O(N^3)$, must use sparse approximations
- Quality depends entirely on derivative estimation (garbage in, garbage out)
- Best used as a residual modeler after sparse symbolic methods rather than primary discovery tool

### Expected Output

A plot of $f(\dot{x})$ with 95% credible bands. If linear damping, the GP posterior will be consistent with a straight line through the origin. Credible bands allow statistical testing of functional form.

---

## Approach 7: Bayesian Model Selection (Surrogate-Assisted)

**Core idea:** Compute Bayesian evidence (Bayes factors) for competing damping models to provide rigorous statistical model selection with uncertainty quantification. Use surrogate likelihood models to make computation tractable.

### Mathematical Formulation

For each model $\mathcal{M}_i$ with parameters $\theta_i$:

$$
p(x_{\text{obs}} | \mathcal{M}_i) = \int p(x_{\text{obs}} | \theta_i, \mathcal{M}_i)\,p(\theta_i | \mathcal{M}_i)\,d\theta_i
$$

Direct MCMC is infeasible (250k+ likelihood evaluations × ODE solves). Instead, train a Neural Spline Flow as a surrogate posterior via simulation-based inference (SBI).

### Implementation Sketch

1. Define 3-4 candidate models: (a) linear $b\dot{x}$, (b) quadratic $c\dot{x}|\dot{x}|$, (c) hybrid $b\dot{x} + c\dot{x}|\dot{x}|$, (d) cubic $d\dot{x}^3$
2. For each model, generate ~50k synthetic trajectories from the prior
3. Train conditional density estimator (Neural Spline Flow) via `sbi` package
4. Approximate Bayes factors from learned posteriors
5. Validate surrogate accuracy via posterior predictive checks

**Libraries:** `sbi` (simulation-based inference), PyTorch, SciPy (`integrate.solve_ivp`), NumPy

### Strengths

- Provides the most rigorous statistical model comparison with uncertainty quantification
- Naturally handles model complexity/fit tradeoff (Occam's razor built in)
- Once the surrogate is trained, posterior sampling is instant

### Weaknesses

- Computationally expensive amortization phase (~2 hours for surrogate training)
- Requires specifying a finite discrete set of candidate models a priori
- Surrogate approximation introduces some bias (~5% KL divergence)
- Best reserved for final statistical validation rather than initial exploration

### Expected Output

A table of Bayes factors ($B_{ij}$) with confidence. Posterior parameter distributions as corner plots. Posterior predictive trajectories overlaid on data.

---

## Summary Comparison

| Approach | Interpretable? | Noise Robust? | Needs Derivatives? | Compute Cost | Best For |
|---|---|---|---|---|---|
| **WSINDy** | Yes (symbolic) | **Very High** | No (integral form) | Low | **Primary discovery (recommended)** |
| **Harmonic Balance** | Yes (classification) | High | No (cycle-based) | Very Low | First-pass diagnostic |
| **Hilbert Envelope** | Yes (classification) | High | No | Very Low | First-pass diagnostic |
| **Energy Balance** | Yes (physics-based) | Moderate | Yes ($\dot{x}$) | Low | Post-hoc validation |
| **Neural ODE** | No (black box) | High | No (learned) | High | Exotic/non-polynomial damping |
| **GP Reconstruction** | Partially (shape) | Low-Moderate | Yes ($\ddot{x}$) | Medium-High | Residual analysis |
| **Bayesian Selection** | Yes (model + params) | High | No (surrogate) | Very High | Final statistical confirmation |

## Recommended Workflow

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

The pipeline is ordered by **increasing computational cost and decreasing interpretability**. Stage 1 costs seconds and immediately classifies the damping type. Stage 2 discovers the exact symbolic form. Stage 3 validates independently. Stage 4 is deployed only for genuinely exotic dynamics.
