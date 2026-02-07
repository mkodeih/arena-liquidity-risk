# Template: Custom Scenario

## Scenario Overview

**Scenario Name**: [Give your scenario a descriptive name]

**Objective**: [What are you trying to demonstrate or test?]

**Created By**: [Your name]

**Date**: [Creation date]

**Version**: [e.g., 1.0]

## Scenario Description

### Purpose

[Detailed description of what this scenario represents and why it's important]

Example:
```
This scenario tests the impact of a sudden payment surge combined with
a moderate reduction in interbank credit availability, representing
conditions during a market stress event where counterparty risk perceptions
increase.
```

### Business Context

[Real-world situation this scenario represents]

### Key Characteristics

- **Market Environment**: [Normal/Stressed/Crisis]
- **Time Period**: [Duration]
- **Stress Factors**: [List applied stresses]
- **Institutions Affected**: [All/Specific subset]
- **Expected Outcome**: [What you expect to see]

## Configuration Parameters

### Institution Configuration

Copy and modify this table:

| Institution | Initial Reserve | Reserve Ratio | Credit Limit | Collateral Haircut | Notes |
|-------------|----------------|---------------|--------------|-------------------|-------|
| INST001     | [value]        | [ratio]       | [limit]      | [haircut]         | [any special notes] |
| INST002     | [value]        | [ratio]       | [limit]      | [haircut]         | [any special notes] |
| INST003     | [value]        | [ratio]       | [limit]      | [haircut]         | [any special notes] |
| INST004     | [value]        | [ratio]       | [limit]      | [haircut]         | [any special notes] |
| INST005     | [value]        | [ratio]       | [limit]      | [haircut]         | [any special notes] |

**Parameter Justification**:
- Reserve levels: [Why chosen]
- Credit limits: [Why chosen]
- Haircuts: [Why chosen]

### Market Conditions

| Parameter               | Value    | Baseline | Change  | Justification |
|-------------------------|----------|----------|---------|---------------|
| Interest Rate           | [value]  | 0.045    | [+/-X%] | [why]         |
| Market Volatility       | [value]  | 0.12     | [+/-X%] | [why]         |
| Liquidity Premium       | [value]  | 0.005    | [+/-X%] | [why]         |
| Asset Correlation       | [value]  | 0.35     | [+/-X%] | [why]         |
| Stress Probability      | [value]  | 0.01     | [+/-X%] | [why]         |
| FX Rate                 | [value]  | 1.00     | [+/-X%] | [why]         |
| Collateral Value Index  | [value]  | 100.0    | [+/-X%] | [why]         |

### Payment Characteristics

| Characteristic          | Value      | Baseline   | Change    | Justification |
|-------------------------|------------|------------|-----------|---------------|
| Arrival Rate            | [rate]     | 125/hr     | [+/-X%]   | [why]         |
| Average Amount          | [amount]   | 250,000    | [+/-X%]   | [why]         |
| Standard Deviation      | [stddev]   | 100,000    | [+/-X%]   | [why]         |
| Priority Distribution   | [%H/N/L]   | 20/70/10   | [change]  | [why]         |

### Arena Model Settings

**Model File**: [Which .doe file to use]

**Replication Parameters**:
- Number of Replications: [n] (recommend 30-50)
- Replication Length: [minutes] (recommend 28,800 for 8-hour day)
- Warm-up Period: [minutes] (recommend 60)
- Time Units: [units] (recommend Minutes)
- Random Seed: [Auto/Fixed]

**Special Settings**:
- [Any unique model configurations]
- [Custom variables]
- [Modified logic]

## Implementation Steps

### Step 1: Prepare Input Files

```bash
# Create scenario-specific directory
mkdir -p data/custom_scenarios/[scenario_name]

# Copy templates
cp data/input-templates/*.xlsx data/custom_scenarios/[scenario_name]/

# Modify files according to configuration above
# [Specific instructions for your scenario]
```

### Step 2: Modify Parameters

Detailed instructions for changing:

1. **Institution Configuration**:
   - Open `institution_config.xlsx`
   - Row-by-row changes: [specific edits]
   - Save as `institution_config_[scenario_name].xlsx`

2. **Market Conditions**:
   - Open `market_conditions.xlsx`
   - Add new row or modify existing scenario
   - Set parameters as specified above

3. **Payment Data**:
   - [Instructions for generating or modifying payment data]
   - [Any special patterns to include]

### Step 3: Validate Input Data

```bash
python scripts/data_preparation.py \
  --input data/custom_scenarios/[scenario_name] \
  --output data/processed/[scenario_name] \
  --verbose
```

**Expected validation results**: [What you should see]

### Step 4: Configure Arena Model

1. Open Arena model: `arena-models/[model_name].doe`

2. Set model variables (Tools → Variables):
   ```
   [VARIABLE_1] = [value]
   [VARIABLE_2] = [value]
   ...
   ```

3. Configure data input:
   - Point to your custom input files
   - Verify connections

4. Set replication parameters as specified

### Step 5: Run Simulation

```bash
# Check model
[Describe any pre-run checks]

# Run simulation
[Step-by-step running instructions]

# Monitor for
[What to watch during execution]
```

### Step 6: Analyze Results

```bash
# Run analysis scripts
python scripts/results_analyzer.py \
  --results data/outputs/[scenario_name]/simulation_results.xlsx \
  --metrics data/outputs/[scenario_name]/risk_metrics.xlsx \
  --output reports/[scenario_name] \
  --baseline BASELINE

# Generate visualizations
python scripts/visualization.py \
  --input data/outputs/[scenario_name] \
  --output figures/[scenario_name] \
  --format png
```

## Expected Results

### Hypothesized Outcomes

**Performance Metrics**:
| Metric                  | Expected Value | Acceptable Range | Rationale |
|-------------------------|----------------|------------------|-----------|
| Settlement Rate         | [X%]           | [min-max]        | [why]     |
| Avg Settlement Time     | [X min]        | [min-max]        | [why]     |
| Max Queue Length        | [X]            | [min-max]        | [why]     |
| Gridlock Events         | [X]            | [min-max]        | [why]     |
| System Throughput       | [X pay/hr]     | [min-max]        | [why]     |

**Risk Metrics**:
| Institution | Expected LCR | Expected NSFR | Expected Risk Score | Notes |
|-------------|--------------|---------------|---------------------|-------|
| INST001     | [value]      | [value]       | [value]             | [notes] |
| INST002     | [value]      | [value]       | [value]             | [notes] |
| INST003     | [value]      | [value]       | [value]             | [notes] |
| INST004     | [value]      | [value]       | [value]             | [notes] |
| INST005     | [value]      | [value]       | [value]             | [notes] |

### Success Criteria

Define what constitutes success for this scenario:

✅ **Pass if**:
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

⚠️ **Warning if**:
1. [Warning condition 1]
2. [Warning condition 2]

❌ **Fail if**:
1. [Failure condition 1]
2. [Failure condition 2]

## Analysis Plan

### Key Questions to Answer

1. [Research question 1]
2. [Research question 2]
3. [Research question 3]

### Metrics to Track

**Primary Metrics**:
- [Metric 1]: [Why important]
- [Metric 2]: [Why important]

**Secondary Metrics**:
- [Metric 3]: [Why important]
- [Metric 4]: [Why important]

### Comparisons to Make

- [ ] Compare with baseline scenario
- [ ] Compare with [other relevant scenario]
- [ ] Compare institutions against each other
- [ ] Compare time periods (early/mid/late day)
- [ ] [Other comparisons]

### Statistical Tests

Planned statistical analyses:
- [Test 1]: To determine [what]
- [Test 2]: To determine [what]

Required confidence level: [X%] (typically 95%)

## Documentation

### Recording Results

Create a results summary document including:

1. **Executive Summary** (1 paragraph)
2. **Key Findings** (bullet points)
3. **Detailed Results** (tables and charts)
4. **Statistical Analysis** (significance tests)
5. **Interpretation** (what results mean)
6. **Recommendations** (actions to take)

### Visualizations to Create

Required plots:
- [ ] Settlement time distribution
- [ ] Queue length over time
- [ ] LCR heatmap by institution
- [ ] Risk score evolution
- [ ] [Custom visualizations specific to scenario]

### Reporting

Results should be reported to:
- [Stakeholder 1]
- [Stakeholder 2]
- [Team/Department]

Report format: [Presentation/Document/Dashboard]

## Sensitivity Analysis

Optional: Test sensitivity to key parameters

**Parameters to vary**:
1. [Parameter 1]: ±10%, ±25%
2. [Parameter 2]: ±10%, ±25%

**Purpose**: Understand robustness of results

## Extensions and Variations

Ideas for building on this scenario:

### Variation 1: [Name]
**Change**: [What to modify]
**Purpose**: [Why interesting]
**Expected**: [Anticipated outcome]

### Variation 2: [Name]
**Change**: [What to modify]
**Purpose**: [Why interesting]
**Expected**: [Anticipated outcome]

### Variation 3: [Name]
**Change**: [What to modify]
**Purpose**: [Why interesting]
**Expected**: [Anticipated outcome]

## Lessons Learned

After completing scenario, document:

### What Worked Well
- [Insight 1]
- [Insight 2]

### Challenges Encountered
- [Challenge 1]: [How resolved]
- [Challenge 2]: [How resolved]

### Unexpected Findings
- [Finding 1]: [Implications]
- [Finding 2]: [Implications]

### Recommendations for Future Scenarios
- [Recommendation 1]
- [Recommendation 2]

## References

**Related Scenarios**:
- [Scenario 1]: [Relationship]
- [Scenario 2]: [Relationship]

**Literature**:
- [Paper/Document 1]: [Relevance]
- [Paper/Document 2]: [Relevance]

**Regulatory Guidance**:
- [Regulation 1]: [How applies]
- [Regulation 2]: [How applies]

## Appendix

### A. Detailed Parameter Calculations

[Show any formulas or calculations used to derive parameters]

Example:
```
Stressed Reserve = Baseline Reserve × (1 - Shock Factor)
                 = 50,000,000 × (1 - 0.30)
                 = 35,000,000
```

### B. Data Files

List all custom data files created:
- `institution_config_[scenario_name].xlsx`
- `payment_data_[scenario_name].csv`
- `market_conditions_[scenario_name].xlsx`

### C. Model Modifications

Document any Arena model changes:
- [Module 1]: [Change made]
- [Variable 2]: [New definition]

### D. Validation Checks

Checks performed to ensure scenario validity:
- [ ] Parameters within realistic ranges
- [ ] No data quality issues
- [ ] Model runs without errors
- [ ] Results pass sanity checks
- [ ] Peer review completed

## Checklist

Before running this scenario:

- [ ] All parameters defined and justified
- [ ] Input files created and validated
- [ ] Arena model configured correctly
- [ ] Expected results documented
- [ ] Analysis plan established
- [ ] Success criteria defined
- [ ] Documentation template ready

After running this scenario:

- [ ] All replications completed successfully
- [ ] Results exported and backed up
- [ ] Analysis scripts run
- [ ] Visualizations generated
- [ ] Results compared with expectations
- [ ] Findings documented
- [ ] Lessons learned recorded
- [ ] Results communicated to stakeholders

## Support

For help with custom scenarios:
- Review [user-guide.md](../docs/user-guide.md)
- Consult [basic_scenario.md](basic_scenario.md) and [stress_test_scenario.md](stress_test_scenario.md)
- Check [troubleshooting.md](../docs/troubleshooting.md)
- Contact [scenario creator/owner]

---

**Notes**:
- Replace all [bracketed placeholders] with your specific values
- Delete sections not relevant to your scenario
- Add sections as needed for your specific case
- Keep documentation updated as scenario evolves
