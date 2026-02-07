# Example: Basic Baseline Scenario

## Objective

This example demonstrates a basic liquidity risk simulation under normal market conditions. It serves as:
- An introduction to running the simulation
- A baseline for comparison with stress scenarios
- Validation of model setup and configuration

## Prerequisites

- Arena simulation software installed
- Project files downloaded and extracted
- Basic familiarity with Arena (see [arena-tutorial.md](../docs/arena-tutorial.md))
- Python 3.8+ with required packages (optional, for analysis)

## Scenario Description

**Market Conditions**: Normal
- Stable interest rates (4.5%)
- Low market volatility (12%)
- Normal payment volumes
- No systemic stress

**Institutions**: 5 financial institutions
- Mix of large and small banks
- Adequate reserves and credit lines
- Normal risk profiles

**Time Period**: 8-hour trading day
- 08:00 to 16:00
- Standard business hours
- Normal payment patterns

## Configuration

### Input Files

Use the following input files from `data/input-templates/`:

**1. Institution Configuration** (`institution_config.xlsx`)

| Institution | Initial Reserve | Reserve Ratio | Credit Limit | Haircut | Risk Category |
|-------------|----------------|---------------|--------------|---------|---------------|
| INST001     | 50,000,000     | 0.15          | 10,000,000   | 0.15    | AAA           |
| INST002     | 25,000,000     | 0.12          | 5,000,000    | 0.20    | AA            |
| INST003     | 15,000,000     | 0.10          | 3,000,000    | 0.25    | A             |
| INST004     | 10,000,000     | 0.13          | 2,500,000    | 0.20    | AA            |
| INST005     | 8,000,000      | 0.14          | 2,000,000    | 0.18    | AA            |

**2. Market Conditions** (`market_conditions.xlsx`)

Use the "NORMAL" scenario row:
- Interest Rate: 0.045 (4.5%)
- Market Volatility: 0.12 (12%)
- Liquidity Premium: 0.005 (0.5%)
- Asset Correlation: 0.35
- Stress Probability: 0.01 (1%)
- FX Rate: 1.00 (baseline)
- Collateral Value Index: 100.0

**3. Payment Parameters** (`data/sample-data/example_payments.csv`)

Use the provided sample payment data with:
- 50 payment transactions
- Mixed priority levels (HIGH, NORMAL, LOW)
- Payment amounts ranging from 140,000 to 1,150,000
- Distributed throughout trading day

### Arena Model Settings

**Model**: `arena-models/liquidity_risk_baseline.doe`

**Replication Parameters**:
- Number of Replications: 30
- Replication Length: 28,800 minutes (8 hours)
- Warm-up Period: 60 minutes (1 hour)
- Base Time Units: Minutes
- Random Seed: Auto (for different streams per replication)

**Other Settings**:
- Statistics Collection: All default statistics enabled
- Animation: On for first run (off for batch runs)
- Output to File: Enabled

## Step-by-Step Instructions

### Step 1: Prepare Input Data

```bash
# Navigate to project directory
cd arena-liquidity-risk

# Validate and prepare data
python scripts/data_preparation.py \
  --input data/input-templates \
  --output data/processed \
  --verbose
```

**Expected output**: Confirmation of successful data preparation and summary statistics.

### Step 2: Open Arena Model

1. Launch Arena software
2. File → Open
3. Navigate to `arena-models/liquidity_risk_baseline.doe`
4. Click Open

### Step 3: Configure Input Data

In Arena:
1. Locate the **ReadWrite** module (if present) or data import section
2. Set file path to your prepared data:
   - Institution config: `data/processed/institutions_processed.csv`
   - Payment data: `data/sample-data/example_payments.csv`
   - Market conditions: `data/processed/markets_processed.csv`
3. Verify connections

### Step 4: Set Run Parameters

1. **Run → Setup → Replication Parameters**
2. Enter:
   - Number of Replications: `30`
   - Replication Length: `28800` minutes
   - Hours Per Day: `24`
   - Warm-up Period: `60` minutes
3. Click OK

### Step 5: Check Model

1. Press **F4** or **Run → Check Model**
2. Review any warnings or errors
3. Fix any issues before proceeding
4. Model should show "0 Errors, 0 Warnings"

### Step 6: Run Single Replication (Test)

1. Click **Run** button (▶) or press **F5**
2. Watch animation to verify model behavior
3. Observe:
   - Payments arriving and being processed
   - Queue lengths staying reasonable
   - No resource deadlocks
   - Statistics updating
4. Wait for completion message

### Step 7: Review Single Run Results

1. After run completes, review **Category Overview**
2. Check key metrics:
   - Entity statistics (cycle time, wait time)
   - Resource utilization
   - Queue lengths
3. Verify results are reasonable

### Step 8: Run Full Experiment (30 Replications)

1. **Run → Setup**: Confirm 30 replications
2. **Run → Batch Run** (Ctrl+F5) for faster execution
3. Or use **Run → Go** with animation off
4. Wait for all replications to complete (several minutes)

### Step 9: Export Results

1. **Run → Results**
2. Select metrics to export
3. **File → Export**
4. Save to `data/outputs/baseline_results.xlsx`

Or use configured automatic export to:
- `data/output-templates/simulation_results.xlsx`
- `data/output-templates/risk_metrics.xlsx`

### Step 10: Analyze Results

Run analysis scripts:

```bash
# Statistical analysis
python scripts/results_analyzer.py \
  --results data/output-templates/simulation_results.xlsx \
  --metrics data/output-templates/risk_metrics.xlsx \
  --output reports/baseline \
  --baseline BASELINE

# Visualizations
python scripts/visualization.py \
  --input data/output-templates \
  --output figures/baseline \
  --format png
```

## Expected Results

### Simulation Results

**Performance Metrics** (mean ± std dev across 30 replications):

| Metric                     | Expected Value    | Acceptable Range |
|----------------------------|-------------------|------------------|
| Total Payments             | 1000 ± 25         | 950-1050         |
| Settled Payments           | 985 ± 15          | 960-1000         |
| Settlement Rate            | 98.5% ± 1%        | > 95%            |
| Rejected Payments          | 3 ± 2             | < 20             |
| Average Settlement Time    | 2.5 ± 0.5 min     | < 5 min          |
| Max Queue Length           | 8 ± 3             | < 15             |
| Gridlock Events            | 0 ± 0             | 0                |
| System Throughput          | 123 ± 5 pay/hr    | > 100 pay/hr     |

**Interpretation**:
- ✅ High settlement rate indicates sufficient liquidity
- ✅ Low average settlement time shows efficient processing
- ✅ Zero gridlock events confirms system stability
- ✅ Low queue lengths indicate adequate capacity

### Risk Metrics

**Liquidity Ratios** (by institution, mean values):

| Institution | LCR    | NSFR   | Intraday Liquidity | Risk Score |
|-------------|--------|--------|-------------------|------------|
| INST001     | 1.45   | 1.15   | 8,500,000        | 0.12       |
| INST002     | 1.28   | 1.08   | 4,200,000        | 0.18       |
| INST003     | 1.15   | 1.02   | 2,800,000        | 0.25       |
| INST004     | 1.22   | 1.05   | 1,850,000        | 0.20       |
| INST005     | 1.35   | 1.12   | 1,450,000        | 0.15       |

**Interpretation**:
- ✅ All LCRs > 1.0 (regulatory minimum met)
- ✅ All NSFRs > 1.0 (stable funding adequate)
- ✅ Positive intraday liquidity throughout day
- ✅ Risk scores in "Low" range (< 0.30)

**System-Wide**:
- Total Credit Used: < 10% of available credit
- Central Bank Facility Draws: 0
- Average Collateral Posted: Minimal
- Overall System Risk: LOW

## Analysis

### Key Observations

1. **System Performs Well**: Under normal conditions, the payment system operates efficiently with:
   - High settlement success rate (> 98%)
   - Fast processing times (< 3 minutes average)
   - No system bottlenecks or gridlocks

2. **Adequate Liquidity**: All institutions maintain:
   - Regulatory minimum ratios (LCR, NSFR)
   - Comfortable buffers above minimums
   - Positive intraday positions

3. **Low Risk Profile**: 
   - Risk scores indicate low probability of liquidity stress
   - No institutions approaching critical thresholds
   - System resilient to normal operational variation

4. **Efficient Resource Usage**:
   - Credit lines underutilized (ample capacity)
   - No central bank facility needed
   - Collateral requirements minimal

### Statistical Validity

**Confidence Intervals** (95% CI for key metrics):

- Settlement Time: [2.3, 2.7] minutes
- Settlement Rate: [97.5%, 99.5%]
- Max Queue Length: [6.5, 9.5] payments

**Variation**: Coefficient of variation < 5% for most metrics indicates stable, predictable performance.

## Visualization

The analysis scripts generate several plots:

1. **Settlement Time Distribution**: Shows normal distribution centered around 2.5 min
2. **Queue Length Boxplot**: Median ~7, few outliers
3. **LCR Heatmap**: All institutions in green zone
4. **Throughput Time Series**: Stable across replications

See `figures/baseline/` directory for generated plots.

## Extensions

Try these variations to explore model behavior:

### Extension 1: Increase Payment Volume
- Modify arrival rate to 150 payments/hour (20% increase)
- **Expected**: Slightly longer settlement times, higher queue lengths
- **Purpose**: Test capacity limits

### Extension 2: Reduce Reserves
- Decrease reserve ratios by 20% (e.g., 0.15 → 0.12)
- **Expected**: Lower LCRs but still above minimum
- **Purpose**: Assess reserve sensitivity

### Extension 3: Different Priority Mix
- Change 50% of payments to HIGH priority
- **Expected**: Faster average settlement, some queue reordering
- **Purpose**: Understand priority impact

### Extension 4: Extended Trading Day
- Increase replication length to 16 hours
- **Expected**: Similar rates, higher total volume
- **Purpose**: Long-term stability check

## Common Issues

### Issue 1: Results Differ from Expected

**Likely causes**:
- Random variation (normal)
- Different Arena version
- Modified parameters

**Solution**: Run more replications (50-100) and compare statistical ranges rather than point estimates.

### Issue 2: Model Runs Slowly

**Solutions**:
- Turn off animation: Run → Run Control → Animation → Off
- Use batch run mode: Ctrl+F5
- Close other applications

### Issue 3: Low Settlement Rate

**Check**:
- Sufficient liquidity reserves
- Credit limits adequate
- No input data errors
- Processing capacity sufficient

## Next Steps

After completing this basic example:

1. **Compare with Stress Test**: Run [stress_test_scenario.md](stress_test_scenario.md) to see how system behaves under adverse conditions

2. **Create Custom Scenario**: Use [custom_scenario.md](custom_scenario.md) template to design your own experiments

3. **Explore DOE**: Try design of experiments in `doe-files/` for systematic parameter studies

4. **Validate Model**: Use historical data (if available) to validate model predictions

## References

- User Guide: [docs/user-guide.md](../docs/user-guide.md)
- Methodology: [docs/methodology.md](../docs/methodology.md)
- Arena Tutorial: [docs/arena-tutorial.md](../docs/arena-tutorial.md)

## Support

For questions or issues:
- Check [troubleshooting.md](../docs/troubleshooting.md)
- Review Arena help documentation (F7)
- Consult project documentation in `docs/`
