#!/usr/bin/env python3
"""
Results Analyzer for Arena Liquidity Risk Simulation

This script analyzes simulation output data and generates comprehensive reports including:
- Statistical analysis of performance metrics
- Scenario comparisons
- Risk indicator calculations
- Confidence intervals and hypothesis tests

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


class ResultsAnalyzer:
    """Analyzes Arena simulation results and generates reports."""
    
    def __init__(self, results_file: Path, metrics_file: Path, 
                 output_dir: Path, confidence: float = 0.95):
        """
        Initialize the results analyzer.
        
        Args:
            results_file: Path to simulation results file
            metrics_file: Path to risk metrics file
            output_dir: Directory for analysis outputs
            confidence: Confidence level for intervals (default 0.95)
        """
        self.results_file = Path(results_file)
        self.metrics_file = Path(metrics_file)
        self.output_dir = Path(output_dir)
        self.confidence = confidence
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load simulation results and metrics data.
        
        Returns:
            Tuple of (results DataFrame, metrics DataFrame)
        """
        print("[INFO] Loading simulation data...")
        
        # Load results
        try:
            results = pd.read_csv(self.results_file, comment='#')
        except:
            results = pd.read_excel(self.results_file)
        
        # Load metrics
        try:
            metrics = pd.read_csv(self.metrics_file, comment='#')
        except:
            metrics = pd.read_excel(self.metrics_file)
        
        print(f"[INFO] Loaded {len(results)} result records and {len(metrics)} metric records")
        return results, metrics
    
    def calculate_basic_statistics(self, df: pd.DataFrame, 
                                   group_by: str = 'Scenario') -> pd.DataFrame:
        """
        Calculate basic statistics for each scenario.
        
        Args:
            df: DataFrame to analyze
            group_by: Column to group by
            
        Returns:
            DataFrame with summary statistics
        """
        print(f"[INFO] Calculating statistics grouped by {group_by}")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'Replication']
        
        stats_dict = {}
        for scenario in df[group_by].unique():
            scenario_data = df[df[group_by] == scenario]
            stats_dict[scenario] = {}
            
            for col in numeric_cols:
                data = scenario_data[col].dropna()
                if len(data) > 0:
                    stats_dict[scenario][f'{col}_mean'] = data.mean()
                    stats_dict[scenario][f'{col}_std'] = data.std()
                    stats_dict[scenario][f'{col}_min'] = data.min()
                    stats_dict[scenario][f'{col}_max'] = data.max()
                    stats_dict[scenario][f'{col}_median'] = data.median()
        
        return pd.DataFrame(stats_dict).T
    
    def calculate_confidence_intervals(self, df: pd.DataFrame,
                                      metrics: List[str],
                                      group_by: str = 'Scenario') -> pd.DataFrame:
        """
        Calculate confidence intervals for key metrics.
        
        Args:
            df: DataFrame to analyze
            metrics: List of metric column names
            group_by: Column to group by
            
        Returns:
            DataFrame with confidence intervals
        """
        print(f"[INFO] Calculating {self.confidence*100}% confidence intervals")
        
        ci_results = []
        alpha = 1 - self.confidence
        
        for scenario in df[group_by].unique():
            scenario_data = df[df[group_by] == scenario]
            row = {'Scenario': scenario, 'N': len(scenario_data)}
            
            for metric in metrics:
                if metric in scenario_data.columns:
                    data = scenario_data[metric].dropna()
                    if len(data) > 1:
                        mean = data.mean()
                        se = stats.sem(data)
                        ci = stats.t.interval(self.confidence, len(data)-1, 
                                            loc=mean, scale=se)
                        row[f'{metric}_mean'] = mean
                        row[f'{metric}_ci_lower'] = ci[0]
                        row[f'{metric}_ci_upper'] = ci[1]
                        row[f'{metric}_margin'] = ci[1] - mean
            
            ci_results.append(row)
        
        return pd.DataFrame(ci_results)
    
    def compare_scenarios(self, df: pd.DataFrame, 
                         baseline: str,
                         metrics: List[str]) -> pd.DataFrame:
        """
        Compare scenarios against baseline using statistical tests.
        
        Args:
            df: DataFrame to analyze
            baseline: Name of baseline scenario
            metrics: List of metrics to compare
            
        Returns:
            DataFrame with comparison results
        """
        print(f"[INFO] Comparing scenarios against baseline: {baseline}")
        
        baseline_data = df[df['Scenario'] == baseline]
        scenarios = [s for s in df['Scenario'].unique() if s != baseline]
        
        comparison_results = []
        
        for scenario in scenarios:
            scenario_data = df[df['Scenario'] == scenario]
            row = {'Scenario': scenario}
            
            for metric in metrics:
                if metric in df.columns:
                    base_values = baseline_data[metric].dropna()
                    scenario_values = scenario_data[metric].dropna()
                    
                    if len(base_values) > 1 and len(scenario_values) > 1:
                        # Perform t-test
                        t_stat, p_value = stats.ttest_ind(scenario_values, base_values)
                        
                        # Calculate percent change
                        pct_change = ((scenario_values.mean() - base_values.mean()) / 
                                     base_values.mean() * 100)
                        
                        row[f'{metric}_pct_change'] = pct_change
                        row[f'{metric}_p_value'] = p_value
                        row[f'{metric}_significant'] = p_value < 0.05
            
            comparison_results.append(row)
        
        return pd.DataFrame(comparison_results)
    
    def calculate_risk_indicators(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite risk indicators.
        
        Args:
            metrics: Risk metrics DataFrame
            
        Returns:
            DataFrame with risk indicators
        """
        print("[INFO] Calculating composite risk indicators")
        
        risk_df = metrics.copy()
        
        # LCR adequacy (target >= 1.0)
        if 'LCR' in risk_df.columns:
            risk_df['LCR_Adequate'] = risk_df['LCR'] >= 1.0
            risk_df['LCR_Gap'] = risk_df['LCR'].apply(lambda x: max(0, 1.0 - x))
        
        # NSFR adequacy (target >= 1.0)
        if 'NSFR' in risk_df.columns:
            risk_df['NSFR_Adequate'] = risk_df['NSFR'] >= 1.0
            risk_df['NSFR_Gap'] = risk_df['NSFR'].apply(lambda x: max(0, 1.0 - x))
        
        # Credit utilization rate
        if 'Credit_Used' in risk_df.columns and 'Institution_ID' in risk_df.columns:
            # This would need credit limits from institution config
            # Placeholder calculation
            risk_df['Credit_Utilization'] = risk_df['Credit_Used'] / 5000000
        
        return risk_df
    
    def generate_summary_report(self, results_stats: pd.DataFrame,
                               metrics_stats: pd.DataFrame,
                               ci_results: pd.DataFrame,
                               comparison: pd.DataFrame) -> str:
        """
        Generate comprehensive summary report.
        
        Args:
            results_stats: Results statistics
            metrics_stats: Metrics statistics
            ci_results: Confidence interval results
            comparison: Scenario comparison results
            
        Returns:
            Report text
        """
        report = []
        report.append("=" * 80)
        report.append("ARENA LIQUIDITY RISK SIMULATION - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Results overview
        report.append("SIMULATION RESULTS SUMMARY")
        report.append("-" * 80)
        report.append(results_stats.to_string())
        report.append("")
        
        # Risk metrics overview
        report.append("RISK METRICS SUMMARY")
        report.append("-" * 80)
        report.append(metrics_stats.to_string())
        report.append("")
        
        # Confidence intervals
        report.append(f"CONFIDENCE INTERVALS ({self.confidence*100}%)")
        report.append("-" * 80)
        report.append(ci_results.to_string())
        report.append("")
        
        # Scenario comparison
        if not comparison.empty:
            report.append("SCENARIO COMPARISON")
            report.append("-" * 80)
            report.append(comparison.to_string())
            report.append("")
        
        # Key findings
        report.append("KEY FINDINGS")
        report.append("-" * 80)
        
        # Find scenarios with issues
        if 'Average_Settlement_Time_mean' in results_stats.columns:
            slow_scenarios = results_stats[
                results_stats['Average_Settlement_Time_mean'] > 5.0
            ]
            if not slow_scenarios.empty:
                report.append(f"⚠ Scenarios with high settlement times (>5 min): {list(slow_scenarios.index)}")
        
        if 'Gridlock_Events_mean' in results_stats.columns:
            gridlock_scenarios = results_stats[
                results_stats['Gridlock_Events_mean'] > 0
            ]
            if not gridlock_scenarios.empty:
                report.append(f"⚠ Scenarios with gridlock events: {list(gridlock_scenarios.index)}")
        
        report.append("")
        return "\n".join(report)
    
    def export_results(self, results_stats: pd.DataFrame,
                      metrics_stats: pd.DataFrame,
                      ci_results: pd.DataFrame,
                      comparison: pd.DataFrame,
                      report_text: str):
        """
        Export analysis results to files.
        
        Args:
            results_stats: Results statistics
            metrics_stats: Metrics statistics
            ci_results: Confidence intervals
            comparison: Scenario comparison
            report_text: Summary report text
        """
        print(f"[INFO] Exporting results to {self.output_dir}")
        
        # Export CSV files
        results_stats.to_csv(self.output_dir / 'results_statistics.csv')
        metrics_stats.to_csv(self.output_dir / 'metrics_statistics.csv')
        ci_results.to_csv(self.output_dir / 'confidence_intervals.csv', index=False)
        if not comparison.empty:
            comparison.to_csv(self.output_dir / 'scenario_comparison.csv', index=False)
        
        # Export text report
        with open(self.output_dir / 'analysis_report.txt', 'w') as f:
            f.write(report_text)
        
        print("[INFO] Analysis complete. Results exported.")
    
    def analyze(self, baseline_scenario: str = 'BASELINE'):
        """
        Execute complete analysis pipeline.
        
        Args:
            baseline_scenario: Name of baseline scenario for comparisons
        """
        # Load data
        results, metrics = self.load_data()
        
        # Calculate statistics
        results_stats = self.calculate_basic_statistics(results)
        metrics_stats = self.calculate_basic_statistics(metrics)
        
        # Calculate confidence intervals
        results_metrics = ['Average_Settlement_Time', 'Max_Queue_Length', 
                          'Gridlock_Events', 'System_Throughput']
        ci_results = self.calculate_confidence_intervals(results, results_metrics)
        
        # Compare scenarios
        comparison = pd.DataFrame()
        if baseline_scenario in results['Scenario'].values:
            comparison = self.compare_scenarios(results, baseline_scenario, 
                                               results_metrics)
        
        # Calculate risk indicators
        risk_indicators = self.calculate_risk_indicators(metrics)
        risk_indicators.to_csv(self.output_dir / 'risk_indicators.csv', index=False)
        
        # Generate report
        report = self.generate_summary_report(results_stats, metrics_stats,
                                              ci_results, comparison)
        
        # Export everything
        self.export_results(results_stats, metrics_stats, ci_results, 
                           comparison, report)
        
        print(report)


def main():
    """Main entry point for results analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze Arena simulation results'
    )
    parser.add_argument(
        '--results',
        type=str,
        default='data/output-templates/simulation_results.xlsx',
        help='Path to simulation results file'
    )
    parser.add_argument(
        '--metrics',
        type=str,
        default='data/output-templates/risk_metrics.xlsx',
        help='Path to risk metrics file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='reports',
        help='Output directory for analysis results'
    )
    parser.add_argument(
        '--baseline',
        type=str,
        default='BASELINE',
        help='Baseline scenario name for comparisons'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.95,
        help='Confidence level for intervals (default: 0.95)'
    )
    
    args = parser.parse_args()
    
    # Create analyzer and run
    analyzer = ResultsAnalyzer(
        args.results, 
        args.metrics,
        args.output,
        args.confidence
    )
    analyzer.analyze(args.baseline)


if __name__ == '__main__':
    main()
