# Methodology: Mathematical and Theoretical Foundations

## Table of Contents
1. [Introduction](#introduction)
2. [Liquidity Risk Fundamentals](#liquidity-risk-fundamentals)
3. [Queueing Theory Framework](#queueing-theory-framework)
4. [Stochastic Process Modeling](#stochastic-process-modeling)
5. [Risk Metrics and Calculations](#risk-metrics-and-calculations)
6. [Model Assumptions](#model-assumptions)
7. [Mathematical Notation](#mathematical-notation)

## Introduction

This document provides the mathematical and theoretical foundations underlying the Arena Liquidity Risk Simulation. The model combines elements from:
- Financial risk management theory
- Queueing theory and operations research
- Stochastic process modeling
- Payment system economics

## Liquidity Risk Fundamentals

### Definition

**Liquidity risk** is the risk that an institution cannot meet its payment obligations when they come due without incurring unacceptable losses. Two primary forms exist:

1. **Funding liquidity risk**: Inability to obtain funding at reasonable cost
2. **Market liquidity risk**: Inability to sell assets without significant price impact

### Key Components

The liquidity position at time $t$ is defined as:

$$L(t) = R(t) + C(t) - O(t)$$

Where:
- $L(t)$ = Available liquidity at time $t$
- $R(t)$ = Liquid reserves
- $C(t)$ = Available credit lines
- $O(t)$ = Outstanding payment obligations

### Liquidity Buffer

Institutions maintain a liquidity buffer to absorb shocks:

$$B = \alpha \cdot E[O_{daily}] + \beta \cdot \sigma[O_{daily}]$$

Where:
- $B$ = Required buffer
- $\alpha, \beta$ = Buffer coefficients
- $E[O_{daily}]$ = Expected daily outflows
- $\sigma[O_{daily}]$ = Standard deviation of daily outflows

## Queueing Theory Framework

### System Model

The payment system is modeled as an **M/G/c queueing system** with:
- Poisson arrival process (rate $\lambda$)
- General service time distribution
- $c$ parallel servers (processing channels)
- Finite buffer capacity $K$

### Arrival Process

Payment arrivals follow a non-homogeneous Poisson process:

$$P(N(t) = n) = \frac{[\Lambda(t)]^n}{n!} e^{-\Lambda(t)}$$

Where $\Lambda(t) = \int_0^t \lambda(s) ds$ is the cumulative intensity function.

### Service Time Distribution

Service time $S$ (payment processing time) follows a log-normal distribution:

$$f_S(s) = \frac{1}{s\sigma\sqrt{2\pi}} \exp\left(-\frac{(\ln s - \mu)^2}{2\sigma^2}\right)$$

Parameters:
- $\mu$ = Mean of log(service time)
- $\sigma$ = Standard deviation of log(service time)

### Queue Length

The expected queue length under steady-state is given by Little's Law:

$$E[L] = \lambda \cdot E[W]$$

Where:
- $E[L]$ = Expected number in system
- $\lambda$ = Arrival rate
- $E[W]$ = Expected time in system

### Waiting Time

Expected waiting time in queue (Pollaczek-Khinchin formula for M/G/1):

$$E[W_q] = \frac{\lambda E[S^2]}{2(1-\rho)}$$

Where:
- $\rho = \lambda E[S]$ = System utilization
- $E[S^2]$ = Second moment of service time

## Stochastic Process Modeling

### Payment Arrival Model

Payment arrivals are modeled as a compound Poisson process:

$$X(t) = \sum_{i=1}^{N(t)} Y_i$$

Where:
- $N(t)$ = Poisson counting process (number of payments)
- $Y_i$ = Random payment amount (i.i.d.)

### Payment Amount Distribution

Payment amounts follow a mixture of log-normal distributions:

$$f_Y(y) = \sum_{j=1}^{m} w_j \cdot \text{LogNormal}(\mu_j, \sigma_j^2)$$

Where:
- $w_j$ = Weight of component $j$ ($ \sum w_j = 1$)
- $\mu_j, \sigma_j$ = Parameters of component $j$

### Reserve Dynamics

Reserve level evolves according to:

$$dR(t) = [I(t) - O(t)]dt + dF(t)$$

Where:
- $I(t)$ = Incoming payment flow
- $O(t)$ = Outgoing payment flow  
- $F(t)$ = Central bank facility draws (jump process)

### Gridlock Model

Gridlock occurs when a circular dependency prevents settlements:

**Gridlock condition**: 
$$\exists \text{ cycle } C: \sum_{i \in C} P_i > \sum_{i \in C} L_i$$

Where:
- $P_i$ = Payment obligations of institution $i$
- $L_i$ = Available liquidity of institution $i$

## Risk Metrics and Calculations

### Liquidity Coverage Ratio (LCR)

$$\text{LCR} = \frac{\text{High Quality Liquid Assets (HQLA)}}{\text{Total Net Cash Outflows over 30 days}}$$

**Regulatory requirement**: LCR ≥ 100%

**Components**:
- **HQLA**: Level 1 and Level 2 assets
- **Net Cash Outflows**: 
  $$\text{NCO} = \max\{\text{Total Expected Outflows} - \min\{\text{Total Expected Inflows}, 75\% \times \text{Outflows}\}, 0\}$$

### Net Stable Funding Ratio (NSFR)

$$\text{NSFR} = \frac{\text{Available Stable Funding (ASF)}}{\text{Required Stable Funding (RSF)}}$$

**Regulatory requirement**: NSFR ≥ 100%

**ASF Calculation**:
$$\text{ASF} = \sum_i c_i \times A_i$$

Where $c_i$ is the ASF factor for liability/equity category $i$

**RSF Calculation**:
$$\text{RSF} = \sum_j d_j \times L_j$$

Where $d_j$ is the RSF factor for asset category $j$

### Intraday Liquidity Position

$$\text{ILP}(t) = R_0 + \sum_{s=0}^{t} [I(s) - O(s)] - \text{Reserve}_{\min}$$

**Constraint**: $\text{ILP}(t) \geq 0$ for all $t$ during the day

### Value at Risk (VaR)

Liquidity VaR at confidence level $\alpha$:

$$\text{VaR}_\alpha = -\inf\{x: P(L \leq x) \geq 1-\alpha\}$$

Typically calculated at $\alpha = 95\%$ or $99\%$

### Expected Shortfall (CVaR)

$$\text{ES}_\alpha = E[L | L \leq \text{VaR}_\alpha]$$

More conservative measure than VaR (captures tail risk)

### Survival Probability

Probability of maintaining positive liquidity over period $[0,T]$:

$$P_{\text{survival}} = P(\min_{t \in [0,T]} L(t) \geq 0)$$

### Settlement Efficiency

$$\text{Efficiency} = \frac{\text{Value Settled}}{\text{Liquidity Used}} = \frac{\sum P_i}{L_{\max}}$$

Higher values indicate more efficient liquidity usage

### Gridlock Intensity

Expected frequency of gridlock events:

$$\lambda_{\text{gridlock}} = \lim_{T \to \infty} \frac{E[N_{\text{gridlock}}(T)]}{T}$$

## Model Assumptions

### Key Assumptions

1. **Independence**: Payment arrivals are independent across institutions
2. **Stationarity**: Statistical properties constant within trading day segments
3. **Rationality**: Institutions optimize liquidity usage
4. **Perfect Information**: All participants observe system state
5. **No Strategic Behavior**: No gaming or manipulation

### Relaxations

The model can be extended to relax assumptions:

- **Correlated arrivals**: Use multivariate Poisson processes
- **Non-stationarity**: Time-dependent arrival rates $\lambda(t)$
- **Strategic behavior**: Game-theoretic extensions
- **Information asymmetry**: Bayesian updating models

### Limitations

1. Does not model:
   - Credit risk contagion
   - Behavioral/panic responses
   - Regulatory interventions beyond standard facilities
   - Market microstructure effects

2. Simplifications:
   - Discrete institution set (reality is continuous entry/exit)
   - Homogeneous processing capabilities
   - Deterministic collateral values (in baseline)

## Mathematical Notation

### Sets and Indices

- $\mathcal{I}$ = Set of financial institutions, $i \in \mathcal{I}$
- $\mathcal{T}$ = Time horizon, $t \in [0, T]$
- $\mathcal{P}$ = Set of payments, $p \in \mathcal{P}$

### Random Variables

- $N(t)$ = Number of payment arrivals by time $t$
- $Y$ = Payment amount (random variable)
- $S$ = Service time (random variable)
- $W$ = Waiting time in queue (random variable)

### Parameters

- $\lambda$ = Arrival rate (payments per unit time)
- $\mu$ = Service rate (payments per unit time)
- $\rho = \lambda/\mu$ = System utilization
- $\alpha$ = Reserve ratio (fraction of assets)
- $\beta$ = Risk aversion parameter
- $\gamma$ = Collateral haircut (discount factor)

### Functions

- $L(t)$ = Liquidity level at time $t$
- $R(t)$ = Reserve balance at time $t$
- $C(t)$ = Available credit at time $t$
- $O(t)$ = Outstanding obligations at time $t$

### Operators

- $E[\cdot]$ = Expected value
- $\text{Var}[\cdot]$ = Variance
- $P(\cdot)$ = Probability
- $\max\{\cdot\}$, $\min\{\cdot\}$ = Maximum, minimum
- $\sum$ = Summation
- $\int$ = Integration
- $\partial/\partial x$ = Partial derivative

### Abbreviations

- LCR = Liquidity Coverage Ratio
- NSFR = Net Stable Funding Ratio
- HQLA = High Quality Liquid Assets
- ASF = Available Stable Funding
- RSF = Required Stable Funding
- VaR = Value at Risk
- ES/CVaR = Expected Shortfall / Conditional VaR
- RTGS = Real-Time Gross Settlement
- DNS = Deferred Net Settlement

## References

See [references.md](references.md) for detailed citations of:
- Basel III liquidity framework
- Queueing theory textbooks
- Payment system research
- Stochastic process theory
