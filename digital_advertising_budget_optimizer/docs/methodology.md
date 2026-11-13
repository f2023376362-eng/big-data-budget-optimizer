# Methodology & Mathematical Formulations
## Digital Advertising Budget Optimization

### 1. Data Synthesis & Distributional Modeling
The synthetic data generator models real-world advertising dynamics across the 5 platforms:
- **Impression Volume Distribution:** Log-normal distribution with location $\mu = 7.5$ and scale $\sigma = 0.85$.
- **Click Behavior:** Generated via Poisson-distributed click arrival conditional on sampled platform CTR:
  $$\lambda = I \times \text{CTR}, \quad C \sim \text{Poisson}(\lambda)$$
- **Conversions:** Generated via Binomial trial modeling where clicks represent independent trials and CVR represents conversion probability:
  $$V \sim \text{Binomial}(C, \text{CVR})$$

### 2. Physical & Semantic Boundary Invariants
The system enforces strict mathematical inequalities:
1. $0 \le C \le I$ (Clicks cannot exceed impressions)
2. $0 \le V \le C$ (Conversions cannot exceed clicks)
3. $\text{Spend} \ge 0.0$ (Spend must be non-negative)
4. $\text{Revenue} \ge 0.0$ (Revenue must be non-negative)

### 3. Simplex Optimization Algorithm for Capital Allocation
Given total budget $B = 1,000,000$ and $N = 5$ advertising platforms:
- Objective: Determine allocation vector $\mathbf{x} = [x_1, x_2, \dots, x_5]^T$ such that:
  $$\sum_{i=1}^5 x_i = 1.0, \quad L_i \le x_i \le U_i \quad \forall i$$
  where $L_i = 0.05$ (5% minimum) and $U_i = 0.45$ (45% maximum).
- Absolute rupee allocation for platform $i$:
  $$A_i = B \cdot x_i$$
  subject to:
  $$\sum_{i=1}^5 A_i = B \quad (\text{Exact to the cent/rupee})$$

### 4. Strategic Weighting Models
- **ROAS Maximization:**
  $$w_i = \text{ROAS}_i^{1.8} \cdot \left(1.0 + 0.3 \cdot \text{CVR}_i\right)$$
- **Conversion Maximization:**
  $$w_i = 1.5 \cdot \left(\frac{1}{\text{CPA}_i}\right)_{\text{norm}} + 1.2 \cdot (\text{CVR}_i)_{\text{norm}} + 0.3 \cdot (\text{CTR}_i)_{\text{norm}}$$
- **Balanced Optimization:**
  $$w_i = 0.45 \cdot (\text{ROAS}_i)_{\text{norm}} + 0.25 \cdot \left(\frac{1}{\text{CPA}_i}\right)_{\text{norm}} + 0.20 \cdot (\text{CVR}_i)_{\text{norm}} - 0.10 \cdot (\sigma_i)_{\text{norm}}$$

