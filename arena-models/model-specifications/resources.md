# Resource Specifications

This document defines resources used in the Arena liquidity risk simulation model.

## Overview

Resources in Arena represent limited capacity elements that can be seized, used, and released by entities. In liquidity simulations, resources model constraints on settlement systems, credit facilities, and operational capacity.

## Resource Types

### 1. Settlement System Capacity

#### Resource: Settlement_System

Models the limited capacity of payment settlement infrastructure.

#### Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Name** | Settlement_System | Payment processing capacity |
| **Type** | Fixed Capacity | Does not vary with time |
| **Capacity** | 100 | Maximum concurrent settlements |
| **State Set** | Idle, Busy | Default states |
| **Costs** | None | No cost assignment |

#### Usage

```
In PROCESS module:
  Type: Seize Delay Release
  Resource: Settlement_System
  Quantity: 1
  Delay: TRIA(1, 2, 5)  # Processing time
```

#### Statistics Tracked

- Utilization rate
- Number busy
- Queue length
- Wait time in queue

#### Capacity Planning

Determine appropriate capacity based on:

```
Average Utilization = (Arrival Rate × Processing Time) / Capacity

Example:
  Arrival Rate = 50 payments/hour = 0.833/minute
  Processing Time = 2 minutes average
  Capacity needed = 0.833 × 2 = 1.67 (use 2-3 for safety)
  
For our model with higher rates:
  Peak Rate = 70/hour = 1.167/minute
  Capacity = 1.167 × 2 = 2.33 (use 3-5)
  
We use 100 to ensure no capacity constraint (for baseline)
```

---

### 2. Credit Line Availability

#### Resource: Credit_Line

Models available credit facility that can be drawn upon.

#### Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Name** | Credit_Line | Credit facility capacity |
| **Type** | Fixed Capacity | Total credit line |
| **Capacity** | Variable | Based on CreditLineLimit variable |
| **State Set** | Available, Used | Custom states |

#### Implementation as Variable

Rather than Arena resource, credit line is tracked via variables:

```
# Variables
CreditLineLimit = 20000000  # Total credit line ($)
CreditLineUsed = 0          # Currently used ($)
AvailableCredit = CreditLineLimit - CreditLineUsed

# Drawing on credit
IF CurrentBalance < 0 THEN
    CreditNeeded = ABS(CurrentBalance)
    IF CreditNeeded <= AvailableCredit THEN
        CreditLineUsed = CreditLineUsed + CreditNeeded
        CurrentBalance = 0  # Credit covers deficit
    ELSE
        # Insufficient credit - liquidity crisis
        ShortfallEvent = 1
    ENDIF
ENDIF

# Repaying credit
IF CurrentBalance > 0 AND CreditLineUsed > 0 THEN
    Repayment = MIN(CurrentBalance, CreditLineUsed)
    CreditLineUsed = CreditLineUsed - Repayment
    CurrentBalance = CurrentBalance - Repayment
ENDIF
```

#### Credit Line Statistics

Track via RECORD modules:
- Credit utilization over time
- Maximum credit used
- Time credit facility is accessed
- Number of credit draws

---

### 3. Collateral Pool

#### Resource: Collateral_Pool

Represents posted collateral that secures credit facilities or payment obligations.

#### Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Name** | Collateral_Pool | Available collateral |
| **Type** | Finite Capacity | Limited by holdings |
| **Capacity** | Variable | Based on CollateralValue |
| **Replenishment** | None | Fixed amount |

#### Variable-Based Implementation

```
# Variables
CollateralValue = 15000000      # Total collateral ($)
CollateralUsed = 0              # Currently pledged ($)
AvailableCollateral = CollateralValue - CollateralUsed
CollateralHaircut = 0.15        # 15% haircut

# Using collateral for payment
IF Payment requires collateral THEN
    CollateralNeeded = Amount * (1 + CollateralHaircut)
    IF CollateralNeeded <= AvailableCollateral THEN
        CollateralUsed = CollateralUsed + CollateralNeeded
        # Process payment
    ELSE
        # Insufficient collateral
        Queue payment
    ENDIF
ENDIF

# Releasing collateral after settlement
CollateralUsed = CollateralUsed - CollateralAmount
```

#### Collateral Stress Scenarios

```
# Market stress increases haircuts
IF MarketStress == 2 THEN  # High stress
    CollateralHaircut = 0.30  # Increase from 15% to 30%
    AvailableCollateral = CollateralValue * (1 - CollateralHaircut)
ENDIF
```

---

### 4. Operations Staff (Optional)

#### Resource: Operations_Staff

Models human capacity for payment review and approval.

#### Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Name** | Operations_Staff | Payment operations team |
| **Type** | Fixed Capacity | Number of staff |
| **Capacity** | 10 | Staff members |
| **Schedule** | Trading_Hours | Only available during trading hours |

#### Scheduling

```
SCHEDULE: Trading_Hours
  Time    Capacity
  0:00    0        # Overnight - no staff
  8:30    5        # Morning - partial staff
  9:00    10       # Full staff
  17:00   5        # Late day - reduced
  18:00   0        # Closed
```

#### Usage for High-Value Payments

```
In PROCESS module (for high-value payments):
  IF Amount > HighValueThreshold THEN
    Type: Seize Delay Release
    Resource: Operations_Staff
    Quantity: 1
    Delay: NORM(5, 1)  # Review time
  ENDIF
```

---

### 5. Resource Sets (Advanced)

#### ResourceSet: Payment_Channels

For multi-channel payment systems (RTGS, ACH, Wire, etc.)

```
RESOURCE SET: Payment_Channels
  Members: RTGS_Channel, ACH_Channel, Wire_Channel
  
Selection Rule: 
  IF Amount > 1000000 THEN
    Use RTGS_Channel
  ELSE IF PaymentType == "Batch" THEN
    Use ACH_Channel
  ELSE
    Use Wire_Channel
  ENDIF
```

---

## Resource Utilization Analysis

### Key Metrics

Track for each resource:

1. **Utilization Rate**
   ```
   Utilization = Total Busy Time / Total Available Time
   Target: 60-80% for efficiency
   ```

2. **Queue Length**
   ```
   Average Queue Length = TAVG(Queue_Length)
   Maximum Queue Length = MAX(Queue_Length)
   ```

3. **Wait Time**
   ```
   Average Wait = TAVG(Wait_Time)
   95th Percentile Wait = Percentile(Wait_Time, 0.95)
   ```

4. **Number Busy**
   ```
   Average Busy = TAVG(Number_Busy)
   Maximum Busy = MAX(Number_Busy)
   ```

### Resource Blocking

Monitor situations where resource unavailability blocks critical processes:

```
# Track resource failures
IF Settlement_System.Available == 0 THEN
    BlockageCount = BlockageCount + 1
    BlockageTime_Start = TNOW
ENDIF
```

---

## Resource Scheduling

### Time-Varying Capacity

Model resources that change capacity over time:

```
SCHEDULE: Settlement_Capacity_Schedule
  Time (hours)    Capacity
  0               50       # Overnight reduced
  9               100      # Full day capacity
  17              75       # Evening reduced
  22              50       # Late night
```

### Failure and Recovery

Model resource failures:

```
# Periodic failure
IF TNOW MOD FailureInterval < FailureDuration THEN
    Settlement_System.Capacity = 0  # Failed
ELSE
    Settlement_System.Capacity = NominalCapacity
ENDIF

# Random failure
IF UNIF(0,1) < FailureProbability THEN
    Settlement_System.Capacity = 0
    SCHEDULE Recovery at TNOW + EXPO(MTTR)
ENDIF
```

---

## Resource Costs

### Cost Tracking (Optional)

Assign costs to resource usage:

```
RESOURCE: Credit_Line
  Busy Cost: 0.0001  # Cost per minute of usage
  Per Use Cost: 50   # Fixed cost per draw

Total Cost = Busy_Time * Busy_Cost + Number_Uses * Per_Use_Cost
```

### Opportunity Costs

Model opportunity costs of liquidity:

```
# Cost of holding excess liquidity
ExcessLiquidity = CurrentBalance - RequiredBuffer
OpportunityCost = ExcessLiquidity * (AnnualRate / 365 / 1440)  # Per minute

# Cost of liquidity shortage
IF CurrentBalance < RequiredBuffer THEN
    ShortageCost = ShortageCost + Penalty * ShortageAmount * TimeStep
ENDIF
```

---

## Resource States

### Custom State Sets

Define custom states for detailed tracking:

```
STATE SET: Credit_States
  - Unused (credit line not accessed)
  - Partially_Used (some credit drawn)
  - Heavily_Used (>75% utilized)
  - Fully_Used (at limit)

Transitions based on CreditLineUsed / CreditLineLimit
```

---

## Multi-Resource Constraints

### AND Logic

Payment requires multiple resources simultaneously:

```
PROCESS:
  Type: Seize Delay Release
  Resources: 
    - Settlement_System: 1
    - Operations_Staff: 1
  Delay: TRIA(3, 5, 8)
```

### OR Logic

Payment can use alternative resources:

```
IF RTGS_Channel.Available THEN
    Use RTGS_Channel
ELSE IF Wire_Channel.Available THEN
    Use Wire_Channel
ELSE
    Queue until available
ENDIF
```

---

## Resource Optimization

### Capacity Planning

Determine optimal resource levels:

```
# Simulation study varying capacity
FOR Capacity = 50 TO 150 STEP 10
    Settlement_System.Capacity = Capacity
    RUN Simulation
    RECORD: Average_Wait_Time, Utilization, Cost
NEXT

# Find optimal balance
Optimal = MIN(Cost) where Wait_Time < Threshold
```

### Cost-Benefit Analysis

```
# Total cost function
Total_Cost = Fixed_Cost * Capacity + 
             Variable_Cost * Usage + 
             Delay_Cost * Wait_Time

Optimize: Minimize Total_Cost
Subject to: Utilization < 0.85
            Wait_Time_95th < Threshold
```

---

## Validation

### Resource Consistency Checks

```
# Verify resource never over-allocated
ASSERT: Number_Busy <= Capacity

# Verify proper release
ASSERT: Total_Seized == Total_Released

# Check utilization bounds
ASSERT: 0 <= Utilization <= 1
```

### Statistical Validation

Compare resource statistics with theoretical results:

```
# For M/M/c queue (Poisson arrivals, exponential service, c servers)
Theoretical_Utilization = (Arrival_Rate * Service_Time) / Capacity
Actual_Utilization = TAVG(Number_Busy) / Capacity

# Should be within statistical variation
ASSERT: ABS(Actual - Theoretical) < Tolerance
```

---

## Best Practices

1. **Minimize resource types**: Only create resources for genuine constraints
2. **Use variables for liquidity**: Faster than resource mechanics
3. **Monitor utilization**: Identify bottlenecks
4. **Test capacity levels**: Sensitivity analysis on capacity
5. **Document assumptions**: Clear specification of resource behavior

---

## References

- Arena User's Guide: Chapter 7 "Resources"
- Arena Help: "RESOURCE Element"
- Queueing Theory: M/M/c and M/G/c models
- Operations Research texts: Resource allocation and scheduling
