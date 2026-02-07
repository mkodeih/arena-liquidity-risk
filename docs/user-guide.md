# User Guide: Arena Liquidity Risk Simulation

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Project Structure](#project-structure)
4. [Running Simulations](#running-simulations)
5. [Input Data Preparation](#input-data-preparation)
6. [Understanding Output](#understanding-output)
7. [Analysis and Visualization](#analysis-and-visualization)
8. [Design of Experiments](#design-of-experiments)
9. [Best Practices](#best-practices)
10. [Advanced Topics](#advanced-topics)

## Getting Started

### Prerequisites

Before using this simulation, ensure you have:

1. **Arena Simulation Software** (Rockwell Automation)
   - Version 16.0 or later recommended
   - Student or Professional edition
   - Valid license

2. **Python 3.8 or later** (for analysis scripts)
   - Anaconda distribution recommended
   - Required packages listed in `requirements.txt`

3. **Microsoft Excel** or compatible spreadsheet software
   - For viewing/editing input templates
   - LibreOffice Calc also compatible

### Quick Start

1. Clone or download the project repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Open Arena model: `arena-models/liquidity_risk_baseline.doe`
4. Prepare input data using templates in `data/input-templates/`
5. Run simulation in Arena
6. Analyze results using scripts in `scripts/`

## Installation

### Installing Arena

1. Download Arena from Rockwell Automation website
2. Run installer with administrator privileges
3. Follow installation wizard
4. Activate license (student, trial, or commercial)
5. Verify installation by opening Arena

### Installing Python Dependencies

```bash
# Navigate to project directory
cd arena-liquidity-risk

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Required Python Packages

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Plotting and visualization
- **seaborn**: Statistical data visualization
- **scipy**: Scientific computing and statistics
- **openpyxl**: Excel file handling

## Project Structure

```
arena-liquidity-risk/
├── arena-models/          # Arena simulation models
│   ├── *.doe             # Model files
│   └── screenshots/      # Model documentation
├── data/                 # Input/output data
│   ├── input-templates/  # Input file templates
│   ├── output-templates/ # Output file templates
│   └── sample-data/      # Example datasets
├── doe-files/            # Design of Experiments
│   ├── baseline_scenarios.doe
│   ├── stress_testing.doe
│   ├── optimization.doe
│   └── sensitivity_analysis.doe
├── docs/                 # Documentation
├── examples/             # Usage examples
├── scripts/              # Analysis scripts
└── tests/               # Validation tests
```

## Running Simulations

### Step 1: Prepare Input Data

1. **Copy templates** from `data/input-templates/` to working directory
2. **Edit institution configuration** (`institution_config.xlsx`):
   - Set initial reserves and reserve ratios
   - Configure credit limits
   - Define collateral haircuts

3. **Configure payment parameters** (`payment_parameters.xlsx`):
   - Define payment flows between institutions
   - Set priorities and amounts
   - Specify timing patterns

4. **Set market conditions** (`market_conditions.xlsx`):
   - Select scenario (NORMAL, STRESS, CRISIS)
   - Adjust interest rates and volatility
   - Configure stress parameters

### Step 2: Load Model in Arena

1. Launch Arena software
2. **File → Open**: Select model from `arena-models/`
3. Recommended starting model: `liquidity_risk_baseline.doe`
4. Review model layout and modules

### Step 3: Configure Simulation Parameters

In Arena:

1. **Run → Setup → Replication Parameters**:
   - Number of Replications: 30-50 (for statistical validity)
   - Replication Length: 28800 minutes (8 hours)
   - Warm-up Period: 60 minutes
   - Base Time Units: Minutes

2. **Run → Setup → Project Parameters**:
   - Title: Descriptive name for experiment
   - Analyst Name: Your name
   - Date: Current date

3. **Tools → Input Analyzer** (if needed):
   - Fit distributions to your payment data
   - Use for arrival rates and payment amounts

### Step 4: Import Data

1. **Navigate to model variables**:
   - Tools → Variables
   - Or use Edit → Data Transfers

2. **Configure ReadWrite module**:
   - Set file path to your input data
   - Map columns to Arena variables
   - Test connection

3. **Verify data import**:
   - Run → Check Model
   - Review any warnings or errors

### Step 5: Run Simulation

1. **Single run** (for testing):
   - Run → Go (or press F5)
   - Monitor animation window
   - Observe real-time statistics

2. **Multiple replications** (for analysis):
   - Run → Setup: Set number of replications
   - Run → Batch Run (faster, no animation)
   - Progress shown in status bar

3. **Monitor progress**:
   - Check Run Controller window
   - Review interim statistics
   - Watch for warnings/errors

### Step 6: Export Results

1. **Automatic export** (if configured):
   - Results written to output files
   - Check `data/output-templates/` directory

2. **Manual export**:
   - Run → Results: View statistics
   - File → Export: Select format (CSV, Excel)
   - Save to designated output directory

## Input Data Preparation

### Institution Configuration

**File**: `institution_config.xlsx`

**Required columns**:
- `Institution_ID`: Unique identifier (e.g., INST001)
- `Institution_Name`: Descriptive name
- `Initial_Reserve`: Starting liquidity (currency units)
- `Reserve_Ratio`: Fraction held as reserves (0-1)
- `Credit_Limit`: Maximum interbank credit
- `Collateral_Haircut`: Discount on collateral (0-1)
- `Liquidity_Buffer`: Emergency reserves
- `Risk_Category`: Credit rating (AAA, AA, A, etc.)

**Validation rules**:
- All amounts must be positive
- Reserve ratios between 0 and 1
- Reserve ratio ≥ 0.10 (regulatory minimum)
- Credit limits reflect counterparty risk

**Example**:
```csv
Institution_ID,Initial_Reserve,Reserve_Ratio,Credit_Limit
INST001,50000000,0.15,10000000
INST002,25000000,0.12,5000000
```

### Payment Parameters

**File**: `payment_parameters.xlsx`

**Required columns**:
- `Payment_ID`: Unique identifier
- `Source_Institution`: Sender ID
- `Target_Institution`: Receiver ID
- `Amount`: Payment value
- `Priority`: HIGH, NORMAL, or LOW
- `Timestamp`: Time of submission (HH:MM:SS)
- `Currency`: Currency code
- `Payment_Type`: RTGS, WIRE, or ACH

**Validation rules**:
- Source ≠ Target (no self-payments)
- Amounts > 0
- All institution IDs must exist in config
- Timestamps in chronological order

**Priority levels**:
- **HIGH**: Immediate processing, bypass queue
- **NORMAL**: Standard FIFO processing
- **LOW**: Process during low-activity periods

### Market Conditions

**File**: `market_conditions.xlsx`

**Scenarios**:
1. **NORMAL**: Baseline market conditions
2. **MODERATE_STRESS**: Elevated volatility
3. **HIGH_STRESS**: Significant disruption
4. **CRISIS**: Extreme market conditions

**Key parameters**:
- `Interest_Rate`: Risk-free rate (annual decimal)
- `Market_Volatility`: Asset price volatility
- `Liquidity_Premium`: Illiquidity spread
- `Stress_Probability`: Extreme event probability
- `Collateral_Value_Index`: Market value multiplier

## Understanding Output

### Simulation Results

**File**: `simulation_results.xlsx`

**Key metrics**:

1. **Total_Payments**: Number of payment arrivals
2. **Settled_Payments**: Successfully completed
3. **Queued_Payments**: Pending at end of day
4. **Rejected_Payments**: Failed due to constraints
5. **Average_Settlement_Time**: Mean processing time (minutes)
6. **Max_Queue_Length**: Peak queue size
7. **Gridlock_Events**: Number of gridlock situations
8. **System_Throughput**: Payments per hour

**Interpretation**:
- **Settlement Rate** = Settled / Total (target > 95%)
- **Rejection Rate** = Rejected / Total (target < 1%)
- High queue lengths indicate capacity constraints
- Gridlock events suggest systemic risk

### Risk Metrics

**File**: `risk_metrics.xlsx`

**Basel III metrics**:

1. **LCR (Liquidity Coverage Ratio)**:
   - Regulatory minimum: 1.0 (100%)
   - Well-capitalized: > 1.2
   - Formula: HQLA / Net 30-day outflows

2. **NSFR (Net Stable Funding Ratio)**:
   - Regulatory minimum: 1.0 (100%)
   - Well-capitalized: > 1.1
   - Formula: ASF / RSF

**Operational metrics**:

3. **Intraday_Liquidity**: Real-time available funds
4. **Available_Reserves**: Remaining liquid assets
5. **Credit_Used**: Interbank credit utilization
6. **Collateral_Posted**: Assets pledged
7. **Facility_Draws**: Central bank borrowing
8. **Risk_Score**: Composite risk (0-1, lower better)

**Risk score interpretation**:
- 0.00-0.15: Low risk (green)
- 0.16-0.30: Moderate risk (yellow)
- 0.31-0.50: High risk (orange)
- > 0.50: Critical risk (red)

## Analysis and Visualization

### Data Preparation

```bash
# Process input data
python scripts/data_preparation.py \
  --input data/input-templates \
  --output data/processed \
  --verbose
```

**Output**: Validated and formatted data files

### Statistical Analysis

```bash
# Analyze simulation results
python scripts/results_analyzer.py \
  --results data/output-templates/simulation_results.xlsx \
  --metrics data/output-templates/risk_metrics.xlsx \
  --output reports \
  --baseline BASELINE \
  --confidence 0.95
```

**Output**:
- `results_statistics.csv`: Summary statistics
- `confidence_intervals.csv`: 95% CIs
- `scenario_comparison.csv`: Statistical tests
- `analysis_report.txt`: Comprehensive report

### Visualization

```bash
# Create plots and charts
python scripts/visualization.py \
  --input data/output-templates \
  --output figures \
  --format png \
  --dpi 300
```

**Output**: Multiple visualization files
- Settlement time distributions
- Scenario comparisons
- Queue length boxplots
- LCR heatmaps
- Risk dashboards
- Gridlock analysis

### Model Validation

```bash
# Validate model outputs
python scripts/validation.py \
  --simulation data/output-templates \
  --historical data/historical \
  --output validation
```

**Output**: Validation report with statistical tests

## Design of Experiments

### Baseline Scenarios

**File**: `doe-files/baseline_scenarios.doe`

**Purpose**: Establish baseline performance under normal conditions

**Factors**:
- Reserve levels (low, medium, high)
- Payment volumes (light, moderate, heavy)
- Market conditions (calm, normal, volatile)

**Runs**: 27 (3³ full factorial)

### Stress Testing

**File**: `doe-files/stress_testing.doe`

**Purpose**: Assess resilience under adverse conditions

**Scenarios**:
1. Liquidity shock (sudden reserve withdrawal)
2. Payment surge (volume spike)
3. Credit crunch (tightened credit limits)
4. Market crash (collateral value drop)
5. Combined stress (multiple simultaneous shocks)

### Optimization

**File**: `doe-files/optimization.doe`

**Purpose**: Find optimal parameter settings

**Method**: Central Composite Design (CCD)
- 5 factors
- 54 runs (factorial + axial + center points)
- Response surface methodology

**Objectives**:
- Maximize LCR
- Minimize settlement time
- Minimize gridlock events
- Maximize throughput

### Sensitivity Analysis

**File**: `doe-files/sensitivity_analysis.doe`

**Purpose**: Identify critical parameters

**Method**: One-at-a-Time (OAT) perturbations
- 13 parameters
- ±10%, ±25%, ±50% perturbations
- 1,950 total runs

**Output**: Parameter ranking by impact

## Best Practices

### Simulation Setup

1. **Sufficient replications**: Run ≥ 30 for statistical validity
2. **Appropriate warm-up**: Allow 1-hour warm-up for steady state
3. **Independent runs**: Use different random seeds
4. **Variance reduction**: Consider common random numbers

### Data Quality

1. **Validate inputs**: Use data_preparation.py script
2. **Check consistency**: Verify institution IDs match
3. **Realistic parameters**: Base on historical data when possible
4. **Document assumptions**: Record any data transformations

### Analysis

1. **Multiple metrics**: Don't rely on single indicator
2. **Confidence intervals**: Report uncertainty
3. **Scenario comparison**: Use statistical tests
4. **Sensitivity checks**: Assess robustness

### Model Verification

1. **Face validity**: Do results make logical sense?
2. **Extreme conditions**: Test with extreme inputs
3. **Comparison**: Validate against historical data
4. **Peer review**: Have others examine model logic

### Documentation

1. **Version control**: Track model and data versions
2. **Record parameters**: Document all settings used
3. **Save everything**: Keep all input/output files
4. **Reproducibility**: Ensure results can be replicated

## Advanced Topics

### Custom Scenarios

See `examples/custom_scenario.md` for creating tailored scenarios

### Extending the Model

1. **Adding institutions**: Expand institution config
2. **New payment types**: Modify Arena model logic
3. **Additional metrics**: Extend output collection
4. **Integration**: Connect to external data sources

### Performance Optimization

1. **Batch runs**: Use Arena's batch runner
2. **Parallel processing**: Multiple scenario instances
3. **Selective output**: Only collect needed statistics
4. **Efficient coding**: Optimize VBA if used

### Regulatory Reporting

Generate Basel III compliant reports:
1. Run monthly scenarios
2. Calculate required ratios
3. Document methodologies
4. Archive all results

## Troubleshooting

For common issues and solutions, see [troubleshooting.md](troubleshooting.md)

## Further Reading

- [methodology.md](methodology.md): Mathematical foundations
- [arena-tutorial.md](arena-tutorial.md): Arena basics
- [references.md](references.md): Academic sources
- Project examples in `examples/` directory
