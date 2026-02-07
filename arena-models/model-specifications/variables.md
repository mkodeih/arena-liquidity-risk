# Variable Specifications

This document defines all variables (global and local) used in the Arena liquidity risk simulation model.

## Overview

Variables in Arena store numerical values that can be accessed and modified throughout the simulation. They are essential for tracking liquidity positions, parameters, and statistics.

## Variable Categories

### 1. Global Variables (System-Wide)

Variables accessible throughout the entire model.

#### Time Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `CurrentTime` | Real | 0.0 | Current simulation time (minutes) |
| `SimulationDay` | Integer | 1 | Current simulation day |
| `TradingHoursStart` | Real | 540 | Trading start (9:00 AM = 540 min) |
| `TradingHoursEnd` | Real | 1020 | Trading end (5:00 PM = 1020 min) |
| `TimeStep` | Real | 1.0 | Simulation time increment (minutes) |

#### Liquidity Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `OpeningBalance` | Real | 10000000 | Starting liquidity position ($) |
| `CurrentBalance` | Real | 10000000 | Current liquidity level ($) |
| `MinimumBalance` | Real | 10000000 | Minimum balance during day ($) |
| `MaximumBalance` | Real | 10000000 | Maximum balance during day ($) |
| `RequiredBuffer` | Real | 2000000 | Minimum required liquidity ($) |
| `CreditLineLimit` | Real | 20000000 | Maximum credit line available ($) |
| `CreditLineUsed` | Real | 0.0 | Current credit line usage ($) |
| `CollateralValue` | Real | 15000000 | Value of posted collateral ($) |
| `AvailableCollateral` | Real | 15000000 | Remaining collateral ($) |

#### Payment Flow Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `PaymentArrivalRate` | Real | 50.0 | Average payments per hour |
| `MeanPaymentAmount` | Real | 1000000 | Mean payment size ($) |
| `StdDevPaymentAmount` | Real | 500000 | Standard deviation of payment size ($) |
| `IncomingPaymentRatio` | Real | 0.5 | Proportion of incoming payments |
| `TotalIncomingValue` | Real | 0.0 | Cumulative incoming payments ($) |
| `TotalOutgoingValue` | Real | 0.0 | Cumulative outgoing payments ($) |
| `NetPaymentFlow` | Real | 0.0 | Net flow (incoming - outgoing) ($) |

#### Risk Metric Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `ShortfallCount` | Integer | 0 | Number of liquidity shortfalls |
| `TimeInDeficit` | Real | 0.0 | Total time with negative balance (min) |
| `MaxDeficit` | Real | 0.0 | Maximum deficit encountered ($) |
| `DeficitStartTime` | Real | -1.0 | Time when deficit began (-1 if none) |
| `VaR_95` | Real | 0.0 | 95% Value at Risk ($) |
| `VaR_99` | Real | 0.0 | 99% Value at Risk ($) |
| `ExpectedShortfall` | Real | 0.0 | Expected Shortfall/CVaR ($) |

#### Monte Carlo Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `NumReplications` | Integer | 1000 | Number of Monte Carlo runs |
| `CurrentReplication` | Integer | 1 | Current replication number |
| `RandomSeed` | Integer | 12345 | Random number generator seed |
| `WarmupPeriod` | Real | 60.0 | Warmup period (minutes) |

#### Market Condition Variables

| Variable Name | Type | Initial Value | Description |
|--------------|------|---------------|-------------|
| `MarketStress` | Integer | 0 | Stress level (0=Normal, 1=Medium, 2=High) |
| `VolatilityMultiplier` | Real | 1.0 | Payment volatility scaling factor |
| `ContagionProbability` | Real | 0.0 | Probability of contagion event |
| `LiquidityShockMagnitude` | Real | 0.0 | Size of external shock ($) |
| `RecoveryRate` | Real | 0.05 | Recovery rate per hour |

### 2. Arrays

For tracking multiple values or institutions.

#### Liquidity History Array

| Array Name | Dimensions | Type | Description |
|-----------|------------|------|-------------|
| `LiquidityHistory` | (480) | Real | Minute-by-minute liquidity levels |
| `PaymentVolume` | (24) | Real | Hourly payment volumes |
| `ArrivalRateSchedule` | (24) | Real | Hour-by-hour arrival rates |

#### Multi-Institution Arrays

| Array Name | Dimensions | Type | Description |
|-----------|------------|------|-------------|
| `InstitutionBalance` | (10) | Real | Balance for each institution |
| `InstitutionCreditLine` | (10) | Real | Credit line for each institution |
| `InstitutionRisk` | (10) | Real | Risk metric for each institution |

### 3. Attributes (Entity-Level Variables)

See [entities.md](entities.md) for entity attribute specifications.

## Variable Initialization

### At Simulation Start

In the **BEGIN** block or initialization logic:

```
CurrentBalance = OpeningBalance
MinimumBalance = OpeningBalance
MaximumBalance = OpeningBalance
TotalIncomingValue = 0
TotalOutgoingValue = 0
ShortfallCount = 0
TimeInDeficit = 0
MaxDeficit = 0
```

### Per Replication

At the start of each Monte Carlo replication:

```
CurrentReplication = MREP
RandomSeed = BaseRandomSeed + MREP
```

## Variable Update Logic

### For Incoming Payment

```
CurrentBalance = CurrentBalance + PaymentAmount
TotalIncomingValue = TotalIncomingValue + PaymentAmount
NetPaymentFlow = TotalIncomingValue - TotalOutgoingValue

IF CurrentBalance > MaximumBalance THEN
    MaximumBalance = CurrentBalance
ENDIF
```

### For Outgoing Payment

```
IF CurrentBalance >= PaymentAmount THEN
    CurrentBalance = CurrentBalance - PaymentAmount
    TotalOutgoingValue = TotalOutgoingValue + PaymentAmount
    NetPaymentFlow = TotalIncomingValue - TotalOutgoingValue
    
    IF CurrentBalance < MinimumBalance THEN
        MinimumBalance = CurrentBalance
    ENDIF
    
    IF CurrentBalance < 0 THEN
        IF DeficitStartTime < 0 THEN
            DeficitStartTime = TNOW
            ShortfallCount = ShortfallCount + 1
        ENDIF
        
        IF ABS(CurrentBalance) > MaxDeficit THEN
            MaxDeficit = ABS(CurrentBalance)
        ENDIF
    ELSE
        IF DeficitStartTime >= 0 THEN
            TimeInDeficit = TimeInDeficit + (TNOW - DeficitStartTime)
            DeficitStartTime = -1
        ENDIF
    ENDIF
ELSE
    # Queue payment for later processing
ENDIF
```

### Time-Varying Arrival Rate

```
HourOfDay = INT((TNOW - TradingHoursStart) / 60)
PaymentArrivalRate = ArrivalRateSchedule(HourOfDay)
```

## Variable Usage Examples

### Calculate Liquidity Ratio

```
LiquidityRatio = CurrentBalance / RequiredBuffer
```

### Check Credit Line Availability

```
AvailableCredit = CreditLineLimit - CreditLineUsed
TotalAvailableLiquidity = CurrentBalance + AvailableCredit
```

### Stress Testing

```
IF MarketStress = 2 THEN  # High stress
    VolatilityMultiplier = 2.0
    MeanPaymentAmount = MeanPaymentAmount * 0.8  # Lower incoming
    StdDevPaymentAmount = StdDevPaymentAmount * 1.5  # Higher variance
ENDIF
```

## Variable Monitoring

### Using RECORD Modules

Track variable changes over time:
- `RECORD`: MinimumBalance, CurrentBalance, TimeInDeficit
- **Type**: Time-Persistent Statistics
- **Identifier**: Variable name

### Using OUTPUT Statistics

Define custom statistics in OUTPUT module:
- Minimum Balance: `TAVG(MinimumBalance)`
- Average Balance: `TAVG(CurrentBalance)`
- Maximum Deficit: `MAX(MaxDeficit)`

## Performance Optimization

### Tips for Efficient Variable Use

1. **Minimize global variables**: Use only what's necessary
2. **Use arrays for related data**: Reduces variable count
3. **Avoid redundant calculations**: Store computed values
4. **Clear variables between replications**: Ensure independence

### Memory Management

For large simulations:
- Limit array sizes to essential needs
- Use CLEAR statement to reset variables
- Monitor memory usage in Arena's statistics

## Validation

### Variable Sanity Checks

Add DECIDE modules to validate:

```
IF CurrentBalance < -CreditLineLimit THEN
    HALT  # Should never exceed credit line
ENDIF

IF MinimumBalance > MaximumBalance THEN
    HALT  # Logic error
ENDIF

IF TotalIncomingValue < 0 THEN
    HALT  # Impossible value
ENDIF
```

### Debug Output

Use WRITE statements for debugging:

```
WRITE "Time: " & TNOW & " Balance: " & CurrentBalance
```

## Advanced Variable Techniques

### Dynamic Variable Updates

Use ASSIGN modules with expressions:

```
LiquidityBufferPercent = (CurrentBalance / OpeningBalance) * 100
TimeUntilClose = TradingHoursEnd - TNOW
```

### Conditional Logic

```
EmergencyFunding = IF(CurrentBalance < 0, ABS(CurrentBalance) * 1.1, 0)
```

### Statistical Calculations

```
PaymentCV = StdDevPaymentAmount / MeanPaymentAmount  # Coefficient of variation
```

## References

- Arena User's Guide: Chapter 4 "Variables and Expressions"
- Arena Help: "VARIABLE Element"
- SIMAN Reference: Variable types and scoping
