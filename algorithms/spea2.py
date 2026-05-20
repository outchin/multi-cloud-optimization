"""SPEA2 implementation for multi-objective optimization."""

import numpy as np
from typing import List, Tuple, Dict, Callable
from algorithms.base import OptimizationAlgorithm


class SPEA2(OptimizationAlgorithm):
    """Strength Pareto Evolutionary Algorithm 2."""
    
    def __init__(self):
        """Initialize SPEA2 algorithm."""
        super().__init__("SPEA2")
        self.population = None
        self.objectives = None
        self.archive = None
        self.archive_objectives = None
    
    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 archive_size: int = None,
                 **kwargs) -> Dict:
        """
        Run SPEA2 optimization.
        
        Args:
            evaluate_func: Function(solution) -> tuple of objectives
            n_variables: Number of decision variables
            n_objectives: Number of objectives
            variable_bounds: (min_idx, max_idx) for instance selection
            population_size: Population size
            n_generations: Number of generations
            archive_size: External archive size (default: population_size)
        
        Returns:
            Results dictionary
        """
        if archive_size is None:
            archive_size = population_size
        
        min_val, max_val = variable_bounds
        
        # Initialize population
        population = np.random.randint(min_val, max_val + 1,
                                      size=(population_size, n_variables))
        
        # Evaluate initial population
        objectives = np.array([evaluate_func(ind) for ind in population])
        
        # Initialize archive (empty)
        archive = np.empty((0, n_variables), dtype=int)
        archive_objectives = np.empty((0, n_objectives))
        
        # Storage for convergence tracking
        convergence_history = []
        
        # Main evolution loop
        for generation in range(n_generations):
            # Combine population and archive
            combined = np.vstack([population, archive]) if len(archive) > 0 else population
            combined_obj = np.vstack([objectives, archive_objectives]) if len(archive_objectives) > 0 else objectives
            
            # Calculate fitness for all individuals
            fitness = self._calculate_fitness(combined_obj)
            
            # Environmental selection (update archive)
            archive, archive_objectives = self._environmental_selection(
                combined, combined_obj, fitness, archive_size
            )
            
            # Track convergence
            pareto_idx = self.get_non_dominated(archive_objectives)
            pareto_objectives = archive_objectives[pareto_idx]
            
            convergence_history.append({
                'generation': generation,
                'pareto_size': len(pareto_idx),
                'archive_size': len(archive),
                'avg_cost': np.mean(pareto_objectives[:, 0]),
                'avg_latency': np.mean(pareto_objectives[:, 1]),
                'avg_performance': np.mean(-pareto_objectives[:, 2]),
            })
            
            if generation % 10 == 0:
                print(f"Generation {generation}/{n_generations} - "
                      f"Archive size: {len(archive)}, Pareto size: {len(pareto_idx)}")
            
            # Generate offspring
            offspring = self._generate_offspring(
                archive, archive_objectives, population_size,
                min_val, max_val, n_variables
            )
            
            # Evaluate offspring
            population = offspring
            objectives = np.array([evaluate_func(ind) for ind in offspring])
        
        # Final archive is the result
        pareto_idx = self.get_non_dominated(archive_objectives)
        
        # Store results
        self.population = population
        self.objectives = objectives
        self.archive = archive
        self.archive_objectives = archive_objectives
        
        self.results = {
            'pareto_front': archive[pareto_idx],
            'pareto_objectives': archive_objectives[pareto_idx],
            'all_solutions': archive,
            'all_objectives': archive_objectives,
            'convergence': convergence_history
        }
        
        return self.results
    
    def _calculate_fitness(self, objectives: np.ndarray) -> np.ndarray:
        """
        Calculate SPEA2 fitness for all individuals.
        
        Fitness = Raw fitness + Density
        Raw fitness = Strength of dominators
        Density = 1 / (k-th nearest neighbor distance + 2)
        """
        n = len(objectives)
        
        # Calculate strength (number of individuals dominated by i)
        strength = np.zeros(n)
        for i in range(n):
            for j in range(n):
                if i != j and self.dominates(objectives[i], objectives[j]):
                    strength[i] += 1
        
        # Calculate raw fitness (sum of strengths of dominators)
        raw_fitness = np.zeros(n)
        for i in range(n):
            for j in range(n):
                if i != j and self.dominates(objectives[j], objectives[i]):
                    raw_fitness[i] += strength[j]
        
        # Calculate density (based on k-th nearest neighbor)
        k = int(np.sqrt(n))  # k-th nearest neighbor
        density = np.zeros(n)
        
        for i in range(n):
            # Compute distances to all other individuals in objective space
            distances = np.linalg.norm(objectives - objectives[i], axis=1)
            
            # Sort distances (exclude self at distance 0)
            sorted_distances = np.sort(distances)
            
            # k-th nearest neighbor distance (k+1 because sorted_distances[0] = 0)
            if len(sorted_distances) > k:
                k_distance = sorted_distances[k]
            else:
                k_distance = sorted_distances[-1]
            
            # Density component
            density[i] = 1.0 / (k_distance + 2.0)
        
        # Total fitness
        fitness = raw_fitness + density
        
        return fitness
    
    def _environmental_selection(self, population: np.ndarray, objectives: np.ndarray,
                                 fitness: np.ndarray, archive_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select individuals for archive.
        
        1. Copy all non-dominated individuals (fitness < 1)
        2. If archive < archive_size, fill with best dominated individuals
        3. If archive > archive_size, truncate using density
        """
        # Get non-dominated individuals (fitness < 1)
        non_dominated_idx = np.where(fitness < 1)[0]
        
        if len(non_dominated_idx) < archive_size:
            # Not enough non-dominated, add best dominated individuals
            dominated_idx = np.where(fitness >= 1)[0]
            
            # Sort dominated by fitness
            sorted_dominated = dominated_idx[np.argsort(fitness[dominated_idx])]
            
            # Select best to fill archive
            n_to_add = archive_size - len(non_dominated_idx)
            selected = np.concatenate([non_dominated_idx, sorted_dominated[:n_to_add]])
        
        elif len(non_dominated_idx) > archive_size:
            # Too many non-dominated, truncate by density
            selected = self._truncate_by_density(
                population[non_dominated_idx],
                objectives[non_dominated_idx],
                archive_size
            )
            selected = non_dominated_idx[selected]
        
        else:
            # Exact fit
            selected = non_dominated_idx
        
        return population[selected], objectives[selected]
    
    def _truncate_by_density(self, population: np.ndarray, objectives: np.ndarray,
                            target_size: int) -> np.ndarray:
        """
        Truncate population to target size by iteratively removing most crowded.
        """
        n = len(population)
        selected = np.arange(n)
        
        while len(selected) > target_size:
            # Compute distances between all pairs
            current_obj = objectives[selected]
            n_current = len(current_obj)
            
            # Find individual with smallest distance to nearest neighbor
            min_distances = np.full(n_current, np.inf)
            
            for i in range(n_current):
                distances = np.linalg.norm(current_obj - current_obj[i], axis=1)
                distances[i] = np.inf  # Exclude self
                min_distances[i] = np.min(distances)
            
            # Remove individual with smallest nearest neighbor distance (most crowded)
            to_remove = np.argmin(min_distances)
            selected = np.delete(selected, to_remove)
        
        return selected
    
    def _generate_offspring(self, archive: np.ndarray, archive_objectives: np.ndarray,
                           offspring_size: int, min_val: int, max_val: int,
                           n_variables: int) -> np.ndarray:
        """Generate offspring through binary tournament, crossover, and mutation."""
        offspring = []
        
        while len(offspring) < offspring_size:
            # Binary tournament selection
            parent1 = self._binary_tournament(archive, archive_objectives)
            parent2 = self._binary_tournament(archive, archive_objectives)
            
            # Crossover
            child = self._crossover(parent1, parent2)
            
            # Mutation
            child = self._mutate(child, 1.0 / n_variables, min_val, max_val)
            
            offspring.append(child)
        
        return np.array(offspring)
    
    def _binary_tournament(self, population: np.ndarray, objectives: np.ndarray) -> np.ndarray:
        """Select individual using binary tournament based on dominance."""
        # Select two random individuals
        idx1, idx2 = np.random.choice(len(population), 2, replace=False)
        
        # Compare based on dominance
        if self.dominates(objectives[idx1], objectives[idx2]):
            return population[idx1].copy()
        elif self.dominates(objectives[idx2], objectives[idx1]):
            return population[idx2].copy()
        else:
            # If non-dominated to each other, choose randomly
            return population[np.random.choice([idx1, idx2])].copy()
    
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Single-point crossover."""
        n = len(parent1)
        point = np.random.randint(1, n)
        child = np.concatenate([parent1[:point], parent2[point:]])
        return child
    
    def _mutate(self, individual: np.ndarray, mutation_prob: float,
                min_val: int, max_val: int) -> np.ndarray:
        """Uniform mutation."""
        mutated = individual.copy()
        for i in range(len(mutated)):
            if np.random.random() < mutation_prob:
                mutated[i] = np.random.randint(min_val, max_val + 1)
        return mutated
    
    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Pareto front from last run."""
        if self.results is None:
            raise ValueError("No results available. Run optimize() first.")
        
        return self.results['pareto_front'], self.results['pareto_objectives']
