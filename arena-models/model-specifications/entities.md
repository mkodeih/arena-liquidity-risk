# Entity Specifications

This document defines all entity types used in the Arena liquidity risk simulation model.

## Overview

Entities in Arena represent dynamic objects that flow through the system. In our liquidity simulation, entities primarily represent payment transactions.

## Entity Types

### 1. Payment Entity

The primary entity type representing individual payment transactions.

#### Attributes

| Attribute Name | Type | Description | Example Values |
|---------------|------|-------------|----------------|
| `PaymentID` | Integer | Unique identifier for the payment | 1, 2, 3, ... |
| `Amount` | Real | Payment amount in currency units | 1,000,000.50 |
| `Timestamp` | Real | Arrival time (minutes from start) | 65.3 |
| `PaymentType` | Integer | Type of payment (1=Incoming, 2=Outgoing) | 1, 2 |
| `Priority` | Integer | Priority level (1=High, 2=Normal, 3=Low) | 1, 2, 3 |
| `InstitutionID` | Integer | Originating/receiving institution | 101, 102, ... |
| `ProcessingTime` | Real | Time required to process | 2.5 |
| `Status` | Integer | Current status (0=Pending, 1=Processing, 2=Settled, 3=Failed) | 0, 1, 2, 3 |
| `QueueTime` | Real | Time spent waiting in queue | 15.2 |
| `SettlementTime` | Real | Actual settlement time | 67.8 |
| `RequiresCollateral` | Integer | Whether collateral is needed (0=No, 1=Yes) | 0, 1 |

#### Attribute Assignment

Attributes are assigned using ASSIGN modules at entity creation:

```
PaymentID = IDENT              # Unique entity ID
Amount = EXPO(MeanAmount)      # Exponential or Log-normal distribution
Timestamp = TNOW               # Current simulation time
PaymentType = DISC(0.5, 1, 1.0, 2)  # 50% incoming, 50% outgoing
Priority = DISC(0.7, 2, 0.95, 1, 1.0, 3)  # 70% normal, 25% high, 5% low
```

#### Lifecycle

1. **Creation**: Entity created at CREATE module with arrival process
2. **Attribute Assignment**: Initial attributes set via ASSIGN
3. **Processing**: Entity flows through payment processing logic
4. **Liquidity Update**: Entity triggers liquidity position updates
5. **Statistics Collection**: Entity recorded in output statistics
6. **Disposal**: Entity disposed after settlement

### 2. Liquidity Position Entity (Alternative Design)

Some models may use a separate entity to represent the institution's liquidity position.

#### Attributes

| Attribute Name | Type | Description |
|---------------|------|-------------|
| `CurrentBalance` | Real | Current liquidity level |
| `MinBalance` | Real | Minimum balance reached |
| `MaxDeficit` | Real | Maximum deficit experienced |
| `TimeInDeficit` | Real | Cumulative time below zero |
| `NumShortfalls` | Integer | Count of deficit events |

**Note**: In our recommended design, liquidity is tracked via global variables rather than entities for efficiency.

### 3. Institution Entity (Multi-Institution Models)

For simulations with multiple institutions:

#### Attributes

| Attribute Name | Type | Description |
|---------------|------|-------------|
| `InstitutionID` | Integer | Unique institution identifier |
| `Name` | String | Institution name |
| `InitialBalance` | Real | Opening liquidity position |
| `CreditLine` | Real | Available credit facility |
| `CollateralValue` | Real | Posted collateral value |
| `RiskProfile` | Integer | Risk classification (1-5) |

## Entity Flow Diagram

```
[CREATE]
   |
   v
[ASSIGN Attributes]
   |
   v
[DECIDE: Type?]
   |
   +---> [Incoming] ---> [ASSIGN: Add to Liquidity]
   |                              |
   +---> [Outgoing] ---> [DECIDE: Sufficient Liquidity?]
                              |
                              +---> [Yes] ---> [ASSIGN: Deduct from Liquidity]
                              |                        |
                              +---> [No] ---> [QUEUE: Wait for Liquidity]
                                                       |
                                                       |
   <---------------------------------------------------+
   |
   v
[RECORD Statistics]
   |
   v
[DISPOSE]
```

## Implementation Notes

### Entity Creation

Use CREATE module with:
- **Type**: Time Between Arrivals
- **Value**: `EXPO(1/ArrivalRate)` for Poisson process
- **Entities per Arrival**: 1
- **Max Arrivals**: Infinite or set limit for testing

### Performance Considerations

- Keep number of attributes minimal for performance
- Use global variables for system-level state (liquidity balance)
- Avoid creating unnecessary entities
- Dispose of entities promptly after processing

### Validation

Test entity attributes by:
1. Using RECORD modules to output attribute values
2. Checking entity counts in Arena's status windows
3. Verifying attribute distributions match specifications
4. Monitoring entity flow through animation

## Advanced Features

### Dynamic Priority

Priority can be dynamically adjusted:
```
Priority = IF(Amount > HighValueThreshold, 1, 2)
```

### Composite Entities

For batch payments, combine multiple sub-payments:
```
BatchSize = UNIF(5, 20)
TotalAmount = SUM of individual amounts
```

### Entity Attributes for Analysis

Additional attributes for detailed analysis:
- `CreationTime`: For measuring system time
- `CounterpartyID`: For network analysis
- `PaymentPurpose`: For categorization
- `RegulatoryFlag`: For compliance tracking

## References

- Arena User's Guide: Chapter 3 "Entities and Attributes"
- Arena Help: Search for "Entity Attributes"
- SIMAN Language Reference: ASSIGN statement
