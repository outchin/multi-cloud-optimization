"""Main entry point for multi-cloud optimization."""

import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from models.workload import Workload, ServiceRequirement
from utils.data_loader import DataLoader
from utils.metrics import SolutionEvaluator
from utils.preferences import UserPreferences, AlgorithmSelector, interactive_preference_input
from algorithms.nsga2 import NSGA2
from algorithms.moead import MOEAD
from algorithms.spea2 import SPEA2


def create_sample_workload() -> Workload:
    """Create a sample microservices workload."""
    services = [
        ServiceRequirement(
            name="frontend",
            vcpu_min=2,
            ram_gb_min=4,
            latency_requirements={"backend": 50, "database": 100}
        ),
        ServiceRequirement(
            name="backend",
            vcpu_min=4,
            ram_gb_min=8,
            min_multi_core_score=3000,
            latency_requirements={"database": 20, "cache": 10}
        ),
        ServiceRequirement(
            name="database",
            vcpu_min=4,
            ram_gb_min=16,
            min_multi_core_score=4000
        ),
        ServiceRequirement(
            name="cache",
            vcpu_min=2,
            ram_gb_min=4,
            min_multi_core_score=2000
        ),
        ServiceRequirement(
            name="worker",
            vcpu_min=2,
            ram_gb_min=4,
            latency_requirements={"database": 100}
        )
    ]
    
    return Workload(
        name="E-Commerce Microservices",
        services=services,
        max_total_cost_per_hour=5.0
    )


def load_workload_from_file(filepath: str) -> Workload:
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


def visualize_pareto_front(objectives: np.ndarray, output_path: str):
    """Create 2D projections of Pareto front."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Cost vs Latency
    axes[0].scatter(objectives[:, 0], objectives[:, 1], alpha=0.6)
    axes[0].set_xlabel('Cost ($/hour)')
    axes[0].set_ylabel('Latency (ms)')
    axes[0].set_title('Cost vs Latency')
    axes[0].grid(True, alpha=0.3)
    
    # Cost vs Performance
    axes[1].scatter(objectives[:, 0], -objectives[:, 2], alpha=0.6)
    axes[1].set_xlabel('Cost ($/hour)')
    axes[1].set_ylabel('Performance (Geekbench)')
    axes[1].set_title('Cost vs Performance')
    axes[1].grid(True, alpha=0.3)
    
    # Latency vs Performance
    axes[2].scatter(objectives[:, 1], -objectives[:, 2], alpha=0.6)
    axes[2].set_xlabel('Latency (ms)')
    axes[2].set_ylabel('Performance (Geekbench)')
    axes[2].set_title('Latency vs Performance')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Pareto front visualization saved to {output_path}")


def save_solutions(solutions: np.ndarray, objectives: np.ndarray,
                   evaluator: SolutionEvaluator, output_path: str):
    """Save solutions to CSV file."""
    with open(output_path, 'w') as f:
        # Header
        f.write("solution_id,cost,latency,performance,")
        for i, service in enumerate(evaluator.workload.services):
            f.write(f"{service.name}_instance,")
        f.write("\n")
        
        # Solutions
        for idx, (sol, obj) in enumerate(zip(solutions, objectives)):
            assignments = evaluator.decode_solution(sol.tolist())
            
            f.write(f"{idx},{obj[0]:.4f},{obj[1]:.2f},{-obj[2]:.0f},")
            for instance in assignments:
                f.write(f"{instance.full_name},")
            f.write("\n")
    
    print(f"Solutions saved to {output_path}")


def plot_convergence(convergence_history: list, output_path: str):
    """Plot convergence curves."""
    generations = [c['generation'] for c in convergence_history]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Pareto size
    axes[0, 0].plot(generations, [c['pareto_size'] for c in convergence_history])
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('Pareto Front Size')
    axes[0, 0].set_title('Pareto Front Growth')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Average cost
    axes[0, 1].plot(generations, [c['avg_cost'] for c in convergence_history])
    axes[0, 1].set_xlabel('Generation')
    axes[0, 1].set_ylabel('Avg Cost ($/hour)')
    axes[0, 1].set_title('Cost Convergence')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Average latency
    axes[1, 0].plot(generations, [c['avg_latency'] for c in convergence_history])
    axes[1, 0].set_xlabel('Generation')
    axes[1, 0].set_ylabel('Avg Latency (ms)')
    axes[1, 0].set_title('Latency Convergence')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Average performance
    axes[1, 1].plot(generations, [c['avg_performance'] for c in convergence_history])
    axes[1, 1].set_xlabel('Generation')
    axes[1, 1].set_ylabel('Avg Performance')
    axes[1, 1].set_title('Performance Convergence')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Convergence plots saved to {output_path}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Multi-Cloud Workload Optimization')
    parser.add_argument('--algorithm', default='nsga2', 
                       choices=['nsga2', 'moead', 'spea2', 'all'],
                       help='Optimization algorithm (or "all" to run all three)')
    parser.add_argument('--workload', type=str,
                       help='Path to workload JSON file (default: sample workload)')
    parser.add_argument('--population', type=int, default=50,
                       help='Population size')
    parser.add_argument('--generations', type=int, default=100,
                       help='Number of generations')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Base output directory')
    parser.add_argument('--interactive', action='store_true',
                       help='Enable interactive preference input')
    parser.add_argument('--cost-weight', type=float,
                       help='Cost weight (0-1, or use percentages with --pct flag)')
    parser.add_argument('--latency-weight', type=float,
                       help='Latency weight (0-1, or use percentages with --pct flag)')
    parser.add_argument('--performance-weight', type=float,
                       help='Performance weight (0-1, or use percentages with --pct flag)')
    parser.add_argument('--pct', action='store_true',
                       help='Use percentages (0-100) instead of weights (0-1)')

    args = parser.parse_args()

    # Determine which algorithms to run
    if args.algorithm == 'all':
        algorithms_to_run = ['nsga2', 'moead', 'spea2']
    else:
        algorithms_to_run = [args.algorithm]

    print("=" * 70)
    print("Multi-Cloud Workload Optimization")
    print("=" * 70)

    # Handle user preferences
    user_preferences = None
    if args.interactive:
        # Interactive mode
        user_preferences = interactive_preference_input()
    elif args.cost_weight is not None and args.latency_weight is not None and args.performance_weight is not None:
        # Command-line weights provided
        if args.pct:
            # Percentages mode
            user_preferences = UserPreferences.from_percentages(
                args.cost_weight, args.latency_weight, args.performance_weight
            )
        else:
            # Weights mode (0-1)
            user_preferences = UserPreferences(
                args.cost_weight, args.latency_weight, args.performance_weight
            )
        print(f"\nUser Preferences: {user_preferences}")

    # If preferences are set and running single algorithm, warn user
    if user_preferences and len(algorithms_to_run) == 1:
        print("\nNote: User preferences are set, but only one algorithm will run.")
        print("   Consider using --algorithm all to compare all algorithms.")
    
    # Load workload
    if args.workload:
        print(f"\nLoading workload from {args.workload}...")
        workload = load_workload_from_file(args.workload)
    else:
        print("\nUsing sample workload...")
        workload = create_sample_workload()
    
    print(f"   {workload}")
    
    # Load cloud data
    print("\nLoading cloud instance data...")
    loader = DataLoader()
    all_instances = loader.load_all_instances()
    print(f"   Loaded {len(all_instances)} cloud instances")

    # Filter instances to those that could potentially meet requirements
    print("\nFiltering compatible instances...")
    compatible_instances = []
    for instance in all_instances:
        # Check if instance could meet any service requirement
        is_compatible = False
        for service in workload.services:
            if service.is_compatible_with(instance):
                is_compatible = True
                break
        if is_compatible:
            compatible_instances.append(instance)
    
    print(f"   Found {len(compatible_instances)} compatible instances")
    
    # Create evaluator
    # Key fix: Reduced latency penalty from 200ms to 100ms
    # This allows more diverse multi-cloud solutions while staying realistic
    evaluator = SolutionEvaluator(workload, compatible_instances, normalize=False)
    
    # Run each algorithm
    all_results = {}
    
    for algo_name in algorithms_to_run:
        print("\n" + "=" * 70)
        print(f"Running {algo_name.upper()}")
        print("=" * 70)
        
        # Create algorithm-specific output directory
        algo_output_dir = Path(args.output_dir) / algo_name
        algo_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize algorithm
        if algo_name == 'nsga2':
            algorithm = NSGA2()
        elif algo_name == 'moead':
            algorithm = MOEAD()
        elif algo_name == 'spea2':
            algorithm = SPEA2()
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")
        
        # Run optimization
        print(f"\nRunning optimization...")
        print(f"   Population size: {args.population}")
        print(f"   Generations: {args.generations}")
        print()
        
        results = algorithm.optimize(
            evaluate_func=lambda sol: evaluator.evaluate(sol.tolist()),
            n_variables=len(workload.services),
            n_objectives=3,
            variable_bounds=(0, len(compatible_instances) - 1),
            population_size=args.population,
            n_generations=args.generations
        )
        
        # Store results
        all_results[algo_name] = results
        
        # Extract results
        pareto_solutions = results['pareto_front']
        pareto_objectives = results['pareto_objectives']
        
        print(f"\nOptimization complete!")
        print(f"   Pareto front size: {len(pareto_solutions)}")
        print(f"\nPareto Front Statistics:")
        print(f"   Cost range: ${np.min(pareto_objectives[:, 0]):.4f} - ${np.max(pareto_objectives[:, 0]):.4f}/hour")
        print(f"   Latency range: {np.min(pareto_objectives[:, 1]):.2f} - {np.max(pareto_objectives[:, 1]):.2f} ms")
        print(f"   Performance range: {-np.max(pareto_objectives[:, 2]):.0f} - {-np.min(pareto_objectives[:, 2]):.0f}")

        # Show top 3 solutions based on user preference (if set)
        if user_preferences:
            # Determine which objective user cares most about
            max_weight = max(user_preferences.cost_weight,
                           user_preferences.latency_weight,
                           user_preferences.performance_weight)

            if user_preferences.cost_weight == max_weight:
                sort_criterion = "Cost"
                sorted_indices = np.argsort(pareto_objectives[:, 0])[:3]  # Sort by cost (ascending)
            elif user_preferences.latency_weight == max_weight:
                sort_criterion = "Latency"
                sorted_indices = np.argsort(pareto_objectives[:, 1])[:3]  # Sort by latency (ascending)
            else:  # performance_weight is max
                sort_criterion = "Performance"
                sorted_indices = np.argsort(pareto_objectives[:, 2])[:3]  # Sort by -performance (ascending = high performance first)
        else:
            # Default: sort by cost
            sort_criterion = "Cost"
            sorted_indices = np.argsort(pareto_objectives[:, 0])[:3]

        print(f"\nTop 3 Solutions by {sort_criterion}:")
        for i, idx in enumerate(sorted_indices, 1):
            sol = pareto_solutions[idx]
            obj = pareto_objectives[idx]
            print(f"\n   Solution {i}:")
            print(f"   Cost: ${obj[0]:.4f}/hour, Latency: {obj[1]:.2f}ms, Performance: {-obj[2]:.0f}")
            summary = evaluator.get_solution_summary(sol.tolist())
            for assignment in summary['assignments']:
                print(f"      {assignment['service']:12s} -> {assignment['instance']}")
        
        # Save results
        print(f"\nSaving results to {algo_output_dir}/...")
        
        # Pareto front visualization
        visualize_pareto_front(
            pareto_objectives,
            algo_output_dir / f"pareto_front.png"
        )
        
        # Solutions CSV
        save_solutions(
            pareto_solutions,
            pareto_objectives,
            evaluator,
            algo_output_dir / f"solutions.csv"
        )
        
        # Convergence plot
        plot_convergence(
            results['convergence'],
            algo_output_dir / f"convergence.png"
        )
        
        # Save raw results
        algorithm.save_results(algo_output_dir / f"results.json")
        
        print(f"Results saved to {algo_output_dir}/")
    
    # If running multiple algorithms, create comparison
    if len(algorithms_to_run) > 1:
        print("\n" + "=" * 70)
        print("ALGORITHM COMPARISON")
        print("=" * 70)

        for algo_name in algorithms_to_run:
            results = all_results[algo_name]
            pareto_obj = results['pareto_objectives']
            print(f"\n{algo_name.upper()}:")
            print(f"   Pareto size: {len(pareto_obj)}")
            print(f"   Cost: ${np.min(pareto_obj[:, 0]):.4f} - ${np.max(pareto_obj[:, 0]):.4f}/hr")
            print(f"   Latency: {np.min(pareto_obj[:, 1]):.2f} - {np.max(pareto_obj[:, 1]):.2f} ms")
            print(f"   Performance: {-np.max(pareto_obj[:, 2]):.0f} - {-np.min(pareto_obj[:, 2]):.0f}")

        # If user preferences are set, perform algorithm selection
        if user_preferences:
            print("\n")
            selector = AlgorithmSelector(user_preferences)
            selection_result = selector.select_best_algorithm(all_results)

            # Print analysis
            print(selection_result['analysis'])

            # Save recommended solution details
            best_algo = selection_result['best_algorithm']
            best_idx = selection_result['best_solution_index']
            best_sol = all_results[best_algo]['pareto_front'][best_idx]

            print("\nRecommended Deployment Configuration:")
            print("-" * 70)
            summary = evaluator.get_solution_summary(best_sol.tolist())
            for assignment in summary['assignments']:
                print(f"  {assignment['service']:12s} -> {assignment['instance']}")
            print("-" * 70)

            # Save selection results
            selection_output_path = Path(args.output_dir) / "algorithm_selection.txt"
            with open(selection_output_path, 'w') as f:
                f.write(selection_result['analysis'])
                f.write("\n\n")
                f.write("=" * 70 + "\n")
                f.write("RECOMMENDED DEPLOYMENT CONFIGURATION\n")
                f.write("=" * 70 + "\n")
                for assignment in summary['assignments']:
                    f.write(f"{assignment['service']:12s} -> {assignment['instance']}\n")

            print(f"\nAlgorithm selection results saved to {selection_output_path}")

    print("\n" + "=" * 70)
    print(f"All optimizations complete!")
    print(f"Results saved in: {args.output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
