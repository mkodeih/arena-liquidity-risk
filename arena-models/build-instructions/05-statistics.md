# 05 - Output Statistics and Risk Metrics

This guide shows how to configure comprehensive output statistics for liquidity risk analysis, including standard Arena outputs, custom statistics, time-series data collection, and export configuration.

## Overview

We'll implement statistics for:
- Standard liquidity risk metrics (VaR, CVaR, shortfall probability)
- Time-series tracking of liquidity positions
- Payment flow statistics
- Queue performance metrics
- Custom calculated statistics
- Automated data export for external analysis

## Understanding Arena Statistics

### Types of Statistics

| Type | Purpose | Example |
|------|---------|---------|
| **Tally** | Observation-based | Payment amounts |
| **Time-Persistent** | State over time | Liquidity balance |
| **Counter** | Event counts | Number of shortfalls |
| **Output** | End-of-replication | Minimum balance |
| **Frequency** | Distribution | Payment types |

### Automatic vs. Custom

**Automatic**:
- Entity statistics (cycle time, wait time)
- Queue statistics (length, time in queue)
- Resource statistics (utilization, busy time)

**Custom**:
- Risk metrics (VaR, Expected Shortfall)
- Business-specific KPIs
- Calculated ratios

## Configuring Standard OUTPUT Statistics

### 1. Access Output Statistic Module

**Basic Process panel > Statistic button** or **Run > Setup > Statistics**

### 2. Define Key Liquidity Metrics

Click **Add** for each statistic:

#### Critical Balance Metrics

| Name | Type | Variable/Expression | Report ID |
|------|------|-------------------|-----------|
| Final_Balance | Output | CurrentBalance | STAT_1 |
| Minimum_Balance | Output | MinimumBalance | STAT_2 |
| Maximum_Balance | Output | MaximumBalance | STAT_3 |
| Max_Exposure | Output | MaxExposure | STAT_4 |
| Opening_Balance | Output | OpeningBalance | STAT_5 |

**Configuration**:
- Type: **Output**
- Report Label: Descriptive name for reports
- Output File: **Yes** (for export)

#### Deficit Metrics

| Name | Type | Expression |
|------|------|------------|
| Shortfall_Count | Output | ShortfallCount |
| Time_In_Deficit | Output | TimeInDeficit |
| Deficit_Probability | Output | ShortfallCount > 0 |
| Avg_Deficit_Duration | Output | TimeInDeficit / MAX(ShortfallCount, 1) |

#### Credit Line Usage

| Name | Type | Expression |
|------|------|------------|
| Max_Credit_Used | Output | CreditLineUsed |
| Credit_Utilization | Output | CreditLineUsed / CreditLineLimit |
| Credit_Used_Flag | Output | CreditLineUsed > 0 |

#### Payment Flow Metrics

| Name | Type | Expression |
|------|------|------------|
| Total_Incoming | Output | TotalIncomingValue |
| Total_Outgoing | Output | TotalOutgoingValue |
| Net_Flow | Output | TotalIncomingValue - TotalOutgoingValue |
| Payment_Imbalance | Output | ABS(TotalIncomingValue - TotalOutgoingValue) |

### 3. Configure Reporting Options

For each OUTPUT statistic:

**Run > Setup > Statistics > Output Tab**

| Option | Setting |
|--------|---------|
| Collect Statistics | Yes |
| Include in Report | Yes |
| Export to File | Yes |
| Calculate Confidence Interval | Yes |
| Confidence Level | 0.95 |

## Implementing RECORD Modules

### 1. Payment Amount Distribution

Add **RECORD** module after payment generation:

| Property | Value |
|----------|-------|
| Name | Record_Payment_Amounts |
| Type | Tally |
| Attribute Name | Amount |
| Tally Name | Payment_Amounts |

Output includes:
- Mean, min, max
- Standard deviation
- Observations count

### 2. Queue Time Tracking

Add **RECORD** after QUEUE module:

| Property | Value |
|----------|-------|
| Name | Record_Queue_Time |
| Type | Time Interval |
| Attribute Name | QueueTime |
| Tally Name | Payment_Queue_Time |

Or use between:
```
Between: QueueEntryTime, TNOW
```

### 3. Settlement Time Distribution

Track time from creation to settlement:

| Property | Value |
|----------|-------|
| Name | Record_Settlement_Time |
| Type | Interval |
| Between | Timestamp, SettlementTime |
| Tally Name | Settlement_Times |

### 4. Payment Count by Type

Add **RECORD** for incoming payments:

| Property | Value |
|----------|-------|
| Type | Count |
| Counter Name | Incoming_Count |

Add **RECORD** for outgoing payments:

| Property | Value |
|----------|-------|
| Type | Count |
| Counter Name | Outgoing_Count |

### 5. Priority Distribution

Add **RECORD** for priority tracking:

| Property | Value |
|----------|-------|
| Type | Tally |
| Attribute | Priority |
| Tally Name | Priority_Distribution |

## Custom Statistics Using DSTAT

### What is DSTAT?

**DSTAT** = Time-weighted average of an expression over simulation run.

**Formula**: 
```
DSTAT = ∫ Expression(t) dt / Total Time
```

### 1. Average Liquidity Position

**Run > Setup > Statistics > Time-Persistent**

| Property | Value |
|----------|-------|
| Name | Avg_Liquidity_Position |
| Type | Time-Persistent |
| Expression | CurrentBalance |
| DSTAT Name | DSTAT_Liquidity |

**Result**: Time-weighted average balance over the trading day.

### 2. Liquidity Buffer Coverage

Track how often buffer is maintained:

| Property | Value |
|----------|-------|
| Expression | CurrentBalance >= RequiredBuffer |
| DSTAT Name | DSTAT_Buffer_Coverage |

**Result**: Proportion of time with adequate buffer (0.0 to 1.0)

### 3. Stress Indicator

| Property | Value |
|----------|-------|
| Expression | CurrentBalance < RequiredBuffer |
| DSTAT Name | DSTAT_Stress_Time |

**Result**: Proportion of day in stressed state.

### 4. Credit Line Utilization Over Time

| Property | Value |
|----------|-------|
| Expression | CreditLineUsed / CreditLineLimit |
| DSTAT Name | DSTAT_Credit_Util |

### 5. Queue Length Over Time

| Property | Value |
|----------|-------|
| Expression | NQ(Queue_Outgoing_Payments) |
| DSTAT Name | DSTAT_Queue_Length |

**Result**: Average number of payments waiting.

## Advanced: Custom Calculated Statistics

### 1. Liquidity at Risk (LaR)

LaR = Opening Balance - Minimum Balance

Add OUTPUT statistic:

| Name | Expression |
|------|------------|
| Liquidity_at_Risk | OpeningBalance - MinimumBalance |

### 2. Relative Drawdown

Percentage decline from opening:

| Name | Expression |
|------|------------|
| Relative_Drawdown | (OpeningBalance - MinimumBalance) / OpeningBalance * 100 |

### 3. Turnover Ratio

Payment activity relative to opening balance:

| Name | Expression |
|------|------------|
| Turnover_Ratio | (TotalIncomingValue + TotalOutgoingValue) / (2 * OpeningBalance) |

### 4. Average Payment Size

| Name | Expression |
|------|------------|
| Avg_Payment_Size | (TotalIncomingValue + TotalOutgoingValue) / (Incoming_Count + Outgoing_Count) |

## Implementing Value at Risk (VaR)

### Understanding VaR in Liquidity Context

**VaR (95%)**: "95% of the time, liquidity will not fall below this level"

### Method 1: Post-Processing

1. Run 1000 replications
2. Collect `MinimumBalance` from each replication
3. Sort values ascending
4. VaR 95% = 5th percentile value (50th smallest)

**In Excel**:
```excel
=PERCENTILE(MinBalanceArray, 0.05)
```

### Method 2: Arena Built-in

Arena Category Overview report provides percentiles automatically.

**Access**: Window > Reports > Category Overview > User Specified

Look for: **Minimum Balance - 5th Percentile**

### Method 3: Custom VBA

Add VBA code to calculate during run:

```vba
Dim MinBalances(1 To 1000) As Double
Dim RepNumber As Integer

Sub OnEndReplication()
    RepNumber = ThisDocument.ModelInfo.NumberOfReplications
    MinBalances(RepNumber) = ThisDocument.Variables("MinimumBalance").Value
    
    If RepNumber = 1000 Then
        Call CalculateVaR
    End If
End Sub

Sub CalculateVaR()
    Dim Sorted() As Double
    Sorted = SortArray(MinBalances)
    VaR95 = Sorted(50)  ' 5th percentile
    CVaR95 = Application.Average(Array(Sorted(1) To Sorted(50)))
    
    MsgBox "VaR 95%: " & VaR95 & vbCrLf & "CVaR 95%: " & CVaR95
End Sub
```

## Conditional Value at Risk (CVaR)

### Definition

**CVaR**: Average of worst 5% outcomes (Expected Shortfall)

More informative than VaR for tail risk.

### Calculation

**Post-processing**:
```
1. Collect all MinimumBalance values
2. Sort ascending
3. CVaR 95% = Average of bottom 5% (replications 1-50)
```

**Excel**:
```excel
=AVERAGE(A1:A50)  ' Where A1:A50 are sorted worst 50 outcomes
```

## Time-Series Data Collection

### 1. Create Time-Series Array

**Variable module**:

| Name | Rows | Columns | Initial Value |
|------|------|---------|---------------|
| BalanceHistory | 480 | 1 | 0 |
| HourlyInflow | 24 | 1 | 0 |
| HourlyOutflow | 24 | 1 | 0 |

### 2. Record Balance Every Minute

Add CREATE module:

| Property | Value |
|----------|-------|
| Name | Create_Balance_Recorder |
| Type | Constant |
| Value | 1.0 |
| Max Arrivals | 480 |

Add ASSIGN module:

```
Minute = INT(TNOW)
BalanceHistory(Minute) = CurrentBalance
```

### 3. Aggregate Hourly Flows

Add logic in payment processing ASSIGN:

```
Hour = INT(TNOW / 60) + 1

IF PaymentType == 1 THEN
    HourlyInflow(Hour) = HourlyInflow(Hour) + Amount
ELSE
    HourlyOutflow(Hour) = HourlyOutflow(Hour) + Amount
ENDIF
```

### 4. Export Time-Series

At end of replication, use WRITE module or VBA:

```vba
Sub ExportTimeSeries()
    Open "BalanceHistory_Rep" & RepNum & ".csv" For Output As #1
    
    For i = 1 To 480
        Write #1, i, BalanceHistory(i)
    Next i
    
    Close #1
End Sub
```

## Export Configuration

### 1. Arena Output Reports

**Window > Reports > Category Overview**

**Export**:
- File > Export > Save As: `Results.txt`
- Format: Tab-delimited or XML

**Automated Export**:
**Run > Setup > Run Control > Output File**: Check "Write Report"

### 2. Using READWRITE Module

From **Advanced Transfer panel**:

#### Setup File

Add READWRITE at start of run:

| Property | Value |
|----------|-------|
| Name | Initialize_Output_File |
| Type | Write to File |
| File Name | Results.csv |
| Recordset Name | OutputData |
| Format | Free Format |
| Assignments | See below |

**Assignments** (header row):
```
WRITE OutputData, "Rep,MinBalance,MaxExposure,ShortfallCount,CreditUsed"
```

#### Write Replication Results

Add READWRITE at end of each replication:

```
WRITE OutputData, MREP, MinimumBalance, MaxExposure, ShortfallCount, CreditLineUsed
```

**MREP** = Current replication number (Arena variable)

### 3. Custom Output Using VBA

More flexible for complex exports:

```vba
Sub OnEndReplication()
    Dim rep As Integer
    Dim fileName As String
    
    rep = ThisDocument.ModelInfo.CurrentReplication
    fileName = "C:\Output\Liquidity_Results.csv"
    
    Open fileName For Append As #1
    
    Print #1, rep & "," & _
              ThisDocument.Variables("MinimumBalance").Value & "," & _
              ThisDocument.Variables("MaxExposure").Value & "," & _
              ThisDocument.Variables("ShortfallCount").Value & "," & _
              ThisDocument.Variables("TimeInDeficit").Value & "," & _
              ThisDocument.Variables("CreditLineUsed").Value
    
    Close #1
End Sub

Sub OnBeginSimulation()
    ' Write header
    Open "C:\Output\Liquidity_Results.csv" For Output As #1
    Print #1, "Replication,MinBalance,MaxExposure,Shortfalls,DeficitTime,CreditUsed"
    Close #1
End Sub
```

### 4. Export to Excel

**Tools > Output Analyzer** (if installed)

Or use VBA to write directly to Excel:

```vba
Dim xlApp As Object
Dim xlBook As Object
Dim xlSheet As Object

Set xlApp = CreateObject("Excel.Application")
Set xlBook = xlApp.Workbooks.Open("C:\Output\Results.xlsx")
Set xlSheet = xlBook.Worksheets(1)

xlSheet.Cells(rep + 1, 1) = rep
xlSheet.Cells(rep + 1, 2) = MinimumBalance
' etc.

xlBook.Save
xlBook.Close
xlApp.Quit
```

## Confidence Intervals

### 1. Enable in Arena

**Run > Setup > Statistics**

For each statistic:
- Check "Calculate Confidence Interval"
- Confidence Level: 0.95

**Output**:
```
Minimum_Balance:  $8.74M ± $0.23M (95% CI)
```

### 2. Interpretation

**Half-width**: ±$0.23M
- "True mean likely between $8.51M and $8.97M"
- Narrower interval = more precision
- Need more replications to narrow

### 3. Acceptable Half-Width

**Rule of Thumb**:
- Half-width < 5% of mean is good
- Example: Mean = $8.74M → Target half-width < $0.44M

### 4. Increasing Precision

If half-width too large:

**Required replications**:
```
n_new = n_old × (h_old / h_target)²

Example:
Current: 100 reps, h = $0.50M
Target: h = $0.25M
Required: 100 × (0.50/0.25)² = 400 reps
```

## Reporting Risk Metrics

### 1. Create Custom Report

**Window > Reports > Create New Report**

**Include**:
- Replication count
- Confidence level
- Key statistics with CIs
- Risk thresholds
- Scenario description

### 2. Automated Reporting

Use VBA to generate formatted report:

```vba
Sub GenerateRiskReport()
    Dim report As String
    
    report = "LIQUIDITY RISK ANALYSIS REPORT" & vbCrLf & vbCrLf
    report = report & "Replications: " & NumReps & vbCrLf
    report = report & "Confidence Level: 95%" & vbCrLf & vbCrLf
    
    report = report & "RISK METRICS:" & vbCrLf
    report = report & "Minimum Balance (mean): $" & Format(AvgMinBalance, "#,##0") & vbCrLf
    report = report & "VaR 95%: $" & Format(VaR95, "#,##0") & vbCrLf
    report = report & "CVaR 95%: $" & Format(CVaR95, "#,##0") & vbCrLf
    report = report & "Shortfall Probability: " & Format(ShortfallProb, "0.0%") & vbCrLf
    
    Open "Risk_Report.txt" For Output As #1
    Print #1, report
    Close #1
End Sub
```

### 3. Regulatory Metrics

Calculate compliance metrics:

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Shortfall Probability | COUNT(MinBalance < 0) / Reps | < 1% |
| Expected Shortfall | AVG(ABS(MIN(MinBalance, 0))) | < $500K |
| Buffer Breach Prob | COUNT(MinBalance < Buffer) / Reps | < 5% |
| Credit Reliance | COUNT(CreditUsed > 0) / Reps | < 10% |

## Visualization Recommendations

### Export for Graphing

**Recommended outputs for plotting**:

1. **Histogram**: Minimum Balance distribution
2. **CDF**: Cumulative distribution of Min Balance
3. **Time Series**: Balance over trading day (select replications)
4. **Box Plot**: Min Balance by scenario
5. **Scatter**: Credit Used vs. Min Balance

### Using Arena Output Analyzer

**Tools > Output Analyzer**

- Import .dat files
- Create histograms
- Plot confidence intervals
- Compare scenarios

### External Tools

**Export CSV and use**:
- Excel: Pivot tables, charts
- R: ggplot2 for publication graphics
- Python: matplotlib, seaborn
- Tableau: Interactive dashboards

## Checklist

- [ ] OUTPUT statistics defined for key metrics
- [ ] RECORD modules track payment distributions
- [ ] DSTAT statistics capture time-weighted measures
- [ ] Custom calculated statistics implemented
- [ ] Time-series arrays created (if needed)
- [ ] VaR/CVaR calculation method chosen
- [ ] Export mechanism configured (READWRITE or VBA)
- [ ] Confidence intervals enabled
- [ ] Test run produces expected statistics
- [ ] Output files generated successfully
- [ ] Report format meets requirements
- [ ] All metrics documented

## Common Issues and Solutions

### Issue: Statistics not appearing in output
- **Solution**: Verify "Collect Statistics" is checked
- Ensure OUTPUT type used for end-of-run metrics

### Issue: Confidence intervals unreasonably wide
- **Solution**: Increase number of replications
- Check for high variance in model (intentional?)

### Issue: DSTAT always zero
- **Solution**: Verify expression syntax
- Ensure variable updates during simulation

### Issue: Export file empty
- **Solution**: Check file path is valid
- Verify WRITE statements execute
- Use absolute paths (C:\Output\...)

### Issue: Queue statistics missing
- **Solution**: Ensure queue has explicit name
- Check "Report Statistics" option in queue module

### Issue: VBA export errors
- **Solution**: Check Excel/file permissions
- Use late binding (CreateObject) not early binding
- Test file write permissions

### Issue: Tally count is zero
- **Solution**: Verify entities pass through RECORD module
- Check connection in model flowchart

## Next Steps

Proceed to **[06-validation.md](06-validation.md)** to verify model correctness, validate against theoretical distributions, and debug issues.

---

**Previous**: [04 - Monte Carlo](04-monte-carlo.md) | **Next**: [06 - Validation](06-validation.md)
