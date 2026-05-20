"""Compare custom vs library algorithm implementations."""

import json
import numpy as np
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List
import pandas as pd


def load_test_results(results_file: str) -> Dict:
    """Load test results from JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)


def compare_pareto_fronts(custom_obj: np.ndarray, library_obj: np.ndarray) -> Dict:
    """Compare Pareto fronts from custom and library implementations.

    Returns metrics:
    - Size difference
    - Objective value differences (mean, max)
    - Overlap/similarity metrics
    """
    comparison = {}

    # Size comparison
    comparison['custom_size'] = len(custom_obj)
    comparison['library_size'] = len(library_obj)
    comparison['size_difference'] = abs(len(custom_obj) - len(library_obj))
    comparison['size_ratio'] = len(library_obj) / len(custom_obj) if len(custom_obj) > 0 else 0

    # Objective statistics
    for impl_name, obj in [('custom', custom_obj), ('library', library_obj)]:
        comparison[f'{impl_name}_cost_mean'] = np.mean(obj[:, 0])
        comparison[f'{impl_name}_cost_std'] = np.std(obj[:, 0])
        comparison[f'{impl_name}_latency_mean'] = np.mean(obj[:, 1])
        comparison[f'{impl_name}_latency_std'] = np.std(obj[:, 1])
        comparison[f'{impl_name}_performance_mean'] = np.mean(-obj[:, 2])
        comparison[f'{impl_name}_performance_std'] = np.std(-obj[:, 2])

    # Difference in means
    comparison['cost_mean_diff'] = abs(comparison['custom_cost_mean'] - comparison['library_cost_mean'])
    comparison['latency_mean_diff'] = abs(comparison['custom_latency_mean'] - comparison['library_latency_mean'])
    comparison['performance_mean_diff'] = abs(comparison['custom_performance_mean'] - comparison['library_performance_mean'])

    # Relative differences (percentage)
    comparison['cost_mean_diff_pct'] = (comparison['cost_mean_diff'] / comparison['custom_cost_mean'] * 100) if comparison['custom_cost_mean'] > 0 else 0
    comparison['latency_mean_diff_pct'] = (comparison['latency_mean_diff'] / comparison['custom_latency_mean'] * 100) if comparison['custom_latency_mean'] > 0 else 0
    comparison['performance_mean_diff_pct'] = (comparison['performance_mean_diff'] / comparison['custom_performance_mean'] * 100) if comparison['custom_performance_mean'] > 0 else 0

    return comparison


def classify_similarity(comparison: Dict) -> str:
    """Classify results as Identical, Similar, or Different.

    Criteria:
    - Identical: All metrics differ by < 1%
    - Similar: All metrics differ by < 10%
    - Different: Any metric differs by >= 10%
    """
    max_diff = max(
        comparison['cost_mean_diff_pct'],
        comparison['latency_mean_diff_pct'],
        comparison['performance_mean_diff_pct']
    )

    if max_diff < 1.0:
        return "IDENTICAL"
    elif max_diff < 10.0:
        return "SIMILAR"
    else:
        return "DIFFERENT"


def compare_algorithm_results(custom_dir: Path, library_dir: Path, algorithm: str) -> Dict:
    """Compare results for a single algorithm."""

    # Load custom results
    custom_results_file = custom_dir / algorithm / "results.json"
    library_results_file = library_dir / algorithm / "results.json"

    if not custom_results_file.exists():
        print(f"Warning: Custom results not found for {algorithm}")
        return None

    if not library_results_file.exists():
        print(f"Warning: Library results not found for {algorithm}")
        return None

    custom_results = load_test_results(custom_results_file)
    library_results = load_test_results(library_results_file)

    custom_obj = np.array(custom_results['pareto_objectives'])
    library_obj = np.array(library_results['pareto_objectives'])

    comparison = compare_pareto_fronts(custom_obj, library_obj)
    comparison['algorithm'] = algorithm
    comparison['similarity'] = classify_similarity(comparison)

    return comparison


def generate_comparison_report(comparisons: List[Dict], output_file: str):
    """Generate comprehensive comparison report."""

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("CUSTOM vs LIBRARY IMPLEMENTATION COMPARISON REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary table
    report_lines.append("SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Algorithm':<12} {'Similarity':<12} {'Size Diff':<12} "
                       f"{'Cost Diff %':<12} {'Latency Diff %':<15} {'Perf Diff %':<12}")
    report_lines.append("-" * 80)

    for comp in comparisons:
        if comp is None:
            continue
        report_lines.append(
            f"{comp['algorithm'].upper():<12} "
            f"{comp['similarity']:<12} "
            f"{comp['size_difference']:<12} "
            f"{comp['cost_mean_diff_pct']:<12.2f} "
            f"{comp['latency_mean_diff_pct']:<15.2f} "
            f"{comp['performance_mean_diff_pct']:<12.2f}"
        )

    report_lines.append("")
    report_lines.append("")

    # Detailed comparison per algorithm
    for comp in comparisons:
        if comp is None:
            continue

        report_lines.append("=" * 80)
        report_lines.append(f"{comp['algorithm'].upper()} - DETAILED COMPARISON")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append(f"Classification: {comp['similarity']}")
        report_lines.append("")

        report_lines.append("Pareto Front Sizes:")
        report_lines.append(f"  Custom:  {comp['custom_size']}")
        report_lines.append(f"  Library: {comp['library_size']}")
        report_lines.append(f"  Difference: {comp['size_difference']} ({comp['size_ratio']:.2f}x)")
        report_lines.append("")

        report_lines.append("Cost:")
        report_lines.append(f"  Custom:  ${comp['custom_cost_mean']:.4f} ± ${comp['custom_cost_std']:.4f}")
        report_lines.append(f"  Library: ${comp['library_cost_mean']:.4f} ± ${comp['library_cost_std']:.4f}")
        report_lines.append(f"  Difference: ${comp['cost_mean_diff']:.4f} ({comp['cost_mean_diff_pct']:.2f}%)")
        report_lines.append("")

        report_lines.append("Latency:")
        report_lines.append(f"  Custom:  {comp['custom_latency_mean']:.2f} ± {comp['custom_latency_std']:.2f} ms")
        report_lines.append(f"  Library: {comp['library_latency_mean']:.2f} ± {comp['library_latency_std']:.2f} ms")
        report_lines.append(f"  Difference: {comp['latency_mean_diff']:.2f} ms ({comp['latency_mean_diff_pct']:.2f}%)")
        report_lines.append("")

        report_lines.append("Performance:")
        report_lines.append(f"  Custom:  {comp['custom_performance_mean']:.0f} ± {comp['custom_performance_std']:.0f}")
        report_lines.append(f"  Library: {comp['library_performance_mean']:.0f} ± {comp['library_performance_std']:.0f}")
        report_lines.append(f"  Difference: {comp['performance_mean_diff']:.0f} ({comp['performance_mean_diff_pct']:.2f}%)")
        report_lines.append("")
        report_lines.append("")

    # Overall assessment
    report_lines.append("=" * 80)
    report_lines.append("OVERALL ASSESSMENT")
    report_lines.append("=" * 80)
    report_lines.append("")

    identical_count = sum(1 for c in comparisons if c and c['similarity'] == 'IDENTICAL')
    similar_count = sum(1 for c in comparisons if c and c['similarity'] == 'SIMILAR')
    different_count = sum(1 for c in comparisons if c and c['similarity'] == 'DIFFERENT')
    total = len([c for c in comparisons if c is not None])

    report_lines.append(f"Total Algorithms Compared: {total}")
    report_lines.append(f"  IDENTICAL: {identical_count} ({identical_count/total*100:.1f}%)")
    report_lines.append(f"  SIMILAR:   {similar_count} ({similar_count/total*100:.1f}%)")
    report_lines.append(f"  DIFFERENT: {different_count} ({different_count/total*100:.1f}%)")
    report_lines.append("")

    if identical_count == total:
        conclusion = "All implementations produce IDENTICAL results. Library implementations are validated."
    elif identical_count + similar_count == total:
        conclusion = "All implementations produce IDENTICAL or SIMILAR results. Library implementations are reliable."
    else:
        conclusion = "Some implementations show DIFFERENT results. Further investigation recommended."

    report_lines.append(f"Conclusion: {conclusion}")
    report_lines.append("")

    # Write report
    report_text = "\n".join(report_lines)

    with open(output_file, 'w') as f:
        f.write(report_text)

    print(report_text)
    print(f"\nComparison report saved to: {output_file}")


def main():
    """Main comparison execution."""
    parser = argparse.ArgumentParser(description='Compare Custom vs Library Implementations')
    parser.add_argument('--custom-dir', type=str, default='results_v2',
                       help='Directory with custom implementation results')
    parser.add_argument('--library-dir', type=str, default='results_v3',
                       help='Directory with library implementation results')
    parser.add_argument('--output', type=str, default='comparison_report.txt',
                       help='Output report file')
    parser.add_argument('--algorithms', nargs='+', default=['nsga2', 'moead', 'spea2'],
                       help='Algorithms to compare')

    args = parser.parse_args()

    custom_dir = Path(args.custom_dir)
    library_dir = Path(args.library_dir)

    print("=" * 80)
    print("COMPARING CUSTOM vs LIBRARY IMPLEMENTATIONS")
    print("=" * 80)
    print(f"Custom directory:  {custom_dir}")
    print(f"Library directory: {library_dir}")
    print(f"Algorithms:        {', '.join(args.algorithms)}")
    print()

    # Compare each algorithm
    comparisons = []
    for algorithm in args.algorithms:
        print(f"Comparing {algorithm.upper()}...")
        comparison = compare_algorithm_results(custom_dir, library_dir, algorithm)
        comparisons.append(comparison)
        if comparison:
            print(f"  Result: {comparison['similarity']}")
        print()

    # Generate report
    generate_comparison_report(comparisons, args.output)


if __name__ == "__main__":
    main()
