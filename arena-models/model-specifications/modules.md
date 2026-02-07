# Module Specifications

This document provides detailed specifications for all Arena modules used in the intraday liquidity risk simulation model.

## Overview

Modules are the building blocks of Arena models. This guide specifies each module type, its configuration, and its role in the liquidity simulation.

## Module List

1. [CREATE - Payment Arrival](#1-create---payment-arrival)
2. [ASSIGN - Attribute Assignment](#2-assign---attribute-assignment)
3. [DECIDE - Decision Logic](#3-decide---decision-logic)
4. [PROCESS - Payment Processing](#4-process---payment-processing)
5. [RECORD - Statistics Collection](#5-record---statistics-collection)
6. [DISPOSE - Entity Termination](#6-dispose---entity-termination)
7. [SCHEDULE - Time-Varying Rates](#7-schedule---time-varying-rates)
8. [READWRITE - Data Import/Export](#8-readwrite---data-importexport)

---

## 1. CREATE - Payment Arrival

### Module: Create_Payments

Generates payment entities according to a Poisson arrival process.

#### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Type** | Random (Expo) | Exponential inter-arrival times |
| **Value** | EXPO(60/PaymentArrivalRate) | Inter-arrival time in minutes |
| **Entities per Arrival** | 1 | One payment per arrival |
| **Max Arrivals** | Infinite | Continuous generation |
| **First Creation** | 0.0 | Start immediately |

#### Expression Details

```
Inter-arrival Time = EXPO(60 / PaymentArrivalRate)

Example: If PaymentArrivalRate = 50 per hour
    Inter-arrival Time = EXPO(60/50) = EXPO(1.2) minutes
    Average rate = 50 payments/hour
```

#### Time-Varying Arrival Rate

For non-homogeneous Poisson process:

```
HourOfDay = INT((TNOW - TradingHoursStart) / 60)
CurrentRate = ArrivalRateSchedule(HourOfDay)
Inter-arrival Time = EXPO(60 / CurrentRate)
```

---

## 2. ASSIGN - Attribute Assignment

Multiple ASSIGN modules handle different attribute assignments.

### Module: Assign_Payment_Attributes

Assigns initial attributes to payment entities.

#### Assignments

```
PaymentID = IDENT
Timestamp = TNOW
Amount = LOGN(MeanPaymentAmount, StdDevPaymentAmount)
PaymentType = DISC(IncomingPaymentRatio, 1, 1.0, 2)
Priority = DISC(0.70, 2, 0.95, 1, 1.0, 3)
Status = 0
QueueTime = 0
InstitutionID = UNIF(1, 10)
```

#### Amount Distribution Options

**Option 1: Log-Normal**
```
Amount = LOGN(MeanAmount, StdDevAmount)
```

**Option 2: Exponential**
```
Amount = EXPO(MeanAmount)
```

**Option 3: Continuous Empirical**
```
Amount = CONT(0.0, 100000, 0.3, 500000, 0.7, 2000000, 1.0, 10000000)
```

### Module: Assign_Incoming_Payment

Updates liquidity for incoming payments.

#### Assignments

```
CurrentBalance = CurrentBalance + Amount
TotalIncomingValue = TotalIncomingValue + Amount
NetPaymentFlow = TotalIncomingValue - TotalOutgoingValue

# Update maximum if needed
MaximumBalance = MAX(MaximumBalance, CurrentBalance)
```

### Module: Assign_Outgoing_Payment

Updates liquidity for outgoing payments.

#### Assignments

```
CurrentBalance = CurrentBalance - Amount
TotalOutgoingValue = TotalOutgoingValue + Amount
NetPaymentFlow = TotalIncomingValue - TotalOutgoingValue

# Update minimum if needed
MinimumBalance = MIN(MinimumBalance, CurrentBalance)

# Track deficit
IF CurrentBalance < 0 THEN
    IF DeficitStartTime < 0 THEN
        DeficitStartTime = TNOW
        ShortfallCount = ShortfallCount + 1
    ENDIF
    MaxDeficit = MAX(MaxDeficit, ABS(CurrentBalance))
ENDIF
```

---

## 3. DECIDE - Decision Logic

### Module: Decide_Payment_Type

Routes payments based on type (incoming vs. outgoing).

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | 2-way by Condition |
| **Condition** | PaymentType == 1 |
| **If True** | Route to incoming processing |
| **If False** | Route to outgoing processing |

### Module: Decide_Liquidity_Sufficiency

Checks if sufficient liquidity exists for outgoing payment.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | 2-way by Condition |
| **Condition** | CurrentBalance >= Amount |
| **If True** | Process payment immediately |
| **If False** | Queue payment |

#### Enhanced Logic with Credit Line

```
Condition: (CurrentBalance >= Amount) OR 
           ((CurrentBalance + (CreditLineLimit - CreditLineUsed)) >= Amount)
```

### Module: Decide_Priority

Routes based on payment priority.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | N-way by Condition |
| **Conditions** | Priority == 1 (High)
                  Priority == 2 (Normal)
                  Priority == 3 (Low) |

---

## 4. PROCESS - Payment Processing

### Module: Process_Payment_Settlement

Simulates payment processing and settlement time.

#### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Action** | Delay | Add processing delay |
| **Delay Type** | Triangular | Realistic processing time |
| **Minimum** | 1.0 | Minimum processing (minutes) |
| **Mode** | 2.0 | Most likely processing |
| **Maximum** | 5.0 | Maximum processing |
| **Units** | Minutes | Time units |

#### With Resource

For capacity-constrained settlement:

| Parameter | Value |
|-----------|-------|
| **Resource** | Settlement_System |
| **Quantity** | 1 |
| **Type** | Seize Delay Release |

### Module: Process_High_Priority

Expedited processing for high-priority payments.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Delay Type** | Constant |
| **Value** | 0.5 | Fast processing (30 seconds) |

---

## 5. RECORD - Statistics Collection

### Module: Record_Liquidity_Position

Records liquidity levels for statistical analysis.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | Time Interval |
| **Value** | CurrentBalance |
| **Tally Name** | Liquidity_Position |
| **Interval** | 1.0 minutes |

### Module: Record_Minimum_Balance

Tracks minimum balance statistic.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | Count |
| **Value** | MinimumBalance |
| **Counter Name** | Min_Daily_Balance |

### Module: Record_Payment_Statistics

Records payment-level statistics.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | Entity Statistics |
| **Attributes** | Amount, QueueTime, ProcessingTime |
| **Tally Name** | Payment_Stats |

---

## 6. DISPOSE - Entity Termination

### Module: Dispose_Completed_Payments

Removes settled payment entities from the system.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Record Entity Statistics** | Yes |
| **Statistics** | Entity time, entity count |

---

## 7. SCHEDULE - Time-Varying Rates

### Module: Schedule_Arrival_Rates

Defines time-varying payment arrival rates throughout the trading day.

#### Schedule Type: Arrival

| Time (Hours) | Rate (per hour) | Description |
|--------------|----------------|-------------|
| 0 (9:00 AM) | 30 | Morning opening |
| 1 (10:00 AM) | 45 | Ramp up |
| 2 (11:00 AM) | 60 | Peak morning |
| 3 (12:00 PM) | 50 | Midday |
| 4 (1:00 PM) | 55 | Afternoon |
| 5 (2:00 PM) | 70 | Peak afternoon |
| 6 (3:00 PM) | 65 | Late afternoon |
| 7 (4:00 PM) | 40 | Wind down |

#### Implementation in CREATE Module

```
CREATE: EXPO(60 / PaymentArrivalRate)
UPDATE: PaymentArrivalRate via SCHEDULE

Or use Arena's built-in schedule:
CREATE: Schedule Value
Schedule: Use schedule defined above
```

---

## 8. READWRITE - Data Import/Export

### Module: ReadWrite_Import_Parameters

Imports simulation parameters from Excel.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | READ |
| **File Name** | "data/input-templates/payment_parameters.xlsx" |
| **Starting Row** | 2 |
| **Variables** | MeanPaymentAmount, StdDevPaymentAmount, PaymentArrivalRate |

### Module: ReadWrite_Export_Results

Exports results to Excel for analysis.

#### Configuration

| Parameter | Value |
|-----------|-------|
| **Type** | WRITE |
| **File Name** | "data/output-templates/simulation_results.xlsx" |
| **Recordset** | Replication, MinimumBalance, MaxDeficit, TimeInDeficit |

---

## Module Flow Diagram

```
[CREATE: Payment Arrival]
         |
         v
[ASSIGN: Payment Attributes]
         |
         v
[DECIDE: Payment Type?]
         |
    +----+----+
    |         |
Incoming   Outgoing
    |         |
    v         v
[ASSIGN:  [DECIDE: Sufficient Liquidity?]
 Add to      |
 Balance]    +------+-------+
    |        |              |
    |       Yes            No
    |        |              |
    |        v              v
    |   [ASSIGN:        [QUEUE: Wait]
    |    Deduct           |
    |    Balance]         |
    |        |            |
    +--------+------------+
             |
             v
    [PROCESS: Settlement]
             |
             v
    [RECORD: Statistics]
             |
             v
        [DISPOSE]
```

## Best Practices

### Module Naming

Use descriptive names:
- `Create_Payments` not `Create 1`
- `Assign_Incoming_Payment` not `Assign 2`
- `Decide_Liquidity_Check` not `Decide 3`

### Module Organization

1. Group related modules together
2. Use vertical alignment in flowchart
3. Label connectors clearly
4. Add text annotations for complex logic

### Error Handling

Add HALT conditions for impossible states:

```
DECIDE: IF CurrentBalance < -CreditLineLimit THEN
    HALT "Credit line exceeded"
ENDIF
```

### Performance

- Minimize ASSIGN modules (combine assignments)
- Use efficient expressions
- Avoid unnecessary DECIDE branches
- Limit RECORD frequency for large simulations

## Validation

### Module Testing

Test each module individually:
1. Create simple test model with just that module
2. Verify outputs match expectations
3. Check edge cases
4. Monitor animation

### Integration Testing

After combining modules:
1. Run short simulation (10 minutes)
2. Check entity flow
3. Verify variable updates
4. Review statistics

## References

- Arena User's Guide: Chapter 5 "Basic Process Panel"
- Arena Help: Individual module help (F1 on module)
- Arena examples: `Examples\Models` directory
