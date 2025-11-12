#!/usr/bin/env python3
"""
Generate sample data files for testing and demonstration.

This script creates sample Terraform plans and CMDB applications
for each pattern type, which can be used to test the validation system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.test_data.generators import save_sample_data_files

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample data files")
    parser.add_argument(
        "--output-dir",
        default="./examples",
        help="Output directory for sample files (default: ./examples)"
    )

    args = parser.parse_args()

    print(f"Generating sample data files in {args.output_dir}...")
    save_sample_data_files(args.output_dir)
    print("Done!")
    print(f"\nGenerated files can be used with:")
    print(f"  python validate.py validate --terraform-plan {args.output_dir}/sample_3_tier_plan.json")
