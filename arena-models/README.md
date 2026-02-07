# Arena Models

This directory contains comprehensive specifications and build instructions for creating the intraday liquidity risk simulation model in Arena.

## Contents

### 1. Model Specifications (`model-specifications/`)

Detailed technical specifications for each component of the Arena model:

- **[entities.md](model-specifications/entities.md)**: Entity definitions and attributes
- **[variables.md](model-specifications/variables.md)**: Global and local variables
- **[modules.md](model-specifications/modules.md)**: Arena module specifications
- **[processes.md](model-specifications/processes.md)**: Process flow descriptions
- **[resources.md](model-specifications/resources.md)**: Resource definitions

### 2. Build Instructions (`build-instructions/`)

Step-by-step guides to construct the model in Arena:

1. **[01-setup.md](build-instructions/01-setup.md)**: Initial setup and configuration
2. **[02-payment-generation.md](build-instructions/02-payment-generation.md)**: Payment arrival and attribute assignment
3. **[03-liquidity-tracking.md](build-instructions/03-liquidity-tracking.md)**: Liquidity position tracking
4. **[04-monte-carlo.md](build-instructions/04-monte-carlo.md)**: Monte Carlo simulation setup
5. **[05-statistics.md](build-instructions/05-statistics.md)**: Statistics collection and output
6. **[06-validation.md](build-instructions/06-validation.md)**: Model validation and testing

### 3. Screenshots (`screenshots/`)

Visual documentation of the model:
- Model flowchart screenshots
- Module configuration screenshots
- Variable definitions
- Output statistics setup

*Add your screenshots here as you build the model*

## Building the Model

Follow these steps in order:

1. Install Arena Simulation Software (version 16.0 or higher)
2. Read through all model specifications to understand the architecture
3. Follow build instructions sequentially (01 through 06)
4. Validate your model at each step
5. Compare your model with the specifications
6. Test with sample data

## Model Overview

The Arena model simulates:
- **Payment flows**: Incoming and outgoing payments with stochastic arrival times and amounts
- **Liquidity tracking**: Real-time monitoring of liquidity position
- **Risk metrics**: Calculation of VaR, shortfall probability, and other risk measures
- **Monte Carlo**: Multiple replications to capture uncertainty

## Key Model Features

- **Time-varying arrival rates**: Payment intensity changes throughout the trading day
- **Log-normal amount distribution**: Realistic payment size modeling
- **Liquidity constraints**: Credit lines and collateral requirements
- **Priority queuing**: High-priority vs. regular payment handling
- **Stress scenarios**: Shock events and crisis conditions

## Tips for Success

1. **Start simple**: Build basic payment flow first, then add complexity
2. **Test frequently**: Validate each module as you build
3. **Use debugging**: Arena's debugger helps identify issues
4. **Document changes**: Keep notes on any customizations
5. **Backup regularly**: Save versions as you progress

## Getting Help

- Refer to `docs/arena-tutorial.md` for Arena basics
- See `docs/troubleshooting.md` for common issues
- Check Arena's built-in help system (F1 key)
- Review example models in Arena's installation directory

## Version Information

- **Arena Version**: 16.0 or higher required
- **Model Version**: 1.0.0
- **Last Updated**: 2024
