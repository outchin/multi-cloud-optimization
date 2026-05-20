"""NSGA-II implementation using pymoo library."""

import numpy as np
from typing import Callable, Tuple, Dict
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from algorithms_library.base import LibraryOptimizationAlgorithm


class MultiCloudProblem(Problem):
    """Problem wrapper for pymoo."""

    def __init__(self, evaluate_func: Callable, n_variables: int,
                 variable_bounds: Tuple[int, int], n_objectives: int = 3):
        """Initialize problem.

        Args:
            evaluate_func: Evaluation function
            n_variables: Number of decision variables
            variable_bounds: (min, max) bounds for variables
            n_objectives: Number of objectives
        """
        self.evaluate_func = evaluate_func
        min_val, max_val = variable_bounds

        super().__init__(
            n_var=n_variables,
            n_obj=n_objectives,
            xl=min_val,  # Lower bounds
            xu=max_val,  # Upper bounds
            vtype=int    # Integer variables
        )

    def _evaluate(self, X, out, *args, **kwargs):
        """Evaluate solutions."""
        # X is array of solutions (n_solutions, n_variables)
        objectives = []
        for x in X:
            # Convert to integers (pymoo uses floats internally)
            x_int = np.round(x).astype(int)
            obj = self.evaluate_func(x_int)
            objectives.append(obj)

        out["F"] = np.array(objectives)


class NSGA2Pymoo(LibraryOptimizationAlgorithm):
    """NSGA-II implementation using pymoo library."""

    def __init__(self):
        """Initialize NSGA-II pymoo wrapper."""
        super().__init__("NSGA-II (pymoo)")

    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 **kwargs) -> Dict:
        """
        Run NSGA-II optimization using pymoo.

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
        # Create problem
        problem = MultiCloudProblem(
            evaluate_func=evaluate_func,
            n_variables=n_variables,
            variable_bounds=variable_bounds,
            n_objectives=n_objectives
        )

        # Create algorithm
        algorithm = NSGA2(pop_size=population_size)

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
        pareto_solutions = np.round(res.X).astype(int)
        pareto_objectives = res.F

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
