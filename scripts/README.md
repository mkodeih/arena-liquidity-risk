# Scripts Directory

This directory contains Python scripts for data preparation, analysis, and visualization of Arena simulation results.

## Contents

### Core Scripts

1. **data_preparation.py**
   - Loads and validates input data files
   - Transforms data into Arena-compatible formats
   - Handles missing values and data quality checks
   - Generates summary statistics for input validation

2. **results_analyzer.py**
   - Analyzes simulation output data
   - Calculates key performance indicators (KPIs)
   - Performs statistical tests and comparisons
   - Generates summary reports

3. **visualization.py**
   - Creates plots and charts for simulation results
   - Generates risk dashboards
   - Produces time-series visualizations
   - Exports publication-quality figures

4. **validation.py**
   - Validates model outputs against historical data
   - Performs sensitivity checks
   - Assesses model calibration
   - Generates validation reports

## Requirements

All scripts require Python 3.8+ and the dependencies listed in `requirements.txt`:
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- openpyxl (for Excel file handling)

## Usage

### Data Preparation
```bash
python data_preparation.py --input data/input-templates/ --output data/processed/
```

### Results Analysis
```bash
python results_analyzer.py --results data/output-templates/simulation_results.xlsx --output reports/
```

### Visualization
```bash
python visualization.py --input data/output-templates/ --output figures/ --format png
```

### Model Validation
```bash
python validation.py --simulation data/output-templates/ --historical data/historical/ --output validation/
```

## Script Descriptions

### data_preparation.py
Prepares input data for Arena simulation models. Key features:
- Validates data formats and ranges
- Checks for missing or invalid values
- Converts between data formats (CSV, Excel)
- Generates input data summaries

### results_analyzer.py
Analyzes simulation outputs and calculates performance metrics. Key features:
- Statistical analysis of multiple replications
- Confidence interval calculation
- Scenario comparison
- KPI tracking and reporting

### visualization.py
Creates comprehensive visualizations of simulation results. Key features:
- Time-series plots of liquidity metrics
- Distribution plots for settlement times
- Risk heatmaps
- Comparative scenario charts

### validation.py
Validates simulation model against real-world data. Key features:
- Goodness-of-fit tests
- Calibration assessment
- Parameter sensitivity validation
- Model robustness checks

## Best Practices

1. **Data Validation**: Always run data_preparation.py before simulation
2. **Multiple Replications**: Analyze at least 30 replications for statistical validity
3. **Version Control**: Keep track of data versions and analysis parameters
4. **Documentation**: Document any data transformations or assumptions

## Outputs

Scripts generate outputs in the following locations:
- Processed data: `data/processed/`
- Analysis reports: `reports/`
- Figures: `figures/`
- Validation results: `validation/`

## Support

For issues or questions:
- Check the documentation in `docs/`
- Review troubleshooting guide: `docs/troubleshooting.md`
- See examples in `examples/`
