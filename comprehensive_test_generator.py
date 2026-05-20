"""
Comprehensive test generator for multi-cloud optimization research.

This script generates ~1000 test cases with:
- Varying application sizes (small, medium, large, extra-large)
- Varying CPU/memory specifications
- Varying user preference weights (cost, latency, performance)
- Runs all three algorithms (NSGA-II, MOEA/D, SPEA2) on each configuration
- Analyzes which algorithm performs best under different conditions
"""

import argparse
import json
import itertools
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import csv
from datetime import datetime

from models.workload import Workload, ServiceRequirement
from utils.data_loader import DataLoader
from utils.metrics import SolutionEvaluator
from utils.preferences_v2 import UserPreferences, AlgorithmSelectorV2
from algorithms.nsga2 import NSGA2
from algorithms.moead import MOEAD
from algorithms.spea2 import SPEA2


# Define application size categories
APP_SIZES = {
    "small": {
        "num_services": 2,
        "vcpu_range": (1, 2),
        "ram_range": (2, 4),
        "description": "Small application (2 services, 1-2 CPU, 2-4GB RAM)"
    },
    "medium": {
        "num_services": 3,
        "vcpu_range": (2, 4),
        "ram_range": (4, 8),
        "description": "Medium application (3 services, 2-4 CPU, 4-8GB RAM)"
    },
    "large": {
        "num_services": 5,
        "vcpu_range": (4, 8),
        "ram_range": (8, 16),
        "description": "Large application (5 services, 4-8 CPU, 8-16GB RAM)"
    },
    "extra_large": {
        "num_services": 7,
        "vcpu_range": (8, 16),
        "ram_range": (16, 32),
        "description": "Extra-large application (7 services, 8-16 CPU, 16-32GB RAM)"
    }
}

# Define preference weight combinations
# Format: (cost%, latency%, performance%)
PREFERENCE_COMBINATIONS = [
    # Balanced
    (33, 33, 34),

    # Cost-focused
    (70, 15, 15),
    (60, 20, 20),
    (50, 25, 25),

    # Latency-focused
    (15, 70, 15),
    (20, 60, 20),
    (25, 50, 25),

    # Performance-focused
    (15, 15, 70),
    (20, 20, 60),
    (25, 25, 50),

    # Two-objective focused
    (45, 45, 10),  # Cost + Latency
    (45, 10, 45),  # Cost + Performance
    (10, 45, 45),  # Latency + Performance
]


def generate_workload(size_category: str, instance_id: int) -> Workload:
    """
    Generate a workload configuration based on size category.

    Args:
        size_category: One of "small", "medium", "large", "extra_large"
        instance_id: Unique identifier for this workload instance

    Returns:
        Workload object
    """
    config = APP_SIZES[size_category]
    num_services = config["num_services"]
    vcpu_min, vcpu_max = config["vcpu_range"]
    ram_min, ram_max = config["ram_range"]

    services = []

    # Generate services with varying specifications
    for i in range(num_services):
        # Randomly vary specs within the range
        vcpu = np.random.randint(vcpu_min, vcpu_max + 1)
        ram = np.random.choice([ram_min, (ram_min + ram_max) // 2, ram_max])

        # Add latency requirements to some services
        latency_reqs = {}
        if i < num_services - 1:
            # Service can communicate with 1-2 other services
            num_deps = min(2, num_services - i - 1)
            for j in range(i + 1, min(i + 1 + num_deps, num_services)):
                # Latency requirements: 10ms, 20ms, 50ms, or 100ms
                latency_reqs[f"service_{j}"] = np.random.choice([10, 20, 50, 100])

        service = ServiceRequirement(
            name=f"service_{i}",
            vcpu_min=vcpu,
            ram_gb_min=ram,
            min_multi_core_score=vcpu * 1000,  # Approximate score based on CPU
            latency_requirements=latency_reqs
        )
        services.append(service)

    return Workload(
        name=f"{size_category}_workload_{instance_id}",
        services=services,
        max_total_cost_per_hour=None  # No hard cost limit
    )


def run_single_test(
    test_id: int,
    workload: Workload,
    preferences: UserPreferences,
    compatible_instances: List,
    population_size: int = 30,
    n_generations: int = 50
) -> Dict:
    """
    Run all three algorithms on a single test configuration.

    Returns:
        Dictionary with test results
    """
    evaluator = SolutionEvaluator(workload, compatible_instances, normalize=False)

    results = {}

    # Run each algorithm
    for algo_name in ['nsga2', 'moead', 'spea2']:
        if algo_name == 'nsga2':
            algorithm = NSGA2()
        elif algo_name == 'moead':
            algorithm = MOEAD()
        else:
            algorithm = SPEA2()

        # Run optimization
        algo_results = algorithm.optimize(
            evaluate_func=lambda sol: evaluator.evaluate(sol.tolist()),
            n_variables=len(workload.services),
            n_objectives=3,
            variable_bounds=(0, len(compatible_instances) - 1),
            population_size=population_size,
            n_generations=n_generations
        )

        results[algo_name] = algo_results

    # Determine best algorithm using global normalization
    selector = AlgorithmSelectorV2(preferences)
    selection = selector.select_best_solutions_globally(results, top_k=1)

    best_algorithm = selection['top_solutions'][0]['algorithm']
    best_score = selection['top_solutions'][0]['weighted_score']
    best_objectives = selection['top_solutions'][0]['objectives']

    # Collect statistics
    test_result = {
        'test_id': test_id,
        'workload_name': workload.name,
        'num_services': len(workload.services),
        'preferences': {
            'cost': preferences.cost_weight,
            'latency': preferences.latency_weight,
            'performance': preferences.performance_weight
        },
        'best_algorithm': best_algorithm,
        'best_score': float(best_score),
        'best_cost': float(best_objectives[0]),
        'best_latency': float(best_objectives[1]),
        'best_performance': float(-best_objectives[2]),
        'algorithm_scores': {
            algo: {
                'pareto_size': len(results[algo]['pareto_front']),
                'min_cost': float(np.min(results[algo]['pareto_objectives'][:, 0])),
                'max_cost': float(np.max(results[algo]['pareto_objectives'][:, 0])),
                'min_latency': float(np.min(results[algo]['pareto_objectives'][:, 1])),
                'max_latency': float(np.max(results[algo]['pareto_objectives'][:, 1])),
                'min_performance': float(-np.max(results[algo]['pareto_objectives'][:, 2])),
                'max_performance': float(-np.min(results[algo]['pareto_objectives'][:, 2]))
            }
            for algo in ['nsga2', 'moead', 'spea2']
        }
    }

    return test_result


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Comprehensive test generator for algorithm comparison'
    )
    parser.add_argument('--output-dir', type=str, default='comprehensive_test_results',
                       help='Output directory for results')
    parser.add_argument('--population', type=int, default=30,
                       help='Population size (smaller for speed)')
    parser.add_argument('--generations', type=int, default=50,
                       help='Number of generations (smaller for speed)')
    parser.add_argument('--tests-per-config', type=int, default=3,
                       help='Number of test instances per configuration')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')

    args = parser.parse_args()

    # Set random seed
    np.random.seed(args.seed)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load cloud instances once
    print("Loading cloud instance data...")
    loader = DataLoader()
    all_instances = loader.load_all_instances()
    print(f"Loaded {len(all_instances)} cloud instances")

    # Generate all test configurations
    print("\nGenerating test configurations...")
    test_configs = []
    test_id = 0

    for size_category in APP_SIZES.keys():
        for pref in PREFERENCE_COMBINATIONS:
            for instance_num in range(args.tests_per_config):
                # Create workload
                workload = generate_workload(size_category, instance_num)

                # Create preferences
                preferences = UserPreferences.from_percentages(pref[0], pref[1], pref[2])

                # Filter compatible instances
                compatible = []
                for instance in all_instances:
                    is_compatible = any(
                        service.is_compatible_with(instance)
                        for service in workload.services
                    )
                    if is_compatible:
                        compatible.append(instance)

                if len(compatible) > 0:
                    test_configs.append({
                        'test_id': test_id,
                        'size_category': size_category,
                        'workload': workload,
                        'preferences': preferences,
                        'compatible_instances': compatible
                    })
                    test_id += 1

    total_tests = len(test_configs)
    print(f"Generated {total_tests} test configurations")
    print(f"  - {len(APP_SIZES)} app sizes")
    print(f"  - {len(PREFERENCE_COMBINATIONS)} preference combinations")
    print(f"  - {args.tests_per_config} instances per config")

    # Run tests
    print(f"\nRunning {total_tests} tests...")
    print(f"Population size: {args.population}, Generations: {args.generations}")
    print("-" * 70)

    all_results = []

    for i, config in enumerate(test_configs, 1):
        print(f"\nTest {i}/{total_tests}: {config['size_category']} - "
              f"Prefs: C={config['preferences'].cost_weight:.0%} "
              f"L={config['preferences'].latency_weight:.0%} "
              f"P={config['preferences'].performance_weight:.0%}")

        result = run_single_test(
            test_id=config['test_id'],
            workload=config['workload'],
            preferences=config['preferences'],
            compatible_instances=config['compatible_instances'],
            population_size=args.population,
            n_generations=args.generations
        )

        all_results.append(result)

        print(f"  Best algorithm: {result['best_algorithm'].upper()} "
              f"(Score: {result['best_score']:.4f})")
        print(f"  Cost: ${result['best_cost']:.4f}, "
              f"Latency: {result['best_latency']:.2f}ms, "
              f"Performance: {result['best_performance']:.0f}")

        # Save incremental progress
        if i % 10 == 0:
            interim_file = output_dir / f"results_interim_{i}.json"
            with open(interim_file, 'w') as f:
                json.dump(all_results, f, indent=2)

    # Save final results
    print(f"\n{'=' * 70}")
    print("All tests complete! Saving results...")

    # Save detailed JSON
    results_file = output_dir / "all_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Detailed results saved to {results_file}")

    # Create summary CSV
    summary_file = output_dir / "summary.csv"
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'test_id', 'workload_name', 'num_services',
            'cost_pref', 'latency_pref', 'performance_pref',
            'best_algorithm', 'best_score',
            'best_cost', 'best_latency', 'best_performance'
        ])

        for result in all_results:
            writer.writerow([
                result['test_id'],
                result['workload_name'],
                result['num_services'],
                f"{result['preferences']['cost']:.0%}",
                f"{result['preferences']['latency']:.0%}",
                f"{result['preferences']['performance']:.0%}",
                result['best_algorithm'],
                f"{result['best_score']:.4f}",
                f"{result['best_cost']:.4f}",
                f"{result['best_latency']:.2f}",
                f"{result['best_performance']:.0f}"
            ])

    print(f"Summary CSV saved to {summary_file}")

    # Generate analysis
    print(f"\n{'=' * 70}")
    print("ANALYSIS SUMMARY")
    print('=' * 70)

    # Algorithm win counts
    algo_wins = {'nsga2': 0, 'moead': 0, 'spea2': 0}
    for result in all_results:
        algo_wins[result['best_algorithm']] += 1

    print("\nAlgorithm Performance:")
    for algo, wins in sorted(algo_wins.items(), key=lambda x: x[1], reverse=True):
        percentage = (wins / total_tests) * 100
        print(f"  {algo.upper()}: {wins}/{total_tests} tests ({percentage:.1f}%)")

    # Performance by application size
    print("\nPerformance by Application Size:")
    for size in APP_SIZES.keys():
        size_results = [r for r in all_results if size in r['workload_name']]
        if size_results:
            size_algo_wins = {'nsga2': 0, 'moead': 0, 'spea2': 0}
            for r in size_results:
                size_algo_wins[r['best_algorithm']] += 1

            print(f"\n  {size.upper()}:")
            for algo, wins in sorted(size_algo_wins.items(), key=lambda x: x[1], reverse=True):
                percentage = (wins / len(size_results)) * 100
                print(f"    {algo.upper()}: {wins}/{len(size_results)} ({percentage:.1f}%)")

    # Performance by preference type
    print("\nPerformance by Preference Type:")

    # Categorize preferences
    for pref_type, condition in [
        ("Cost-focused", lambda p: p['cost'] >= 0.5),
        ("Latency-focused", lambda p: p['latency'] >= 0.5),
        ("Performance-focused", lambda p: p['performance'] >= 0.5),
        ("Balanced", lambda p: max(p['cost'], p['latency'], p['performance']) < 0.5)
    ]:
        pref_results = [r for r in all_results if condition(r['preferences'])]
        if pref_results:
            pref_algo_wins = {'nsga2': 0, 'moead': 0, 'spea2': 0}
            for r in pref_results:
                pref_algo_wins[r['best_algorithm']] += 1

            print(f"\n  {pref_type}:")
            for algo, wins in sorted(pref_algo_wins.items(), key=lambda x: x[1], reverse=True):
                percentage = (wins / len(pref_results)) * 100
                print(f"    {algo.upper()}: {wins}/{len(pref_results)} ({percentage:.1f}%)")

    print(f"\n{'=' * 70}")
    print(f"Results saved to: {output_dir}/")
    print('=' * 70)


if __name__ == "__main__":
    main()
