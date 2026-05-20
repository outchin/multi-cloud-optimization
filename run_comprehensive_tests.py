"""
Master Script for Running Comprehensive Algorithm Tests
Orchestrates workload generation, preference generation, and testing.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\nERROR: {description} failed!")
        sys.exit(1)

    print(f"\n{description} completed successfully!")


def main():
    """Main orchestration script."""
    parser = argparse.ArgumentParser(
        description='Run comprehensive algorithm testing pipeline'
    )

    # Workload generation options
    parser.add_argument('--workload-dir', default='test_workloads',
                       help='Directory for generated workloads')
    parser.add_argument('--sizes', nargs='+',
                       default=['tiny', 'small', 'medium', 'large', 'xlarge'],
                       choices=['tiny', 'small', 'medium', 'large', 'xlarge'],
                       help='Size categories to generate')
    parser.add_argument('--services', nargs='+', type=int,
                       default=[3, 5, 7],
                       help='Service counts to generate')
    parser.add_argument('--latency-profiles', nargs='+',
                       default=['strict', 'moderate', 'relaxed'],
                       choices=['strict', 'moderate', 'relaxed'],
                       help='Latency profiles to generate')

    # Preference generation options
    parser.add_argument('--preference-dir', default='test_preferences',
                       help='Directory for generated preferences')
    parser.add_argument('--preference-mode', default='diverse',
                       choices=['diverse', 'systematic', 'preset'],
                       help='Preference generation mode')
    parser.add_argument('--preference-count', type=int, default=50,
                       help='Number of preferences (for diverse mode)')

    # Testing options
    parser.add_argument('--population', type=int, default=50,
                       help='Population size for algorithms')
    parser.add_argument('--generations', type=int, default=100,
                       help='Number of generations')
    parser.add_argument('--output-dir', default='comprehensive_test_results',
                       help='Output directory for test results')
    parser.add_argument('--test-limit', type=int,
                       help='Limit number of test cases (for quick testing)')

    # Pipeline control
    parser.add_argument('--skip-workload-gen', action='store_true',
                       help='Skip workload generation step')
    parser.add_argument('--skip-preference-gen', action='store_true',
                       help='Skip preference generation step')
    parser.add_argument('--only-generate', action='store_true',
                       help='Only generate workloads and preferences, skip testing')

    args = parser.parse_args()

    print("=" * 70)
    print("COMPREHENSIVE ALGORITHM TESTING PIPELINE")
    print("=" * 70)
    print()
    print("This pipeline will:")
    print("  1. Generate test workloads (if not skipped)")
    print("  2. Generate user preference combinations (if not skipped)")
    print("  3. Run comprehensive tests across all combinations (if not skipped)")
    print()

    # Step 1: Generate workloads
    if not args.skip_workload_gen:
        workload_cmd = [
            'python3', 'workload_generator.py',
            '--output-dir', args.workload_dir,
            '--sizes', *args.sizes,
            '--services', *map(str, args.services),
            '--latency', *args.latency_profiles
        ]

        run_command(workload_cmd, "Step 1: Generating Test Workloads")
    else:
        print("\nSkipping workload generation (using existing workloads)")

    # Step 2: Generate preferences
    if not args.skip_preference_gen:
        preference_cmd = [
            'python3', 'preference_generator.py',
            '--output-dir', args.preference_dir,
            '--mode', args.preference_mode,
            '--count', str(args.preference_count)
        ]

        run_command(preference_cmd, "Step 2: Generating User Preferences")
    else:
        print("\nSkipping preference generation (using existing preferences)")

    # Determine preference file path
    if args.preference_mode == 'diverse':
        preference_file = Path(args.preference_dir) / f'preferences_diverse_{args.preference_count}.json'
    elif args.preference_mode == 'systematic':
        preference_file = Path(args.preference_dir) / 'preferences_systematic_step10.json'
    else:  # preset
        preference_file = Path(args.preference_dir) / 'preferences_preset.json'

    # Check if preference file exists
    if not preference_file.exists():
        print(f"\nERROR: Preference file not found: {preference_file}")
        print("Please run preference generation first or check the file path.")
        sys.exit(1)

    # Exit if only generating
    if args.only_generate:
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nWorkloads directory: {args.workload_dir}")
        print(f"Preferences file: {preference_file}")
        print("\nTo run tests, execute this script again without --only-generate")
        return

    # Step 3: Run comprehensive tests
    test_cmd = [
        'python3', 'comprehensive_algorithm_tester.py',
        '--workload-dir', args.workload_dir,
        '--preference-file', str(preference_file),
        '--population', str(args.population),
        '--generations', str(args.generations),
        '--output-dir', args.output_dir
    ]

    if args.test_limit:
        test_cmd.extend(['--limit', str(args.test_limit)])

    run_command(test_cmd, "Step 3: Running Comprehensive Tests")

    # Final summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print("\nResults saved to:")
    print(f"  - Workloads: {args.workload_dir}/")
    print(f"  - Preferences: {preference_file}")
    print(f"  - Test Results: {args.output_dir}/")
    print()
    print("Key result files:")
    print(f"  - CSV: {args.output_dir}/test_results.csv")
    print(f"  - Summary: {args.output_dir}/test_summary.txt")
    print(f"  - Detailed JSON: {args.output_dir}/test_results_detailed.json")
    print("=" * 70)


if __name__ == '__main__':
    main()
