# Test Scenarios for Arena Liquidity Risk Simulation

## Overview

This document defines test scenarios for validating the Arena liquidity risk simulation model. Each scenario tests specific aspects of model behavior under controlled conditions.

## Test Scenario Index

1. [Baseline Functionality Tests](#1-baseline-functionality-tests)
2. [Boundary Condition Tests](#2-boundary-condition-tests)
3. [Stress Condition Tests](#3-stress-condition-tests)
4. [Logic Verification Tests](#4-logic-verification-tests)
5. [Performance Tests](#5-performance-tests)
6. [Integration Tests](#6-integration-tests)
7. [Regression Tests](#7-regression-tests)

---

## 1. Baseline Functionality Tests

### Test 1.1: Single Payment Processing

**Objective**: Verify basic payment settlement

**Setup**:
- 1 institution
- 1 payment of 100,000
- Adequate reserves (10,000,000)
- No queues

**Procedure**:
1. Create single payment at t=0
2. Run simulation for 10 minutes
3. Check payment settled

**Expected Results**:
- Payment settles within 1-2 minutes
- No queue formation
- Reserve decreases by 100,000
- LCR > 1.0

**Pass Criteria**: ☐ Payment settled successfully

---

### Test 1.2: Multiple Sequential Payments

**Objective**: Verify queue management

**Setup**:
- 1 institution
- 10 payments arriving sequentially (1 per minute)
- Each payment: 50,000
- Initial reserves: 5,000,000

**Procedure**:
1. Release payments 1 per minute
2. Run simulation for 20 minutes
3. Monitor queue and settlement

**Expected Results**:
- All payments settle
- Queue length ≤ 2 at any time
- FIFO order maintained
- No gridlock

**Pass Criteria**: ☐ All 10 payments settled in order

---

### Test 1.3: Priority Queue Handling

**Objective**: Verify priority processing

**Setup**:
- 1 institution
- 5 LOW priority payments (100,000 each)
- 3 HIGH priority payments (100,000 each)
- HIGH payments arrive after LOW payments in queue
- Processing capacity: 1 payment per minute

**Procedure**:
1. Queue 5 LOW priority payments
2. Add 3 HIGH priority payments
3. Observe processing order

**Expected Results**:
- HIGH priority payments processed first
- LOW priority payments wait
- Correct priority ordering

**Pass Criteria**: ☐ All HIGH payments settle before LOW payments

---

## 2. Boundary Condition Tests

### Test 2.1: Zero Liquidity

**Objective**: Test behavior with no reserves

**Setup**:
- 1 institution
- Initial reserves: 0
- 1 payment: 100,000
- Credit limit: 0

**Procedure**:
1. Attempt to process payment
2. Observe system response

**Expected Results**:
- Payment queued (not rejected immediately)
- Waits for liquidity source
- Eventually rejected or requires facility

**Pass Criteria**: ☐ System handles gracefully, no crash

---

### Test 2.2: Maximum Capacity

**Objective**: Test at system limits

**Setup**:
- 5 institutions
- Payment arrival rate: 500/hour (very high)
- Limited processing capacity
- Standard reserves

**Procedure**:
1. Run high-volume scenario
2. Monitor queue growth
3. Check for system saturation

**Expected Results**:
- Queues grow but stabilize
- Settlement rate decreases but system functional
- No infinite queue growth

**Pass Criteria**: ☐ System remains stable, queues bounded

---

### Test 2.3: Single Large Payment

**Objective**: Test with payment >> reserves

**Setup**:
- 1 institution
- Reserves: 1,000,000
- Single payment: 50,000,000
- Credit available: 10,000,000

**Procedure**:
1. Submit large payment
2. Observe handling

**Expected Results**:
- Payment queued
- Credit utilized
- Facility drawn if needed
- Or rejected if insufficient total liquidity

**Pass Criteria**: ☐ Appropriate handling (credit/facility or reject)

---

## 3. Stress Condition Tests

### Test 3.1: Liquidity Shock

**Objective**: Test sudden reserve depletion

**Setup**:
- Start with adequate reserves (20M)
- At t=60, reserves drop to 5M (75% shock)
- Payment flow continues

**Procedure**:
1. Run baseline for 1 hour
2. Apply reserve shock
3. Continue for 4 hours
4. Monitor system response

**Expected Results**:
- LCR drops below 1.0
- Queue lengths increase
- Settlement times increase
- Central bank facility activated

**Pass Criteria**: ☐ System survives shock, uses facility

---

### Test 3.2: Payment Surge

**Objective**: Test sudden volume increase

**Setup**:
- Normal arrival rate (125/hr)
- At t=120, rate jumps to 300/hr
- Standard reserves

**Procedure**:
1. Run normal conditions
2. Trigger surge
3. Monitor throughput and queues

**Expected Results**:
- Queue lengths spike
- Settlement time increases
- Some payments may be rejected
- System eventually processes backlog

**Pass Criteria**: ☐ System handles surge, no crash

---

### Test 3.3: Gridlock Scenario

**Objective**: Test circular payment dependency

**Setup**:
- 3 institutions: A, B, C
- A owes 5M to B (waiting for liquidity)
- B owes 4M to C (waiting for payment from A)
- C owes 3M to A (waiting for payment from B)
- Each institution has minimal reserves

**Procedure**:
1. Create circular dependency
2. Observe gridlock detection
3. Check resolution mechanism

**Expected Results**:
- Gridlock detected
- Resolution triggered (facility, optimization, or timeout)
- Payments eventually settle

**Pass Criteria**: ☐ Gridlock detected and resolved

---

## 4. Logic Verification Tests

### Test 4.1: LCR Calculation

**Objective**: Verify LCR formula implementation

**Setup**:
- HQLA (High Quality Liquid Assets): 10,000,000
- Expected outflows (30 days): 8,000,000
- Expected inflows (30 days): 2,000,000
- Net outflows: 8,000,000 - min(2,000,000, 0.75*8,000,000) = 6,000,000

**Procedure**:
1. Configure institution with above values
2. Run simulation
3. Check calculated LCR

**Expected Results**:
- LCR = 10,000,000 / 6,000,000 = 1.67

**Pass Criteria**: ☐ LCR = 1.67 ± 0.01

---

### Test 4.2: NSFR Calculation

**Objective**: Verify NSFR formula implementation

**Setup**:
- Available Stable Funding (ASF): 90,000,000
- Required Stable Funding (RSF): 75,000,000

**Procedure**:
1. Configure institution
2. Run simulation
3. Check calculated NSFR

**Expected Results**:
- NSFR = 90,000,000 / 75,000,000 = 1.20

**Pass Criteria**: ☐ NSFR = 1.20 ± 0.01

---

### Test 4.3: Credit Limit Enforcement

**Objective**: Verify credit limits respected

**Setup**:
- Institution A credit limit: 5,000,000
- Attempt to use 6,000,000 in credit

**Procedure**:
1. Create payments requiring 6M credit
2. Monitor credit usage

**Expected Results**:
- Credit usage caps at 5,000,000
- Additional amounts require facility or queued

**Pass Criteria**: ☐ Credit never exceeds 5,000,000

---

### Test 4.4: Collateral Haircut Application

**Objective**: Verify haircut calculation

**Setup**:
- Collateral market value: 10,000,000
- Haircut: 20% (0.20)

**Procedure**:
1. Post collateral
2. Check borrowing capacity

**Expected Results**:
- Borrowing capacity = 10,000,000 × (1 - 0.20) = 8,000,000

**Pass Criteria**: ☐ Capacity = 8,000,000

---

## 5. Performance Tests

### Test 5.1: Execution Time

**Objective**: Verify acceptable runtime

**Setup**:
- Standard scenario
- 30 replications
- 8-hour simulation day

**Procedure**:
1. Run full experiment
2. Time execution

**Expected Results**:
- Total time < 30 minutes
- Per replication < 1 minute

**Pass Criteria**: ☐ Execution time acceptable

---

### Test 5.2: Memory Usage

**Objective**: Ensure no memory leaks

**Setup**:
- Extended run (24-hour sim time)
- Multiple replications

**Procedure**:
1. Monitor memory during run
2. Check for growth

**Expected Results**:
- Memory stable throughout
- No continuous growth

**Pass Criteria**: ☐ Memory usage stable

---

### Test 5.3: Large-Scale Test

**Objective**: Test with many institutions

**Setup**:
- 50 institutions
- 10,000 payments
- Standard parameters

**Procedure**:
1. Scale up scenario
2. Run simulation
3. Monitor performance

**Expected Results**:
- Model completes successfully
- Results statistically valid
- Execution time acceptable (< 2 hours)

**Pass Criteria**: ☐ Large-scale scenario successful

---

## 6. Integration Tests

### Test 6.1: Data Import

**Objective**: Verify file reading

**Setup**:
- Sample CSV files with test data
- Institution config
- Payment data
- Market conditions

**Procedure**:
1. Load test data files
2. Run data_preparation.py
3. Verify import in Arena

**Expected Results**:
- All files load successfully
- Data correctly mapped to variables
- No import errors

**Pass Criteria**: ☐ All test data imported correctly

---

### Test 6.2: Data Export

**Objective**: Verify output file creation

**Setup**:
- Run baseline scenario
- Configure output to files

**Procedure**:
1. Run simulation
2. Check output files created
3. Verify file contents

**Expected Results**:
- simulation_results.xlsx created
- risk_metrics.xlsx created
- Files contain expected data
- Formats correct (CSV/Excel compatible)

**Pass Criteria**: ☐ Output files correct and complete

---

### Test 6.3: Python Script Integration

**Objective**: Verify analysis pipeline

**Setup**:
- Simulation output files
- Python environment configured

**Procedure**:
1. Run data_preparation.py
2. Run results_analyzer.py
3. Run visualization.py
4. Run validation.py

**Expected Results**:
- All scripts execute successfully
- Outputs generated in expected directories
- No Python errors

**Pass Criteria**: ☐ Full analysis pipeline functional

---

## 7. Regression Tests

### Test 7.1: Baseline Regression

**Objective**: Ensure model changes don't affect baseline

**Setup**:
- Standard baseline scenario
- Compare with previous validated results

**Procedure**:
1. Run baseline scenario
2. Compare with reference results
3. Check for significant differences

**Expected Results**:
- Settlement rate within ±2% of reference
- LCR within ±5% of reference
- Queue lengths within ±3 of reference

**Pass Criteria**: ☐ Results consistent with previous version

---

### Test 7.2: Stress Test Regression

**Objective**: Verify stress scenario consistency

**Setup**:
- Standard stress scenario
- Reference results from previous version

**Procedure**:
1. Run stress scenario
2. Compare with reference
3. Statistical comparison

**Expected Results**:
- Key metrics within confidence intervals
- No significant changes (p > 0.05)

**Pass Criteria**: ☐ Stress results consistent

---

### Test 7.3: DOE Regression

**Objective**: Ensure DOE results reproducible

**Setup**:
- Factorial design experiment
- Fixed random seeds
- Reference results

**Procedure**:
1. Run DOE with same seeds
2. Compare factor effects
3. Check statistical significance

**Expected Results**:
- Factor effects within ±10%
- Significance patterns match
- Response surface similar

**Pass Criteria**: ☐ DOE results reproducible

---

## Test Execution Log

### Execution Record

| Test ID | Date | Version | Result | Tester | Notes |
|---------|------|---------|--------|--------|-------|
| 1.1 | | | ☐ Pass ☐ Fail | | |
| 1.2 | | | ☐ Pass ☐ Fail | | |
| 1.3 | | | ☐ Pass ☐ Fail | | |
| 2.1 | | | ☐ Pass ☐ Fail | | |
| 2.2 | | | ☐ Pass ☐ Fail | | |
| 2.3 | | | ☐ Pass ☐ Fail | | |
| 3.1 | | | ☐ Pass ☐ Fail | | |
| 3.2 | | | ☐ Pass ☐ Fail | | |
| 3.3 | | | ☐ Pass ☐ Fail | | |
| 4.1 | | | ☐ Pass ☐ Fail | | |
| 4.2 | | | ☐ Pass ☐ Fail | | |
| 4.3 | | | ☐ Pass ☐ Fail | | |
| 4.4 | | | ☐ Pass ☐ Fail | | |
| 5.1 | | | ☐ Pass ☐ Fail | | |
| 5.2 | | | ☐ Pass ☐ Fail | | |
| 5.3 | | | ☐ Pass ☐ Fail | | |
| 6.1 | | | ☐ Pass ☐ Fail | | |
| 6.2 | | | ☐ Pass ☐ Fail | | |
| 6.3 | | | ☐ Pass ☐ Fail | | |
| 7.1 | | | ☐ Pass ☐ Fail | | |
| 7.2 | | | ☐ Pass ☐ Fail | | |
| 7.3 | | | ☐ Pass ☐ Fail | | |

### Summary

**Total Tests**: 22
**Tests Passed**: _____
**Tests Failed**: _____
**Pass Rate**: _____%

**Overall Status**: ☐ All Pass ☐ Failures Noted

---

## Issue Tracking

### Failed Tests

| Test ID | Issue Description | Severity | Assigned To | Status |
|---------|------------------|----------|-------------|--------|
| | | ☐ Critical ☐ Major ☐ Minor | | ☐ Open ☐ In Progress ☐ Resolved |
| | | ☐ Critical ☐ Major ☐ Minor | | ☐ Open ☐ In Progress ☐ Resolved |
| | | ☐ Critical ☐ Major ☐ Minor | | ☐ Open ☐ In Progress ☐ Resolved |

---

## Test Environment

**Arena Version**: __________________
**Python Version**: __________________
**OS**: __________________
**Hardware**: __________________

**Test Data Location**: data/test-scenarios/
**Reference Results Location**: data/reference-results/

---

## Approval

**Test Plan Approved By**: __________________ Date: __________

**Test Execution Approved By**: __________________ Date: __________

**Results Reviewed By**: __________________ Date: __________

---

**Document Version**: 1.0
**Last Updated**: [Date]
**Next Test Cycle**: [Date]
