# 01 - Setup and Initial Configuration

This guide walks through setting up Arena and creating the initial model structure for the intraday liquidity risk simulation.

## Prerequisites

### Software Requirements

- **Arena Simulation Software** (Rockwell Automation)
  - Version 16.0 or higher
  - Professional or Academic license
  - Installation size: ~2 GB

- **Microsoft Office**
  - Excel 2016 or later (for data import/export)

- **System Requirements**
  - Windows 10/11 (64-bit recommended)
  - 8 GB RAM minimum (16 GB recommended)
  - 10 GB free disk space

### Knowledge Prerequisites

- Basic understanding of discrete-event simulation
- Familiarity with liquidity risk concepts
- Basic statistics (distributions, mean, variance)

## Installation Steps

### 1. Install Arena

1. Download Arena from Rockwell Automation website or use installation media
2. Run installer as Administrator
3. Choose **Full Installation** to include all modules
4. Accept license agreement
5. Complete installation (may take 15-30 minutes)
6. Restart computer if prompted

### 2. Verify Installation

1. Launch Arena
2. Go to **Help > About Arena**
3. Verify version is 16.0 or higher
4. Check that license is valid

### 3. Configure Arena Settings

1. **Tools > Options**
2. **General** tab:
   - Decimal places: 2
   - Time units: Minutes
3. **Run Control** tab:
   - Animation speed: Medium
   - Pause on error: Checked
4. **Project Parameters** tab:
   - Default time units: Minutes
   - Default distance units: Meters

## Creating the New Model

### 1. Start New Model

1. **File > New** or press Ctrl+N
2. Save immediately: **File > Save As**
   - Name: `Liquidity_Risk_Simulation.doe`
   - Location: Your project directory
3. Set base time units: **Run > Setup > Project Parameters**
   - Base Time Units: **Minutes**

### 2. Model Description

Add documentation to your model:

1. **Tools > Edit Model Description**
2. Enter:
   ```
   Title: Intraday Liquidity Risk Simulation
   Analyst: [Your Name]
   Date: [Current Date]
   
   Description:
   Monte Carlo simulation for estimating intraday liquidity risk
   in financial institutions. Models payment flows and tracks
   liquidity positions to calculate VaR and shortfall probability.
   
   Based on: "Estimating the intraday liquidity risk of financial
   institutions: a Monte Carlo simulation approach"
   ```

### 3. Set Project Parameters

**Run > Setup > Project Parameters**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Time Units | Minutes | Standard for intraday |
| Hours Per Day | 24 | Full day |
| Base Time Units | Minutes | |

### 4. Configure Run Control

**Run > Setup > Replication Parameters**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Number of Replications | 30 | Start with 30 for testing |
| Replication Length | 480 | 8 trading hours |
| Hours Per Day | 24 | |
| Warm-up Period | 0 | No warm-up for daily simulation |
| Initialize System | Yes | Fresh start each replication |

### 5. Set Up Random Number Streams

For reproducibility and proper Monte Carlo simulation:

**Setup > Random Number Streams**

Configure 10 streams:

| Stream | Purpose | Initial Seed |
|--------|---------|--------------|
| 1 | Payment arrivals | 12345 |
| 2 | Payment amounts | 23456 |
| 3 | Payment types | 34567 |
| 4 | Payment priorities | 45678 |
| 5 | Processing times | 56789 |
| 6 | Stress events | 67890 |
| 7 | Contagion | 78901 |
| 8 | Reserved | 89012 |
| 9 | Reserved | 90123 |
| 10 | Reserved | 10234 |

**Important**: Different streams ensure independence between random processes.

## Define Global Variables

### 1. Open Variable Module

1. Go to **Basic Process** panel
2. Click **Variable** button (database icon)
3. Click **Add** to create new variables

### 2. Create Essential Variables

**Liquidity Variables:**

| Name | Initial Value | Rows | Columns | Type |
|------|---------------|------|---------|------|
| OpeningBalance | 10000000 | 1 | 1 | Real |
| CurrentBalance | 10000000 | 1 | 1 | Real |
| MinimumBalance | 10000000 | 1 | 1 | Real |
| MaximumBalance | 10000000 | 1 | 1 | Real |
| RequiredBuffer | 2000000 | 1 | 1 | Real |
| CreditLineLimit | 20000000 | 1 | 1 | Real |
| CreditLineUsed | 0 | 1 | 1 | Real |

**Payment Variables:**

| Name | Initial Value | Rows | Columns | Type |
|------|---------------|------|---------|------|
| PaymentArrivalRate | 50 | 1 | 1 | Real |
| MeanPaymentAmount | 1000000 | 1 | 1 | Real |
| StdDevPaymentAmount | 500000 | 1 | 1 | Real |
| IncomingPaymentRatio | 0.5 | 1 | 1 | Real |
| TotalIncomingValue | 0 | 1 | 1 | Real |
| TotalOutgoingValue | 0 | 1 | 1 | Real |

**Risk Metrics:**

| Name | Initial Value | Rows | Columns | Type |
|------|---------------|------|---------|------|
| ShortfallCount | 0 | 1 | 1 | Integer |
| TimeInDeficit | 0 | 1 | 1 | Real |
| MaxDeficit | 0 | 1 | 1 | Real |
| DeficitStartTime | -1 | 1 | 1 | Real |

**Tip**: Copy these to a text file or Excel for reference.

### 3. Create Arrays (Optional)

For time-series tracking:

| Name | Rows | Columns | Description |
|------|------|---------|-------------|
| LiquidityHistory | 480 | 1 | Minute-by-minute balance |
| PaymentVolume | 24 | 1 | Hourly payment counts |
| ArrivalRateSchedule | 24 | 1 | Time-varying rates |

## Define Attributes

Attributes belong to entities (payments). Set these up now for use later.

**Click Attribute button in Basic Process panel**

| Name | Initial Value | Type |
|------|---------------|------|
| PaymentID | 0 | Integer |
| Amount | 0 | Real |
| Timestamp | 0 | Real |
| PaymentType | 0 | Integer |
| Priority | 0 | Integer |
| Status | 0 | Integer |
| QueueTime | 0 | Real |
| SettlementTime | 0 | Real |
| ProcessingTime | 0 | Real |

## Set Up Resources (Optional)

For capacity-constrained settlement:

**Click Resource button**

| Name | Type | Capacity | State Set |
|------|------|----------|-----------|
| Settlement_System | Fixed Capacity | 100 | Default |

**Notes**: 
- High capacity (100) means effectively no constraint
- Reduce for capacity analysis
- Can add schedule later for time-varying capacity

## Configure Queues (Advanced)

For explicit queue management:

**Click Queue button**

| Name | Type |
|------|------|
| Queue_High_Priority | First In First Out |
| Queue_Normal | First In First Out |
| Queue_Low_Priority | First In First Out |

## Organize Model Window

### 1. Set View Preferences

**View > Layers**
- Check **Flowchart**
- Check **Queue**
- Check **Variable**

**View > Status Bars**
- Check **Replication Status**
- Check **Run Status**

### 2. Zoom and Layout

- Set zoom to 100% (View > Zoom > 100%)
- Show grid: **View > Grid**
- Snap to grid: **View > Snap to Grid**

## Validate Initial Setup

### Checklist

- [ ] Arena software installed and licensed
- [ ] New model created and saved
- [ ] Time units set to Minutes
- [ ] Replication parameters configured
- [ ] Random number streams defined
- [ ] Global variables created
- [ ] Attributes defined
- [ ] Model description entered

### Test Run

1. **Run > Go** (or F5)
2. Model should run for 1 replication (480 minutes)
3. Should complete with no errors
4. Check **Window > Reports > Category Overview**

**Expected**: No errors, replication completes successfully (even with empty model).

## Save and Backup

1. **File > Save** (Ctrl+S)
2. Create backup: **File > Save As**
   - Name: `Liquidity_Risk_Simulation_v1_Setup.doe`
   - Keep version history for major milestones

## Common Issues and Solutions

### Issue: Arena won't start
- **Solution**: Check license server, reinstall if needed

### Issue: Cannot set time units to Minutes
- **Solution**: Close all models, restart Arena, set in new model

### Issue: Variables not saving
- **Solution**: Click OK in Variable dialog, save model immediately

### Issue: Random number stream errors
- **Solution**: Ensure seeds are positive integers, unique per stream

## Next Steps

Proceed to **[02-payment-generation.md](02-payment-generation.md)** to build the payment arrival and attribute assignment logic.

## Additional Resources

- **Arena Help**: Press F1 in any Arena window
- **Arena Examples**: `C:\Program Files\Rockwell Software\Arena\Examples`
- **Arena User's Guide**: Installed with Arena, comprehensive reference
- **Video Tutorials**: Rockwell Automation website

## Quick Reference: Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run simulation | F5 |
| Stop simulation | F4 |
| Save model | Ctrl+S |
| Help | F1 |
| Zoom in | Ctrl+Plus |
| Zoom out | Ctrl+Minus |
| Toggle animation | Alt+A |

---

**Next**: [02 - Payment Generation](02-payment-generation.md)
