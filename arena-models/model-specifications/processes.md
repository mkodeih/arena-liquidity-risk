# Process Specifications

This document describes the key processes and workflows in the Arena liquidity risk simulation model.

## Overview

Processes define how entities (payments) flow through the system and how the liquidity position evolves over time. This document describes the logic and implementation of each major process.

## Main Processes

### 1. Payment Generation Process

#### Purpose
Generate payment entities with realistic arrival patterns and characteristics.

#### Process Flow

```
START
  |
  v
[Wait for Next Arrival]
  | (Exponential inter-arrival time based on current rate)
  v
[Create Payment Entity]
  |
  v
[Assign PaymentID = IDENT]
  |
  v
[Assign Timestamp = TNOW]
  |
  v
[Determine Payment Amount]
  | (Log-normal or Exponential distribution)
  v
[Determine Payment Type]
  | (Incoming vs Outgoing based on probability)
  v
[Determine Priority Level]
  | (High/Normal/Low based on distribution)
  v
[Route to Processing]
  |
  v
CONTINUE TO LIQUIDITY UPDATE PROCESS
```

#### Implementation Details

**Arrival Process:**
- Non-homogeneous Poisson process
- Rate varies by time of day
- Higher rates during opening and closing hours
- Lower rates during lunch period

**Amount Generation:**
```
IF Use_LogNormal THEN
    Amount = LOGN(MeanPaymentAmount, StdDevPaymentAmount)
ELSE
    Amount = EXPO(MeanPaymentAmount)
ENDIF

# Ensure minimum and maximum bounds
Amount = MAX(MinPaymentAmount, MIN(Amount, MaxPaymentAmount))
```

**Type Determination:**
```
Random = UNIF(0, 1)
IF Random <= IncomingPaymentRatio THEN
    PaymentType = 1  # Incoming
ELSE
    PaymentType = 2  # Outgoing
ENDIF
```

---

### 2. Liquidity Update Process

#### Purpose
Update the institution's liquidity position based on payment flows.

#### Process Flow for Incoming Payments

```
[Incoming Payment Arrives]
  |
  v
[Add Amount to CurrentBalance]
  | CurrentBalance = CurrentBalance + Amount
  v
[Update TotalIncomingValue]
  | TotalIncomingValue = TotalIncomingValue + Amount
  v
[Update NetPaymentFlow]
  | NetPaymentFlow = TotalIncomingValue - TotalOutgoingValue
  v
[Check if New Maximum]
  | IF CurrentBalance > MaximumBalance THEN
  |     MaximumBalance = CurrentBalance
  v
[Check for Deficit Recovery]
  | IF Was in deficit AND now positive THEN
  |     TimeInDeficit = TimeInDeficit + (TNOW - DeficitStartTime)
  |     DeficitStartTime = -1
  v
[Release Queued Payments]
  | Try to process queued outgoing payments
  v
CONTINUE TO SETTLEMENT PROCESS
```

#### Process Flow for Outgoing Payments

```
[Outgoing Payment Arrives]
  |
  v
[Check Liquidity Sufficiency]
  |
  +--[Sufficient?]--+
  |                 |
  YES              NO
  |                 |
  v                 v
[Process        [Queue Payment]
 Immediately]      |
  |                v
  v           [Wait for Liquidity]
[Deduct Amount]    |
  | CurrentBalance = CurrentBalance - Amount
  v                |
[Update Total]     |
  | TotalOutgoingValue += Amount
  v                |
[Update Net Flow]  |
  |                |
  v                |
[Check New Minimum]|
  | IF CurrentBalance < MinimumBalance
  |     MinimumBalance = CurrentBalance
  v                |
[Check Deficit]    |
  | IF CurrentBalance < 0
  |     Track deficit metrics
  v                |
  |                |
  +<---------------+
  |
  v
CONTINUE TO SETTLEMENT PROCESS
```

#### Liquidity Tracking Logic

```
# After each outgoing payment
IF CurrentBalance < MinimumBalance THEN
    MinimumBalance = CurrentBalance
ENDIF

# Deficit tracking
IF CurrentBalance < 0 THEN
    IF DeficitStartTime < 0 THEN
        # Entering deficit for first time
        DeficitStartTime = TNOW
        ShortfallCount = ShortfallCount + 1
    ENDIF
    
    # Track maximum deficit depth
    IF ABS(CurrentBalance) > MaxDeficit THEN
        MaxDeficit = ABS(CurrentBalance)
    ENDIF
ELSE
    # Check if recovering from deficit
    IF DeficitStartTime >= 0 THEN
        # Was in deficit, now recovered
        TimeInDeficit = TimeInDeficit + (TNOW - DeficitStartTime)
        DeficitStartTime = -1
    ENDIF
ENDIF
```

---

### 3. Queue Management Process

#### Purpose
Manage payments waiting for sufficient liquidity.

#### Process Flow

```
[Payment Needs Queueing]
  |
  v
[Determine Queue Based on Priority]
  |
  +--[Priority?]--+
  |               |
 High          Normal/Low
  |               |
  v               v
[Queue_High]  [Queue_Normal]
  |               |
  +-------+-------+
          |
          v
[Record Queue Entry Time]
  | QueueTime_Start = TNOW
  v
[Wait for Liquidity Signal]
  |
  v
[Periodically Check Liquidity]
  | (On each incoming payment)
  v
[Sufficient Now?]
  |
  +--[Yes]--[No]--+
  |               |
  v               v
[Dequeue]    [Continue
  |           Waiting]
  v               |
[Calculate      <-+
 QueueTime]
  | QueueTime = TNOW - QueueTime_Start
  v
[Process Payment]
  |
  v
CONTINUE TO LIQUIDITY UPDATE PROCESS
```

#### Queue Processing Priority

1. **High-priority queue** processed first
2. **Normal queue** processed in FIFO order
3. **Low-priority queue** processed last

#### Queue Release Logic

```
# Triggered after each incoming payment
WHILE CurrentBalance > 0 AND Queue not empty DO
    # Try to process highest priority queued payment
    NextPayment = DEQUEUE(Queue_High)
    IF NextPayment is NULL THEN
        NextPayment = DEQUEUE(Queue_Normal)
    ENDIF
    IF NextPayment is NULL THEN
        NextPayment = DEQUEUE(Queue_Low)
    ENDIF
    
    IF NextPayment != NULL THEN
        IF CurrentBalance >= NextPayment.Amount THEN
            PROCESS(NextPayment)
        ELSE
            REQUEUE(NextPayment)  # Put back and stop trying
            BREAK
        ENDIF
    ENDIF
END WHILE
```

---

### 4. Settlement Process

#### Purpose
Simulate payment settlement with realistic processing times.

#### Process Flow

```
[Payment Ready for Settlement]
  |
  v
[Seize Settlement System Resource]
  | (If capacity constrained)
  v
[Process for Settlement Time]
  | Delay = TRIA(MinTime, ModeTime, MaxTime)
  v
[Update Settlement Timestamp]
  | SettlementTime = TNOW
  v
[Calculate Processing Time]
  | ProcessingTime = SettlementTime - Timestamp
  v
[Release Settlement System]
  |
  v
[Update Status]
  | Status = 2 (Settled)
  v
CONTINUE TO STATISTICS COLLECTION
```

#### Settlement Time Distribution

```
# Normal conditions
SettlementTime = TRIA(1.0, 2.0, 5.0)  # minutes

# Stress conditions
IF MarketStress > 0 THEN
    SettlementTime = SettlementTime * (1 + 0.5 * MarketStress)
ENDIF

# Priority-based
IF Priority == 1 THEN  # High priority
    SettlementTime = TRIA(0.5, 1.0, 2.0)
ENDIF
```

---

### 5. Risk Calculation Process

#### Purpose
Calculate risk metrics throughout the simulation.

#### Continuous Updates

Risk metrics are updated continuously as the simulation runs:

```
# After each liquidity update
Current_VaR_Estimate = ABS(MinimumBalance)
Current_Shortfall_Prob = ShortfallCount / TotalPayments

# Store for end-of-day analysis
LiquidityHistory(INT(TNOW)) = CurrentBalance
```

#### End-of-Replication Calculations

```
[Replication Complete]
  |
  v
[Record Minimum Balance]
  | Store MinimumBalance for this replication
  v
[Record Maximum Deficit]
  | Store MaxDeficit for this replication
  v
[Record Time in Deficit]
  | Store TimeInDeficit for this replication
  v
[Calculate Shortfall Indicator]
  | ShortfallOccurred = (MinimumBalance < 0) ? 1 : 0
  v
[Export to Results Array]
  |
  v
NEXT REPLICATION
```

#### Cross-Replication Analysis

After all replications complete:

```
# VaR Calculation
SORT MinimumBalance_Array ascending
VaR_95 = Percentile(MinimumBalance_Array, 0.05)
VaR_99 = Percentile(MinimumBalance_Array, 0.01)

# Expected Shortfall
Deficits = MinimumBalance_Array[MinimumBalance < 0]
ES_95 = AVERAGE(Deficits where value < VaR_95)

# Shortfall Probability
NumShortfalls = COUNT(MinimumBalance < 0)
ShortfallProb = NumShortfalls / TotalReplications

# Confidence Intervals
CI_95_Lower = VaR_95 - 1.96 * STDEV(MinimumBalance_Array) / SQRT(N)
CI_95_Upper = VaR_95 + 1.96 * STDEV(MinimumBalance_Array) / SQRT(N)
```

---

### 6. Monte Carlo Replication Process

#### Purpose
Execute multiple independent simulation runs to capture uncertainty.

#### Process Flow

```
[Simulation Start]
  |
  v
FOR Replication = 1 TO NumReplications
  |
  v
  [Initialize Variables]
    | Reset all liquidity variables
    | Set random seed = BaseSeed + Replication
    v
  [Run Simulation Day]
    | Generate payments and track liquidity
    | Duration = TradingHoursEnd - TradingHoursStart
    v
  [Collect Statistics]
    | Record MinimumBalance, MaxDeficit, etc.
    v
  [Store Results]
    | Save to output arrays/file
    v
NEXT Replication
  |
  v
[Aggregate Results]
  | Calculate VaR, ES, probabilities
  v
[Generate Report]
  |
  v
END
```

#### Random Number Stream Management

```
# Setup (before first replication)
STREAMS = 10  # Number of independent streams

# Assignments:
Stream 1: Payment arrival times
Stream 2: Payment amounts
Stream 3: Payment types
Stream 4: Payment priorities
Stream 5: Settlement times
Stream 6-10: Reserved for stress scenarios

# Per replication
FOR i = 1 TO STREAMS
    SEED(i, BaseSeed + i * 1000 + Replication)
NEXT i
```

---

### 7. Stress Testing Process

#### Purpose
Simulate crisis scenarios with adverse market conditions.

#### Shock Event Process

```
[Normal Operation]
  |
  v
[Shock Trigger Time?]
  | IF TNOW >= ShockStartTime THEN
  v
[Apply Shock Parameters]
  | IncomingPaymentRatio = IncomingPaymentRatio * (1 - ShockMagnitude)
  | StdDevPaymentAmount = StdDevPaymentAmount * (1 + VolatilityIncrease)
  | CreditLineLimit = CreditLineLimit * (1 - CreditLineHaircut)
  v
[Mark Stress Period]
  | MarketStress = 2 (High)
  v
[Continue Simulation with Shock]
  |
  v
[Recovery Time?]
  | IF TNOW >= ShockEndTime THEN
  v
[Gradual Recovery]
  | FOR t = 1 TO RecoveryPeriod
  |     IncomingPaymentRatio = IncomingPaymentRatio + RecoveryRate
  |     [Other parameters recover gradually]
  v
[Return to Normal]
  | MarketStress = 0
  v
CONTINUE
```

#### Contagion Process

```
[Counterparty Failure Event]
  |
  v
[Check Contagion Probability]
  | IF UNIF(0,1) < ContagionProbability THEN
  v
[Apply Contagion Effects]
  | LiquidityShock = CounterpartyExposure * LossGivenDefault
  | CurrentBalance = CurrentBalance - LiquidityShock
  |
  | # Haircut on collateral
  | CollateralHaircut = 0.30
  | AvailableCollateral = AvailableCollateral * (1 - CollateralHaircut)
  v
[Propagate to Network]
  | FOR each connected institution
  |     Apply proportional shock
  v
CONTINUE
```

---

## Process Validation

### Testing Each Process

1. **Isolation Testing**: Test each process independently
2. **Integration Testing**: Combine processes and validate interactions
3. **Boundary Testing**: Test with extreme parameter values
4. **Stress Testing**: Validate under crisis conditions

### Validation Metrics

- Entity flow rates match theoretical expectations
- Liquidity balances are mathematically consistent
- Queue lengths are reasonable
- Processing times follow specified distributions
- Risk metrics converge with more replications

## Performance Optimization

### Process Efficiency Tips

1. **Minimize assignments**: Combine multiple updates
2. **Efficient queuing**: Use priority queues appropriately
3. **Conditional processing**: Skip unnecessary logic
4. **Batch updates**: Update statistics periodically, not continuously

### Scalability Considerations

- For large payment volumes (>10,000/day), use batching
- For long simulation periods, use sub-model approach
- For multiple institutions, parallelize where possible

## References

- Arena User's Guide: Chapter 6 "Modeling Detailed Operations"
- Simulation textbooks: Queuing theory and stochastic processes
- Basel III: Monitoring tools for intraday liquidity management
