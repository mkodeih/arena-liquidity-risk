# 02 - Payment Generation Process

This guide shows how to create the payment arrival process and assign initial payment attributes.

## Overview

We'll build the payment generation logic that:
- Creates payment entities using a Poisson process
- Assigns payment amounts from a log-normal distribution
- Determines payment type (incoming vs. outgoing)
- Sets payment priority levels
- Records arrival timestamps

## Building the Payment Arrival Module

### 1. Add CREATE Module

From the **Basic Process** panel:

1. Drag **CREATE** module to model window
2. Double-click to open configuration
3. Set properties:

| Property | Value | Description |
|----------|-------|-------------|
| Name | Create_Payments | Descriptive name |
| Entity Type | Payment | Create new type |
| Type | Random (Expo) | Poisson arrivals |
| Value | EXPO(60/PaymentArrivalRate) | Inter-arrival time |
| Entities per Arrival | 1 | One at a time |
| Max Arrivals | Infinite | No limit |
| First Creation | 0.0 | Start immediately |

4. Click **OK**

**Understanding the Expression**:
```
EXPO(60/PaymentArrivalRate)
- PaymentArrivalRate = 50 payments per hour
- 60/50 = 1.2 minutes between arrivals on average
- EXPO(1.2) = exponential distribution (Poisson process)
```

### 2. Add ASSIGN Module for Basic Attributes

From **Basic Process** panel:

1. Drag **ASSIGN** module to model window
2. Connect CREATE to ASSIGN with connector
3. Double-click ASSIGN to configure
4. Name: `Assign_Payment_Attributes`

**Assignments** (Click Add button for each):

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Attribute | PaymentID | IDENT |
| Attribute | Timestamp | TNOW |
| Attribute | Status | 0 |
| Attribute | QueueTime | 0 |
| Attribute | ProcessingTime | 0 |

**Notes**:
- `IDENT`: Unique entity identifier
- `TNOW`: Current simulation time
- Status 0 = Pending

### 3. Add ASSIGN for Payment Amount

Add another ASSIGN module (or add to previous):

1. Drag new **ASSIGN** module
2. Name: `Assign_Payment_Amount`
3. Connect previous module to this one

**Assignment**:

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Attribute | Amount | LOGN(MeanPaymentAmount, StdDevPaymentAmount) |

**Alternative Distributions**:

**Log-Normal** (Recommended):
```
Amount = LOGN(1000000, 500000)
- Mean ≈ $1M, StdDev ≈ $500K
- Positive values only
- Right-skewed (realistic for payments)
```

**Exponential**:
```
Amount = EXPO(1000000)
- Mean = $1M
- Simple, memoryless
```

**Triangular** (for bounded amounts):
```
Amount = TRIA(100000, 1000000, 10000000)
- Min = $100K, Mode = $1M, Max = $10M
```

**Empirical** (from data):
```
Amount = CONT(0.0, 100000, 0.3, 500000, 0.7, 2000000, 1.0, 10000000)
- 30% ≤ $500K
- 70% ≤ $2M
- 100% ≤ $10M
```

### 4. Add ASSIGN for Payment Type

Add ASSIGN for payment direction:

1. Name: `Assign_Payment_Type`

**Assignment**:

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Attribute | PaymentType | DISC(IncomingPaymentRatio, 1, 1.0, 2) |

**Explanation**:
```
DISC(IncomingPaymentRatio, 1, 1.0, 2)
- DISC = Discrete distribution
- If random ≤ 0.5: PaymentType = 1 (Incoming)
- If random > 0.5: PaymentType = 2 (Outgoing)
- 50/50 split by default
```

**Alternative**: Use separate probabilities
```
DISC(0.4, 1, 1.0, 2)  # 40% incoming, 60% outgoing
```

### 5. Add ASSIGN for Priority

Add priority assignment:

1. Name: `Assign_Priority`

**Assignment**:

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Attribute | Priority | DISC(0.70, 2, 0.95, 1, 1.0, 3) |

**Explanation**:
```
DISC(0.70, 2, 0.95, 1, 1.0, 3)
- 70% Normal priority (2)
- 25% High priority (1)
- 5% Low priority (3)
```

**Adjust** based on your institution:
```
More high priority: DISC(0.50, 1, 0.95, 2, 1.0, 3)
```

### 6. Add ASSIGN for Institution ID (Multi-Institution)

For network simulations:

**Assignment**:

| Type | Variable Name | New Value |
|------|---------------|-----------|
| Attribute | InstitutionID | DISC(0.2, 1, 0.4, 2, 0.6, 3, 0.8, 4, 1.0, 5) |

Or random uniform:
```
InstitutionID = UNIF(1, 10)  # 10 institutions
```

## Time-Varying Arrival Rates

### Option 1: Using SCHEDULE

1. **Edit > Schedules**
2. Click **Add**
3. Name: `Arrival_Rate_Schedule`
4. Type: **Arrival**
5. Time Units: **Hours**

**Schedule Values**:

| Time (Hours) | Value (per hour) |
|--------------|------------------|
| 0 | 30 |
| 1 | 45 |
| 2 | 60 |
| 3 | 50 |
| 4 | 55 |
| 5 | 70 |
| 6 | 65 |
| 7 | 40 |

6. In CREATE module:
   - Type: **Schedule**
   - Value: **Arrival_Rate_Schedule**

### Option 2: Using Variable Logic

Add ASSIGN before CREATE to update rate:

```
# Calculate hour of day
HourOfDay = INT((TNOW - TradingHoursStart) / 60)

# Look up rate from array
PaymentArrivalRate = ArrivalRateSchedule(HourOfDay)
```

Then CREATE uses: `EXPO(60/PaymentArrivalRate)`

## Validation and Testing

### 1. Add Temporary RECORD Module

To verify attributes:

1. Drag **RECORD** module after assignments
2. Name: `Record_Payment_Attributes`
3. Type: **Count**
4. Value: **IDENT**
5. Counter Name: **Payment_Count**

### 2. Add Temporary DISPOSE

1. Drag **DISPOSE** module
2. Name: `Dispose_Payments_Temp`
3. Connect RECORD to DISPOSE

### 3. Run Test Simulation

1. **Run > Setup > Replication Parameters**
   - Number of Replications: 1
   - Replication Length: 480 minutes (8 hours)

2. **Run > Go** (F5)

3. Check results:
   - **Window > Reports > Category Overview**
   - Entities Created: Should be ~400 (50/hr × 8 hrs)

### 4. Verify Distributions

**Check payment amounts**:
1. Add RECORD for Amount:
   - Type: **Time Persistent**
   - Attribute: **Amount**
   - Tally: **Payment_Amounts**

2. After run, view statistics:
   - Average should be near $1M
   - Verify reasonable range

**Check payment types**:
1. Add RECORD for PaymentType
2. Verify ~50% are type 1, ~50% are type 2

### 5. Debug with Animation

Enable to see payments flowing:

1. **Run > Run Control > Animation Speed**: Slow
2. **View > Entity > Show Picture**: Yes
3. Run and watch entities move

## Advanced Features

### Batch Arrivals

Create multiple payments at once:

In CREATE module:
- Entities per Arrival: **UNIF(1, 5)**
- Represents batch payment processing

### Payment Bursts

Model sudden spikes:

```
# In ASSIGN before amount assignment
IF TNOW >= BurstTime AND TNOW <= BurstTime + BurstDuration THEN
    PaymentArrivalRate = PaymentArrivalRate * 3
ENDIF
```

### Conditional Attributes

Amount depends on priority:

```
IF Priority == 1 THEN
    Amount = LOGN(5000000, 2000000)  # Larger high-priority
ELSE
    Amount = LOGN(1000000, 500000)   # Normal amounts
ENDIF
```

## Flow Diagram

```
[CREATE: Payments]
    |
    v
[ASSIGN: PaymentID, Timestamp, Status]
    |
    v
[ASSIGN: Amount ~ LOGN(...)]
    |
    v
[ASSIGN: PaymentType ~ DISC(...)]
    |
    v
[ASSIGN: Priority ~ DISC(...)]
    |
    v
[Ready for routing to liquidity logic]
```

## Common Issues

### Issue: Too many/few payments
- **Solution**: Check `60/PaymentArrivalRate` calculation
- Verify PaymentArrivalRate variable value

### Issue: Negative payment amounts
- **Solution**: Use LOGN or add `MAX(Amount, 0)`

### Issue: All payments same type
- **Solution**: Check DISC expression syntax

### Issue: Compile errors
- **Solution**: Ensure all referenced variables exist
- Check attribute names match exactly

## Checklist

- [ ] CREATE module configured with Poisson arrivals
- [ ] Basic attributes assigned (ID, timestamp, status)
- [ ] Amount distribution implemented (LOGN recommended)
- [ ] Payment type assignment working (50/50 split)
- [ ] Priority levels assigned
- [ ] Test run produces expected number of entities
- [ ] Distributions verified in output statistics
- [ ] Model saved

## Next Steps

Proceed to **[03-liquidity-tracking.md](03-liquidity-tracking.md)** to implement the liquidity position tracking logic.

---

**Previous**: [01 - Setup](01-setup.md) | **Next**: [03 - Liquidity Tracking](03-liquidity-tracking.md)
