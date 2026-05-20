"""MOEA/D implementation using pymoo library."""

import numpy as np
from typing import Callable, Tuple, Dict
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from algorithms_library.nsga2_pymoo import MultiCloudProblem
from algorithms_library.base import LibraryOptimizationAlgorithm


class MOEADPymoo(LibraryOptimizationAlgorithm):
    """MOEA/D implementation using pymoo library."""

    def __init__(self):
        """Initialize MOEA/D pymoo wrapper."""
        super().__init__("MOEA/D (pymoo)")

    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 n_neighbors: int = 20,
                 **kwargs) -> Dict:
        """
        Run MOEA/D optimization using pymoo.

        Args:
            evaluate_func: Function(solution) -> tuple of objectives
            n_variables: Number of decision variables
            n_objectives: Number of objectives
            variable_bounds: (min_idx, max_idx) for instance selection
            population_size: Population size
            n_generations: Number of generations
            n_neighbors: Neighborhood size

        Returns:
            Results dictionary
        """
        # Create problem
        problem = MultiCloudProblem(
            evaluate_func=evaluate_func,
            n_variables=n_variables,
            variable_bounds=variable_bounds,
            n_objectives=n_objectives
        )

        # Generate reference directions for MOEA/D
        # For 3 objectives, use Das-Dennis approach
        ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=12)

        # Create algorithm
        algorithm = MOEAD(
            ref_dirs=ref_dirs,
            n_neighbors=n_neighbors,
            prob_neighbor_mating=0.9
        )

        # Run optimization
        print(f"Running {self.name} optimization...")
        res = minimize(
            problem,
            algorithm,
            ('n_gen', n_generations),
            verbose=True,
            seed=42
        )

        # Extract results and convert to integers
        if res.X is not None:
            pareto_solutions = np.round(res.X).astype(int)
            pareto_objectives = res.F

            # Ensure 2D arrays
            if len(pareto_solutions.shape) == 1:
                pareto_solutions = pareto_solutions.reshape(1, -1)
            if len(pareto_objectives.shape) == 1:
                pareto_objectives = pareto_objectives.reshape(1, -1)
        else:
            # Fallback if no solutions found
            pareto_solutions = np.array([])
            pareto_objectives = np.array([])

        # Create convergence history (simplified)
        convergence_history = []
        for gen in range(n_generations):
            convergence_history.append({
                'generation': gen,
                'pareto_size': len(pareto_solutions) if len(pareto_solutions) > 0 else 0,
                'avg_cost': np.mean(pareto_objectives[:, 0]) if len(pareto_objectives) > 0 else 0,
                'avg_latency': np.mean(pareto_objectives[:, 1]) if len(pareto_objectives) > 0 else 0,
                'avg_performance': np.mean(-pareto_objectives[:, 2]) if len(pareto_objectives) > 0 else 0,
            })

        self.results = {
            'pareto_front': pareto_solutions,
            'pareto_objectives': pareto_objectives,
            'all_solutions': pareto_solutions,
            'all_objectives': pareto_objectives,
            'convergence': convergence_history
        }

        print(f"{self.name} completed. Pareto front size: {len(pareto_solutions)}")
        return self.results

    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Pareto front from last run."""
        if self.results is None:
            raise ValueError("No results available. Run optimize() first.")

        return self.results['pareto_front'], self.results['pareto_objectives']
