"""
Comprehensive Algorithm Testing Framework
Tests Custom vs Library implementations across multiple workloads and preferences.
"""

import json
import time
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

from models.workload import Workload, ServiceRequirement
from utils.data_loader import DataLoader
from utils.metrics import SolutionEvaluator
from utils.preferences_v2 import UserPreferences

# Custom implementations
from algorithms.nsga2 import NSGA2
from algorithms.moead import MOEAD
from algorithms.spea2 import SPEA2

# Library implementations
from algorithms_library.nsga2_pymoo import NSGA2Pymoo
from algorithms_library.moead_pymoo import MOEADPymoo
from algorithms_library.spea2_platypus import SPEA2Platypus


class ComprehensiveAlgorithmTester:
    """Run comprehensive tests across algorithms, workloads, and preferences."""

    def __init__(self, population_size: int = 50, n_generations: int = 100):
        """
        Initialize tester.

        Args:
            population_size: Population size for algorithms
            n_generations: Number of generations
        """
        self.population_size = population_size
        self.n_generations = n_generations

        # Algorithm configurations
        self.custom_algorithms = {
            'nsga2': NSGA2(),
            'moead': MOEAD(),
            'spea2': SPEA2()
        }

        self.library_algorithms = {
            'nsga2': NSGA2Pymoo(),
            'moead': MOEADPymoo(),
            'spea2': SPEA2Platypus()
        }

        # Load cloud data once
        print("Loading cloud instance data...")
        loader = DataLoader()
        self.all_instances = loader.load_all_instances()
        print(f"Loaded {len(self.all_instances)} cloud instances\n")

        # Results storage
        self.test_results = []

    def load_workload_from_file(self, filepath: str) -> Workload:
        """Load workload configuration from JSON file."""
        with open(filepath, 'r') as f:
            config = json.load(f)

        services = []
        for svc in config['services']:
            services.append(ServiceRequirement(
                name=svc['name'],
                vcpu_min=svc['vcpu_min'],
                ram_gb_min=svc['ram_gb_min'],
                architecture_preference=svc.get('architecture_preference'),
                min_single_core_score=svc.get('min_single_core_score'),
                min_multi_core_score=svc.get('min_multi_core_score'),
                max_hourly_cost=svc.get('max_hourly_cost'),
                latency_requirements=svc.get('latency_requirements', {})
            ))

        return Workload(
            name=config['name'],
            services=services,
            max_total_cost_per_hour=config.get('max_total_cost_per_hour'),
            max_total_cost_per_month=config.get('max_total_cost_per_month'),
            prefer_single_provider=config.get('prefer_single_provider', False),
            prefer_single_region=config.get('prefer_single_region', False)
        )

    def get_compatible_instances(self, workload: Workload) -> List:
        """Filter compatible instances for a workload."""
        compatible = []
        for instance in self.all_instances:
            is_compatible = False
            for service in workload.services:
                if service.is_compatible_with(instance):
                    is_compatible = True
                    break
            if is_compatible:
                compatible.append(instance)
        return compatible

    def run_algorithm(self, algorithm, algorithm_name: str, implementation_type: str,
                     evaluator: SolutionEvaluator, n_variables: int,
                     variable_bounds: Tuple[int, int]) -> Dict:
        """
        Run a single algorithm and return results with timing.

        Args:
            algorithm: Algorithm instance
            algorithm_name: Name of algorithm (nsga2, moead, spea2)
            implementation_type: 'custom' or 'library'
            evaluator: Solution evaluator
            n_variables: Number of variables
            variable_bounds: Variable bounds

        Returns:
            Dictionary with results and metadata
        """
        print(f"  Running {algorithm_name.upper()} ({implementation_type})...", end=" ")

        start_time = time.time()

        try:
            results = algorithm.optimize(
                evaluate_func=lambda sol: evaluator.evaluate(
                    sol.tolist() if hasattr(sol, 'tolist') else list(sol)
                ),
                n_variables=n_variables,
                n_objectives=3,
                variable_bounds=variable_bounds,
                population_size=self.population_size,
                n_generations=self.n_generations
            )

            execution_time = time.time() - start_time

            pareto_front = results['pareto_front']
            pareto_objectives = results['pareto_objectives']

            # Ensure 2D arrays
            if len(pareto_front.shape) == 1:
                pareto_front = pareto_front.reshape(1, -1)
            if len(pareto_objectives.shape) == 1:
                pareto_objectives = pareto_objectives.reshape(1, -1)

            print(f"Done! ({execution_time:.2f}s, {len(pareto_front)} solutions)")

            return {
                'algorithm': algorithm_name,
                'implementation': implementation_type,
                'pareto_front': pareto_front,
                'pareto_objectives': pareto_objectives,
                'pareto_size': len(pareto_front),
                'execution_time': execution_time,
                'success': True
            }

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"Failed! ({str(e)})")

            return {
                'algorithm': algorithm_name,
                'implementation': implementation_type,
                'pareto_front': None,
                'pareto_objectives': None,
                'pareto_size': 0,
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }

    def find_best_solution(self, pareto_objectives: np.ndarray,
                          user_preference: UserPreferences) -> Tuple[int, float, np.ndarray]:
        """
        Find best solution based on user preferences.

        Args:
            pareto_objectives: Pareto front objectives
            user_preference: User preferences

        Returns:
            (best_index, best_score, best_objectives)
        """
        if pareto_objectives is None or len(pareto_objectives) == 0:
            return -1, float('inf'), None

        # Normalize objectives globally across all solutions
        costs = pareto_objectives[:, 0]
        latencies = pareto_objectives[:, 1]
        performances = -pareto_objectives[:, 2]  # Convert to positive

        # Normalize (0-1 scale)
        cost_norm = (costs - costs.min()) / (costs.max() - costs.min() + 1e-10)
        lat_norm = (latencies - latencies.min()) / (latencies.max() - latencies.min() + 1e-10)
        perf_norm = (performances - performances.min()) / (performances.max() - performances.min() + 1e-10)

        # Weighted scores (lower is better)
        weighted_scores = (
            user_preference.cost_weight * cost_norm +
            user_preference.latency_weight * lat_norm +
            user_preference.performance_weight * (1 - perf_norm)  # Invert performance (higher is better)
        )

        best_idx = np.argmin(weighted_scores)
        best_score = weighted_scores[best_idx]
        best_objectives = pareto_objectives[best_idx]

        return best_idx, best_score, best_objectives

    def run_test_case(self, workload_path: str, preference: Tuple[int, int, int],
                     test_id: int) -> Dict:
        """
        Run a single test case with a workload and preference.

        Args:
            workload_path: Path to workload JSON file
            preference: (cost_pct, latency_pct, performance_pct)
            test_id: Test case ID

        Returns:
            Test results dictionary
        """
        cost_pct, lat_pct, perf_pct = preference

        print(f"\n{'=' * 70}")
        print(f"Test Case {test_id}")
        print(f"{'=' * 70}")
        print(f"Workload: {Path(workload_path).name}")
        print(f"Preference: Cost={cost_pct}%, Latency={lat_pct}%, Performance={perf_pct}%")
        print()

        # Load workload
        workload = self.load_workload_from_file(workload_path)

        # Get compatible instances
        compatible_instances = self.get_compatible_instances(workload)
        print(f"Compatible instances: {len(compatible_instances)}")

        if len(compatible_instances) == 0:
            print("WARNING: No compatible instances found!")
            return None

        # Create evaluator
        evaluator = SolutionEvaluator(workload, compatible_instances, normalize=False)

        # Create user preference
        user_pref = UserPreferences.from_percentages(cost_pct, lat_pct, perf_pct)

        # Extract workload metadata
        workload_metadata = {}
        try:
            with open(workload_path, 'r') as f:
                config = json.load(f)
                workload_metadata = config.get('metadata', {})
        except:
            pass

        # Run all algorithms (custom + library)
        all_results = []

        print("\nRunning Custom Implementations:")
        for algo_name, algorithm in self.custom_algorithms.items():
            result = self.run_algorithm(
                algorithm, algo_name, 'custom',
                evaluator, len(workload.services),
                (0, len(compatible_instances) - 1)
            )
            all_results.append(result)

        print("\nRunning Library Implementations:")
        for algo_name, algorithm in self.library_algorithms.items():
            result = self.run_algorithm(
                algorithm, algo_name, 'library',
                evaluator, len(workload.services),
                (0, len(compatible_instances) - 1)
            )
            all_results.append(result)

        # Find best solution for each algorithm
        print("\nFinding best solutions based on user preferences...")

        best_overall = None
        best_overall_score = float('inf')

        for result in all_results:
            if not result['success']:
                continue

            best_idx, best_score, best_obj = self.find_best_solution(
                result['pareto_objectives'], user_pref
            )

            result['best_solution_index'] = best_idx
            result['best_solution_score'] = best_score
            result['best_solution_objectives'] = best_obj

            # Track overall winner
            if best_score < best_overall_score:
                best_overall_score = best_score
                best_overall = result

        # Determine winner
        if best_overall:
            winner_name = f"{best_overall['algorithm']}_{best_overall['implementation']}"
            winner_score = best_overall['best_solution_score']
            winner_obj = best_overall['best_solution_objectives']

            print(f"\nWINNER: {winner_name.upper()}")
            print(f"  Score: {winner_score:.6f}")
            print(f"  Cost: ${winner_obj[0]:.4f}/hr")
            print(f"  Latency: {winner_obj[1]:.2f}ms")
            print(f"  Performance: {-winner_obj[2]:.0f}")
        else:
            winner_name = "NONE"
            winner_score = float('inf')
            winner_obj = None

        # Compile test case result
        test_result = {
            'test_id': test_id,
            'workload_path': workload_path,
            'workload_name': workload.name,
            'workload_metadata': workload_metadata,
            'num_services': len(workload.services),
            'num_compatible_instances': len(compatible_instances),
            'preference_cost': cost_pct,
            'preference_latency': lat_pct,
            'preference_performance': perf_pct,
            'winner_algorithm': winner_name,
            'winner_score': winner_score,
            'winner_objectives': winner_obj.tolist() if winner_obj is not None else None,
            'algorithm_results': all_results
        }

        return test_result

    def run_comprehensive_tests(self, workload_dir: str, preference_file: str,
                               output_dir: str = 'comprehensive_test_results',
                               limit: int = None) -> str:
        """
        Run comprehensive tests across all workloads and preferences.

        Args:
            workload_dir: Directory containing workload JSON files
            preference_file: JSON file containing preferences
            output_dir: Output directory for results
            limit: Limit number of test cases (for testing)

        Returns:
            Path to results CSV file
        """
        # Load workloads
        workload_files = sorted(Path(workload_dir).glob('workload_*.json'))
        print(f"Found {len(workload_files)} workload files")

        # Load preferences
        with open(preference_file, 'r') as f:
            pref_data = json.load(f)
            preferences = [
                (p['cost_weight'], p['latency_weight'], p['performance_weight'])
                for p in pref_data['preferences']
            ]
        print(f"Loaded {len(preferences)} preference combinations")

        # Calculate total tests
        total_tests = len(workload_files) * len(preferences)
        if limit:
            total_tests = min(total_tests, limit)

        print(f"\nTotal test cases to run: {total_tests}")
        print(f"Population size: {self.population_size}")
        print(f"Generations: {self.n_generations}")
        print(f"Algorithms: 6 (3 custom + 3 library)")
        print()

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Run tests
        test_id = 1
        for workload_file in workload_files:
            for preference in preferences:
                if limit and test_id > limit:
                    break

                test_result = self.run_test_case(
                    str(workload_file), preference, test_id
                )

                if test_result:
                    self.test_results.append(test_result)

                test_id += 1

            if limit and test_id > limit:
                break

        # Save results
        csv_path = self.save_results_to_csv(output_path)
        json_path = self.save_results_to_json(output_path)
        summary_path = self.generate_summary(output_path)

        print(f"\n{'=' * 70}")
        print(f"TESTING COMPLETE!")
        print(f"{'=' * 70}")
        print(f"Total tests run: {len(self.test_results)}")
        print(f"Results saved to:")
        print(f"  - CSV: {csv_path}")
        print(f"  - JSON: {json_path}")
        print(f"  - Summary: {summary_path}")
        print(f"{'=' * 70}")

        return csv_path

    def save_results_to_csv(self, output_dir: Path) -> str:
        """Save results to CSV file."""
        csv_path = output_dir / 'test_results.csv'

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            header = [
                'Test_ID', 'Workload_Name', 'Workload_File',
                'Size_Category', 'Num_Services', 'Latency_Profile',
                'Num_Compatible_Instances',
                'Pref_Cost%', 'Pref_Latency%', 'Pref_Performance%',
                'Winner_Algorithm', 'Winner_Implementation', 'Winner_Score',
                'Winner_Cost', 'Winner_Latency', 'Winner_Performance',
            ]

            # Add columns for each algorithm result
            algo_names = ['nsga2_custom', 'moead_custom', 'spea2_custom',
                         'nsga2_library', 'moead_library', 'spea2_library']

            for algo in algo_names:
                header.extend([
                    f'{algo}_pareto_size',
                    f'{algo}_exec_time',
                    f'{algo}_best_score',
                    f'{algo}_best_cost',
                    f'{algo}_best_latency',
                    f'{algo}_best_performance'
                ])

            writer.writerow(header)

            # Data rows
            for result in self.test_results:
                meta = result['workload_metadata']

                # Parse winner
                winner_parts = result['winner_algorithm'].split('_')
                winner_algo = winner_parts[0] if len(winner_parts) > 0 else 'NONE'
                winner_impl = winner_parts[1] if len(winner_parts) > 1 else 'NONE'

                winner_obj = result['winner_objectives']
                if winner_obj:
                    winner_cost = winner_obj[0]
                    winner_lat = winner_obj[1]
                    winner_perf = -winner_obj[2]
                else:
                    winner_cost = winner_lat = winner_perf = None

                row = [
                    result['test_id'],
                    result['workload_name'],
                    Path(result['workload_path']).name,
                    meta.get('size_category', 'unknown'),
                    result['num_services'],
                    meta.get('latency_profile', 'unknown'),
                    result['num_compatible_instances'],
                    result['preference_cost'],
                    result['preference_latency'],
                    result['preference_performance'],
                    winner_algo,
                    winner_impl,
                    f"{result['winner_score']:.6f}" if result['winner_score'] != float('inf') else 'INF',
                    f"{winner_cost:.4f}" if winner_cost is not None else '',
                    f"{winner_lat:.2f}" if winner_lat is not None else '',
                    f"{winner_perf:.0f}" if winner_perf is not None else '',
                ]

                # Add algorithm-specific data
                algo_results_dict = {
                    f"{r['algorithm']}_{r['implementation']}": r
                    for r in result['algorithm_results']
                }

                for algo_name in algo_names:
                    r = algo_results_dict.get(algo_name, {})
                    if r and r.get('success'):
                        best_obj = r.get('best_solution_objectives')
                        row.extend([
                            r.get('pareto_size', 0),
                            f"{r.get('execution_time', 0):.2f}",
                            f"{r.get('best_solution_score', float('inf')):.6f}",
                            f"{best_obj[0]:.4f}" if best_obj is not None else '',
                            f"{best_obj[1]:.2f}" if best_obj is not None else '',
                            f"{-best_obj[2]:.0f}" if best_obj is not None else '',
                        ])
                    else:
                        row.extend(['', '', '', '', '', ''])

                writer.writerow(row)

        print(f"\nCSV results saved to: {csv_path}")
        return str(csv_path)

    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to Python native types."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        else:
            return obj

    def save_results_to_json(self, output_dir: Path) -> str:
        """Save detailed results to JSON file."""
        json_path = output_dir / 'test_results_detailed.json'

        # Convert numpy arrays and types to Python native types
        serializable_results = []
        for result in self.test_results:
            # Deep copy and convert all numpy types
            serializable = self._convert_numpy_types(result)
            serializable_results.append(serializable)

        output_data = {
            'test_configuration': {
                'population_size': self.population_size,
                'n_generations': self.n_generations,
                'algorithms_tested': 6,
                'total_test_cases': len(self.test_results)
            },
            'results': serializable_results
        }

        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Detailed JSON results saved to: {json_path}")
        return str(json_path)

    def generate_summary(self, output_dir: Path) -> str:
        """Generate summary report."""
        summary_path = output_dir / 'test_summary.txt'

        with open(summary_path, 'w') as f:
            f.write("COMPREHENSIVE ALGORITHM TESTING SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total test cases: {len(self.test_results)}\n")
            f.write(f"Population size: {self.population_size}\n")
            f.write(f"Generations: {self.n_generations}\n\n")

            # Winner distribution
            f.write("WINNER DISTRIBUTION\n")
            f.write("-" * 70 + "\n")

            winner_counts = {}
            for result in self.test_results:
                winner = result['winner_algorithm']
                winner_counts[winner] = winner_counts.get(winner, 0) + 1

            for winner, count in sorted(winner_counts.items(), key=lambda x: -x[1]):
                pct = (count / len(self.test_results)) * 100
                f.write(f"{winner:25s}: {count:4d} ({pct:5.1f}%)\n")

            # By implementation type
            f.write("\n\nWINNER BY IMPLEMENTATION TYPE\n")
            f.write("-" * 70 + "\n")

            impl_counts = {'custom': 0, 'library': 0, 'none': 0}
            for result in self.test_results:
                winner = result['winner_algorithm']
                if 'custom' in winner:
                    impl_counts['custom'] += 1
                elif 'library' in winner:
                    impl_counts['library'] += 1
                else:
                    impl_counts['none'] += 1

            for impl_type, count in sorted(impl_counts.items(), key=lambda x: -x[1]):
                pct = (count / len(self.test_results)) * 100
                f.write(f"{impl_type:25s}: {count:4d} ({pct:5.1f}%)\n")

            # By algorithm (regardless of implementation)
            f.write("\n\nWINNER BY ALGORITHM TYPE\n")
            f.write("-" * 70 + "\n")

            algo_counts = {}
            for result in self.test_results:
                winner = result['winner_algorithm']
                algo_name = winner.split('_')[0] if '_' in winner else winner
                algo_counts[algo_name] = algo_counts.get(algo_name, 0) + 1

            for algo, count in sorted(algo_counts.items(), key=lambda x: -x[1]):
                pct = (count / len(self.test_results)) * 100
                f.write(f"{algo:25s}: {count:4d} ({pct:5.1f}%)\n")

        print(f"Summary report saved to: {summary_path}")
        return str(summary_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive Algorithm Testing Framework'
    )
    parser.add_argument('--workload-dir', required=True,
                       help='Directory containing workload JSON files')
    parser.add_argument('--preference-file', required=True,
                       help='JSON file containing user preferences')
    parser.add_argument('--population', type=int, default=50,
                       help='Population size (default: 50)')
    parser.add_argument('--generations', type=int, default=100,
                       help='Number of generations (default: 100)')
    parser.add_argument('--output-dir', default='comprehensive_test_results',
                       help='Output directory')
    parser.add_argument('--limit', type=int,
                       help='Limit number of test cases (for testing)')

    args = parser.parse_args()

    print("=" * 70)
    print("COMPREHENSIVE ALGORITHM TESTING FRAMEWORK")
    print("=" * 70)
    print()

    tester = ComprehensiveAlgorithmTester(
        population_size=args.population,
        n_generations=args.generations
    )

    tester.run_comprehensive_tests(
        workload_dir=args.workload_dir,
        preference_file=args.preference_file,
        output_dir=args.output_dir,
        limit=args.limit
    )


if __name__ == '__main__':
    main()
