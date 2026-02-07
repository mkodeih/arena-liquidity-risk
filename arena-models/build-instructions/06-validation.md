# 06 - Model Validation and Verification

This guide provides comprehensive techniques for validating your liquidity risk simulation model, ensuring correct implementation, and debugging common issues.

## Overview

Validation ensures:
- **Correctness**: Model behaves as specified
- **Accuracy**: Results match theoretical expectations
- **Reliability**: Consistent, reproducible outputs
- **Credibility**: Stakeholder confidence in results

We'll cover:
- Verification of model logic
- Statistical validation of distributions
- Sanity checks and boundary testing
- Debugging techniques
- Performance validation
- Documentation standards

## Model Verification Steps

### 1. Static Verification (Before Running)

#### Check Module Connections

**Visual inspection**:
- All modules connected in logical sequence
- No orphaned modules
- Arrows point in correct direction
- Decision branches properly labeled

**Arena Check**:
**Run > Check Model**

Reviews:
- Syntax errors
- Undefined variables
- Missing attributes
- Resource conflicts

#### Verify Parameter Values

Create checklist:

| Parameter | Expected | Actual | Status |
|-----------|----------|--------|--------|
| OpeningBalance | 10000000 | ? | ✓ |
| PaymentArrivalRate | 50 | ? | ✓ |
| MeanPaymentAmount | 1000000 | ? | ✓ |
| ReplicationLength | 480 | ? | ✓ |
| NumReplications | 1000 | ? | ✓ |

**View all variables**:
- Click **Variable** button → Review spreadsheet

#### Validate Logic Flow

**Trace each entity type**:

1. **Incoming payment** path:
   - CREATE → ASSIGN attributes → DECIDE (type=1) → ASSIGN (add to balance) → RECORD → DISPOSE

2. **Outgoing payment** path:
   - CREATE → ASSIGN attributes → DECIDE (type=2) → DECIDE (liquidity check) → Branch A (sufficient) or Branch B (insufficient)

3. **Queued payment** path:
   - QUEUE → Wait for liquidity → SEIZE → ASSIGN (deduct) → DISPOSE

**Document** with flowchart or notes.

### 2. Dynamic Verification (Test Runs)

#### Single Entity Test

**Purpose**: Verify one payment processes correctly.

**Setup**:
1. **CREATE**: Max Arrivals = 1
2. **Run > Setup**: Replication Length = 10 minutes
3. Enable animation: **Run > Run Control > Animation**: Slow

**Run and observe**:
- Entity created at t=0
- Attributes assigned correctly (check variables window)
- Routes through correct DECIDE branches
- Balance updates as expected
- Entity disposed

**Check**:
```
Initial Balance: $10M
Payment: $1M (outgoing)
Expected Final Balance: $9M
Actual Final Balance: ?  → Must match!
```

#### Deterministic Test

**Purpose**: Remove randomness to verify exact calculations.

**Setup**:
1. Set all distributions to constants:
   - Inter-arrival time: `5.0` (not EXPO(...))
   - Amount: `1000000.0` (not LOGN(...))
   - Type: `1` (all incoming) or `2` (all outgoing)

2. Run 1 replication, 60 minutes

**Expected outcomes**:

**All incoming, $1M each, 5 min intervals**:
- Payments: 60/5 = 12
- Final Balance: $10M + 12×$1M = $22M
- Min Balance: $10M (never decreased)

**All outgoing, $1M each, 5 min intervals**:
- Payments: 12
- Final Balance: $10M - 12×$1M = -$2M
- Min Balance: -$2M
- Credit Used: $2M (if implemented)

**Verify**: Actual matches expected exactly.

#### Mass Balance Check

**Conservation principle**: Total in - Total out = Net change

**Formula**:
```
CurrentBalance = OpeningBalance + TotalIncomingValue - TotalOutgoingValue
```

**Test**:
Run simulation, check:
```
Expected: 10M + 24M - 20M = 14M
Actual: 14M  ✓
```

If not equal:
- Check for missing updates
- Verify incoming/outgoing logic
- Look for duplicate processing

## Statistical Validation

### 1. Validate Input Distributions

#### Payment Arrivals (Poisson Process)

**Theory**: Poisson process with rate λ

**Test**:
1. Record all inter-arrival times
2. Check distribution is exponential with mean = 1/λ

**Expected**:
- λ = 50/hour = 0.833/minute
- Mean inter-arrival = 1.2 minutes

**Arena test**:
Add RECORD for inter-arrival:
```
Type: Tally
Attribute: INT
Tally: Interarrival_Times
```

**After 1000 reps, check report**:
- Mean ≈ 1.2 ± 0.05 minutes
- Std Dev ≈ 1.2 (should equal mean for exponential)

**Statistical test (Chi-Square)**:
```python
# In Python/R after export
from scipy import stats
observed = np.array(interarrival_times)
expected_cdf = lambda x: 1 - np.exp(-x/1.2)
ks_stat, p_value = stats.kstest(observed, expected_cdf)
# p_value > 0.05 → Distribution is correct
```

#### Payment Amounts (Log-Normal)

**Theory**: LOGN(μ, σ)

**Test**:
1. Collect all payment amounts
2. Take natural log
3. Check if ln(Amount) ~ Normal(μ', σ')

**Arena test**:
RECORD module:
```
Type: Tally
Attribute: Amount
Tally: Payment_Amounts
```

**Expected** (for LOGN(1000000, 500000)):
- Mean ≈ $1M (approximate for log-normal)
- Std Dev ≈ $500K
- Min > 0 (always positive)
- Right-skewed distribution

**Validation**:
Export data, create histogram:
- Should be right-skewed
- No negative values
- ~68% within [$500K, $1.5M] (rough check)

#### Payment Type (Discrete)

**Theory**: DISC(0.5, 1, 1.0, 2) → 50/50 split

**Test**:
Count payment types in report:
```
Incoming (Type 1): ~50%
Outgoing (Type 2): ~50%
```

**Statistical test**:
```
Expected: 50% incoming
Observed: 523/1000 = 52.3%

Chi-square test:
χ² = (523-500)²/500 + (477-500)²/500 = 2.12
Critical value (α=0.05, df=1): 3.84
2.12 < 3.84 → Accept (distribution is correct)
```

**In Arena**:
Count using DECIDE branches or tally:
```
Incoming_Count / (Incoming_Count + Outgoing_Count) ≈ 0.50
```

### 2. Validate Output Distributions

#### Minimum Balance Distribution

**Sanity checks**:
1. **Range**: All values should be ≤ Opening Balance
2. **Shape**: Likely left-skewed (more small drops than large)
3. **Convergence**: Mean stabilizes as replications increase

**Plot histogram** of MinimumBalance across replications:
- Export values
- Create histogram in Excel/Python
- Check for unexpected patterns (e.g., bimodal, gaps)

#### Shortfall Probability

**Theoretical validation** (if possible):

For simple cases, derive analytical probability:
```
Example:
If payments = EXPO(1M), arrivals = Poisson(50/hr)
Opening = $10M
Can compute P(Balance < 0) analytically

Compare to simulation result
```

**Empirical validation**:
```
Shortfall_Probability = ShortfallCount / NumReplications

Check:
- 0 ≤ p ≤ 1
- Increases with higher payment volume
- Decreases with higher opening balance
```

### 3. Validate Relationships

#### Expected Relationships

Test that model responds correctly to parameter changes:

| Change | Expected Result | Test |
|--------|----------------|------|
| ↑ Opening Balance | ↓ Shortfall Prob | Run with 10M, 15M, 20M |
| ↑ Payment Rate | ↑ Shortfall Prob | Run with λ=40, 50, 60 |
| ↑ Payment Size | ↑ Max Exposure | Run with μ=1M, 2M, 3M |
| ↑ Incoming Ratio | ↓ Shortfall Prob | Run with 40%, 50%, 60% |
| ↑ Credit Limit | ↓ Rejection Rate | Run with 10M, 20M, 30M |

**Monotonicity tests**:
All relationships should be monotonic (no reversals).

#### Correlation Checks

**Expected correlations**:
- Max Exposure ↔ Shortfall Count: Positive (high)
- Min Balance ↔ Shortfall Count: Negative (high)
- Credit Used ↔ Time in Deficit: Positive

**Test in Excel**:
```excel
=CORREL(MaxExposureRange, ShortfallCountRange)
```

Should match expectations.

## Sanity Checks

### 1. Boundary Conditions

#### Zero Opening Balance

**Setup**: OpeningBalance = 0

**Expected**:
- First outgoing payment fails
- Immediate deficit
- MaxExposure = sum of all outgoing before incoming

**Test**: Run and verify.

#### Infinite Opening Balance

**Setup**: OpeningBalance = 999999999999

**Expected**:
- No shortfalls
- MinBalance very high
- No credit used

**Test**: Run and verify.

#### Zero Payment Rate

**Setup**: PaymentArrivalRate = 0 (or Max Arrivals = 0)

**Expected**:
- No payments created
- Balance unchanged
- FinalBalance = OpeningBalance

**Test**: Run and verify.

#### All Incoming Payments

**Setup**: IncomingPaymentRatio = 1.0

**Expected**:
- Balance always increasing
- No shortfalls
- MaxBalance >> OpeningBalance

**Test**: Run and verify.

#### All Outgoing Payments

**Setup**: IncomingPaymentRatio = 0.0

**Expected**:
- Balance always decreasing
- Shortfalls certain (eventually)
- Heavy credit usage

**Test**: Run and verify.

### 2. Extreme Values

#### Very Large Payment

**Setup**: Single payment of $100M (> opening balance)

**Expected**:
- If outgoing: Triggers shortfall
- If incoming: Massive surplus
- Model handles gracefully (no crash)

#### Very High Payment Rate

**Setup**: PaymentArrivalRate = 1000 (1000/hour)

**Expected**:
- Model runs (may be slow)
- Statistics still collected
- No overflow errors

### 3. Conservation Laws

#### Payment Count

**Check**:
```
Total_Payments_Created = Incoming_Count + Outgoing_Count + Rejected_Count + Queued_Count
```

Should balance exactly.

#### Value Conservation

**Check**:
```
CurrentBalance = OpeningBalance + TotalIncoming - TotalOutgoing - TotalRejected
```

(Adjust for credit if used)

#### Time Accounting

**Check**:
```
TimeInDeficit + TimeAboveBuffer + TimeInBuffer = ReplicationLength
```

Ensure no time lost or duplicated.

## Debugging Techniques

### 1. Animation

**Enable detailed animation**:

**View > Layers**:
- Check all layers
- Show entity pictures
- Show queue contents

**Run > Run Control > Animation Speed**: Very Slow

**Watch for**:
- Entities stuck in queue
- Variables not updating
- Unexpected routing
- Disposal without processing

### 2. Breakpoints

**Set breakpoints** to pause at specific events:

**Run > Breakpoints**

**Options**:
- Time: Pause at specific time (e.g., TNOW = 240)
- Condition: Pause when expression true (e.g., CurrentBalance < 0)
- Entity count: Pause after N entities

**Use**:
- Pause when issue occurs
- Inspect variable values
- Step through logic

### 3. Variable Watch

**Monitor critical variables**:

**View > Variable > Animation**

Add variables to watch:
- CurrentBalance
- QueuedPaymentCount
- ShortfallCount

**Real-time display** during animation.

### 4. Debug Output

**Add temporary RECORD modules**:

Place at strategic points:
- After each DECIDE: Count entities per branch
- After assignments: Tally variable values
- Before/after critical logic

**Check counts** to identify where entities are lost or duplicated.

### 5. Simplification

**If model is complex and buggy**:

1. **Disable features** one at a time:
   - Remove queue logic → Direct rejection
   - Remove credit line → Simple deficit
   - Single priority level

2. **Verify core** works correctly

3. **Re-enable features** incrementally

4. **Test after each addition**

### 6. Logging

**Add write statements** for debugging:

```vba
Sub OnAssignModule()
    Open "Debug_Log.txt" For Append As #1
    Print #1, "Time: " & TNOW & _
              " Entity: " & IDENT & _
              " Amount: " & Amount & _
              " Balance: " & CurrentBalance
    Close #1
End Sub
```

Review log to trace execution.

### 7. Check Reports

**After run, examine**:

**Window > Reports > Entity > All Entities**:
- Total entities created
- Total disposed
- Should match (no lost entities)

**Window > Reports > Queue**:
- Current contents (should be 0 at end)
- Max length (reasonable?)
- Average wait time

**Window > Reports > Variable**:
- Final values
- Match expectations?

## Common Issues and Solutions

### Issue: No payments created
**Symptoms**: Entity count = 0

**Checks**:
- CREATE module connected?
- Max Arrivals not set to 0?
- Replication length > 0?
- Time units consistent?

**Solution**: Verify CREATE module configuration.

### Issue: All payments rejected
**Symptoms**: Rejected_Count = Total_Count

**Checks**:
- Opening balance > 0?
- Liquidity check condition correct?
- Credit line implemented?

**Solution**: Review DECIDE logic for liquidity check.

### Issue: Balance becomes negative without credit
**Symptoms**: CurrentBalance < 0, no credit line

**Checks**:
- Outgoing logic allowing negative balance?
- Missing check before deduction?

**Solution**: Add condition:
```
IF CurrentBalance >= Amount THEN
    CurrentBalance = CurrentBalance - Amount
ELSE
    Route to Queue/Rejection
ENDIF
```

### Issue: Queue never empties
**Symptoms**: NQ(Queue) > 0 at end

**Checks**:
- Queue processing logic implemented?
- Incoming payments trigger check?
- Deadlock condition?

**Solution**: 
- Add periodic queue processor
- Verify liquidity release logic

### Issue: Wrong distribution in output
**Symptoms**: Mean far from expected

**Checks**:
- Correct distribution function?
- Parameters in right units?
- Random stream assigned?
- Truncation/censoring occurring?

**Solution**: 
- Review ASSIGN expressions
- Check for MAX/MIN constraints
- Verify stream independence

### Issue: Confidence intervals too wide
**Symptoms**: Half-width > 10% of mean

**Checks**:
- Enough replications? (Need ~1000)
- High variance in model? (Expected?)
- Initialization issues?

**Solution**: 
- Increase replications
- Check for bugs causing variance
- Verify independence between reps

### Issue: Results not reproducible
**Symptoms**: Different results each run with same seeds

**Checks**:
- "Initialize Between Replications" enabled?
- Same random seeds?
- Time-dependent logic?
- External data sources changing?

**Solution**:
- Enable initialization
- Fix all random seeds
- Remove clock-dependent logic

### Issue: Model runs very slowly
**Symptoms**: Minutes per replication

**Checks**:
- Animation enabled?
- High payment rate?
- Inefficient queue processing?
- Excessive RECORD modules?

**Solution**:
- Disable animation for batch runs
- Optimize queue logic
- Remove debug RECORD modules
- Use batch mode

### Issue: Overflow errors
**Symptoms**: "Variable out of range"

**Checks**:
- Very large payment amounts?
- Cumulative variables unbounded?
- Array index out of bounds?

**Solution**:
- Add bounds checks
- Use double precision variables
- Verify array indices

### Issue: Statistics not collected
**Symptoms**: Output report shows "N/A"

**Checks**:
- "Collect Statistics" enabled?
- Entities reach RECORD module?
- Variable actually changes?

**Solution**:
- Enable statistics collection
- Verify module connections
- Check variable update logic

## Performance Validation

### 1. Run Time Benchmarks

**Expected performance**:

| Replications | Typical Time | Notes |
|--------------|--------------|-------|
| 1 | 1-5 seconds | With animation |
| 30 | 30-60 seconds | Batch mode |
| 1000 | 15-40 minutes | Batch mode |

**If slower**:
- Check for infinite loops
- Reduce animation overhead
- Optimize complex logic

### 2. Memory Usage

**Monitor**:
- Task Manager during run
- Arena should use < 2 GB for typical model

**If excessive**:
- Check for memory leaks in VBA
- Reduce array sizes
- Clear temporary data

## Documentation Standards

### 1. Model Documentation

**Required sections**:

1. **Purpose**: Brief description
2. **Scope**: What's included/excluded
3. **Assumptions**: Key assumptions listed
4. **Parameters**: All inputs documented
5. **Logic**: Major decision points explained
6. **Outputs**: Statistics calculated
7. **Validation**: Tests performed
8. **Limitations**: Known constraints

**Access**: **Tools > Edit Model Documentation**

### 2. Version Control

**Naming convention**:
```
Liquidity_Risk_v1.0_Baseline.doe
Liquidity_Risk_v1.1_AddedQueues.doe
Liquidity_Risk_v2.0_FinalValidated.doe
```

**Track changes**:
- Major versions (1.0, 2.0): Significant changes
- Minor versions (1.1, 1.2): Bug fixes, tweaks

### 3. Results Documentation

**For each run, record**:
- Date/time
- Version number
- Parameter values
- Scenario description
- Number of replications
- Random seeds used
- Key results
- Observations

**Template**:
```
Run ID: LR_2024-01-15_Base
Model: Liquidity_Risk_v2.0.doe
Scenario: Base case
Replications: 1000
Seeds: Default (123456, 234567, ...)
Results:
  - VaR 95%: $8.2M
  - Shortfall Prob: 3.2%
  - Avg Min Balance: $9.1M
Notes: Validated, ready for presentation
```

## Final Validation Checklist

### Model Logic
- [ ] All modules connected correctly
- [ ] No syntax errors (Run > Check Model)
- [ ] Single entity test passed
- [ ] Deterministic test passed
- [ ] Mass balance verified

### Statistical Validation
- [ ] Input distributions validated (arrivals, amounts, types)
- [ ] Output distributions reasonable
- [ ] Parameter sensitivity tests passed
- [ ] Relationships monotonic and correct

### Sanity Checks
- [ ] Boundary conditions tested (zero, infinite, extreme)
- [ ] Conservation laws hold
- [ ] No entity losses or duplications

### Outputs
- [ ] All statistics calculated correctly
- [ ] Confidence intervals reasonable
- [ ] VaR/CVaR match manual calculation
- [ ] Export working properly

### Performance
- [ ] Run time acceptable
- [ ] Memory usage normal
- [ ] Reproducible results (same seeds → same output)
- [ ] Scales to required replications (1000+)

### Documentation
- [ ] Model documentation complete
- [ ] Parameters documented
- [ ] Validation tests recorded
- [ ] Version controlled
- [ ] Results logged

## Next Steps

**Your model is now complete and validated!**

### Recommended Actions

1. **Run production scenarios**:
   - Base case
   - Stress scenarios
   - Sensitivity analysis

2. **Generate reports**:
   - Risk metrics summary
   - Confidence intervals
   - Visualization

3. **Present results**:
   - Executive summary
   - Technical details
   - Regulatory compliance

4. **Maintain model**:
   - Update parameters periodically
   - Re-validate with new data
   - Version control changes

### Additional Resources

- **Arena User's Guide**: Comprehensive reference
- **Arena Help**: Press F1 in any module
- **Rockwell Support**: Technical assistance
- **Academic Papers**: Latest research on liquidity risk simulation

---

**Previous**: [05 - Statistics](05-statistics.md) | **Back to Start**: [01 - Setup](01-setup.md)

## Congratulations!

You've completed the Arena Liquidity Risk Simulation build instructions. Your model should now be:
- ✅ Correctly implemented
- ✅ Statistically validated
- ✅ Fully tested
- ✅ Well documented
- ✅ Ready for production use

**Questions or issues?** Review the troubleshooting sections or consult Arena documentation.
