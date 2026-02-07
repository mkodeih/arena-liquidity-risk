# 04 - Monte Carlo Simulation Setup

This guide shows how to configure Arena for Monte Carlo simulation with multiple independent replications, proper random number stream management, batch runs, and scenario analysis.

## Overview

Monte Carlo simulation provides:
- Statistical confidence in risk estimates
- Distribution of outcomes (not just point estimates)
- Probability of extreme events (Value at Risk)
- Sensitivity analysis across scenarios
- Robust results through repeated sampling

We'll configure:
- Multiple independent replications
- Random number stream controls
- Scenario management
- Batch run execution
- Output analysis for confidence intervals

## Understanding Monte Carlo in Arena

### Replication vs. Simulation Run

**Replication**: One complete simulation run (e.g., one trading day)
- Uses specific random number seeds
- Produces one sample outcome
- Independent from other replications

**Simulation**: Collection of all replications
- Aggregates statistics across replications
- Provides mean, variance, confidence intervals

### Independence Requirements

Each replication must be:
1. **Statistically independent**: Different random seeds
2. **Identically configured**: Same parameters
3. **Complete**: Full simulation period

## Configuring Replication Parameters

### 1. Access Run Setup

**Run > Setup > Replication Parameters**

### 2. Set Number of Replications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Number of Replications | 1000 | Recommended minimum |
| Replication Length | 480 | Minutes (8 hours trading) |
| Hours Per Day | 24 | Standard |
| Warm-up Period | 0 | No warm-up for daily model |
| Base Time Units | Minutes | Match project settings |
| Initialize Between Replications | Yes | Critical for independence |

**Choosing Number of Replications**:

| Replications | Use Case | Confidence |
|--------------|----------|------------|
| 30 | Initial testing | Low |
| 100 | Development | Medium |
| 500 | Analysis | Good |
| 1000 | Production | High |
| 5000+ | Publication | Very High |

**Rule of Thumb**: For 95% CI with ±5% accuracy, need ~1000 replications.

### 3. Initialize System Between Replications

**Critical Setting**: 

Check **"Initialize System"** box:
- Resets all variables to initial values
- Clears queues and statistics
- Ensures independence
- Prevents carryover effects

### 4. Set Replication Length

Match your institution's operating hours:

| Institution | Hours | Minutes | Notes |
|-------------|-------|---------|-------|
| US Bank | 8 | 480 | 9 AM - 5 PM |
| 24-hour | 24 | 1440 | Full day |
| European Bank | 9 | 540 | Extended hours |
| Settlement Window | 6 | 360 | Core hours only |

**Example**: TARGET2 operates 7 AM - 6 PM = 11 hours = 660 minutes

## Random Number Stream Management

### 1. Understanding Streams

Arena uses **independent random number streams** to generate random variables.

**Why Multiple Streams**:
- Ensures independence between different random processes
- Allows sensitivity analysis (vary one stream, fix others)
- Prevents correlation artifacts
- Enables Common Random Numbers (CRN) for scenario comparison

### 2. Configure Random Streams

**Tools > Run Setup > Random Number Streams** or access via dialog in modules.

**Recommended Stream Allocation**:

| Stream | Process | Used In | Seed |
|--------|---------|---------|------|
| 1 | Payment arrivals | CREATE (inter-arrival time) | 123456 |
| 2 | Payment amounts | ASSIGN (Amount) | 234567 |
| 3 | Payment direction | ASSIGN (PaymentType) | 345678 |
| 4 | Payment priority | ASSIGN (Priority) | 456789 |
| 5 | Processing times | PROCESS delays | 567890 |
| 6 | Stress events | Scenario triggers | 678901 |
| 7 | Institution selection | Multi-bank models | 789012 |
| 8 | Settlement delays | Network latency | 890123 |
| 9 | Reserved | Future use | 901234 |
| 10 | Reserved | Future use | 12345 |

### 3. Set Stream Numbers in Modules

**CREATE Module** (Payment arrivals):
```
Value: EXPO(60/PaymentArrivalRate, 1)
                                    ^
                                Stream number
```

**ASSIGN Module** (Payment amount):
```
Amount = LOGN(MeanPaymentAmount, StdDevPaymentAmount, 2)
                                                       ^
                                                   Stream number
```

**General Syntax**:
```
DISTRIBUTION(parameter1, parameter2, stream)
```

### 4. Verify Stream Independence

Run diagnostic:

**Tools > Run Setup > Advanced > Display Stream Usage**

Check:
- Each stream used for single purpose
- No stream used >10,000 times/replication (may cycle)
- Stream numbers are unique

## Implementing Common Random Numbers (CRN)

### Purpose

Compare scenarios using **identical random conditions**:
- Scenario A: Opening balance = $10M
- Scenario B: Opening balance = $15M
- **Same payment arrivals, amounts** (via CRN)

This reduces variance in comparing scenarios.

### Implementation

1. **Fix random seeds** across scenarios
2. **Maintain stream assignments**
3. **Change only parameters under study**

**Example**:
```
Base Case: OpeningBalance = 10M, Seed 1 = 123456
Scenario 1: OpeningBalance = 15M, Seed 1 = 123456  (same!)
Scenario 2: OpeningBalance = 8M,  Seed 1 = 123456  (same!)
```

Result: All scenarios see identical payment patterns, isolating effect of opening balance.

## Setting Up Scenario Analysis

### Option 1: Manual Parameter Changes

1. Run base case (1000 replications)
2. **File > Save As** → `Liquidity_Scenario1.doe`
3. Change parameters (e.g., `PaymentArrivalRate = 60`)
4. Run again
5. Compare outputs

### Option 2: Using Process Analyzer (PAN)

**Tools > Process Analyzer** (if licensed)

1. **Controls** (Parameters to vary):
   - Opening Balance: 5M, 10M, 15M, 20M
   - Arrival Rate: 40, 50, 60, 70
   - Mean Amount: 800K, 1M, 1.2M

2. **Responses** (Metrics to track):
   - Minimum Balance (mean)
   - Maximum Exposure (95th percentile)
   - Shortfall Count (mean)
   - Credit Line Used (max)

3. **Set Replications**: 1000 per scenario

4. **Run All Scenarios**

PAN will:
- Run all combinations
- Tabulate results
- Generate response surface plots
- Identify optimal settings

### Option 3: Using VBA Macros

Create Visual Basic script to:
- Loop through parameter values
- Run simulation
- Export results
- Aggregate statistics

**Example VBA** (simplified):
```vba
For OpeningBalance = 5000000 To 20000000 Step 5000000
    ThisDocument.Variables("OpeningBalance").Value = OpeningBalance
    ThisDocument.Run
    ExportResults "Results_" & OpeningBalance & ".txt"
Next
```

### Option 4: Scenario Variables

Define scenario selector variable:

**In Variable module**:
- Name: `ScenarioID`
- Initial Value: 1

**In ASSIGN module (startup)**:
```
IF ScenarioID == 1 THEN
    OpeningBalance = 10000000
    PaymentArrivalRate = 50
ELSE IF ScenarioID == 2 THEN
    OpeningBalance = 15000000
    PaymentArrivalRate = 60
ELSE IF ScenarioID == 3 THEN
    OpeningBalance = 8000000
    PaymentArrivalRate = 70
ENDIF
```

Change `ScenarioID` before each run batch.

## Configuring Batch Runs

### 1. Set Up Run Control

**Run > Setup > Run Control**

| Parameter | Value |
|-----------|-------|
| Run Mode | Batch |
| Pause on Completion | No |
| Show Animation | No |
| Generate Reports | Yes |
| Clear Statistics | Yes |

### 2. Optimize Performance

**For faster batch runs**:

**Run > Setup > Advanced**:
- Disable animation: **Unchecked**
- Suppress message boxes: **Checked**
- Fast-forward mode: **Checked**
- Statistics collection only: **Checked**

**Tools > Options > Run Control**:
- Animation speed: **Off**
- Update displays: **Never**

### 3. Command Line Execution

Arena can run from command line for automation:

```batch
"C:\Program Files\Rockwell Software\Arena\Arena.exe" /run /quit "C:\Models\Liquidity_Risk_Simulation.doe"
```

Parameters:
- `/run`: Start simulation immediately
- `/quit`: Exit Arena after completion
- `/batch`: Suppress dialogs

**Batch script** example:
```batch
@echo off
SET ARENA="C:\Program Files\Rockwell Software\Arena\Arena.exe"
SET MODEL="C:\Models\Liquidity_Risk_Simulation.doe"

FOR %%S IN (1 2 3 4 5) DO (
    echo Running Scenario %%S
    %ARENA% /run /quit %MODEL%
    timeout /t 10
)
```

## Handling Long Run Times

### 1. Estimate Duration

**Formula**:
```
Total Time = Replications × Time per Replication × Overhead Factor

Example:
1000 reps × 2 seconds × 1.2 = 2400 seconds = 40 minutes
```

### 2. Progress Monitoring

Enable run-time display:

**Run > Setup > Run Control**:
- Show replication status: **Yes**
- Display interval: Every 10 replications

Watch status bar for:
- Current replication number
- Estimated time remaining
- Completion percentage

### 3. Checkpoint/Restart (Advanced)

For very long runs (>1000 reps):

1. Split into batches:
   - Run 1-500 → Export results
   - Run 501-1000 → Export results
   - Combine in post-processing

2. Use process analyzer incremental mode

3. Save intermediate results

## Independent Scenarios Setup

### 1. Stress Testing Scenarios

Define scenarios for regulatory compliance:

| Scenario | Description | Parameters |
|----------|-------------|------------|
| Base | Normal conditions | Default values |
| Stress 1 | Payment surge | Arrival rate × 2 |
| Stress 2 | Large payment shock | 10% of payments × 5 |
| Stress 3 | Low opening liquidity | Opening balance × 0.5 |
| Stress 4 | Constrained inflows | Incoming ratio = 0.3 |
| Combined | Multiple stresses | All above |

### 2. Implementing Shocks

**Option A**: Event-triggered shock

Add CREATE module:
```
Name: Create_Stress_Event
Type: Constant
Value: 240  (at 4 hours)
Max Arrivals: 1
```

Connect to ASSIGN:
```
PaymentArrivalRate = PaymentArrivalRate * 2
ShockActive = 1
```

**Option B**: Random shock timing

```
ShockTime = UNIF(60, 420, 6)  # Random time between 1-7 hours
```

In ASSIGN logic:
```
IF TNOW >= ShockTime AND ShockActive == 0 THEN
    PaymentArrivalRate = PaymentArrivalRate * 2
    ShockActive = 1
ENDIF
```

### 3. Scenario Documentation

Create scenario log file:

**File > Export > Documentation**

Include:
- Scenario ID and name
- Parameter values
- Random seeds
- Run date/time
- Results summary

## Output Configuration for Multiple Replications

### 1. Set Output Statistics

**Run > Setup > Statistics > Output**

Select statistics to collect **across replications**:

| Statistic | Type | Expression |
|-----------|------|------------|
| Avg_Min_Balance | Average | MinimumBalance |
| Avg_Max_Exposure | Average | MaxExposure |
| SD_Min_Balance | Std Deviation | MinimumBalance |
| 95th_Exposure | Percentile | MaxExposure |

### 2. Configure Half-Width Intervals

**Run > Setup > Statistics > Confidence Intervals**

| Parameter | Value |
|-----------|-------|
| Confidence Level | 0.95 (95%) |
| Method | Student's t |
| Include in Report | Yes |

### 3. Replication-Specific Output

To save individual replication results:

Add RECORD at end of run:
```
Type: Time Persistent
Variable: MinimumBalance
Tally: Rep_Min_Balance
```

Export after each replication:
**File > Export > Output Data > Append Mode**

## Validation of Monte Carlo Setup

### 1. Verify Independence

Run test with 10 replications:

Check output report:
- Each replication should have different `MinimumBalance`
- No patterns or trends across replications
- Standard deviation > 0

### 2. Check Convergence

Plot cumulative mean vs. replication number:

| Replications | Cum. Mean Min Balance | Stabilized? |
|--------------|----------------------|-------------|
| 10 | $8.2M | No |
| 50 | $8.5M | No |
| 100 | $8.7M | Getting close |
| 500 | $8.73M | Yes |
| 1000 | $8.74M | Yes |

**Convergence**: When adding replications doesn't change mean by >1%

### 3. Verify Random Streams

Add temporary RECORD modules to check distributions:

```
RECORD: Payment_Amounts
Type: Tally
Attribute: Amount
```

After run, verify:
- Distribution matches specification (e.g., log-normal)
- Mean close to parameter
- No truncation or censoring

## Advanced: Latin Hypercube Sampling

For better coverage with fewer replications:

### 1. Concept

Instead of pure random sampling, divide parameter space into strata.

### 2. Implementation (External)

1. Use Excel/Python to generate Latin Hypercube samples
2. Create parameter file with one row per replication
3. Read in Arena using READWRITE

Example:
```
# Replication 1: OpeningBalance = 9.2M, ArrivalRate = 48
# Replication 2: OpeningBalance = 14.1M, ArrivalRate = 71
# etc.
```

**Benefits**: Reduced variance, fewer replications needed (500 vs. 1000)

## Checklist

- [ ] Number of replications set (1000 recommended)
- [ ] Replication length matches operating hours
- [ ] Initialize between replications enabled
- [ ] Random number streams assigned to processes
- [ ] Stream independence verified
- [ ] Scenario parameters defined
- [ ] Common random numbers implemented (if comparing scenarios)
- [ ] Batch run mode configured
- [ ] Animation disabled for performance
- [ ] Output statistics configured for replication aggregation
- [ ] Confidence intervals enabled
- [ ] Independence test passed
- [ ] Convergence validated
- [ ] Documentation of scenarios complete

## Next Steps

Proceed to **[05-statistics.md](05-statistics.md)** to configure comprehensive output statistics, risk metrics, and data export.

---

**Previous**: [03 - Liquidity Tracking](03-liquidity-tracking.md) | **Next**: [05 - Statistics](05-statistics.md)
