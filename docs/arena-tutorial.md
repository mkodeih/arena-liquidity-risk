# Arena Tutorial: Introduction to Arena Simulation Software

## Table of Contents
1. [What is Arena?](#what-is-arena)
2. [Arena Interface Overview](#arena-interface-overview)
3. [Basic Modeling Concepts](#basic-modeling-concepts)
4. [Building Your First Model](#building-your-first-model)
5. [Common Modules](#common-modules)
6. [Running Simulations](#running-simulations)
7. [Animation and Visualization](#animation-and-visualization)
8. [Data Input/Output](#data-inputoutput)
9. [Tips and Tricks](#tips-and-tricks)

## What is Arena?

Arena is a discrete-event simulation software developed by Rockwell Automation. It allows users to:
- Model complex systems using flowchart-style diagrams
- Simulate system behavior over time
- Analyze performance metrics and optimize processes
- Visualize system dynamics through animation

### Key Features

- **Visual modeling**: Drag-and-drop interface
- **Built-in modules**: Pre-configured building blocks
- **Statistical analysis**: Automatic output analysis
- **Animation**: Dynamic visualization of model execution
- **Flexibility**: Customizable with VBA and expressions

### Applications

Arena is widely used for:
- Manufacturing process optimization
- Service system design (healthcare, banking, call centers)
- Supply chain management
- **Financial systems** (payment systems, liquidity management)

## Arena Interface Overview

### Main Windows

1. **Model Window** (Flowchart View)
   - Where you build your model
   - Drag modules from panels
   - Connect modules with flowlines

2. **Project Bar**
   - Basic Process panel (most common modules)
   - Advanced Process panel
   - Blocks panel (lower-level constructs)

3. **Spreadsheet View**
   - Access via toolbar or double-clicking modules
   - Edit module parameters in table format
   - Useful for batch editing

4. **Arena Variables Window**
   - View and edit variables, attributes, entities
   - Define global parameters

### Toolbar

Key toolbar buttons:
- **Run** (▶): Start simulation
- **Pause** (⏸): Pause during run
- **End** (⏹): Stop simulation
- **Run Setup**: Configure replication parameters
- **Check Model**: Verify model for errors

## Basic Modeling Concepts

### Entities

**Entities** are objects that flow through the system.

Examples:
- In manufacturing: Parts, products
- In services: Customers, documents
- **In payment systems: Payment transactions**

### Attributes

**Attributes** are characteristics of entities.

Examples:
- Payment amount
- Priority level
- Arrival time
- Source/destination institution

### Resources

**Resources** are constrained assets that process entities.

Examples:
- Machines, workers
- Service counters
- **Payment processing channels**

### Variables

**Variables** store global information.

Types:
- **System variables**: Automatically updated (e.g., TNOW = current time)
- **User variables**: Custom-defined values

### Events

**Events** are occurrences that change system state.

Examples:
- Entity arrival
- Resource seizes/releases
- Variable updates

## Building Your First Model

### Simple Queue Model

Let's build a basic queueing system:

**Step 1: Add Create Module**

1. From Basic Process panel, drag **Create** to model window
2. Double-click to configure:
   - Name: "Payment Arrivals"
   - Entity Type: Payment
   - Type: Random (Exponential)
   - Value: 5 (mean interarrival time)
   - Entities per Arrival: 1

**Step 2: Add Process Module**

1. Drag **Process** module
2. Configure:
   - Name: "Settlement Process"
   - Action: Seize Delay Release
   - Resources: Add "Processor" with quantity 1
   - Delay Type: Constant or Expression
   - Value: 3 (processing time)

**Step 3: Add Dispose Module**

1. Drag **Dispose** module
2. Configure:
   - Name: "Completed Payments"

**Step 4: Connect Modules**

1. Click Connect button (or Ctrl+K)
2. Click first module, then second
3. Repeat for all connections:
   - Create → Process → Dispose

**Step 5: Set Run Parameters**

1. Run → Setup → Replication Parameters
2. Set:
   - Replication Length: 100 (time units)
   - Number of Replications: 10

**Step 6: Run Model**

1. Click Run button (▶)
2. Watch animation
3. View results when complete

### Understanding Results

After running:
1. Check **Category Overview**:
   - Entity: Time in system, waiting time
   - Resource: Utilization, queues
2. Review **Entity > Time** for cycle time statistics
3. Examine **Resource > Usage** for utilization

## Common Modules

### Basic Process Panel

#### Create
**Purpose**: Generate entities entering system

**Key Parameters**:
- Entity Type: What kind of entity
- Time Between Arrivals: Distribution (Exponential, Constant, etc.)
- Entities per Arrival: Batch size
- Max Arrivals: Limit (or Infinite)
- First Creation: Start time

**Example**:
```
Name: Payment Arrivals
Type: Random (Exponential)
Value: EXPO(5)  # Mean = 5 minutes
```

#### Dispose
**Purpose**: Remove entities from system

**Key Parameters**:
- Record Entity Statistics: Yes/No

**Usage**: Place at end of process flow

#### Process
**Purpose**: Main processing activity

**Action Types**:
1. **Delay**: Hold entity for time period
2. **Seize Delay Release**: Capture resource, delay, free resource
3. **Seize Delay**: Capture resource and delay (release elsewhere)
4. **Delay Release**: Delay then free resource

**Key Parameters**:
- Resources: Which resources to use
- Delay Type: Constant, Expression, Distribution
- Units: Time units

#### Decide
**Purpose**: Branch logic based on conditions

**Types**:
1. **2-way by Condition**: If-then-else
2. **2-way by Chance**: Probabilistic split
3. **N-way by Condition**: Multiple conditions

**Examples**:
```
# Condition
If: Payment Amount > 1000000
Then: High Priority Branch
Else: Normal Branch

# Chance
60% → Branch 1
40% → Branch 2
```

#### Assign
**Purpose**: Set attribute or variable values

**Assignments**:
- Variable: Global value
- Attribute: Entity-specific value
- Entity Type: Change entity type

**Example**:
```
Assign: Payment.Priority = "HIGH"
Assign: Total_Volume = Total_Volume + Payment.Amount
```

#### Batch
**Purpose**: Combine multiple entities

**Types**:
- Permanent: Entities merged permanently
- Temporary: Can be separated later

**Usage**: Aggregate payments for batch processing

#### Separate
**Purpose**: Split or duplicate entities

**Types**:
- Duplicate Original: Make copies
- Split Existing Batch: Undo batch operation

### Advanced Process Panel

#### Hold
**Purpose**: Wait for condition or signal

**Types**:
- Wait for Signal
- Wait for Condition
- Scan for Condition
- Infinite Hold

#### Release
**Purpose**: Free resources seized elsewhere

**Usage**: Paired with Seize or Process (Seize Delay type)

#### Seize
**Purpose**: Capture resources without delay

**Usage**: When delay occurs in separate module

#### Station
**Purpose**: Define locations in model

**Usage**: For entity routing and animation

#### Route
**Purpose**: Send entity to station

**Options**:
- By Time: Delay before arrival
- By Sequence: Follow route sequence

## Running Simulations

### Run Setup

**Run → Setup → Replication Parameters**

Configure:
1. **Number of Replications**: How many runs
   - Minimum: 30 for statistical validity
   - More replications = better estimates

2. **Replication Length**: Simulation duration
   - Use time units (minutes, hours, days)
   - Match real-world period

3. **Warm-up Period**: Steady-state time
   - Statistics not collected during warm-up
   - Allow system to reach equilibrium

4. **Base Time Units**: Default time unit
   - Minutes (common choice)
   - Hours, seconds, days

5. **Hours Per Day**: For calendar conversion
   - Default: 24

### Run Control

**Interactive Run** (with animation):
- Click Run (▶) or press F5
- Watch animation in real-time
- Pause, step, or end as needed
- Useful for debugging

**Batch Run** (no animation):
- Faster execution
- Multiple replications
- Run → Batch Run or Ctrl+F5
- Use for large experiments

### Checking Model

Before running:
1. **Run → Check Model** or F4
2. Review any errors or warnings
3. Fix issues before proceeding

Common errors:
- Unconnected modules
- Missing resources
- Invalid expressions
- Circular logic

## Animation and Visualization

### Adding Animation

#### Resource Pictures

1. Click **Resource** button in toolbar
2. Place in model window
3. Right-click → Picture Placement → Edit
4. Configure:
   - Resource: Which resource to display
   - Idle Picture: When not busy
   - Busy Picture: When processing

#### Variables

Display variable values:
1. Click **Variable** button
2. Place in model window
3. Double-click to configure:
   - Expression: Variable name or formula

#### Plots

Real-time charts:
1. Click **Plot** button
2. Configure:
   - Type: Time series, histogram, etc.
   - Expression: What to plot

#### Queues

Visualize waiting lines:
1. Click **Queue** button
2. Place and configure
3. Entities animate in queue

### Animation Tips

- **Strategic placement**: Put animation elements where visible
- **Color coding**: Use colors for status (red = busy, green = idle)
- **Labels**: Add text to explain animation elements
- **Scaling**: Adjust speed for visibility (Run → Run Control → Animation Speed)

## Data Input/Output

### Reading Data from Files

**ReadWrite Module** (Advanced Transfer panel):

1. Drag ReadWrite to model
2. Configure:
   - Type: Read
   - File Name: Path to file
   - Recordset: Define columns
   - Assignments: Map to variables/attributes

**Example**:
```
File: payments.txt
Format: Column delimited (CSV)
Columns: PaymentID, Amount, Priority
Assign to: Payment.ID, Payment.Amount, Payment.Priority
```

### Writing Data to Files

**ReadWrite Module**:

1. Configure:
   - Type: Write
   - File Name: Output path
   - Format: Define output columns
   - Expressions: What to write

**Example**:
```
File: results.csv
Write: TNOW, Entity.ID, Entity.WaitTime
```

### Excel Integration

**Using VBA**:
1. Tools → Visual Basic Editor
2. Write VBA code to read/write Excel
3. Call from Arena modules

**ActiveX Data Objects (ADO)**:
- More robust than VBA
- Configure in ReadWrite module
- Connection string to Excel file

## Tips and Tricks

### Modeling Best Practices

1. **Start simple**: Build basic model, then add complexity
2. **Test incrementally**: Run after each addition
3. **Use submodels**: Organize complex models
4. **Comment liberally**: Use module names and labels
5. **Version control**: Save versions before major changes

### Performance Optimization

1. **Minimize animation**: Slow down execution
2. **Use expressions wisely**: Complex formulas impact speed
3. **Limit statistics**: Only collect needed data
4. **Batch operations**: Process groups when possible

### Debugging

Common issues and solutions:

**Problem**: Entities stuck in queue
- **Solution**: Check resource availability, seize/release balance

**Problem**: Unexpected results
- **Solution**: Add Assign modules to track attributes, use debugger

**Problem**: Model runs very slowly
- **Solution**: Reduce animation, simplify expressions

**Problem**: Statistics don't make sense
- **Solution**: Check warm-up period, verify all modules

### Keyboard Shortcuts

- **F4**: Check model
- **F5**: Run simulation
- **F7**: Arena help
- **Ctrl+K**: Connect modules
- **Ctrl+D**: Duplicate selection
- **Ctrl+G**: Group objects
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo

### Useful Expressions

**Random distributions**:
- `EXPO(mean)`: Exponential
- `NORM(mean, stddev)`: Normal
- `UNIF(min, max)`: Uniform
- `TRIA(min, mode, max)`: Triangular
- `WEIB(beta, alpha)`: Weibull

**System variables**:
- `TNOW`: Current simulation time
- `TFIN`: Replication end time
- `NR(Resource)`: Number of busy units
- `NQ(Queue)`: Current queue length

**Logical operators**:
- `&&`: AND
- `||`: OR
- `!`: NOT
- `==`: Equals
- `!=`: Not equals

## Next Steps

### Learning More

1. **Arena Help**: Press F7 for comprehensive documentation
2. **Sample models**: Explore Arena's example files
3. **Textbooks**: "Simulation with Arena" by Kelton et al.
4. **Online tutorials**: Rockwell Automation website

### Applying to Liquidity Risk

1. Review project models in `arena-models/`
2. Study `liquidity_risk_baseline.doe` structure
3. Examine payment entity flow
4. Understand resource constraints (liquidity, credit)
5. Analyze risk metric collection

### Further Resources

- [user-guide.md](user-guide.md): Project-specific usage
- [methodology.md](methodology.md): Mathematical foundations
- Arena User's Guide: Detailed reference
- Arena Help system: Context-sensitive help
