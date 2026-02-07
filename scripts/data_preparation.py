#!/usr/bin/env python3
"""
Data Preparation Script for Arena Liquidity Risk Simulation

This script prepares input data for the Arena simulation model by:
- Loading and validating input files
- Checking data quality and completeness
- Transforming data into Arena-compatible formats
- Generating summary statistics

Author: Arena Liquidity Risk Project
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class DataPreparator:
    """Handles data preparation for Arena simulation inputs."""
    
    def __init__(self, input_dir: Path, output_dir: Path, verbose: bool = True):
        """
        Initialize the data preparator.
        
        Args:
            input_dir: Directory containing input data files
            output_dir: Directory for processed output files
            verbose: Whether to print detailed progress information
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def load_payment_data(self, filename: str = "payment_parameters.xlsx") -> pd.DataFrame:
        """
        Load and validate payment parameter data.
        
        Args:
            filename: Name of payment data file
            
        Returns:
            DataFrame containing validated payment data
        """
        self.log(f"Loading payment data from {filename}")
        filepath = self.input_dir / filename
        
        try:
            # Try reading as CSV first (since .xlsx files are actually CSV in templates)
            df = pd.read_csv(filepath, comment='#')
        except:
            # Fall back to Excel format
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_cols = ['Payment_ID', 'Source_Institution', 'Target_Institution', 
                        'Amount', 'Priority', 'Timestamp']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate data
        if df['Amount'].min() <= 0:
            raise ValueError("Payment amounts must be positive")
        
        if df['Source_Institution'].equals(df['Target_Institution']).any():
            self.log("Warning: Found payments where source equals target")
        
        self.log(f"Loaded {len(df)} payment records")
        return df
    
    def load_institution_config(self, filename: str = "institution_config.xlsx") -> pd.DataFrame:
        """
        Load and validate institution configuration data.
        
        Args:
            filename: Name of institution config file
            
        Returns:
            DataFrame containing validated institution data
        """
        self.log(f"Loading institution configuration from {filename}")
        filepath = self.input_dir / filename
        
        try:
            df = pd.read_csv(filepath, comment='#')
        except:
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_cols = ['Institution_ID', 'Institution_Name', 'Initial_Reserve', 
                        'Reserve_Ratio', 'Credit_Limit']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate reserve ratios
        if (df['Reserve_Ratio'] < 0).any() or (df['Reserve_Ratio'] > 1).any():
            raise ValueError("Reserve ratios must be between 0 and 1")
        
        # Check regulatory minimum (typically 10%)
        if (df['Reserve_Ratio'] < 0.10).any():
            self.log("Warning: Some institutions below regulatory reserve minimum (10%)")
        
        self.log(f"Loaded {len(df)} institution records")
        return df
    
    def load_market_conditions(self, filename: str = "market_conditions.xlsx") -> pd.DataFrame:
        """
        Load and validate market conditions data.
        
        Args:
            filename: Name of market conditions file
            
        Returns:
            DataFrame containing validated market data
        """
        self.log(f"Loading market conditions from {filename}")
        filepath = self.input_dir / filename
        
        try:
            df = pd.read_csv(filepath, comment='#')
        except:
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_cols = ['Scenario', 'Interest_Rate', 'Market_Volatility', 
                        'Stress_Probability']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate ranges
        if (df['Market_Volatility'] < 0).any():
            raise ValueError("Market volatility cannot be negative")
        
        if (df['Stress_Probability'] < 0).any() or (df['Stress_Probability'] > 1).any():
            raise ValueError("Stress probability must be between 0 and 1")
        
        self.log(f"Loaded {len(df)} market scenarios")
        return df
    
    def validate_data_consistency(self, payments: pd.DataFrame, 
                                  institutions: pd.DataFrame) -> bool:
        """
        Validate consistency across data files.
        
        Args:
            payments: Payment data
            institutions: Institution data
            
        Returns:
            True if data is consistent
        """
        self.log("Validating data consistency")
        
        # Check that all institutions in payments exist in config
        inst_ids = set(institutions['Institution_ID'])
        source_ids = set(payments['Source_Institution'])
        target_ids = set(payments['Target_Institution'])
        
        missing_sources = source_ids - inst_ids
        missing_targets = target_ids - inst_ids
        
        if missing_sources:
            self.log(f"Warning: Unknown source institutions: {missing_sources}")
        
        if missing_targets:
            self.log(f"Warning: Unknown target institutions: {missing_targets}")
        
        return len(missing_sources) == 0 and len(missing_targets) == 0
    
    def generate_summary_statistics(self, payments: pd.DataFrame, 
                                   institutions: pd.DataFrame,
                                   markets: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for input data.
        
        Args:
            payments: Payment data
            institutions: Institution data
            markets: Market conditions data
            
        Returns:
            Dictionary containing summary statistics
        """
        self.log("Generating summary statistics")
        
        summary = {
            'payment_stats': {
                'total_payments': len(payments),
                'total_value': payments['Amount'].sum(),
                'avg_payment': payments['Amount'].mean(),
                'std_payment': payments['Amount'].std(),
                'min_payment': payments['Amount'].min(),
                'max_payment': payments['Amount'].max(),
                'priority_distribution': payments['Priority'].value_counts().to_dict()
            },
            'institution_stats': {
                'total_institutions': len(institutions),
                'total_reserves': institutions['Initial_Reserve'].sum(),
                'avg_reserve_ratio': institutions['Reserve_Ratio'].mean(),
                'total_credit_capacity': institutions['Credit_Limit'].sum(),
                'avg_credit_limit': institutions['Credit_Limit'].mean()
            },
            'market_stats': {
                'scenarios': len(markets),
                'avg_interest_rate': markets['Interest_Rate'].mean(),
                'avg_volatility': markets['Market_Volatility'].mean(),
                'max_stress_prob': markets['Stress_Probability'].max()
            }
        }
        
        return summary
    
    def export_processed_data(self, payments: pd.DataFrame, 
                             institutions: pd.DataFrame,
                             markets: pd.DataFrame,
                             summary: Dict):
        """
        Export processed data files.
        
        Args:
            payments: Processed payment data
            institutions: Processed institution data
            markets: Processed market data
            summary: Summary statistics
        """
        self.log("Exporting processed data")
        
        # Export to CSV for Arena compatibility
        payments.to_csv(self.output_dir / 'payments_processed.csv', index=False)
        institutions.to_csv(self.output_dir / 'institutions_processed.csv', index=False)
        markets.to_csv(self.output_dir / 'markets_processed.csv', index=False)
        
        # Export summary as text file
        with open(self.output_dir / 'data_summary.txt', 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ARENA LIQUIDITY RISK SIMULATION - DATA SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("PAYMENT STATISTICS:\n")
            f.write("-" * 60 + "\n")
            for key, value in summary['payment_stats'].items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\n")
                else:
                    f.write(f"{key}: {value:,.2f}\n")
            
            f.write("\nINSTITUTION STATISTICS:\n")
            f.write("-" * 60 + "\n")
            for key, value in summary['institution_stats'].items():
                f.write(f"{key}: {value:,.2f}\n")
            
            f.write("\nMARKET STATISTICS:\n")
            f.write("-" * 60 + "\n")
            for key, value in summary['market_stats'].items():
                f.write(f"{key}: {value:,.4f}\n")
        
        self.log(f"Data exported to {self.output_dir}")
    
    def prepare_all(self) -> bool:
        """
        Execute complete data preparation pipeline.
        
        Returns:
            True if preparation successful
        """
        try:
            # Load data
            payments = self.load_payment_data()
            institutions = self.load_institution_config()
            markets = self.load_market_conditions()
            
            # Validate consistency
            is_consistent = self.validate_data_consistency(payments, institutions)
            if not is_consistent:
                self.log("Warning: Data consistency issues detected")
            
            # Generate summary
            summary = self.generate_summary_statistics(payments, institutions, markets)
            
            # Export results
            self.export_processed_data(payments, institutions, markets, summary)
            
            self.log("Data preparation completed successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Data preparation failed: {str(e)}", file=sys.stderr)
            return False


def main():
    """Main entry point for data preparation script."""
    parser = argparse.ArgumentParser(
        description='Prepare input data for Arena liquidity risk simulation'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/input-templates',
        help='Input directory containing raw data files'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed',
        help='Output directory for processed files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create preparator and run
    preparator = DataPreparator(args.input, args.output, args.verbose)
    success = preparator.prepare_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
