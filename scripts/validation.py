#!/usr/bin/env python3
"""
Model Validation Script for Arena Liquidity Risk Simulation

This script validates the simulation model by:
- Comparing outputs against historical data
- Performing goodness-of-fit tests
- Assessing parameter sensitivity
- Evaluating model calibration

Author: Arena Liquidity Risk Project
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from scipy import stats
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')


class ModelValidator:
    """Validates Arena simulation model against historical data."""
    
    def __init__(self, simulation_dir: Path, historical_dir: Path, 
                 output_dir: Path):
        """
        Initialize the model validator.
        
        Args:
            simulation_dir: Directory with simulation outputs
            historical_dir: Directory with historical data
            output_dir: Directory for validation reports
        """
        self.simulation_dir = Path(simulation_dir)
        self.historical_dir = Path(historical_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_simulation_data(self) -> pd.DataFrame:
        """Load simulation results."""
        print("[INFO] Loading simulation data...")
        
        results_file = self.simulation_dir / 'simulation_results.xlsx'
        try:
            df = pd.read_csv(results_file, comment='#')
        except:
            df = pd.read_excel(results_file)
        
        print(f"[INFO] Loaded {len(df)} simulation records")
        return df
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical data if available."""
        print("[INFO] Looking for historical data...")
        
        # Try to find historical data file
        hist_file = self.historical_dir / 'historical_metrics.csv'
        if not hist_file.exists():
            hist_file = self.historical_dir / 'historical_metrics.xlsx'
        
        if hist_file.exists():
            try:
                df = pd.read_csv(hist_file)
            except:
                df = pd.read_excel(hist_file)
            print(f"[INFO] Loaded {len(df)} historical records")
            return df
        else:
            print("[WARNING] No historical data found")
            return pd.DataFrame()
    
    def test_distribution_fit(self, simulated: np.ndarray, 
                             historical: np.ndarray,
                             metric_name: str) -> Dict:
        """
        Test if simulated distribution matches historical distribution.
        
        Args:
            simulated: Simulated data values
            historical: Historical data values
            metric_name: Name of the metric being tested
            
        Returns:
            Dictionary with test results
        """
        print(f"[INFO] Testing distribution fit for {metric_name}...")
        
        results = {'metric': metric_name}
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_pval = stats.ks_2samp(simulated, historical)
        results['ks_statistic'] = ks_stat
        results['ks_pvalue'] = ks_pval
        results['ks_pass'] = ks_pval > 0.05
        
        # T-test for means
        t_stat, t_pval = stats.ttest_ind(simulated, historical)
        results['t_statistic'] = t_stat
        results['t_pvalue'] = t_pval
        results['means_equal'] = t_pval > 0.05
        
        # F-test for variances
        f_stat = np.var(simulated, ddof=1) / np.var(historical, ddof=1)
        df1 = len(simulated) - 1
        df2 = len(historical) - 1
        f_pval = 2 * min(stats.f.cdf(f_stat, df1, df2),
                        1 - stats.f.cdf(f_stat, df1, df2))
        results['f_statistic'] = f_stat
        results['f_pvalue'] = f_pval
        results['variances_equal'] = f_pval > 0.05
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(simulated, ddof=1) + np.var(historical, ddof=1)) / 2)
        cohens_d = (np.mean(simulated) - np.mean(historical)) / pooled_std
        results['cohens_d'] = cohens_d
        
        return results
    
    def validate_against_historical(self, sim_data: pd.DataFrame,
                                    hist_data: pd.DataFrame,
                                    metrics: List[str]) -> pd.DataFrame:
        """
        Validate simulation against historical data.
        
        Args:
            sim_data: Simulation data
            hist_data: Historical data
            metrics: List of metrics to validate
            
        Returns:
            DataFrame with validation results
        """
        if hist_data.empty:
            print("[WARNING] Skipping historical validation - no data available")
            return pd.DataFrame()
        
        print("[INFO] Validating against historical data...")
        
        validation_results = []
        
        for metric in metrics:
            if metric in sim_data.columns and metric in hist_data.columns:
                sim_values = sim_data[metric].dropna().values
                hist_values = hist_data[metric].dropna().values
                
                if len(sim_values) > 0 and len(hist_values) > 0:
                    result = self.test_distribution_fit(sim_values, hist_values, metric)
                    validation_results.append(result)
        
        return pd.DataFrame(validation_results)
    
    def check_face_validity(self, sim_data: pd.DataFrame) -> Dict:
        """
        Check face validity - do results make logical sense?
        
        Args:
            sim_data: Simulation data
            
        Returns:
            Dictionary with face validity checks
        """
        print("[INFO] Performing face validity checks...")
        
        checks = {}
        
        # Check 1: Settlement times should be positive
        if 'Average_Settlement_Time' in sim_data.columns:
            checks['positive_settlement_times'] = (
                sim_data['Average_Settlement_Time'] > 0
            ).all()
        
        # Check 2: Settled payments <= Total payments
        if 'Settled_Payments' in sim_data.columns and 'Total_Payments' in sim_data.columns:
            checks['settled_le_total'] = (
                sim_data['Settled_Payments'] <= sim_data['Total_Payments']
            ).all()
        
        # Check 3: Queue length should be non-negative
        if 'Max_Queue_Length' in sim_data.columns:
            checks['non_negative_queue'] = (
                sim_data['Max_Queue_Length'] >= 0
            ).all()
        
        # Check 4: Throughput should be positive
        if 'System_Throughput' in sim_data.columns:
            checks['positive_throughput'] = (
                sim_data['System_Throughput'] > 0
            ).all()
        
        # Check 5: Gridlock events should be non-negative integers
        if 'Gridlock_Events' in sim_data.columns:
            checks['valid_gridlock'] = (
                (sim_data['Gridlock_Events'] >= 0) & 
                (sim_data['Gridlock_Events'] == sim_data['Gridlock_Events'].astype(int))
            ).all()
        
        checks['all_passed'] = all(checks.values())
        
        return checks
    
    def assess_sensitivity(self, sim_data: pd.DataFrame) -> pd.DataFrame:
        """
        Assess output sensitivity to scenario changes.
        
        Args:
            sim_data: Simulation data
            
        Returns:
            DataFrame with sensitivity metrics
        """
        print("[INFO] Assessing parameter sensitivity...")
        
        if 'Scenario' not in sim_data.columns:
            print("[WARNING] No scenario column found")
            return pd.DataFrame()
        
        scenarios = sim_data['Scenario'].unique()
        if len(scenarios) < 2:
            print("[WARNING] Need at least 2 scenarios for sensitivity analysis")
            return pd.DataFrame()
        
        sensitivity = []
        numeric_cols = sim_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col != 'Replication':
                scenario_means = sim_data.groupby('Scenario')[col].mean()
                
                sensitivity.append({
                    'Metric': col,
                    'Min_Value': scenario_means.min(),
                    'Max_Value': scenario_means.max(),
                    'Range': scenario_means.max() - scenario_means.min(),
                    'Coefficient_of_Variation': scenario_means.std() / scenario_means.mean()
                })
        
        return pd.DataFrame(sensitivity)
    
    def check_statistical_validity(self, sim_data: pd.DataFrame) -> Dict:
        """
        Check statistical validity of replications.
        
        Args:
            sim_data: Simulation data
            
        Returns:
            Dictionary with statistical validity checks
        """
        print("[INFO] Checking statistical validity...")
        
        checks = {}
        
        # Check for sufficient replications
        reps_per_scenario = sim_data.groupby('Scenario').size()
        checks['min_replications'] = reps_per_scenario.min()
        checks['sufficient_replications'] = reps_per_scenario.min() >= 30
        
        # Check for independence (Durbin-Watson test for autocorrelation)
        if 'System_Throughput' in sim_data.columns:
            for scenario in sim_data['Scenario'].unique():
                scenario_data = sim_data[sim_data['Scenario'] == scenario]['System_Throughput']
                if len(scenario_data) > 2:
                    dw = self._durbin_watson(scenario_data.values)
                    checks[f'durbin_watson_{scenario}'] = dw
                    # DW should be close to 2 for no autocorrelation
                    checks[f'independent_{scenario}'] = 1.5 < dw < 2.5
        
        return checks
    
    def _durbin_watson(self, residuals: np.ndarray) -> float:
        """Calculate Durbin-Watson statistic."""
        diff = np.diff(residuals)
        return np.sum(diff**2) / np.sum(residuals**2)
    
    def generate_validation_report(self, face_checks: Dict,
                                   stat_checks: Dict,
                                   sensitivity: pd.DataFrame,
                                   historical_val: pd.DataFrame) -> str:
        """
        Generate comprehensive validation report.
        
        Args:
            face_checks: Face validity results
            stat_checks: Statistical validity results
            sensitivity: Sensitivity analysis results
            historical_val: Historical validation results
            
        Returns:
            Report text
        """
        report = []
        report.append("=" * 80)
        report.append("ARENA LIQUIDITY RISK MODEL - VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Face validity
        report.append("FACE VALIDITY CHECKS")
        report.append("-" * 80)
        for check, result in face_checks.items():
            status = "✓ PASS" if result else "✗ FAIL"
            report.append(f"{status}: {check}")
        report.append("")
        
        # Statistical validity
        report.append("STATISTICAL VALIDITY CHECKS")
        report.append("-" * 80)
        for check, result in stat_checks.items():
            if isinstance(result, bool):
                status = "✓ PASS" if result else "✗ FAIL"
                report.append(f"{status}: {check}")
            else:
                report.append(f"{check}: {result:.4f}")
        report.append("")
        
        # Sensitivity analysis
        if not sensitivity.empty:
            report.append("SENSITIVITY ANALYSIS")
            report.append("-" * 80)
            report.append(sensitivity.to_string(index=False))
            report.append("")
        
        # Historical validation
        if not historical_val.empty:
            report.append("HISTORICAL VALIDATION RESULTS")
            report.append("-" * 80)
            report.append(historical_val.to_string(index=False))
            report.append("")
            
            # Summary
            n_tests = len(historical_val)
            n_passed = historical_val['ks_pass'].sum()
            report.append(f"Distribution tests passed: {n_passed}/{n_tests} ({n_passed/n_tests*100:.1f}%)")
        
        report.append("")
        report.append("=" * 80)
        
        overall_valid = (
            face_checks.get('all_passed', False) and
            stat_checks.get('sufficient_replications', False)
        )
        
        if overall_valid:
            report.append("OVERALL ASSESSMENT: MODEL APPEARS VALID ✓")
        else:
            report.append("OVERALL ASSESSMENT: MODEL REQUIRES FURTHER CALIBRATION ⚠")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def validate(self):
        """Execute complete validation pipeline."""
        # Load data
        sim_data = self.load_simulation_data()
        hist_data = self.load_historical_data()
        
        # Perform validation checks
        face_checks = self.check_face_validity(sim_data)
        stat_checks = self.check_statistical_validity(sim_data)
        sensitivity = self.assess_sensitivity(sim_data)
        
        # Historical validation
        metrics_to_validate = ['Average_Settlement_Time', 'Max_Queue_Length',
                              'System_Throughput']
        historical_val = self.validate_against_historical(
            sim_data, hist_data, metrics_to_validate
        )
        
        # Generate report
        report = self.generate_validation_report(
            face_checks, stat_checks, sensitivity, historical_val
        )
        
        # Export results
        print(f"[INFO] Exporting validation results to {self.output_dir}")
        
        if not sensitivity.empty:
            sensitivity.to_csv(self.output_dir / 'sensitivity_analysis.csv', index=False)
        
        if not historical_val.empty:
            historical_val.to_csv(self.output_dir / 'historical_validation.csv', index=False)
        
        with open(self.output_dir / 'validation_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\n[INFO] Validation complete. Results saved to {self.output_dir}")


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description='Validate Arena simulation model'
    )
    parser.add_argument(
        '--simulation',
        type=str,
        default='data/output-templates',
        help='Directory with simulation outputs'
    )
    parser.add_argument(
        '--historical',
        type=str,
        default='data/historical',
        help='Directory with historical data (if available)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='validation',
        help='Output directory for validation results'
    )
    
    args = parser.parse_args()
    
    # Create validator and run
    validator = ModelValidator(args.simulation, args.historical, args.output)
    validator.validate()


if __name__ == '__main__':
    main()
