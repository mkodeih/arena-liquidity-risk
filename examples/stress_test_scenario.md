# Example: Stress Test Scenario

## Objective

This example demonstrates liquidity risk simulation under severe stress conditions. It shows:
- System behavior during market crisis
- Regulatory ratio degradation
- Gridlock potential
- Resilience testing
- Recovery mechanisms

## Scenario Description

**Market Conditions**: Crisis
- High interest rates (12%)
- Extreme market volatility (45%)
- Payment surge (50% increase)
- Collateral value decline (30% drop)
- Credit tightening

**Stress Factors** (Applied Simultaneously):

1. **Liquidity Shock**: 30% reduction in available reserves
2. **Payment Surge**: 50% increase in payment arrivals
3. **Credit Crunch**: 40% reduction in interbank credit limits
4. **Market Crash**: Collateral values decline 30%
5. **Correlation Spike**: Asset correlation jumps to 0.90

## Configuration

### Stress Parameters

**Modified Institution Configuration**:

| Institution | Initial Reserve | Reserve Ratio | Credit Limit | Modified Reserve | Modified Credit |
|-------------|----------------|---------------|--------------|------------------|-----------------|
| INST001     | 50,000,000     | 0.15          | 10,000,000   | 35,000,000      | 6,000,000      |
| INST002     | 25,000,000     | 0.12          | 5,000,000    | 17,500,000      | 3,000,000      |
| INST003     | 15,000,000     | 0.10          | 3,000,000    | 10,500,000      | 1,800,000      |
| INST004     | 10,000,000     | 0.13          | 2,500,000    | 7,000,000       | 1,500,000      |
| INST005     | 8,000,000      | 0.14          | 2,000,000    | 5,600,000       | 1,200,000      |

**Market Conditions** (CRISIS scenario):
- Interest Rate: 0.120 (12%)
- Market Volatility: 0.45 (45%)
- Liquidity Premium: 0.080 (8%)
- Asset Correlation: 0.90
- Stress Probability: 0.35 (35% per day)
- FX Rate: 0.85 (15% depreciation)
- Collateral Value Index: 70.0 (30% decline)

**Payment Parameters**:
- Arrival Rate: 187.5 payments/hour (50% increase)
- Average Amount: 375,000 (50% increase)
- Use higher-volume payment data or duplicate baseline payments

### Arena Model Settings

**Model**: `arena-models/liquidity_risk_stress.doe`

**Replication Parameters**:
- Number of Replications: 50 (more needed for stress scenario variability)
- Replication Length: 28,800 minutes (8 hours)
- Warm-up Period: 60 minutes
- Base Time Units: Minutes

## Step-by-Step Instructions

### Step 1: Prepare Stress Input Data

Create modified input files:

**1. Copy baseline files**:
```bash
cp data/input-templates/institution_config.xlsx data/stress/institution_config_stress.xlsx
cp data/input-templates/market_conditions.xlsx data/stress/market_conditions_stress.xlsx
```

**2. Modify files**:
- Edit institution config to apply 30% reserve reduction
- Edit credit limits (40% reduction)
- Select CRISIS scenario in market conditions
- Increase payment volumes in payment data

**3. Validate**:
```bash
python scripts/data_preparation.py \
  --input data/stress \
  --output data/processed_stress \
  --verbose
```

### Step 2: Load Stress Model

1. Open Arena
2. Load `arena-models/liquidity_risk_stress.doe`
3. Or use baseline model with modified parameters

### Step 3: Configure Stress Parameters

Update model variables (Tools → Variables):

```
RESERVE_SHOCK_FACTOR = 0.70      # 30% reduction
CREDIT_SHOCK_FACTOR = 0.60       # 40% reduction  
ARRIVAL_RATE_MULTIPLIER = 1.50   # 50% increase
COLLATERAL_VALUE_FACTOR = 0.70   # 30% decline
STRESS_MODE = TRUE               # Enable stress logic
```

### Step 4: Set Extended Replications

Due to higher variability in stress:
- **Replications**: 50 (not 30)
- **Run time**: Longer (10-15 minutes total)

### Step 5: Run Stress Test

1. Check model (F4)
2. Run batch mode (Ctrl+F5) - animation may be confusing under stress
3. Monitor progress
4. Wait for all 50 replications

### Step 6: Export and Analyze

```bash
# Analysis
python scripts/results_analyzer.py \
  --results data/output-templates/simulation_results.xlsx \
  --metrics data/output-templates/risk_metrics.xlsx \
  --output reports/stress_test \
  --baseline BASELINE

# Visualizations
python scripts/visualization.py \
  --input data/output-templates \
  --output figures/stress_test \
  --format png
```

## Expected Results

### Simulation Results (Degraded Performance)

| Metric                     | Baseline      | Stress Test   | Change      |
|----------------------------|---------------|---------------|-------------|
| Total Payments             | 1000          | 1500          | +50%        |
| Settled Payments           | 985 (98.5%)   | 1275 (85%)    | -13.5 pp    |
| Average Settlement Time    | 2.5 min       | 8.5 min       | +240%       |
| Max Queue Length           | 8             | 42            | +425%       |
| Gridlock Events            | 0             | 2.3 ± 1.5     | N/A         |
| System Throughput          | 123 pay/hr    | 159 pay/hr    | +29%        |
| Rejected Payments          | 3 (0.3%)      | 95 (6.3%)     | +6.0 pp     |

**Key Observations**:
- ⚠️ Settlement rate drops but stays above 80% (acceptable in stress)
- ⚠️ Settlement times increase significantly (still under 15 min average)
- ⚠️ Queue lengths grow substantially (but system doesn't fail)
- ⚠️ Gridlock events occur but are resolved
- ✅ System continues to function despite stress

### Risk Metrics (Regulatory Stress)

**Liquidity Ratios Under Stress**:

| Institution | LCR (Baseline) | LCR (Stress) | NSFR (Baseline) | NSFR (Stress) |
|-------------|----------------|--------------|-----------------|---------------|
| INST001     | 1.45           | 1.05         | 1.15            | 1.02          |
| INST002     | 1.28           | 0.98         | 1.08            | 0.95          |
| INST003     | 1.15           | 0.89         | 1.02            | 0.91          |
| INST004     | 1.22           | 0.95         | 1.05            | 0.97          |
| INST005     | 1.35           | 1.08         | 1.12            | 1.00          |

**Regulatory Assessment**:
- ❌ INST002 and INST003 fall below LCR minimum (1.0)
- ❌ INST002, INST003 below NSFR minimum (1.0)
- ⚠️ INST001, INST004, INST005 meet minimums but with low buffers
- 🔔 **Regulatory action required** for non-compliant institutions

**Stress Indicators**:
- Total Credit Used: 75% of available (high utilization)
- Central Bank Facility Draws: 8-12 instances per day
- Collateral Posted: Near maximum
- Intraday Liquidity: Multiple negative periods

### Risk Score Evolution

| Institution | Baseline Score | Stress Score | Risk Level Change |
|-------------|----------------|--------------|-------------------|
| INST001     | 0.12 (Low)     | 0.32 (High)  | ⬆️ 2 levels       |
| INST002     | 0.18 (Low)     | 0.54 (Critical) | ⬆️ 3 levels    |
| INST003     | 0.25 (Moderate)| 0.62 (Critical) | ⬆️ 2 levels    |
| INST004     | 0.20 (Moderate)| 0.48 (High)  | ⬆️ 1 level        |
| INST005     | 0.15 (Low)     | 0.36 (High)  | ⬆️ 2 levels       |

## Detailed Analysis

### Gridlock Analysis

**Typical Gridlock Pattern**:
1. **Time**: Usually occurs mid-day (11:00-13:00)
2. **Trigger**: Large payment requiring coordination
3. **Involved**: 3-4 institutions in circular dependency
4. **Duration**: 15-30 minutes before resolution
5. **Resolution**: Central bank facility or payment netting

**Gridlock Example**:
```
INST002 owes 2M to INST003 (waiting for liquidity)
INST003 owes 1.8M to INST004 (waiting for INST002 payment)
INST004 owes 1.5M to INST002 (waiting for INST003 payment)
→ Circular wait resolved by facility draw or queue optimization
```

### Liquidity Consumption Pattern

**Intraday Liquidity Profile** (INST002):

| Time  | Available Liquidity | Change      | Event                |
|-------|---------------------|-------------|----------------------|
| 08:00 | 17,500,000         | Baseline    | Market open          |
| 09:30 | 12,300,000         | -5.2M       | Large outflows       |
| 11:15 | 4,800,000          | -7.5M       | Gridlock scenario    |
| 11:45 | 8,200,000          | +3.4M       | Facility draw        |
| 14:00 | 6,500,000          | -1.7M       | Continued stress     |
| 16:00 | 9,100,000          | +2.6M       | End-of-day inflows   |

**Pattern**: Mid-day trough requiring intervention

### Central Bank Facility Usage

**Facility Draws**:
- INST002: 4 draws, total 15M
- INST003: 5 draws, total 12M
- INST004: 2 draws, total 6M
- Average rate: 5% (penalty rate for stress borrowing)
- Total cost: ~50,000 in interest charges per day

**Interpretation**: Facility serves its purpose as liquidity backstop

### Queue Dynamics

**Maximum Queue Composition** (at peak):
- HIGH priority: 5 payments (≈800K avg)
- NORMAL priority: 28 payments (≈400K avg)
- LOW priority: 9 payments (≈200K avg)
- Total queued value: ≈15M

**Queue Resolution**:
- Priority payments processed first
- Some LOW payments deferred until next day
- No queue collapse or infinite growth

## Stress Scenarios Tested

This example actually includes 5 sub-scenarios:

### Scenario A: Liquidity Shock Only
- 30% reserve reduction
- Other factors normal
- **Result**: Manageable with facility access

### Scenario B: Payment Surge Only
- 50% volume increase
- Normal reserves/credit
- **Result**: Longer queues but acceptable

### Scenario C: Credit Crunch Only
- 40% credit reduction
- Normal reserves/volumes
- **Result**: Increased gridlock risk

### Scenario D: Market Crash Only
- 30% collateral value decline
- Other factors normal
- **Result**: Reduced borrowing capacity

### Scenario E: Combined Stress (Primary)
- All factors applied together
- **Result**: Significant stress but system survives

## Regulatory Implications

### Basel III Compliance

**Under Normal Conditions**: ✅ All institutions compliant

**Under Stress**: ❌ 2/5 institutions non-compliant
- INST002: LCR 0.98, NSFR 0.95 (both below 1.0)
- INST003: LCR 0.89, NSFR 0.91 (both below 1.0)

**Required Actions**:
1. **Immediate**:
   - Activate liquidity management plans
   - Access central bank facilities
   - Restrict outflows

2. **Short-term** (1-2 days):
   - Raise additional capital
   - Sell HQLA to meet ratios
   - Reduce lending

3. **Medium-term** (1-2 weeks):
   - Restructure balance sheet
   - Increase stable funding
   - Rebuild buffers

### Stress Test Pass/Fail

**Criteria**:
- LCR remains > 0.85 even in stress: ✅ Passed (min observed: 0.89)
- NSFR remains > 0.90 in stress: ✅ Passed (min observed: 0.91)
- No unresolved gridlocks: ✅ Passed (all resolved < 30 min)
- Settlement rate > 75%: ✅ Passed (achieved 85%)
- Central bank facility < 20% of reserves: ✅ Passed (max 15%)

**Overall Assessment**: System demonstrates adequate resilience ✅

## Visualizations

Generated plots show:

1. **Settlement Time Distribution**: Right-skewed, long tail in stress
2. **Queue Length Over Time**: Spikes during gridlock episodes
3. **LCR Heatmap**: Red zones for INST002 and INST003
4. **Facility Usage Bar Chart**: INST002 and INST003 highest users
5. **Risk Score Evolution**: All institutions elevated

## Recommendations

Based on stress test results:

### For INST002 and INST003 (Non-Compliant)

**Immediate Actions**:
1. Increase reserve holdings by 20-25%
2. Negotiate higher credit lines
3. Diversify funding sources
4. Implement stricter outflow limits

**Structural Improvements**:
1. Shift asset mix toward HQLA
2. Extend funding tenor (improve NSFR)
3. Reduce maturity mismatch
4. Build larger liquidity buffers

### For All Institutions

**Operational Enhancements**:
1. Improve intraday monitoring
2. Enhance gridlock detection/prevention
3. Optimize queue management
4. Strengthen facility access procedures

**Risk Management**:
1. Conduct stress tests quarterly
2. Maintain stress test contingency plans
3. Monitor leading indicators
4. Coordinate with central bank

### System-Wide

**Infrastructure**:
1. Enhance payment prioritization algorithms
2. Implement real-time gridlock detection
3. Improve settlement efficiency
4. Consider liquidity-saving mechanisms

## Extensions

### Extension 1: Recovery Scenario
- Start with stress conditions
- Gradually relax constraints over time
- **Purpose**: Test recovery path

### Extension 2: Worse Stress
- Apply 50% reserve shock
- 100% payment volume increase
- **Purpose**: Find breaking point

### Extension 3: Individual Institution Failure
- Remove INST002 from system mid-day
- **Purpose**: Test contagion effects

### Extension 4: Policy Interventions
- Implement emergency measures
- Relax regulatory requirements temporarily
- **Purpose**: Evaluate crisis responses

## Lessons Learned

1. **Resilience Matters**: Buffers above minimums are essential
2. **Facility Access**: Central bank backstop is critical
3. **Gridlock Management**: Early detection and resolution key
4. **Combined Shocks**: Multiple factors amplify effects
5. **Monitoring**: Real-time tracking enables proactive management

## Next Steps

After this stress test:

1. **Compare with Baseline**: Review [basic_scenario.md](basic_scenario.md) to understand degradation
2. **Design Custom Stress**: Use [custom_scenario.md](custom_scenario.md) for specific concerns
3. **Optimize Parameters**: Run `doe-files/optimization.doe` to find robustness improvements
4. **Validate Model**: Check if stress results align with historical stress events

## References

- Basel III Stress Testing: BCBS Publications 238, 295
- User Guide: [docs/user-guide.md](../docs/user-guide.md)
- Methodology: [docs/methodology.md](../docs/methodology.md)
- Stress Testing DOE: `doe-files/stress_testing.doe`

## Support

For stress testing questions:
- Consult methodology documentation for stress formulas
- Review regulatory guidelines for acceptance criteria
- Check troubleshooting guide if results seem wrong
- Contact risk management team for interpretation
