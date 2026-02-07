# Troubleshooting Guide

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Arena Model Problems](#arena-model-problems)
3. [Data Import/Export Issues](#data-importexport-issues)
4. [Simulation Runtime Errors](#simulation-runtime-errors)
5. [Python Script Issues](#python-script-issues)
6. [Performance Problems](#performance-problems)
7. [Results Analysis Issues](#results-analysis-issues)
8. [Common Error Messages](#common-error-messages)

## Installation Issues

### Arena Won't Install

**Problem**: Installation fails or hangs

**Solutions**:
1. Run installer as administrator
2. Disable antivirus temporarily
3. Check system requirements (Windows OS, sufficient RAM)
4. Install .NET Framework 4.5 or later
5. Try compatibility mode (Windows 7/8)

### License Activation Fails

**Problem**: Cannot activate Arena license

**Solutions**:
1. Verify license key is correct
2. Check internet connection
3. Contact Rockwell Automation support
4. For student version, verify academic email
5. Try offline activation if available

### Python Installation Issues

**Problem**: pip install fails

**Solutions**:
```bash
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt --verbose

# If SSL errors
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Install packages individually if batch fails
pip install pandas numpy matplotlib seaborn scipy openpyxl
```

## Arena Model Problems

### Model Won't Open

**Problem**: Double-clicking .doe file doesn't open model

**Solutions**:
1. Open Arena first, then File → Open
2. Check file association (should be Arena)
3. Verify file isn't corrupted (check file size)
4. Try opening a backup copy
5. Check Arena version compatibility

### "Module Not Found" Error

**Problem**: Arena reports missing modules

**Solutions**:
1. Check which panels are loaded: Tools → Template Panel → Panel Attachments
2. Attach required panels (Basic Process, Advanced Process)
3. If custom templates used, ensure template files exist
4. Reset to default template panel if necessary

### Model Runs But No Entities Flow

**Problem**: Simulation starts but nothing happens

**Checklist**:
1. **Create module**: Check "Max Arrivals" isn't 0
2. **Connections**: Verify all modules connected with flowlines
3. **Resources**: Check resources exist and have capacity > 0
4. **Seize/Release**: Ensure balanced (every seize has release)
5. **Conditions**: Check Decide modules for blocking conditions
6. **Variables**: Verify variables initialized correctly

**Debug steps**:
```
1. Add Assign modules to track: TNOW, Entity count
2. Use Run → Run Control → Step (F10) to step through
3. Check Entity > Current for entities in system
4. Review Process > Queue for blocked entities
```

### Entities Get Stuck

**Problem**: Entities accumulate in queues indefinitely

**Common causes**:
1. **Resource shortage**: Not enough capacity
   - Solution: Increase resource capacity or reduce arrival rate

2. **Deadlock**: Circular waiting
   - Solution: Check resource allocation order

3. **Unbalanced seize/release**: Resources never freed
   - Solution: Match every Seize with Release

4. **Condition never met**: Hold or Decide blocks forever
   - Solution: Review condition logic

**Debugging**:
```
# Add to model:
- Assign: EntityType.Count = EntityType.Count + 1
- Variable animation showing queue lengths
- Breakpoint using Hold module

# Check during run:
- Current queue statistics (Window → Current Statistics)
- Resource utilization (should be < 100% in steady state)
```

### "Can't Resolve Variable" Error

**Problem**: Arena doesn't recognize variable name

**Solutions**:
1. Check spelling and capitalization (case-sensitive)
2. Define variable if not created:
   - Tools → Variables → Arrays/Variables
   - Add new row with variable name
3. For attributes: Use Entity.AttributeName format
4. For arrays: Use ArrayName(Index) format
5. Check for special characters (use underscore, not space)

## Data Import/Export Issues

### ReadWrite Module Can't Find File

**Problem**: "File not found" error

**Solutions**:
1. Use absolute path: `C:\Users\Name\Documents\data.csv`
2. Place file in Arena model directory
3. Check file extension matches (case-sensitive on some systems)
4. Verify file isn't open in Excel (lock issue)
5. Check permissions (read/write access)

**Testing**:
```
# In VBA or expression:
MsgBox("Looking for: " & [File Path])
# Verify path is what you expect
```

### Data Not Importing Correctly

**Problem**: Data loads but values are wrong

**Checklist**:
1. **File format**: CSV vs. Tab-delimited vs. Fixed-width
2. **Delimiter**: Comma, tab, semicolon, space
3. **Headers**: First row headers or data?
4. **Data types**: Text vs. numeric
5. **Decimal separator**: Period vs. comma (regional settings)

**Solution steps**:
```
1. Open file in text editor to verify format
2. Check ReadWrite recordset definition
3. Test with simple file (1-2 rows)
4. Add Assign module after read to display values
5. Use VBA debugger to inspect imported values
```

### Excel File Won't Open

**Problem**: Cannot read .xlsx files

**Solutions**:
1. Install Microsoft Access Database Engine
2. Use CSV format instead of Excel
3. Check 32-bit vs 64-bit compatibility
4. Verify Excel not corrupted (open in Excel first)
5. Try saving as Excel 97-2003 (.xls)

### Output File Not Created

**Problem**: Results not written to file

**Solutions**:
1. Check write permissions for target directory
2. Verify file path in ReadWrite module
3. Ensure WriteFile module executed during run
4. Close target file if open in Excel
5. Check disk space available

## Simulation Runtime Errors

### "Simulation Stopped" Unexpectedly

**Problem**: Simulation terminates before replication end

**Common causes**:
1. **Division by zero**: Check all expressions
2. **Array out of bounds**: Verify array indices
3. **Negative time**: Check delay expressions
4. **Resource error**: Invalid resource reference
5. **VBA error**: If custom code used

**Debugging**:
```
# Enable error checking:
Run → Run Control → Command → Break on Error

# Add error handling in VBA:
On Error Resume Next
[Your code]
If Err.Number <> 0 Then
    MsgBox "Error: " & Err.Description
End If
```

### Very Large or Very Small Numbers

**Problem**: Statistics show infinity, -infinity, or NaN

**Causes**:
1. Division by zero
2. Log of negative number
3. Square root of negative number
4. Overflow (number too large)

**Solutions**:
1. Add validation: `IF(Denominator>0, Numerator/Denominator, 0)`
2. Use MAX/MIN functions: `MAX(Value, 0)`
3. Check expressions in Assign and Decide modules
4. Review formulas in Variable definitions

### Replication Takes Forever

**Problem**: Single replication runs much longer than expected

**Possible issues**:
1. **Infinite loop**: Logic error causing endless cycling
2. **Too many entities**: Create module overwhelming system
3. **Animation speed**: Run too slow for observation
4. **Deadlock**: All entities blocked

**Solutions**:
1. Set replication length limit
2. Add max arrivals limit in Create
3. Turn off animation: Run → Run Control → Animation → Off
4. Add Dispose modules to remove excess entities

## Python Script Issues

### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solutions**:
```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install missing package
pip install [package-name]

# Verify installation
pip list | grep [package-name]

# Check Python version
python --version  # Should be 3.8+
```

### File Not Found in Scripts

**Problem**: Scripts can't find input files

**Solutions**:
```bash
# Check current directory
pwd  # Linux/Mac
cd   # Windows

# Run from project root
cd arena-liquidity-risk

# Use absolute paths in arguments
python scripts/data_preparation.py --input /full/path/to/data

# Or specify paths relatively
python scripts/data_preparation.py --input ./data/input-templates
```

### Pandas/Excel Read Errors

**Problem**: `Error tokenizing data` or `BadZipFile`

**Solutions**:
```python
# For CSV with comments
df = pd.read_csv('file.csv', comment='#')

# For Excel without openpyxl
pip install openpyxl
df = pd.read_excel('file.xlsx', engine='openpyxl')

# For encoding issues
df = pd.read_csv('file.csv', encoding='utf-8')
# or
df = pd.read_csv('file.csv', encoding='latin-1')

# For delimiter issues
df = pd.read_csv('file.csv', sep=',')  # or '\t' for tab
```

### Visualization Errors

**Problem**: Matplotlib/Seaborn plots don't display

**Solutions**:
```python
# Ensure matplotlib backend set
import matplotlib
matplotlib.use('Agg')  # For saving without display

# Or for display
import matplotlib.pyplot as plt
plt.ion()  # Interactive mode

# Save figures instead of show
plt.savefig('output.png')
plt.close()

# Check if running headless
# Use Agg backend for servers without display
```

## Performance Problems

### Slow Simulation

**Problem**: Model runs very slowly

**Optimization strategies**:

1. **Disable animation**:
   ```
   Run → Run Control → Animation → Off
   Or Ctrl + Shift + A
   ```

2. **Reduce entities**:
   - Lower arrival rates
   - Add entity disposal points
   - Use batching for bulk processing

3. **Simplify expressions**:
   - Avoid complex formulas in tight loops
   - Pre-calculate values in variables
   - Use lookup tables instead of calculations

4. **Limit statistics collection**:
   - Disable unnecessary tallies
   - Reduce output frequency
   - Turn off detailed statistics

5. **Use batch run mode**:
   ```
   Run → Batch Run (Ctrl+F5)
   Much faster than interactive
   ```

### Memory Issues

**Problem**: "Out of memory" errors

**Solutions**:
1. Reduce number of entities in system
2. Clear entity pictures (use simple shapes)
3. Limit animation objects
4. Close other applications
5. Increase virtual memory (Windows)
6. Run smaller replication batches

### Python Scripts Slow

**Problem**: Analysis scripts take too long

**Optimization**:
```python
# Use vectorized operations
df['new_col'] = df['col1'] + df['col2']  # Fast
# Not: df['new_col'] = df.apply(lambda x: x['col1'] + x['col2'], axis=1)  # Slow

# Read only needed columns
df = pd.read_csv('file.csv', usecols=['col1', 'col2'])

# Use chunks for large files
for chunk in pd.read_csv('file.csv', chunksize=10000):
    process(chunk)

# Filter early
df = df[df['Scenario'] == 'BASELINE']  # Do this first
```

## Results Analysis Issues

### Statistics Don't Make Sense

**Problem**: Results are illogical or unexpected

**Verification steps**:

1. **Check warm-up period**:
   - Statistics shouldn't include transient behavior
   - Set appropriate warm-up time

2. **Verify replication length**:
   - Long enough to reach steady state?
   - Covers full cycle of behavior?

3. **Inspect individual replications**:
   - Look for outliers
   - Check variability across runs

4. **Review model logic**:
   - Step through one entity manually
   - Verify formulas and conditions

### Confidence Intervals Too Wide

**Problem**: High variability in results

**Solutions**:
1. Increase number of replications (30+ minimum)
2. Use variance reduction techniques:
   - Common random numbers
   - Antithetic variates
3. Check for model bugs causing variability
4. Ensure warm-up period is adequate
5. Consider longer replication length

### Missing Output Data

**Problem**: Expected statistics not in output

**Solutions**:
1. **Enable statistics collection**:
   - Tally modules for custom statistics
   - ReadWrite for file output
   - Output analyzer configuration

2. **Check output file**:
   - Verify file was created
   - Check write permissions
   - Look in Arena default output location

3. **Review statistic definitions**:
   - Ensure expression is valid
   - Check recording condition

## Common Error Messages

### "Resource Not Available"

**Meaning**: Trying to release resource not seized

**Fix**: 
- Check seize/release pairs match
- Verify resource name spelling
- Ensure entity seized resource before releasing

### "Expression Error"

**Meaning**: Invalid expression syntax

**Common issues**:
- Missing parentheses
- Undefined variable
- Wrong function name
- Type mismatch

**Example fixes**:
```
# Wrong
Average Payment Amount  # Spaces in name

# Right
Average_Payment_Amount

# Wrong
IF Payment.Amount > 1000000 THEN Priority = HIGH

# Right
IF(Payment.Amount > 1000000, "HIGH", "NORMAL")
```

### "Queue Not Found"

**Meaning**: Referencing non-existent queue

**Fix**:
- Create queue in Resources module
- Check spelling of queue name
- Verify queue associated with correct process

### "Index Out of Bounds"

**Meaning**: Array index invalid

**Fix**:
```
# Define array size correctly
MyArray(1 to 100)  # Not (0 to 99) if using 1-based indexing

# Check index before use
IF(Index >= 1 && Index <= 100, MyArray(Index), 0)
```

### "Type Mismatch"

**Meaning**: Wrong data type for operation

**Examples**:
```
# Wrong
"100" + 50  # String + number

# Right
100 + 50    # Number + number

# Wrong
IF(Payment.Type = HIGH, ...)  # HIGH not quoted

# Right
IF(Payment.Type == "HIGH", ...)
```

## Getting Help

### Resources

1. **Arena Help**: Press F7 in Arena
2. **Arena User's Guide**: Comprehensive reference
3. **Rockwell Automation**: Support forum and knowledge base
4. **Project documentation**: See `docs/` directory
5. **Arena examples**: Included with Arena installation

### Reporting Issues

When seeking help, provide:
1. Arena version number
2. Error message (exact text)
3. Steps to reproduce
4. Model file (if possible)
5. Screenshot of error
6. What you've already tried

### Debug Checklist

Before asking for help:
- [ ] Checked this troubleshooting guide
- [ ] Ran Check Model (F4)
- [ ] Reviewed error messages carefully
- [ ] Tested with simpler input
- [ ] Verified file paths and formats
- [ ] Checked for typos in variable names
- [ ] Consulted Arena help (F7)
- [ ] Tried on different computer (if hardware issue suspected)

## Prevention Tips

### Best Practices

1. **Save often**: Use Save As for versions
2. **Test incrementally**: Build and test in small steps
3. **Document changes**: Comment why you did something
4. **Backup regularly**: Keep multiple versions
5. **Validate inputs**: Check data before import
6. **Start simple**: Begin with minimal model
7. **Use version control**: Track changes systematically

### Model Development Checklist

- [ ] Model checked for errors (F4)
- [ ] Test run completed successfully
- [ ] Results look reasonable
- [ ] All modules properly connected
- [ ] Resources defined and balanced
- [ ] Variables initialized
- [ ] Input data validated
- [ ] Output collection configured
- [ ] Animation working (if used)
- [ ] Documentation updated
