# Examples Directory

This directory contains practical examples demonstrating how to use the Arena liquidity risk simulation models.

## Contents

### Example Scenarios

1. **[basic_scenario.md](basic_scenario.md)** - Simple baseline simulation
   - Getting started tutorial
   - Normal market conditions
   - Standard parameter settings
   - Result interpretation

2. **[stress_test_scenario.md](stress_test_scenario.md)** - Stress testing example
   - Adverse market conditions
   - Multiple stress factors
   - Risk metric analysis
   - Regulatory compliance checks

3. **[custom_scenario.md](custom_scenario.md)** - Creating custom scenarios
   - Template for new scenarios
   - Parameter customization guide
   - Advanced configuration options
   - Best practices

## Using These Examples

### Quick Start

1. Read [basic_scenario.md](basic_scenario.md) first
2. Follow step-by-step instructions
3. Run the example in Arena
4. Review results and compare with expected outcomes

### Learning Path

**Beginner**:
- Start with basic_scenario.md
- Understand fundamental concepts
- Get comfortable with Arena interface

**Intermediate**:
- Try stress_test_scenario.md
- Learn about risk scenarios
- Analyze different market conditions

**Advanced**:
- Use custom_scenario.md as template
- Create your own scenarios
- Combine multiple stress factors
- Optimize parameters

## Example Data

Each example includes:
- **Input data**: Sample configuration files
- **Expected output**: Reference results
- **Parameter settings**: Complete configuration
- **Analysis notes**: Interpretation guidance

## File Locations

Example data files are stored in:
```
data/
├── sample-data/
│   └── example_payments.csv         # Sample payment data
├── input-templates/
│   ├── institution_config.xlsx      # Institution setup
│   ├── payment_parameters.xlsx      # Payment configuration
│   └── market_conditions.xlsx       # Market scenarios
└── output-templates/
    ├── simulation_results.xlsx      # Expected output format
    └── risk_metrics.xlsx            # Risk metric format
```

## Running Examples

### Using Arena

1. Open Arena model from `arena-models/`
2. Load example input data
3. Configure per example instructions
4. Run simulation
5. Compare results with example output

### Using Python Scripts

```bash
# Prepare example data
python scripts/data_preparation.py \
  --input data/sample-data \
  --output data/processed

# Run analysis (after Arena simulation)
python scripts/results_analyzer.py \
  --results data/output-templates/simulation_results.xlsx \
  --metrics data/output-templates/risk_metrics.xlsx \
  --output reports/example_analysis

# Create visualizations
python scripts/visualization.py \
  --input data/output-templates \
  --output figures/examples \
  --format png
```

## Modifying Examples

### To Customize an Example

1. Copy the example markdown file
2. Modify parameters as needed
3. Update input data files
4. Document your changes
5. Run and validate results

### Parameter Guidelines

**Safe to modify**:
- Payment amounts (within realistic ranges)
- Arrival rates (adjust for system capacity)
- Reserve levels (maintain regulatory minimums)
- Replication counts (more is better)

**Modify with caution**:
- Market volatility (affects stability)
- Credit limits (impacts gridlock risk)
- Collateral haircuts (regulatory constraints)
- System capacity (may cause bottlenecks)

## Expected Results

### Basic Scenario
- Settlement rate: > 98%
- Average settlement time: 2-3 minutes
- LCR: > 1.2 (well-capitalized)
- Gridlock events: 0
- Queue length: < 10 payments

### Stress Test Scenario
- Settlement rate: 85-95% (degraded)
- Average settlement time: 5-10 minutes
- LCR: 1.0-1.1 (meets minimum)
- Gridlock events: 1-3 possible
- Queue length: < 50 payments

## Common Issues

### Results Don't Match Examples

**Possible causes**:
1. Different random seed (normal variation)
2. Arena version differences
3. Modified input parameters
4. Incorrect model configuration

**Solutions**:
- Check parameter settings carefully
- Verify input data matches example
- Run multiple replications (≥30)
- Compare statistical ranges, not point estimates

### Can't Reproduce Results

**Troubleshooting**:
1. Verify Arena model version
2. Check all input files loaded correctly
3. Confirm replication parameters
4. Use same random seed if exact reproduction needed

See [troubleshooting.md](../docs/troubleshooting.md) for more help.

## Contributing Examples

To contribute a new example:

1. Create comprehensive markdown documentation
2. Provide all input data files
3. Include expected output (sample results)
4. Document parameter rationale
5. Test thoroughly before submitting
6. Follow existing example format

### Example Template Structure

```markdown
# Example: [Name]

## Objective
[What this example demonstrates]

## Prerequisites
[Required knowledge/setup]

## Configuration
[Parameter settings]

## Step-by-Step Instructions
[Detailed procedure]

## Expected Results
[What you should see]

## Analysis
[How to interpret results]

## Extensions
[Ideas for further exploration]
```

## Related Documentation

- **Model Documentation**: `../arena-models/README.md`
- **User Guide**: `../docs/user-guide.md`
- **Methodology**: `../docs/methodology.md`
- **Troubleshooting**: `../docs/troubleshooting.md`

## Support

For questions about examples:
1. Check example documentation carefully
2. Review user guide
3. Consult troubleshooting guide
4. Refer to Arena tutorial
5. Contact project maintainers

## License

Examples are provided under the same license as the main project. See `../LICENSE` for details.
