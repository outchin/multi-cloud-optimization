"""Base class for library-based optimization algorithms."""

import numpy as np
from typing import Tuple
from abc import ABC, abstractmethod


class LibraryOptimizationAlgorithm(ABC):
    """Base class for library-based multi-objective optimization algorithms."""

    def __init__(self, name: str):
        """Initialize algorithm.

        Args:
            name: Algorithm name
        """
        self.name = name
        self.results = None

    @abstractmethod
    def optimize(self, *args, **kwargs):
        """Run optimization (to be implemented by subclasses)."""
        pass

    @abstractmethod
    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Pareto front from last run."""
        pass

    def dominates(self, obj1: np.ndarray, obj2: np.ndarray) -> bool:
        """Check if obj1 dominates obj2 (minimization)."""
        return np.all(obj1 <= obj2) and np.any(obj1 < obj2)

    def get_non_dominated(self, objectives: np.ndarray) -> np.ndarray:
        """Get indices of non-dominated solutions."""
        n = len(objectives)
        is_dominated = np.zeros(n, dtype=bool)

        for i in range(n):
            if is_dominated[i]:
                continue
            for j in range(n):
                if i != j and not is_dominated[j]:
                    if self.dominates(objectives[j], objectives[i]):
                        is_dominated[i] = True
                        break

        return np.where(~is_dominated)[0]
