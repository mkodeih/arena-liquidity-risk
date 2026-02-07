# 03 - Liquidity Position Tracking

This guide shows how to implement the core liquidity tracking logic that monitors cash positions, processes incoming/outgoing payments, and handles liquidity shortfalls.

## Overview

We'll build the liquidity tracking system that:
- Separates incoming and outgoing payments using DECIDE logic
- Updates current liquidity position with each payment
- Tracks minimum and maximum liquidity levels
- Queues payments when liquidity is insufficient
- Records exposure metrics and deficit periods
- Implements overdraft/credit line logic

## Understanding Liquidity Flow

### Basic Concept

```
Initial Balance: $10M
+ Incoming Payment: +$2M → Balance: $12M
- Outgoing Payment: -$3M → Balance: $9M
```

### Edge Cases

1. **Insufficient Liquidity**: Outgoing payment > Current balance
2. **Credit Line Usage**: Tap emergency credit facility
3. **Queue Management**: Hold payments until liquidity improves
4. **Priority Processing**: High-priority bypass normal queues

## Building the Payment Router

### 1. Add DECIDE Module for Payment Direction

From **Basic Process** panel:

1. Drag **DECIDE** module to model window
2. Connect from payment generation modules
3. Double-click to configure

**Configuration**:

| Property | Value | Description |
|----------|-------|-------------|
| Name | Decide_Payment_Direction | Route by type |
| Type | 2-way by Condition | If-then-else |
| If | PaymentType == 1 | Incoming payments |
| Else | | Outgoing payments |

**Alternative using N-way**:

| Property | Value |
|----------|-------|
| Type | N-way by Condition |
| Conditions | PaymentType == 1, PaymentType == 2 |

### 2. Connect Exit Points

The DECIDE module will have two exits:
- **True**: Route to incoming payment processing
- **False**: Route to outgoing payment processing

## Processing Incoming Payments

### 1. Add ASSIGN for Incoming Payments

From **Basic Process** panel:

1. Drag **ASSIGN** module
2. Connect from DECIDE "True" exit
3. Name: `Process_Incoming_Payment`

**Assignments** (Click Add for each):

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Variable | CurrentBalance | CurrentBalance + Amount |
| Variable | TotalIncomingValue | TotalIncomingValue + Amount |
| Variable | MaximumBalance | MAX(MaximumBalance, CurrentBalance) |
| Attribute | SettlementTime | TNOW |
| Attribute | Status | 1 |

**Explanation**:
- Increase current balance by payment amount
- Track cumulative incoming value
- Update maximum balance if new high
- Record settlement timestamp
- Status 1 = Settled

### 2. Add RECORD for Incoming Tracking

Add **RECORD** module:

| Property | Value |
|----------|-------|
| Name | Record_Incoming |
| Type | Count |
| Value | IDENT |
| Counter | Incoming_Payment_Count |

### 3. Check Queued Payments

After incoming payment settles, check if queued outgoing payments can now process:

Add **DECIDE** module:

| Property | Value |
|----------|-------|
| Name | Check_Queue_Status |
| Type | 2-way by Condition |
| If | NQ(Queue_Outgoing_Payments) > 0 |

**If True**: Signal queue to process
**If False**: Continue to dispose

## Processing Outgoing Payments

### 1. Add DECIDE for Liquidity Check

Before processing outgoing payment:

1. Drag **DECIDE** module
2. Connect from DECIDE "False" exit (outgoing payments)
3. Name: `Check_Liquidity_Availability`

**Configuration**:

| Property | Value |
|----------|-------|
| Type | 2-way by Condition |
| If | CurrentBalance >= Amount |

**Explanation**:
- **True**: Sufficient liquidity → Process payment
- **False**: Insufficient liquidity → Queue or use credit

### 2. Process Outgoing Payment (Sufficient Liquidity)

Add **ASSIGN** module for "True" path:

Name: `Process_Outgoing_Payment`

**Assignments**:

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Variable | CurrentBalance | CurrentBalance - Amount |
| Variable | TotalOutgoingValue | TotalOutgoingValue + Amount |
| Variable | MinimumBalance | MIN(MinimumBalance, CurrentBalance) |
| Attribute | SettlementTime | TNOW |
| Attribute | Status | 1 |
| Attribute | QueueTime | 0 |

**Additional Check for Deficit**:

Add another ASSIGN to track if balance goes negative (using credit):

```
IF CurrentBalance < 0 THEN
    MaxDeficit = MIN(MaxDeficit, CurrentBalance)
    CreditLineUsed = -1 * CurrentBalance
ENDIF
```

### 3. Record Outgoing Payment

Add **RECORD** module:

| Property | Value |
|----------|-------|
| Name | Record_Outgoing |
| Type | Count |
| Counter | Outgoing_Payment_Count |

Also add tally for amount:

| Property | Value |
|----------|-------|
| Type | Time Interval |
| Attribute | QueueTime |
| Tally | Outgoing_Queue_Time |

### 4. Handle Insufficient Liquidity (Queue Path)

For "False" path from liquidity check:

#### Option A: Hold in Queue

1. Add **QUEUE** module
   - Name: `Queue_Outgoing_Payments`
   - Type: **Based on Attribute** (Priority)
   - Attribute Name: `Priority`
   - Order: **Smallest Value First** (1=High priority)

2. Add **ASSIGN** before queue:
   - Attribute: `QueueEntryTime` = `TNOW`

3. Add **SEIZE** after queue when liquidity available
   - Resource: `Liquidity_Available`
   - Quantity: `Amount`

#### Option B: Use Credit Line

Add **DECIDE** before queue:

| Property | Value |
|----------|-------|
| Name | Check_Credit_Line |
| Type | 2-way by Condition |
| If | CreditLineUsed + Amount <= CreditLineLimit |

**If True**: Use credit, process payment
**If False**: Queue payment

**ASSIGN** for credit usage:

| Variable Name | New Value |
|---------------|-----------|
| CreditLineUsed | CreditLineUsed + Amount |
| CurrentBalance | CurrentBalance - Amount |
| ShortfallCount | ShortfallCount + 1 |

#### Option C: Reject Payment

Add **RECORD** to track rejections:

| Property | Value |
|----------|-------|
| Name | Record_Rejection |
| Type | Count |
| Counter | Rejected_Payment_Count |

Then **DISPOSE** rejected payment.

## Advanced Liquidity Tracking

### 1. Track Time in Deficit

Use ASSIGN logic to monitor deficit periods:

```
# When balance goes negative
IF CurrentBalance < 0 AND DeficitStartTime < 0 THEN
    DeficitStartTime = TNOW
ENDIF

# When balance recovers
IF CurrentBalance >= 0 AND DeficitStartTime >= 0 THEN
    TimeInDeficit = TimeInDeficit + (TNOW - DeficitStartTime)
    DeficitStartTime = -1
ENDIF
```

### 2. Calculate Exposure Metrics

Add **ASSIGN** module after each balance update:

**Peak Exposure**:
```
IF CurrentBalance < 0 THEN
    MaxExposure = MAX(MaxExposure, -1 * CurrentBalance)
ENDIF
```

**Liquidity Ratio**:
```
LiquidityRatio = CurrentBalance / RequiredBuffer
```

**Stress Indicator**:
```
IF CurrentBalance < RequiredBuffer THEN
    StressIndicator = 1
ELSE
    StressIndicator = 0
ENDIF
```

### 3. Implement Intraday Credit Line Repayment

When incoming payment arrives and credit line is used:

```
IF CreditLineUsed > 0 THEN
    Repayment = MIN(Amount, CreditLineUsed)
    CreditLineUsed = CreditLineUsed - Repayment
    # Remainder increases balance
    CurrentBalance = CurrentBalance + (Amount - Repayment)
ELSE
    CurrentBalance = CurrentBalance + Amount
ENDIF
```

## Queue Management Logic

### 1. Priority-Based Processing

Create separate queues by priority:

| Queue Name | Priority Level |
|------------|----------------|
| Queue_High_Priority | 1 |
| Queue_Normal | 2 |
| Queue_Low_Priority | 3 |

Use **DECIDE** after insufficient liquidity check:

```
IF Priority == 1 THEN
    Route to Queue_High_Priority
ELSE IF Priority == 2 THEN
    Route to Queue_Normal
ELSE
    Route to Queue_Low_Priority
ENDIF
```

### 2. Periodic Queue Processing

Add **CREATE** module for queue processor:

| Property | Value |
|----------|-------|
| Name | Create_Queue_Processor |
| Type | Constant |
| Value | 5 |
| Entities per Arrival | 1 |
| Max Arrivals | 96 |

**Logic**: Every 5 minutes, check queues for processable payments.

Add **DECIDE** in processor:

```
# Check each queue in priority order
IF NQ(Queue_High_Priority) > 0 THEN
    # Try to process first item
    IF CurrentBalance >= ATTR(Queue_High_Priority, 1, Amount) THEN
        REMOVE from Queue_High_Priority
        PROCESS payment
    ENDIF
ENDIF
```

### 3. Time-Based Queue Limits

Reject payments queued too long:

Add **DECIDE** after queue:

```
IF TNOW - QueueEntryTime > MaxQueueTime THEN
    Route to Rejection
ELSE
    Continue processing
ENDIF
```

## Tracking Variables Summary

Add these to your Variable definitions:

| Name | Initial Value | Description |
|------|---------------|-------------|
| CurrentBalance | 10000000 | Running liquidity position |
| MinimumBalance | 10000000 | Lowest balance reached |
| MaximumBalance | 10000000 | Highest balance reached |
| TotalIncomingValue | 0 | Sum of incoming payments |
| TotalOutgoingValue | 0 | Sum of outgoing payments |
| MaxExposure | 0 | Peak negative position |
| CreditLineUsed | 0 | Current credit usage |
| CreditLineLimit | 20000000 | Max credit available |
| ShortfallCount | 0 | Number of liquidity events |
| TimeInDeficit | 0 | Minutes in negative position |
| DeficitStartTime | -1 | When deficit began (-1 = none) |
| QueuedPaymentCount | 0 | Payments waiting |
| RejectedPaymentCount | 0 | Payments rejected |

## Complete Flow Diagram

```
[Payment from Generator]
        |
        v
[DECIDE: Incoming or Outgoing?]
    |                    |
    |                    v
    |            [DECIDE: Sufficient Liquidity?]
    |                |              |
    |                v              v
    |            [ASSIGN:        [DECIDE: Use Credit?]
    |             Deduct            |              |
    |             Balance]          v              v
    |                |          [ASSIGN:       [QUEUE:
    |                v           Use Credit]    Wait]
    v                |              |              |
[ASSIGN:             v              v              v
 Add to          [RECORD]       [RECORD]       [PROCESS
 Balance]            |              |           When Ready]
    |                v              v              |
    v            [Check Queue]  [Check Queue]      v
[RECORD]             |              |          [ASSIGN:
    |                v              v           Deduct]
    v            [DISPOSE]      [DISPOSE]          |
[Check Queue]                                      v
    |                                          [RECORD]
    v                                              |
[DISPOSE]                                          v
                                               [DISPOSE]
```

## Validation Steps

### 1. Test Balanced Flows

Set equal incoming/outgoing rates:
- `IncomingPaymentRatio = 0.5`
- Run simulation
- Verify: `CurrentBalance ≈ OpeningBalance`

### 2. Test Deficit Scenario

Create intentional deficit:
- Reduce opening balance: `OpeningBalance = 1000000`
- Increase payment size: `MeanPaymentAmount = 2000000`
- Run simulation
- Verify: `ShortfallCount > 0`, `MaxExposure > 0`

### 3. Test Queue Processing

- Set low opening balance
- Verify payments enter queue: `NQ(Queue_Outgoing_Payments) > 0`
- Verify queue drains when liquidity arrives
- Check queue time statistics

### 4. Verify Credit Line

- Set `CreditLineLimit = 5000000`
- Run simulation with deficit
- Verify: `CreditLineUsed <= CreditLineLimit`
- Check repayment logic works

## Common Issues and Solutions

### Issue: Balance becomes extremely negative
- **Solution**: Check credit line logic is implemented
- Verify: `CurrentBalance - Amount` not exceeding `CreditLineLimit`

### Issue: Queue never drains
- **Solution**: Ensure incoming payments trigger queue check
- Implement periodic queue processor

### Issue: Wrong payment types processed
- **Solution**: Verify DECIDE condition: `PaymentType == 1` (not `=`)
- Check attribute assignment in payment generation

### Issue: MinimumBalance not updating
- **Solution**: Use `MIN(MinimumBalance, CurrentBalance)` not MAX
- Update after every balance change

### Issue: Queue time always zero
- **Solution**: Record `QueueEntryTime` when entering queue
- Calculate: `QueueTime = TNOW - QueueEntryTime` when leaving

### Issue: Priority not working
- **Solution**: Queue type must be "Based on Attribute"
- Attribute name must match exactly: `Priority`
- Order: "Smallest Value First" (1 = High priority)

## Performance Optimization

### 1. Batch Queue Processing

Instead of checking queue after each payment:
- Process queues every 5-10 minutes
- Reduces overhead in high-volume scenarios

### 2. Limit Queue Size

Add capacity constraint:
```
IF NQ(Queue_Outgoing_Payments) >= MaxQueueSize THEN
    Route to Rejection
ENDIF
```

### 3. Early Rejection

Check if payment will ever be processable:
```
IF Amount > OpeningBalance + CreditLineLimit THEN
    Route to Rejection immediately
ENDIF
```

## Checklist

- [ ] DECIDE module separates incoming/outgoing payments
- [ ] Incoming payments increase CurrentBalance
- [ ] Outgoing payments checked for sufficient liquidity
- [ ] Queue implemented for insufficient liquidity
- [ ] Priority-based queue ordering configured
- [ ] Credit line logic implemented with limit checks
- [ ] Minimum and maximum balance tracked
- [ ] Deficit time tracking working
- [ ] Queue processing logic tested
- [ ] All tracking variables defined
- [ ] Test runs show expected behavior
- [ ] Model saved with versioning

## Next Steps

Proceed to **[04-monte-carlo.md](04-monte-carlo.md)** to set up multiple replications and configure the Monte Carlo simulation framework.

---

**Previous**: [02 - Payment Generation](02-payment-generation.md) | **Next**: [04 - Monte Carlo](04-monte-carlo.md)
