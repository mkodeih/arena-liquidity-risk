# Design of Experiments (DOE) for Arena Liquidity Risk Simulation

## Overview

This repository contains four Design of Experiments (DOE) files specifically crafted for systematic exploration of liquidity risk scenarios using Arena Simulation Software. These experimental designs enable comprehensive analysis of intraday liquidity dynamics, stress testing, optimization, and sensitivity analysis.

## DOE Files

### 1. baseline_scenarios.doe

**Purpose:** Establish baseline understanding of how fundamental liquidity parameters affect system stability.

**Design Type:** Full Factorial Design (90 experimental runs)

**Factors:**
- **Initial Liquidity Ratio** (0.05 to 0.30, 6 levels): The starting liquidity buffer as a ratio of total assets
- **Daily Withdrawal Rate** (0.01 to 0.10, 5 levels): Daily withdrawal demand as proportion of liquid assets  
- **Market Stress Level** (Low, Medium, High): Market conditions affecting asset liquidation

**Response Variables:**
- **Days to Illiquidity:** Number of days the system can maintain adequate liquidity
- **Maximum Drawdown:** Peak-to-trough decline in liquidity buffer

**Use Case:** This design systematically explores all combinations of baseline parameters to identify critical thresholds and interaction effects. Use this to understand which parameters most significantly impact liquidity sustainability under normal operating conditions.

**Replications:** 30 per scenario for statistical robustness

---

### 2. stress_testing.doe

**Purpose:** Evaluate system resilience under extreme market shocks and contagion scenarios.

**Design Type:** Fractional Factorial Design - ½ fraction, Resolution V (40 experimental runs)

**Factors:**
- **Shock Magnitude** (5%, 10%, 15%, 20%, 25%): Severity of sudden liquidity shock
- **Recovery Time** (5, 10, 15, 20 days): Duration for market to return to normal
- **Contagion Probability** (0.1, 0.3, 0.5, 0.7): Likelihood of shock spreading to connected institutions

**Response Variables:**
- **Survival Probability:** Probability of maintaining adequate liquidity throughout stress period
- **Liquidity Coverage Ratio:** Minimum LCR achieved during the scenario

**Use Case:** Efficiently tests stress scenarios with reduced experimental burden while maintaining ability to estimate main effects and two-way interactions. Critical for regulatory stress testing and capital adequacy assessment.

**Replications:** 30 per scenario

---

### 3. optimization.doe

**Purpose:** Find optimal liquidity management policies that balance cost and risk.

**Design Type:** Central Composite Design (CCD) for Response Surface Methodology (20 experimental runs)

**Factors:**
- **Cash Buffer Percentage** (5-25%, continuous): Target cash holdings
- **Asset Liquidation Threshold** (10-50%, continuous): Trigger point for selling assets
- **Emergency Funding Cost** (0.5-5%, continuous): Annual rate for emergency facilities

**Response Variables:**
- **Total Cost:** Aggregate operational cost including buffer maintenance and emergency funding
- **Risk-Adjusted Return:** Return on assets adjusted for liquidity risk exposure

**Use Case:** Enables quadratic response surface modeling to find optimal parameter settings. The design includes factorial points (corners), axial points (star), and center points to estimate curvature and identify optimal operating conditions.

**Replications:** 30 per scenario

---

### 4. sensitivity_analysis.doe

**Purpose:** Quantify how sensitive each output is to variations in input parameters.

**Design Type:** One-at-a-Time (OAT) Design with ±20% parameter variations (27 experimental runs)

**Factors:** 13 parameters varied individually:
- Initial_Liquidity_Ratio
- Daily_Withdrawal_Rate
- Market_Stress_Level
- Cash_Buffer_Percentage
- Asset_Liquidation_Threshold
- Emergency_Funding_Cost
- Shock_Magnitude
- Recovery_Time
- Contagion_Probability
- Interest_Rate
- Asset_Volatility
- Correlation_Coefficient
- Regulatory_Minimum

**Response Variables:**
- Days_To_Illiquidity (with elasticity measure)
- Maximum_Drawdown (with elasticity measure)
- Survival_Probability (with elasticity measure)
- Total_Cost (with elasticity measure)
- Risk_Adjusted_Return (with elasticity measure)
- Liquidity_Coverage_Ratio (with elasticity measure)

**Use Case:** Identifies which parameters have the greatest influence on model outputs. Results displayed as tornado diagrams and spider plots to prioritize data collection efforts and model refinement.

**Replications:** 30 per scenario

---

## How to Import into Arena

### Step-by-Step Instructions:

1. **Open Arena Simulation Software**
   - Launch Rockwell Arena (version 14.0 or later recommended)

2. **Access Process Analyzer**
   - Navigate to: `Tools → Process Analyzer` (PAN)
   - Or press `Ctrl+P`

3. **Import DOE File**
   - In Process Analyzer, click `File → Import Design`
   - Browse to the desired `.doe` file
   - Select the file and click `Open`

4. **Link to Simulation Model**
   - The DOE file will prompt you to link variables to your Arena model
   - Map each factor in the DOE to the corresponding variable in your simulation model
   - Map response variables to output statistics in your model

5. **Verify Configuration**
   - Review the scenario matrix to ensure all runs are correctly configured
   - Check that replication settings match (30 replications recommended)
   - Verify warmup period and run length settings

6. **Execute Scenarios**
   - Click `Scenarios → Run All` to execute all experimental runs
   - Monitor progress in the Process Analyzer window
   - Estimated runtime: varies by model complexity (allow several hours for complete designs)

### Variable Mapping Guide:

When importing, you'll need to map DOE factors to Arena model variables. Ensure your Arena model includes:

**Input Variables (controllable):**
- Liquidity ratio parameters
- Withdrawal rate distributions
- Market stress indicators
- Policy thresholds
- Cost parameters

**Output Variables (responses):**
- Time-based metrics (days to illiquidity)
- Performance ratios (LCR, drawdown)
- Financial metrics (costs, returns)
- Probability measures

---

## Expected Outputs and Analysis Approach

### baseline_scenarios.doe

**Expected Outputs:**
- Main effects plots showing impact of each factor
- Interaction plots revealing synergistic effects
- Cube plots for three-way factor visualization
- ANOVA table with statistical significance tests

**Analysis Approach:**
1. Identify statistically significant factors (p < 0.05)
2. Examine interaction plots for non-additive effects
3. Determine critical thresholds where system behavior changes
4. Develop predictive equations for days to illiquidity

**Key Questions Answered:**
- What is the minimum safe initial liquidity ratio?
- How do withdrawal rates and market stress interact?
- Which factor combinations lead to rapid illiquidity?

---

### stress_testing.doe

**Expected Outputs:**
- Main effects and two-way interaction estimates
- Alias structure showing confounded effects
- Normal probability plots for effect screening
- Survival curves under different stress scenarios

**Analysis Approach:**
1. Screen for significant main effects
2. Identify critical two-way interactions
3. Map failure regions in parameter space
4. Estimate probability distributions of survival

**Key Questions Answered:**
- What shock magnitude can the system withstand?
- How does recovery time affect resilience?
- What is the contagion risk threshold?

---

### optimization.doe

**Expected Outputs:**
- Quadratic response surface equations
- 3D surface plots showing response topology
- Contour plots for multi-objective trade-offs
- Optimal parameter settings using desirability functions

**Analysis Approach:**
1. Fit second-order polynomial models
2. Check model adequacy (R², lack-of-fit tests)
3. Identify stationary points (minima, maxima, saddle points)
4. Perform multi-objective optimization using desirability

**Key Questions Answered:**
- What cash buffer minimizes total cost?
- What is the optimal liquidation threshold?
- How to balance cost versus risk-adjusted return?

---

### sensitivity_analysis.doe

**Expected Outputs:**
- Elasticity coefficients for each parameter
- Tornado diagrams ranking parameter importance
- Spider plots showing sensitivity across parameters
- Standardized regression coefficients

**Analysis Approach:**
1. Calculate elasticity: E = (ΔY/Y) / (ΔX/X)
2. Rank parameters by absolute elasticity
3. Identify robust vs. sensitive outputs
4. Prioritize parameters for further refinement

**Key Questions Answered:**
- Which parameters most influence model outputs?
- Which outputs are most sensitive to parameter uncertainty?
- Where should data collection efforts focus?

---

## Linking to Simulation Model Files

These DOE files are designed to work with Arena simulation models implementing intraday liquidity risk dynamics. The models should include:

**Required Model Components:**
- **Entities:** Cash flows, withdrawal requests, asset liquidation orders
- **Resources:** Liquid asset pools, emergency funding facilities
- **Processes:** Daily withdrawal processing, asset liquidation, funding drawdown
- **Variables:** Liquidity ratios, coverage metrics, cost accumulators
- **Expressions:** Stress level multipliers, contagion triggers, threshold conditions

**Model File Structure:**
```
/models
  ├── baseline_liquidity_model.doe  (corresponds to baseline_scenarios.doe)
  ├── stress_test_model.doe         (corresponds to stress_testing.doe)
  ├── optimization_model.doe         (corresponds to optimization.doe)
  └── sensitivity_model.doe          (corresponds to sensitivity_analysis.doe)
```

**Integration Steps:**
1. Open the corresponding Arena model file
2. Import the DOE file via Process Analyzer
3. Map DOE factors to model input variables
4. Map DOE responses to model output statistics
5. Run experiments and collect results

---

## Research Foundation

These experimental designs are based on concepts from intraday liquidity simulation research, incorporating:

- **Basel III Liquidity Standards:** LCR and NSFR requirements
- **Stress Testing Frameworks:** Regulatory and internal stress scenarios
- **Network Effects:** Contagion and systemic risk propagation
- **Optimization Theory:** Multi-objective cost-risk trade-offs
- **Sensitivity Analysis:** Morris method and variance-based approaches

The designs enable comprehensive exploration of the liquidity risk landscape while maintaining statistical efficiency and practical feasibility.

---

## Statistical Considerations

### Sample Size (Replications)
All designs specify 30 replications per scenario to:
- Achieve 95% confidence intervals
- Detect moderate effect sizes (Cohen's d ≥ 0.5)
- Account for stochastic variability in simulation outputs

### Randomization
Arena automatically randomizes:
- Run order to prevent systematic bias
- Random number streams across replications
- Seed values for independent samples

### Blocking
If computational resources are limited, consider:
- Running designs in blocks over time
- Using common random numbers for variance reduction
- Implementing sequential experimentation strategies

---

## Advanced Usage

### Sequential Experimentation
1. Start with **sensitivity_analysis.doe** to screen parameters
2. Use significant parameters in **baseline_scenarios.doe**
3. Apply **stress_testing.doe** to extreme scenarios
4. Optimize using **optimization.doe** for final policies

### Metamodeling
Results from these DOEs can be used to build metamodels:
- Regression models for prediction
- Neural networks for complex relationships
- Kriging models for spatial interpolation
- Use metamodels for real-time risk assessment

### Integration with Risk Management
- Export optimal parameters to production systems
- Use sensitivity rankings for model governance
- Implement stress scenarios in contingency planning
- Update DOE designs as new data becomes available

---

## Technical Requirements

**Software:**
- Rockwell Arena Simulation Software (v14.0+)
- Process Analyzer (PAN) module
- OptQuest (optional, for optimization)
- Output Analyzer (optional, for detailed statistical analysis)

**Hardware:**
- Minimum: 8 GB RAM, quad-core processor
- Recommended: 16+ GB RAM, 8+ core processor
- Storage: 10+ GB free space for output files

**Computational Time:**
- Baseline scenarios: ~4-8 hours
- Stress testing: ~2-4 hours
- Optimization: ~1-3 hours
- Sensitivity analysis: ~1-2 hours

*Times vary based on model complexity and hardware specifications*

---

## Troubleshooting

### Common Issues:

**Issue:** DOE file fails to import  
**Solution:** Verify Arena version compatibility and file format integrity

**Issue:** Variable mapping errors  
**Solution:** Ensure Arena model variables match DOE factor names exactly

**Issue:** Insufficient memory errors  
**Solution:** Reduce replications or run scenarios in batches

**Issue:** Convergence problems in optimization  
**Solution:** Check bounds and ensure response surface is well-behaved

---

## References and Further Reading

1. **Arena Documentation:**
   - Rockwell Automation. (2023). Arena User's Guide. Chapter 10: Process Analyzer.

2. **DOE Methodology:**
   - Montgomery, D.C. (2017). Design and Analysis of Experiments (9th ed.). Wiley.
   - Box, G.E.P., & Draper, N.R. (2007). Response Surfaces, Mixtures, and Ridge Analyses (2nd ed.). Wiley.

3. **Liquidity Risk Simulation:**
   - Basel Committee on Banking Supervision. (2013). Basel III: The Liquidity Coverage Ratio and liquidity risk monitoring tools.
   - Bouchaud, J.P., et al. (2013). "How Markets Slowly Digest Changes in Supply and Demand." In Handbook of Financial Markets.

4. **Sensitivity Analysis:**
   - Saltelli, A., et al. (2008). Global Sensitivity Analysis: The Primer. Wiley.

---

## Support and Contact

For questions about these DOE files or Arena simulation implementation:
- Review Arena documentation and tutorials
- Consult with simulation modeling experts
- Refer to academic literature on liquidity risk modeling

---

## License

These DOE files are provided for research and educational purposes. Modify and extend as needed for your specific liquidity risk analysis requirements.

---

**Last Updated:** 2026-02-07  
**Version:** 1.0  
**Compatible with:** Arena 14.0 and later
