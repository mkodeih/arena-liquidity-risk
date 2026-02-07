#!/usr/bin/env python3
"""
Visualization Script for Arena Liquidity Risk Simulation

This script creates comprehensive visualizations of simulation results including:
- Time-series plots of liquidity metrics
- Distribution plots for settlement times and queue lengths
- Risk heatmaps and dashboards
- Scenario comparison charts

Author: Arena Liquidity Risk Project
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class SimulationVisualizer:
    """Creates visualizations for Arena simulation results."""
    
    def __init__(self, input_dir: Path, output_dir: Path, 
                 format: str = 'png', dpi: int = 300):
        """
        Initialize the visualizer.
        
        Args:
            input_dir: Directory containing simulation output files
            output_dir: Directory for visualization outputs
            format: Output format (png, pdf, svg)
            dpi: Resolution for raster formats
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.format = format
        self.dpi = dpi
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> tuple:
        """
        Load simulation data files.
        
        Returns:
            Tuple of (results, metrics) DataFrames
        """
        print("[INFO] Loading simulation data...")
        
        # Load results
        results_file = self.input_dir / 'simulation_results.xlsx'
        try:
            results = pd.read_csv(results_file, comment='#')
        except:
            results = pd.read_excel(results_file)
        
        # Load metrics
        metrics_file = self.input_dir / 'risk_metrics.xlsx'
        try:
            metrics = pd.read_csv(metrics_file, comment='#')
        except:
            metrics = pd.read_excel(metrics_file)
        
        print(f"[INFO] Loaded {len(results)} result records and {len(metrics)} metric records")
        return results, metrics
    
    def plot_settlement_time_distribution(self, results: pd.DataFrame):
        """
        Create distribution plot for settlement times by scenario.
        
        Args:
            results: Simulation results DataFrame
        """
        print("[INFO] Creating settlement time distribution plot...")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        scenarios = results['Scenario'].unique()
        for scenario in scenarios:
            data = results[results['Scenario'] == scenario]['Average_Settlement_Time']
            ax.hist(data, alpha=0.6, label=scenario, bins=20)
        
        ax.set_xlabel('Average Settlement Time (minutes)')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Settlement Times by Scenario')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        filename = self.output_dir / f'settlement_time_distribution.{self.format}'
        plt.tight_layout()
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_scenario_comparison(self, results: pd.DataFrame, 
                                metrics: List[str]):
        """
        Create bar chart comparing scenarios across multiple metrics.
        
        Args:
            results: Simulation results DataFrame
            metrics: List of metric column names to compare
        """
        print("[INFO] Creating scenario comparison plot...")
        
        scenarios = results['Scenario'].unique()
        scenario_means = results.groupby('Scenario')[metrics].mean()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, metric in enumerate(metrics[:4]):
            ax = axes[idx]
            scenario_means[metric].plot(kind='bar', ax=ax, color='steelblue')
            ax.set_title(f'{metric} by Scenario')
            ax.set_ylabel(metric)
            ax.set_xlabel('Scenario')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / f'scenario_comparison.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_queue_length_boxplot(self, results: pd.DataFrame):
        """
        Create boxplot showing queue length distribution by scenario.
        
        Args:
            results: Simulation results DataFrame
        """
        print("[INFO] Creating queue length boxplot...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.boxplot(data=results, x='Scenario', y='Max_Queue_Length', ax=ax)
        ax.set_title('Maximum Queue Length Distribution by Scenario')
        ax.set_ylabel('Maximum Queue Length')
        ax.set_xlabel('Scenario')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / f'queue_length_boxplot.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_lcr_heatmap(self, metrics: pd.DataFrame):
        """
        Create heatmap of LCR values across institutions and scenarios.
        
        Args:
            metrics: Risk metrics DataFrame
        """
        print("[INFO] Creating LCR heatmap...")
        
        if 'LCR' not in metrics.columns or 'Institution_ID' not in metrics.columns:
            print("[WARNING] Required columns not found for LCR heatmap")
            return
        
        # Pivot data for heatmap
        pivot_data = metrics.pivot_table(
            values='LCR',
            index='Institution_ID',
            columns='Scenario',
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='RdYlGn',
                   center=1.0, vmin=0.8, vmax=1.5, ax=ax)
        ax.set_title('Liquidity Coverage Ratio (LCR) by Institution and Scenario')
        ax.set_xlabel('Scenario')
        ax.set_ylabel('Institution')
        
        plt.tight_layout()
        filename = self.output_dir / f'lcr_heatmap.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_throughput_time_series(self, results: pd.DataFrame):
        """
        Create time series plot of system throughput.
        
        Args:
            results: Simulation results DataFrame
        """
        print("[INFO] Creating throughput time series plot...")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for scenario in results['Scenario'].unique():
            scenario_data = results[results['Scenario'] == scenario]
            scenario_data = scenario_data.sort_values('Replication')
            ax.plot(scenario_data['Replication'], 
                   scenario_data['System_Throughput'],
                   marker='o', label=scenario, alpha=0.7)
        
        ax.set_xlabel('Replication')
        ax.set_ylabel('System Throughput (payments/hour)')
        ax.set_title('System Throughput Across Replications')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / f'throughput_time_series.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_risk_dashboard(self, metrics: pd.DataFrame):
        """
        Create comprehensive risk dashboard with multiple panels.
        
        Args:
            metrics: Risk metrics DataFrame
        """
        print("[INFO] Creating risk dashboard...")
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # LCR distribution
        ax1 = fig.add_subplot(gs[0, :2])
        if 'LCR' in metrics.columns:
            sns.violinplot(data=metrics, x='Scenario', y='LCR', ax=ax1)
            ax1.axhline(y=1.0, color='r', linestyle='--', label='Regulatory Minimum')
            ax1.set_title('LCR Distribution by Scenario')
            ax1.legend()
        
        # NSFR distribution
        ax2 = fig.add_subplot(gs[0, 2])
        if 'NSFR' in metrics.columns:
            metrics.boxplot(column='NSFR', by='Scenario', ax=ax2)
            ax2.axhline(y=1.0, color='r', linestyle='--')
            ax2.set_title('NSFR by Scenario')
            plt.sca(ax2)
            plt.xticks(rotation=45)
        
        # Credit utilization
        ax3 = fig.add_subplot(gs[1, :2])
        if 'Credit_Used' in metrics.columns:
            credit_by_scenario = metrics.groupby('Scenario')['Credit_Used'].mean()
            credit_by_scenario.plot(kind='bar', ax=ax3, color='coral')
            ax3.set_title('Average Credit Utilization by Scenario')
            ax3.set_ylabel('Credit Used')
            ax3.tick_params(axis='x', rotation=45)
        
        # Facility draws
        ax4 = fig.add_subplot(gs[1, 2])
        if 'Facility_Draws' in metrics.columns:
            facility_total = metrics.groupby('Scenario')['Facility_Draws'].sum()
            ax4.pie(facility_total, labels=facility_total.index, autopct='%1.1f%%')
            ax4.set_title('Central Bank Facility Usage')
        
        # Risk score
        ax5 = fig.add_subplot(gs[2, :])
        if 'Risk_Score' in metrics.columns and 'Institution_ID' in metrics.columns:
            risk_pivot = metrics.pivot_table(
                values='Risk_Score',
                index='Institution_ID',
                columns='Scenario',
                aggfunc='mean'
            )
            sns.heatmap(risk_pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax5)
            ax5.set_title('Composite Risk Score by Institution and Scenario')
        
        fig.suptitle('Liquidity Risk Dashboard', fontsize=16, y=0.995)
        
        filename = self.output_dir / f'risk_dashboard.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def plot_gridlock_analysis(self, results: pd.DataFrame):
        """
        Create gridlock event analysis plot.
        
        Args:
            results: Simulation results DataFrame
        """
        print("[INFO] Creating gridlock analysis plot...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gridlock frequency by scenario
        gridlock_freq = results.groupby('Scenario')['Gridlock_Events'].mean()
        gridlock_freq.plot(kind='bar', ax=ax1, color='crimson')
        ax1.set_title('Average Gridlock Events by Scenario')
        ax1.set_ylabel('Average Gridlock Events')
        ax1.set_xlabel('Scenario')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Gridlock vs Queue Length scatter
        ax2.scatter(results['Max_Queue_Length'], 
                   results['Gridlock_Events'],
                   c=results['Scenario'].astype('category').cat.codes,
                   alpha=0.6, cmap='viridis')
        ax2.set_xlabel('Maximum Queue Length')
        ax2.set_ylabel('Gridlock Events')
        ax2.set_title('Gridlock Events vs Queue Length')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / f'gridlock_analysis.{self.format}'
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Saved: {filename}")
    
    def create_all_visualizations(self):
        """Create all available visualizations."""
        results, metrics = self.load_data()
        
        # Create all plots
        self.plot_settlement_time_distribution(results)
        
        comparison_metrics = ['Average_Settlement_Time', 'Max_Queue_Length',
                            'Gridlock_Events', 'System_Throughput']
        self.plot_scenario_comparison(results, comparison_metrics)
        
        self.plot_queue_length_boxplot(results)
        self.plot_lcr_heatmap(metrics)
        self.plot_throughput_time_series(results)
        self.plot_risk_dashboard(metrics)
        self.plot_gridlock_analysis(results)
        
        print(f"\n[INFO] All visualizations saved to {self.output_dir}")


def main():
    """Main entry point for visualization script."""
    parser = argparse.ArgumentParser(
        description='Create visualizations for Arena simulation results'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/output-templates',
        help='Input directory containing simulation output files'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='figures',
        help='Output directory for visualizations'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='png',
        choices=['png', 'pdf', 'svg'],
        help='Output format for figures'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='Resolution for raster formats (default: 300)'
    )
    
    args = parser.parse_args()
    
    # Create visualizer and generate plots
    visualizer = SimulationVisualizer(
        args.input,
        args.output,
        args.format,
        args.dpi
    )
    visualizer.create_all_visualizations()


if __name__ == '__main__':
    main()
