# Arena Liquidity Risk Simulation

A comprehensive Arena simulation project for **intraday liquidity risk estimation** in financial institutions using **Monte Carlo methods**.

## Overview

This project provides a complete framework for simulating and analyzing intraday liquidity risk in financial institutions. It is based on the research paper:

> **"Estimating the intraday liquidity risk of financial institutions: a Monte Carlo simulation approach"**

The simulation models payment flows, liquidity positions, and risk metrics to help institutions:
- Estimate Value at Risk (VaR) for intraday liquidity
- Test stress scenarios and resilience
- Optimize liquidity buffer requirements
- Comply with regulatory requirements (e.g., Basel III liquidity standards)

## Features

- **Arena Model Specifications**: Detailed documentation for building the simulation model in Arena software
- **Design of Experiments (DOE)**: Pre-configured experimental designs for various scenarios
- **Data Templates**: Excel templates for input parameters and output analysis
- **Python Analysis Tools**: Scripts for data preparation, results analysis, and visualization
- **Comprehensive Documentation**: User guides, methodology explanations, and tutorials
- **Example Scenarios**: Ready-to-use scenarios for quick start

## Project Structure

```
arena-liquidity-risk/
├── README.md                  # This file
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── arena-models/              # Arena model specifications and build instructions
│   ├── model-specifications/  # Detailed model component specifications
│   ├── build-instructions/    # Step-by-step building guides
│   └── screenshots/           # Model screenshots and diagrams
├── doe-files/                 # Design of Experiments files for Arena
├── data/                      # Data templates and sample datasets
│   ├── input-templates/       # Input parameter templates
│   ├── output-templates/      # Output result templates
│   └── sample-data/           # Example datasets
├── scripts/                   # Python analysis and visualization tools
├── docs/                      # Comprehensive documentation
├── examples/                  # Example scenarios and use cases
└── tests/                     # Validation checklists and test scenarios
```

## Quick Start

### Prerequisites

1. **Arena Simulation Software** (Rockwell Automation)
   - Version 16.0 or higher recommended
   - Professional or Academic license

2. **Python 3.8+** (for analysis scripts)
   ```bash
   pip install -r requirements.txt
   ```

3. **Microsoft Excel** (for data templates)

### Getting Started

1. **Build the Arena Model**
   - Follow the step-by-step instructions in `arena-models/build-instructions/`
   - Start with `01-setup.md` and proceed sequentially
   - Refer to `arena-models/model-specifications/` for detailed component specs

2. **Run a Basic Scenario**
   - Open the completed Arena model
   - Import `doe-files/baseline_scenarios.doe`
   - Run the simulation (recommended: 1,000+ replications)
   - Export results to Excel

3. **Analyze Results**
   ```bash
   python scripts/results_analyzer.py
   python scripts/visualization.py
   ```

4. **Explore Examples**
   - See `examples/basic_scenario.md` for a normal market conditions scenario
   - Try `examples/stress_test_scenario.md` for crisis simulation
   - Customize `examples/custom_scenario.md` for your specific needs

## Documentation

- **[Methodology](docs/methodology.md)**: Theoretical background and mathematical formulations
- **[User Guide](docs/user-guide.md)**: Complete usage instructions
- **[Arena Tutorial](docs/arena-tutorial.md)**: Arena basics for new users
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions
- **[References](docs/references.md)**: Academic papers and resources

## Key Concepts

### Monte Carlo Simulation
The model uses Monte Carlo methods to generate thousands of possible intraday scenarios, capturing the stochastic nature of payment flows.

### Risk Metrics
- **Value at Risk (VaR)**: Maximum expected loss at a given confidence level
- **Expected Shortfall (ES/CVaR)**: Average loss beyond VaR threshold
- **Shortfall Probability**: Likelihood of liquidity deficit
- **Time in Deficit**: Duration of liquidity shortages

### Payment Process
- **Arrival Process**: Poisson process with time-varying rates
- **Amount Distribution**: Log-normal distribution
- **Payment Types**: Incoming and outgoing payments
- **Priority Levels**: High-priority vs. regular payments

## Use Cases

1. **Regulatory Compliance**: Meet Basel III intraday liquidity monitoring requirements
2. **Risk Management**: Quantify and manage intraday liquidity risk
3. **Stress Testing**: Evaluate resilience under crisis scenarios
4. **Buffer Optimization**: Determine optimal liquidity buffer sizes
5. **Operational Planning**: Plan for peak payment periods

## Contributing

Contributions are welcome! Please feel free to:
- Report issues or bugs
- Suggest enhancements
- Submit pull requests
- Share your scenarios and results

## Citation

If you use this project in your research, please cite:

```bibtex
@software{arena_liquidity_risk,
  title = {Arena Liquidity Risk Simulation},
  author = {Arena Liquidity Risk Project},
  year = {2024},
  url = {https://github.com/mkodeih/arena-liquidity-risk}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on academic research in financial risk management and Monte Carlo simulation
- Built for Arena Simulation Software by Rockwell Automation
- Inspired by Basel III liquidity risk frameworks

## Support

For questions, issues, or support:
- Check the [documentation](docs/)
- Review [troubleshooting guide](docs/troubleshooting.md)
- Open an issue on GitHub

## Disclaimer

This simulation framework is for educational and research purposes. It should be used as part of a comprehensive risk management framework and not as the sole basis for liquidity management decisions. Always validate results with historical data and regulatory requirements.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Active Development