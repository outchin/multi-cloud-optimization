"""Base interface for multi-objective optimization algorithms."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
import numpy as np


class OptimizationAlgorithm(ABC):
    """Base class for optimization algorithms."""
    
    def __init__(self, name: str):
        """
        Initialize algorithm.
        
        Args:
            name: Algorithm name
        """
        self.name = name
        self.results = None
    
    @abstractmethod
    def optimize(self, 
                 evaluate_func,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 **kwargs) -> Dict:
        """
        Run optimization.
        
        Args:
            evaluate_func: Function that evaluates a solution and returns objectives
            n_variables: Number of decision variables
            n_objectives: Number of objectives
            variable_bounds: Tuple of (min, max) for variable values
            population_size: Population size
            n_generations: Number of generations
            **kwargs: Algorithm-specific parameters
        
        Returns:
            Dictionary containing:
                - pareto_front: List of non-dominated solutions
                - pareto_objectives: Objective values for pareto front
                - all_solutions: All evaluated solutions
                - convergence: Convergence metrics per generation
        """
        pass
    
    @abstractmethod
    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get Pareto front from last optimization run.
        
        Returns:
            Tuple of (solutions, objectives)
        """
        pass
    
    def dominates(self, obj1: np.ndarray, obj2: np.ndarray) -> bool:
        """
        Check if obj1 dominates obj2 (minimization).
        
        Args:
            obj1: First objective vector
            obj2: Second objective vector
        
        Returns:
            True if obj1 dominates obj2
        """
        # obj1 dominates obj2 if:
        # - obj1 is at least as good as obj2 in all objectives
        # - obj1 is strictly better in at least one objective
        at_least_as_good = np.all(obj1 <= obj2)
        strictly_better = np.any(obj1 < obj2)
        return at_least_as_good and strictly_better
    
    def get_non_dominated(self, objectives: np.ndarray) -> np.ndarray:
        """
        Get indices of non-dominated solutions.
        
        Args:
            objectives: Array of shape (n_solutions, n_objectives)
        
        Returns:
            Array of indices of non-dominated solutions
        """
        n = len(objectives)
        is_dominated = np.zeros(n, dtype=bool)
        
        for i in range(n):
            for j in range(n):
                if i != j and self.dominates(objectives[j], objectives[i]):
                    is_dominated[i] = True
                    break
        
        return np.where(~is_dominated)[0]
    
    def calculate_hypervolume(self, pareto_objectives: np.ndarray, 
                             reference_point: np.ndarray) -> float:
        """
        Calculate hypervolume indicator.
        
        Args:
            pareto_objectives: Pareto front objectives
            reference_point: Reference point (worst values)
        
        Returns:
            Hypervolume value
        """
        # Simple 2D hypervolume calculation
        # For 3D, would need more sophisticated algorithm
        if pareto_objectives.shape[1] == 2:
            # Sort by first objective
            sorted_idx = np.argsort(pareto_objectives[:, 0])
            sorted_objs = pareto_objectives[sorted_idx]
            
            hv = 0.0
            for i, obj in enumerate(sorted_objs):
                width = reference_point[0] - obj[0]
                if i == 0:
                    height = reference_point[1] - obj[1]
                else:
                    height = sorted_objs[i-1][1] - obj[1]
                hv += width * height
            
            return hv
        else:
            # For 3+ objectives, return 0 (would need WFG algorithm)
            return 0.0
    
    def save_results(self, filename: str):
        """Save optimization results to file."""
        if self.results is None:
            raise ValueError("No results to save. Run optimize() first.")
        
        import json
        with open(filename, 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            serializable_results = {}
            for key, value in self.results.items():
                if isinstance(value, np.ndarray):
                    serializable_results[key] = value.tolist()
                else:
                    serializable_results[key] = value
            json.dump(serializable_results, f, indent=2)
