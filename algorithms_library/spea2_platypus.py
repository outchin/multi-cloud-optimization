"""SPEA2 implementation using Platypus library."""

import numpy as np
from typing import Callable, Tuple, Dict
from platypus import SPEA2, Problem, Integer
from algorithms_library.base import LibraryOptimizationAlgorithm


class SPEA2Platypus(LibraryOptimizationAlgorithm):
    """SPEA2 implementation using Platypus library."""

    def __init__(self):
        """Initialize SPEA2 Platypus wrapper."""
        super().__init__("SPEA2 (Platypus)")

    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 **kwargs) -> Dict:
        """
        Run SPEA2 optimization using Platypus.

        Args:
            evaluate_func: Function(solution) -> tuple of objectives
            n_variables: Number of decision variables
            n_objectives: Number of objectives
            variable_bounds: (min_idx, max_idx) for instance selection
            population_size: Population size
            n_generations: Number of generations

        Returns:
            Results dictionary
        """
        min_val, max_val = variable_bounds

        # Define Platypus problem
        def platypus_evaluate(vars):
            """Wrapper for evaluation function."""
            solution = np.array(vars, dtype=int)
            objectives = evaluate_func(solution)
            return objectives

        # Create problem
        problem = Problem(n_variables, n_objectives)

        # Add integer variables
        for i in range(n_variables):
            problem.types[i] = Integer(min_val, max_val)

        # Set evaluation function
        problem.function = platypus_evaluate

        # Create algorithm
        algorithm = SPEA2(problem, population_size=population_size)

        # Run optimization
        print(f"Running {self.name} optimization...")

        # Track progress
        for gen in range(n_generations):
            algorithm.step()
            if gen % 10 == 0:
                print(f"Generation {gen}/{n_generations}")

        print(f"Generation {n_generations}/{n_generations}")

        # Extract results
        pareto_solutions = []
        pareto_objectives = []

        for solution in algorithm.result:
            # Handle both single values and lists
            if hasattr(solution.variables[0], '__iter__') and not isinstance(solution.variables[0], str):
                # Variables is a list of lists, flatten it
                vars = [int(v) if not hasattr(v, '__iter__') else int(v[0]) for v in solution.variables]
            else:
                vars = [int(v) for v in solution.variables]
            objs = solution.objectives
            pareto_solutions.append(vars)
            pareto_objectives.append(objs)

        pareto_solutions = np.array(pareto_solutions)
        pareto_objectives = np.array(pareto_objectives)

        # Ensure 2D arrays
        if len(pareto_solutions.shape) == 1:
            pareto_solutions = pareto_solutions.reshape(1, -1)
        if len(pareto_objectives.shape) == 1:
            pareto_objectives = pareto_objectives.reshape(1, -1)

        # Create convergence history (simplified)
        convergence_history = []
        for gen in range(n_generations):
            convergence_history.append({
                'generation': gen,
                'pareto_size': len(pareto_solutions),
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
