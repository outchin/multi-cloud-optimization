"""MOEA/D implementation for multi-objective optimization."""

import numpy as np
from typing import List, Tuple, Dict, Callable
from algorithms.base import OptimizationAlgorithm


class MOEAD(OptimizationAlgorithm):
    """Multi-Objective Evolutionary Algorithm based on Decomposition."""
    
    def __init__(self):
        """Initialize MOEA/D algorithm."""
        super().__init__("MOEA/D")
        self.population = None
        self.objectives = None
        self.weight_vectors = None
    
    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 n_neighbors: int = 20,
                 decomposition: str = 'tchebycheff',
                 **kwargs) -> Dict:
        """
        Run MOEA/D optimization.
        
        Args:
            evaluate_func: Function(solution) -> tuple of objectives
            n_variables: Number of decision variables
            n_objectives: Number of objectives
            variable_bounds: (min_idx, max_idx) for instance selection
            population_size: Population size
            n_generations: Number of generations
            n_neighbors: Neighborhood size
            decomposition: Decomposition method ('tchebycheff' or 'weighted_sum')
        
        Returns:
            Results dictionary
        """
        min_val, max_val = variable_bounds
        
        # Generate weight vectors
        self.weight_vectors = self._generate_weight_vectors(n_objectives, population_size)
        
        # Initialize population
        population = np.random.randint(min_val, max_val + 1, 
                                      size=(population_size, n_variables))
        
        # Evaluate initial population
        objectives = np.array([evaluate_func(ind) for ind in population])
        
        # Compute ideal point (best value for each objective)
        ideal_point = np.min(objectives, axis=0)
        
        # Compute neighborhood structure
        neighbors = self._compute_neighbors(self.weight_vectors, n_neighbors)
        
        # Storage for convergence tracking
        convergence_history = []
        
        # Main evolution loop
        for generation in range(n_generations):
            # Update ideal point
            ideal_point = np.minimum(ideal_point, np.min(objectives, axis=0))
            
            # For each subproblem
            for i in range(population_size):
                # Generate offspring from neighborhood
                parent_indices = self._select_parents(neighbors[i], 2)
                parent1 = population[parent_indices[0]]
                parent2 = population[parent_indices[1]]
                
                # Crossover
                offspring = self._crossover(parent1, parent2)
                
                # Mutation
                offspring = self._mutate(offspring, 1.0 / n_variables, min_val, max_val)
                
                # Evaluate offspring
                offspring_obj = np.array(evaluate_func(offspring))
                
                # Update ideal point
                ideal_point = np.minimum(ideal_point, offspring_obj)
                
                # Update neighbors
                for j in neighbors[i]:
                    # Compute scalar fitness using decomposition
                    current_fitness = self._scalar_fitness(
                        objectives[j], self.weight_vectors[j], ideal_point, decomposition
                    )
                    offspring_fitness = self._scalar_fitness(
                        offspring_obj, self.weight_vectors[j], ideal_point, decomposition
                    )
                    
                    # Replace if offspring is better
                    if offspring_fitness < current_fitness:
                        population[j] = offspring.copy()
                        objectives[j] = offspring_obj.copy()
            
            # Track convergence
            pareto_idx = self.get_non_dominated(objectives)
            pareto_objectives = objectives[pareto_idx]
            
            convergence_history.append({
                'generation': generation,
                'pareto_size': len(pareto_idx),
                'avg_cost': np.mean(pareto_objectives[:, 0]),
                'avg_latency': np.mean(pareto_objectives[:, 1]),
                'avg_performance': np.mean(-pareto_objectives[:, 2]),
            })
            
            if generation % 10 == 0:
                print(f"Generation {generation}/{n_generations} - "
                      f"Pareto size: {len(pareto_idx)}")
        
        # Final Pareto front
        pareto_idx = self.get_non_dominated(objectives)
        
        # Store results
        self.population = population
        self.objectives = objectives
        
        self.results = {
            'pareto_front': population[pareto_idx],
            'pareto_objectives': objectives[pareto_idx],
            'all_solutions': population,
            'all_objectives': objectives,
            'convergence': convergence_history
        }
        
        return self.results
    
    def _generate_weight_vectors(self, n_objectives: int, population_size: int) -> np.ndarray:
        """
        Generate uniformly distributed weight vectors.
        
        For 3 objectives, use simplex lattice design.
        """
        if n_objectives == 2:
            # For 2 objectives, simply distribute along [0,1]
            weights = np.zeros((population_size, 2))
            for i in range(population_size):
                w1 = i / (population_size - 1)
                weights[i] = [w1, 1 - w1]
            return weights
        
        elif n_objectives == 3:
            # For 3 objectives, use Das-Dennis approach (simplex lattice)
            # Approximate number of divisions
            H = int(np.cbrt(population_size))
            
            weights = []
            for i in range(H + 1):
                for j in range(H + 1 - i):
                    k = H - i - j
                    w = np.array([i / H, j / H, k / H])
                    weights.append(w)
            
            weights = np.array(weights)
            
            # If we have more than needed, randomly sample
            if len(weights) > population_size:
                indices = np.random.choice(len(weights), population_size, replace=False)
                weights = weights[indices]
            # If we have fewer, fill with random weights
            elif len(weights) < population_size:
                extra = population_size - len(weights)
                random_weights = np.random.random((extra, n_objectives))
                random_weights = random_weights / random_weights.sum(axis=1, keepdims=True)
                weights = np.vstack([weights, random_weights])
            
            return weights
        
        else:
            # For other dimensions, use random weights
            weights = np.random.random((population_size, n_objectives))
            weights = weights / weights.sum(axis=1, keepdims=True)
            return weights
    
    def _compute_neighbors(self, weight_vectors: np.ndarray, n_neighbors: int) -> List[np.ndarray]:
        """
        Compute neighborhood structure based on weight vector distances.
        
        Returns list where neighbors[i] contains indices of closest weight vectors.
        """
        n = len(weight_vectors)
        neighbors = []
        
        for i in range(n):
            # Compute Euclidean distances to all other weight vectors
            distances = np.linalg.norm(weight_vectors - weight_vectors[i], axis=1)
            
            # Get indices of n_neighbors closest vectors (including itself)
            neighbor_indices = np.argsort(distances)[:n_neighbors]
            neighbors.append(neighbor_indices)
        
        return neighbors
    
    def _select_parents(self, neighbor_indices: np.ndarray, n_parents: int) -> np.ndarray:
        """Select random parents from neighborhood."""
        return np.random.choice(neighbor_indices, n_parents, replace=False)
    
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Single-point crossover."""
        n = len(parent1)
        point = np.random.randint(1, n)
        offspring = np.concatenate([parent1[:point], parent2[point:]])
        return offspring
    
    def _mutate(self, individual: np.ndarray, mutation_prob: float,
                min_val: int, max_val: int) -> np.ndarray:
        """Uniform mutation."""
        mutated = individual.copy()
        for i in range(len(mutated)):
            if np.random.random() < mutation_prob:
                mutated[i] = np.random.randint(min_val, max_val + 1)
        return mutated
    
    def _scalar_fitness(self, objectives: np.ndarray, weights: np.ndarray,
                       ideal_point: np.ndarray, method: str) -> float:
        """
        Compute scalar fitness using decomposition.
        
        Args:
            objectives: Objective values
            weights: Weight vector
            ideal_point: Ideal point (best value for each objective)
            method: 'tchebycheff' or 'weighted_sum'
        
        Returns:
            Scalar fitness value (lower is better)
        """
        if method == 'tchebycheff':
            # Tchebycheff approach: minimize max_i { w_i * |f_i - z_i*| }
            diff = np.abs(objectives - ideal_point)
            weighted_diff = weights * diff
            # Add small epsilon to avoid division by zero
            weighted_diff = np.where(weights > 0, weighted_diff, 0)
            return np.max(weighted_diff)
        
        elif method == 'weighted_sum':
            # Weighted sum: minimize sum_i { w_i * f_i }
            return np.sum(weights * objectives)
        
        else:
            raise ValueError(f"Unknown decomposition method: {method}")
    
    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Pareto front from last run."""
        if self.results is None:
            raise ValueError("No results available. Run optimize() first.")
        
        return self.results['pareto_front'], self.results['pareto_objectives']
