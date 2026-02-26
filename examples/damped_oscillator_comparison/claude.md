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

## Approach 1: Sparse Identification of Nonlinear Dynamics (SINDy)

**Core idea:** Build a library of candidate nonlinear terms and use sparse regression to select which terms are active in the governing ODE, effectively performing symbolic regression via LASSO.

### Mathematical Formulation

Rewrite the system as $\ddot{x} = -\frac{k}{m}x - \frac{1}{m}f(\dot{x})$. Construct a library matrix $\Theta(\dot{x})$ of candidate functions:

$$
\Theta(\dot{x}) = \begin{bmatrix} \dot{x} & \dot{x}|\dot{x}| & \dot{x}^3 & \text{sign}(\dot{x}) & \cdots \end{bmatrix}
$$

Then solve:

$$
\ddot{x} + \frac{k}{m}x = \Theta(\dot{x})\,\xi
$$

with the sparsity-promoting objective:

$$
\min_\xi \left\| \ddot{x} + \frac{k}{m}x - \Theta(\dot{x})\xi \right\|_2^2 + \lambda\|\xi\|_1
$$

### Implementation Sketch

1. Smooth noisy $x(t)$ using a Savitzky-Golay filter or total-variation regularized differentiation to estimate $\dot{x}$, $\ddot{x}$
2. Build $\Theta$ from ~10-15 candidate basis functions (polynomials in $\dot{x}$, absolute-value terms, sign functions)
3. Solve via `sklearn.linear_model.Lasso` or sequential thresholded least squares (STLSQ)
4. Use cross-validation or information criteria (AIC/BIC) to select $\lambda$

```python
from pysindy import SINDy
from pysindy.differentiation import SmoothedFiniteDifference
from pysindy.optimizers import STLSQ

differentiator = SmoothedFiniteDifference(smoother_kw={"window_length": 15})
model = SINDy(optimizer=STLSQ(threshold=0.05),
              differentiation_method=differentiator)
model.fit(X, t=dt)
model.print()
```

### Strengths

- Produces interpretable symbolic expressions
- Well-suited for this exact class of problems (ODE discovery)
- Fast, no GPU needed
- Directly gives you the functional form

### Weaknesses

- Heavily dependent on numerical differentiation quality — noise at $\sigma=0.05$ will corrupt $\ddot{x}$ estimates
- Requires that the true function is well-represented in the candidate library
- Fails if the damping is truly novel (not in the library)

### Expected Output

A sparse coefficient vector $\xi$ with 1-2 nonzero entries, e.g., $f(\dot{x}) = 0.32\,\dot{x} + 0.08\,\dot{x}|\dot{x}|$, plus a parsimonious model complexity score.

---

## Approach 2: Bayesian Model Selection with MCMC

**Core idea:** Define a discrete set of candidate damping models, embed each in a Bayesian ODE framework, and compute posterior model probabilities via marginal likelihoods (Bayes factors).

### Mathematical Formulation

For each model $\mathcal{M}_i$ with parameters $\theta_i$:

$$
p(x_{\text{obs}} | \mathcal{M}_i) = \int p(x_{\text{obs}} | \theta_i, \mathcal{M}_i)\,p(\theta_i | \mathcal{M}_i)\,d\theta_i
$$

Likelihood (assuming i.i.d. Gaussian noise):

$$
p(x_{\text{obs}} | \theta_i) = \prod_{j=1}^{N} \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{(x_{\text{obs},j} - x_{\text{model},j}(\theta_i))^2}{2\sigma^2}\right)
$$

where $x_{\text{model}}(\theta_i)$ is obtained by numerically integrating the ODE with `scipy.integrate.solve_ivp`. Model posterior:

$$
p(\mathcal{M}_i | x_{\text{obs}}) \propto p(x_{\text{obs}} | \mathcal{M}_i)\,p(\mathcal{M}_i)
$$

### Implementation Sketch

1. Define 3-4 candidate models: (a) linear $b\dot{x}$, (b) quadratic $c\dot{x}|\dot{x}|$, (c) hybrid $b\dot{x} + c\dot{x}|\dot{x}|$, (d) cubic $d\dot{x}^3$
2. For each model, run MCMC (e.g., `emcee` or `numpyro`) to sample the posterior $p(\theta_i | x_{\text{obs}}, \mathcal{M}_i)$
3. Estimate marginal likelihoods via harmonic mean estimator, thermodynamic integration, or nested sampling (`dynesty`)
4. Compute Bayes factors between all model pairs

```python
import dynesty

def log_likelihood(params, model_type):
    x_sim = solve_ode(params, model_type)
    residuals = x_obs - x_sim
    return -0.5 * np.sum(residuals**2 / sigma**2)

sampler = dynesty.NestedSampler(log_likelihood, prior_transform, ndim=n_params)
sampler.run_nested()
results = sampler.results
log_Z = results.logz[-1]  # marginal likelihood
```

### Strengths

- Provides rigorous statistical model comparison with uncertainty quantification
- Naturally handles the model complexity/fit tradeoff (Occam's razor built in)
- Gives full posterior distributions on parameters, not just point estimates

### Weaknesses

- Computationally expensive — each likelihood evaluation requires an ODE solve
- Marginal likelihood estimation can be numerically unstable
- Requires specifying a finite discrete set of candidate models a priori

### Expected Output

A table of Bayes factors ($B_{ij}$) with confidence: e.g., "Strong evidence for hybrid model over linear ($\ln B_{31} = 8.2$)". Posterior parameter distributions as corner plots. Posterior predictive trajectories overlaid on data.

---

## Approach 3: Neural ODE with Physics-Informed Structure

**Core idea:** Parameterize the unknown damping function as a small neural network $f_\theta(\dot{x})$ and learn it end-to-end by integrating the ODE through a differentiable solver, training against observed trajectories.

### Mathematical Formulation

$$
\frac{d}{dt}\begin{pmatrix}x \\ v\end{pmatrix} = \begin{pmatrix}v \\ -\frac{k}{m}x - \frac{1}{m}f_\theta(v)\end{pmatrix}
$$

Loss function:

$$
\mathcal{L}(\theta) = \frac{1}{N}\sum_{j=1}^{N}\left(x_{\text{obs}}(t_j) - x_\theta(t_j)\right)^2 + \lambda_{\text{mono}}\,\mathcal{R}_{\text{physics}}(\theta)
$$

where $\mathcal{R}_{\text{physics}}$ can enforce physical priors, e.g., that $f$ is odd: $f(-v) = -f(v)$, and dissipative: $v \cdot f(v) > 0$.

### Implementation Sketch

1. Define $f_\theta$ as a 2-hidden-layer MLP: $\mathbb{R} \to \mathbb{R}$ (e.g., [1, 32, 32, 1] with `tanh` activations)
2. Use `torchdiffeq.odeint_adjoint` for memory-efficient backpropagation through the ODE solver
3. Train with Adam, learning rate scheduling, and mini-batching over time windows
4. Post-hoc: evaluate the learned $f_\theta(v)$ over a grid of $v$ values and fit symbolic candidates

```python
import torch
from torchdiffeq import odeint_adjoint as odeint

class DampingNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(1, 32), torch.nn.Tanh(),
            torch.nn.Linear(32, 32), torch.nn.Tanh(),
            torch.nn.Linear(32, 1))
    def forward(self, v):
        return self.net(v)

class PhysicsODE(torch.nn.Module):
    def __init__(self, m, k, damping_net):
        super().__init__()
        self.m, self.k = m, k
        self.f = damping_net
    def forward(self, t, state):
        x, v = state[..., 0:1], state[..., 1:2]
        dxdt = v
        dvdt = -(self.k/self.m)*x - (1/self.m)*self.f(v)
        return torch.cat([dxdt, dvdt], dim=-1)
```

### Strengths

- Makes no assumption about the functional form — can discover arbitrary damping functions
- Leverages known physics ($m$, $k$, ODE structure) while learning only the unknown part
- Differentiable ODE solvers are mature

### Weaknesses

- The learned $f_\theta$ is a black box; requires post-hoc symbolic distillation to get an equation
- Can overfit to noise, especially with limited data
- Training can be unstable (stiff ODEs, exploding gradients)
- Non-convex optimization with local minima

### Expected Output

A plot of $f_\theta(v)$ vs $v$ revealing the functional shape (linear? quadratic? hybrid?). Overlay of predicted vs observed trajectories. The plot shape then guides symbolic identification.

---

## Approach 4: Gaussian Process Regression on the Force Residual

**Core idea:** Estimate $\dot{x}$ and $\ddot{x}$ from data, compute the residual force $r = -m\ddot{x} - kx$ (which equals $f(\dot{x})$), and fit a Gaussian process to learn $f$ as a function of $\dot{x}$ with full uncertainty.

### Mathematical Formulation

From the ODE: $f(\dot{x}) = -m\ddot{x} - kx$. Estimate derivatives from data, then we have noisy observations:

$$
r_j = f(v_j) + \epsilon_j, \quad \epsilon_j \sim \mathcal{N}(0, \sigma_r^2)
$$

Place a GP prior on $f$:

$$
f \sim \mathcal{GP}(0, k_{\text{RBF}}(v, v'))
$$

Posterior mean and variance give a nonparametric estimate of the damping function with confidence bands.

### Implementation Sketch

1. Apply a smoothing spline or Gaussian process regression on $x(t)$ itself to get smooth $\dot{x}(t)$, $\ddot{x}(t)$ (derivative of a GP is also a GP)
2. Compute residuals $r_j = -m\ddot{x}_j - kx_j$
3. Fit GP: $r \sim \mathcal{GP}(v)$ using `sklearn.gaussian_process.GaussianProcessRegressor` or `GPy`
4. Evaluate posterior mean on a dense $v$-grid, inspect shape

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

# After computing residuals r and velocities v
kernel = RBF(length_scale=0.5) + WhiteKernel(noise_level=0.01)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
gp.fit(v.reshape(-1, 1), r)

v_grid = np.linspace(v.min(), v.max(), 500).reshape(-1, 1)
f_mean, f_std = gp.predict(v_grid, return_std=True)
```

### Strengths

- Fully nonparametric — no candidate library needed
- Provides uncertainty quantification (credible intervals)
- Simple to implement
- The GP posterior mean can be visually inspected to distinguish linear from quadratic behavior

### Weaknesses

- Garbage in, garbage out — the quality depends entirely on derivative estimation
- Noise amplification: second derivatives from noisy data at $\sigma = 0.05$ will produce large residual noise $\sigma_r$
- Scalability to 10,000 data points may require sparse GP approximations

### Expected Output

A plot of $f(v)$ with 95% credible bands. If linear damping, the GP posterior will be consistent with a straight line through the origin. The credible bands allow statistical testing of linearity.

---

## Approach 5: Symbolic Regression via Genetic Programming

**Core idea:** Use evolutionary algorithms to search the space of mathematical expressions for the damping function that best explains the data while minimizing expression complexity.

### Mathematical Formulation

Same residual setup as Approach 4. Minimize a multi-objective fitness:

$$
\text{Pareto front of:} \quad \left(\underbrace{\sum_j (r_j - \hat{f}(v_j))^2}_{\text{accuracy}},\;\; \underbrace{C(\hat{f})}_{\text{complexity}}\right)
$$

where $C(\hat{f})$ counts the number of nodes in the expression tree.

### Implementation Sketch

1. Compute residuals as in Approach 4
2. Use `PySR` (Python interface to symbolic regression) with operators `{+, -, *, /, abs, square, cube}`
3. Run with population size ~100, for ~50 generations
4. Inspect the Pareto front of accuracy vs complexity

```python
from pysr import PySRRegressor

model = PySRRegressor(
    niterations=50,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["abs", "square", "cube"],
    complexity_of_operators={"abs": 1, "square": 1, "cube": 1},
    maxsize=15,
    populations=20,
    loss="loss(prediction, target) = (prediction - target)^2",
)
model.fit(v.reshape(-1, 1), r)
print(model)  # prints Pareto-optimal expressions
```

### Strengths

- Discovers the actual symbolic form, not just a numerical approximation
- Can find unexpected functional forms not in a predefined library
- Multi-objective optimization naturally balances parsimony and accuracy

### Weaknesses

- Stochastic — results vary across runs
- Computationally expensive for large expression spaces
- Still depends on good derivative estimates
- May converge to algebraically equivalent but visually different expressions

### Expected Output

A Pareto front table:

| Complexity | Expression | MSE |
|---|---|---|
| 2 | $0.31 v$ | $4.2 \times 10^{-3}$ |
| 5 | $0.31 v + 0.08 v \|v\|$ | $1.1 \times 10^{-4}$ |
| 7 | $0.30 v + 0.08 v^2 \text{sgn}(v)$ | $1.0 \times 10^{-4}$ |

A sharp MSE drop at a particular complexity indicates the correct model.

---

## Approach 6: Weak-Form Equation Discovery (Integral Formulation)

**Core idea:** Avoid computing noisy derivatives entirely by multiplying the ODE by smooth test functions and integrating by parts, converting differential equations into integral equations that are far more robust to noise.

### Mathematical Formulation

Multiply $m\ddot{x} + f(\dot{x}) + kx = 0$ by a smooth test function $\phi(t)$ with compact support and integrate by parts:

$$
m\int \ddot{x}\,\phi\,dt = -m\int \dot{x}\,\dot{\phi}\,dt + \text{boundary terms}
$$

This gives, for each test function $\phi_i$:

$$
-m\int \dot{x}\,\dot{\phi}_i\,dt + \int f(\dot{x})\,\phi_i\,dt + k\int x\,\phi_i\,dt = 0
$$

Expand $f(\dot{x}) = \sum_k \xi_k \psi_k(\dot{x})$ in a basis and solve:

$$
\sum_k \xi_k \underbrace{\int \psi_k(\dot{x})\,\phi_i\,dt}_{G_{ik}} = m\int \dot{x}\,\dot{\phi}_i\,dt - k\int x\,\phi_i\,dt
$$

This is a linear system $G\xi = b$ — solvable with sparse regression.

### Implementation Sketch

1. Estimate only $\dot{x}$ (first derivative, much less noisy than second)
2. Choose test functions: B-splines, bump functions, or Gaussians with varying centers/widths
3. Compute all integrals via numerical quadrature (`scipy.integrate.trapezoid`)
4. Solve $G\xi = b$ with LASSO or STLSQ

```python
from scipy.integrate import trapezoid

# Gaussian test functions centered at different times
def test_fn(t, t0, width=0.1):
    return np.exp(-(t - t0)**2 / (2 * width**2))

def test_fn_dot(t, t0, width=0.1):
    return -(t - t0) / width**2 * test_fn(t, t0, width)

# For each test function, compute integral equations
b_vec = []
G_rows = []
for t0 in test_centers:
    phi = test_fn(t, t0)
    dphi = test_fn_dot(t, t0)
    b_i = m * trapezoid(x_dot * dphi, t) - k * trapezoid(x * phi, t)
    g_row = [trapezoid(psi_k(x_dot) * phi, t) for psi_k in basis_fns]
    b_vec.append(b_i)
    G_rows.append(g_row)
```

### Strengths

- Dramatically more noise-robust than pointwise derivative methods
- The key innovation: integration is a smoothing operation, differentiation is a roughening operation
- This is the state-of-the-art approach in the SINDy literature (called WSINDy)
- Only needs first derivatives, not second

### Weaknesses

- Requires choosing test function parameters (widths, centers) — some tuning needed
- More complex implementation than standard SINDy
- Still requires a candidate library of basis functions $\psi_k$

### Expected Output

Same as SINDy (sparse coefficient vector), but with significantly lower variance in the estimated coefficients. Confidence intervals from bootstrap resampling of test functions.

---

## Approach 7: Physics-Informed Neural Network (PINN) with Embedded Model Selection

**Core idea:** Train a neural network to fit $x(t)$ while simultaneously satisfying the ODE as a soft constraint, with the damping function parameterized as a learnable mixture of candidate models weighted by a Gumbel-Softmax selector.

### Mathematical Formulation

Let $\hat{x}(t; \theta_x)$ be a neural network approximation of $x(t)$. Define:

$$
f_{\text{mix}}(\dot{x}) = \sum_{i=1}^{K} w_i \cdot f_i(\dot{x}; \alpha_i)
$$

where $w_i = \text{softmax}(\gamma_i / \tau)$ with temperature $\tau \to 0$ during training (annealing). The candidates $f_i$ are parameterized forms (linear, quadratic, cubic).

Loss:

$$
\mathcal{L} = \underbrace{\frac{1}{N}\sum_j \left(x_{\text{obs}}(t_j) - \hat{x}(t_j)\right)^2}_{\text{data fidelity}} + \lambda \underbrace{\frac{1}{N_c}\sum_l \left(m\ddot{\hat{x}}(t_l) + f_{\text{mix}}(\dot{\hat{x}}(t_l)) + k\hat{x}(t_l)\right)^2}_{\text{physics residual}} + \mu\,H(w)
$$

where $H(w) = -\sum_i w_i \log w_i$ is an entropy penalty encouraging selection of a single model.

### Implementation Sketch

1. Build a PINN for $\hat{x}(t)$: MLP with ~3 layers, input $t$, output $\hat{x}$
2. Compute $\dot{\hat{x}}, \ddot{\hat{x}}$ via automatic differentiation (`torch.autograd.grad`)
3. Define 3-4 candidate damping functions, each with learnable coefficients $\alpha_i$
4. Train with annealing: start with high $\tau$ (explore all models), gradually decrease (commit to one)
5. At convergence, inspect $w_i$ to determine the selected model

### Strengths

- No numerical differentiation needed — autodiff provides exact derivatives of the network
- Jointly fits the trajectory and discovers the ODE
- The Gumbel-Softmax trick provides differentiable model selection
- Works well even with sparse or irregularly sampled data

### Weaknesses

- PINNs are notoriously hard to train (loss balancing is an art)
- The physics loss and data loss compete, requiring careful $\lambda$ tuning
- Computationally heavier than SINDy-family methods
- May converge to trivial solutions if the network just memorizes data and ignores physics

### Expected Output

Model selection weights converging during training (e.g., $w_{\text{linear}} \to 0.02$, $w_{\text{quadratic}} \to 0.95$, $w_{\text{hybrid}} \to 0.03$). Learned coefficients $\alpha_i$ with uncertainty from ensemble training. Training loss curves showing physics residual decreasing.

---

## Summary Comparison

| Approach | Interpretable? | Noise Robust? | Needs Derivatives? | Complexity | Best For |
|---|---|---|---|---|---|
| **SINDy** | Yes (symbolic) | Moderate | Yes ($\dot{x}, \ddot{x}$) | Low | Quick first pass |
| **Bayesian Model Selection** | Yes (model + params) | High | No (ODE solve) | High | Rigorous statistical comparison |
| **Neural ODE** | No (black box) | High | No (learned) | Medium | Unknown/exotic damping |
| **GP on Residuals** | Partially (shape) | Low | Yes ($\ddot{x}$) | Low | Visual exploration |
| **Symbolic Regression** | Yes (exact formula) | Moderate | Yes ($\ddot{x}$) | Medium | Discovering unexpected forms |
| **Weak-Form (WSINDy)** | Yes (symbolic) | **Very High** | Only $\dot{x}$ | Medium | **Noisy data (recommended)** |
| **PINN + Model Select** | Yes (weights) | High | No (autodiff) | High | Sparse/irregular sampling |

## Recommended Workflow

1. Start with **WSINDy** (Approach 6) for a noise-robust symbolic result
2. Validate with **Bayesian model selection** (Approach 2) for statistical confidence
3. Use **Neural ODE** (Approach 3) as a model-free sanity check — if its learned $f(v)$ curve disagrees with the symbolic result, investigate further
