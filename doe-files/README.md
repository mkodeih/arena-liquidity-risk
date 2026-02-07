# Design of Experiments (DOE) Files

This directory contains pre-configured Design of Experiments (DOE) files for Arena simulations.

## Overview

DOE files define structured experimental designs to systematically explore parameter spaces and analyze simulation results. These files can be imported into Arena's Process Analyzer for automated experimentation.

## Available DOE Files

### 1. [baseline_scenarios.doe](baseline_scenarios.doe)
**Purpose**: Baseline liquidity risk assessment under normal conditions

**Design Type**: Full Factorial Design  
**Factors**: 3 (Initial Liquidity Ratio, Payment Arrival Rate, Market Stress)  
**Responses**: 2 (Shortfall Probability, Maximum Deficit)  
**Scenarios**: 90 (6 × 5 × 3)  
**Replications**: 30 per scenario

**Use When**:
- Establishing baseline risk metrics
- Initial model calibration
- Comparing normal vs. moderate stress conditions

### 2. [stress_testing.doe](stress_testing.doe)
**Purpose**: Stress testing under crisis conditions

**Design Type**: Fractional Factorial Design (2^(5-1))  
**Factors**: 5 (Shock Magnitude, Recovery Days, Contagion, Credit Reduction, Haircut)  
**Responses**: 3 (Survival Probability, LCR, Days to Failure)  
**Scenarios**: 16 (fractional design)  
**Replications**: 50 per scenario

**Use When**:
- Regulatory stress testing (CCAR, DFAST)
- Crisis scenario planning
- Identifying critical vulnerabilities

### 3. [optimization.doe](optimization.doe)
**Purpose**: Optimize liquidity management parameters

**Design Type**: Central Composite Design (CCD)  
**Factors**: 3 (Cash Buffer %, Asset Liquidation Threshold, Emergency Funding Cost)  
**Responses**: 2 (Total Cost, Risk-Adjusted Return)  
**Scenarios**: 15 (8 factorial + 6 axial + 1 center)  
**Replications**: 40 per scenario

**Use When**:
- Determining optimal buffer sizes
- Balancing cost vs. risk
- Response surface methodology

### 4. [sensitivity_analysis.doe](sensitivity_analysis.doe)
**Purpose**: Sensitivity analysis of key parameters

**Design Type**: One-at-a-Time (OAT)  
**Parameters**: 8 key simulation inputs  
**Variation**: ±20% from base case  
**Replications**: Varies by parameter

**Use When**:
- Identifying most influential parameters
- Model validation and calibration
- Risk driver analysis

## How to Use DOE Files

### Importing into Arena

1. Open your Arena model
2. **Tools > Process Analyzer**
3. **File > Open** and select DOE file
4. Verify controls (input variables) match your model
5. Verify responses (output statistics) are defined
6. **Scenarios > Add** to generate scenarios
7. **File > Save** to save Process Analyzer (.PAN) file
8. **Run > Run Scenarios** to execute

### Modifying DOE Files

DOE files are text-based and can be edited:

1. Open in text editor (Notepad++, VS Code)
2. Modify factor levels or add new factors
3. Save with same format
4. Re-import into Arena

### Creating Custom DOE

Use provided files as templates:

1. Copy existing DOE file
2. Modify factor names and levels
3. Update response definitions
4. Adjust replication counts
5. Save with descriptive name

## DOE File Format

### Structure

```
# Comments start with #
# Design metadata
DESIGN_TYPE: <Type>
FACTORS: <Number>
RESPONSES: <Number>
REPLICATIONS: <Number>

# Factor definitions
FACTOR_N:
  Name: <Variable_Name>
  Type: <Continuous|Discrete|Categorical>
  Levels: [values]
  
# Response definitions
RESPONSE_N:
  Name: <Statistic_Name>
  Type: <Continuous|Integer>
  Objective: <Minimize|Maximize|Target> (optional)
```

### Example

```
DESIGN_TYPE: FULL_FACTORIAL
FACTORS: 2
RESPONSES: 1
REPLICATIONS: 20

FACTOR_1:
  Name: OpeningBalance
  Type: Continuous
  Levels: [5000000, 10000000, 15000000]

FACTOR_2:
  Name: PaymentArrivalRate
  Type: Continuous
  Levels: [30, 50, 70]

RESPONSE_1:
  Name: MinimumBalance
  Type: Continuous
```

## Design Types Explained

### Full Factorial
- Tests all combinations of factor levels
- Complete information, no confounding
- Can be large (n^k scenarios for k factors with n levels each)

### Fractional Factorial
- Tests subset of combinations
- Reduces runs while preserving main effects
- Some interactions may be confounded
- Resolution III-V depending on fraction

### Central Composite Design (CCD)
- For response surface optimization
- Factorial points + axial points + center
- Enables quadratic model fitting
- Alpha (axial distance) = 1.682 for rotatability

### One-at-a-Time (OAT)
- Simplest sensitivity analysis
- Varies one parameter while holding others constant
- May miss interaction effects
- Good for initial screening

## Response Metrics

### Common Risk Metrics

| Metric | Arena Statistic | Description |
|--------|----------------|-------------|
| Shortfall Probability | Custom expression | P(MinBalance < 0) |
| VaR 95% | OMAX(MinimumBalance) × 0.95 | 95th percentile of min balance |
| Expected Shortfall | Custom | Average of deficits |
| Max Deficit | MAX(MaxDeficit) | Worst-case deficit |
| Time in Deficit | TAVG(TimeInDeficit) | Average time below zero |
| Liquidity Coverage Ratio | Custom ratio | Liquid assets / net outflows |

### Defining Custom Responses

In Arena OUTPUT Statistics:

```
Expression: (MinimumBalance < 0)
Type: Average
Statistic: Shortfall_Indicator

Then in Process Analyzer:
Response = DAVG(Shortfall_Indicator)
```

## Analysis Workflow

### 1. Screen Parameters (OAT)
Identify which parameters matter most

### 2. Baseline Analysis (Full Factorial)
Understand normal operating conditions

### 3. Stress Testing (Fractional Factorial)
Evaluate extreme scenarios efficiently

### 4. Optimization (CCD)
Find optimal parameter settings

### 5. Validation
Verify results with targeted runs

## Statistical Considerations

### Sample Size

Replications needed for confidence interval:

```
n = (Z * σ / E)^2

Where:
- Z = 1.96 for 95% confidence
- σ = estimated standard deviation
- E = desired margin of error

Example: For σ=$1M, E=$100K
n = (1.96 * 1000000 / 100000)^2 = 384 replications
```

### Common Random Numbers (CRN)

For fair comparison across scenarios:
- Use same random number streams
- Same seed across scenarios
- Set in Run Setup > Random Number Streams

### Power Analysis

Ensure sufficient power to detect differences:
- Power > 0.8 recommended
- Effect size based on practical significance
- Use pilot runs to estimate variance

## Tips and Best Practices

### Efficient Experimentation

1. **Start small**: Test with fewer replications initially
2. **Screen first**: Use OAT to eliminate unimportant factors
3. **Sequential approach**: Build understanding progressively
4. **Document**: Keep notes on scenario definitions
5. **Version control**: Save DOE files with version numbers

### Parameter Selection

- Choose realistic ranges based on historical data
- Include extreme values for stress testing
- Consider regulatory scenarios (Basel III)
- Align with institution's risk appetite

### Output Analysis

- Check for normality of responses
- Look for outliers and investigate
- Plot response surfaces for CCD
- Use ANOVA for factorial designs
- Calculate confidence intervals

## Troubleshooting

### Issue: Scenarios won't run
- **Solution**: Verify control names match model variables exactly
- Check that all required controls are defined

### Issue: Missing response values
- **Solution**: Ensure OUTPUT statistics are defined in model
- Check that response names match OUTPUT names

### Issue: High variance in results
- **Solution**: Increase replications
- Check model for unintended randomness
- Verify proper use of random number streams

### Issue: Process Analyzer crashes
- **Solution**: Reduce number of scenarios
- Split large designs into batches
- Increase system memory allocation

## Further Reading

- Arena Process Analyzer User's Guide
- Montgomery: "Design and Analysis of Experiments"
- Arena Help: Search "Process Analyzer"
- DOE tutorials in Arena Examples directory

## File Maintenance

- Review annually or when model changes
- Update levels based on current business conditions
- Archive old versions
- Document major changes in comments

---

**Version**: 1.0  
**Last Updated**: 2024  
**Maintainer**: Project Team
