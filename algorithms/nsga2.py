"""NSGA-II implementation for multi-objective optimization."""

import numpy as np
from typing import List, Tuple, Dict, Callable
from algorithms.base import OptimizationAlgorithm


class NSGA2(OptimizationAlgorithm):
    """Non-dominated Sorting Genetic Algorithm II."""
    
    def __init__(self):
        """Initialize NSGA-II algorithm."""
        super().__init__("NSGA-II")
        self.population = None
        self.objectives = None
    
    def optimize(self,
                 evaluate_func: Callable,
                 n_variables: int,
                 n_objectives: int,
                 variable_bounds: Tuple[int, int],
                 population_size: int,
                 n_generations: int,
                 crossover_prob: float = 0.9,
                 mutation_prob: float = None,
                 **kwargs) -> Dict:
        """
        Run NSGA-II optimization.
        
        Args:
            evaluate_func: Function(solution) -> tuple of objectives
            n_variables: Number of decision variables (services to assign)
            n_objectives: Number of objectives (3: cost, latency, performance)
            variable_bounds: (min_idx, max_idx) for instance selection
            population_size: Population size (should be even)
            n_generations: Number of generations
            crossover_prob: Crossover probability
            mutation_prob: Mutation probability (default: 1/n_variables)
        
        Returns:
            Results dictionary
        """
        if mutation_prob is None:
            mutation_prob = 1.0 / n_variables
        
        min_val, max_val = variable_bounds
        
        # Initialize population randomly
        population = np.random.randint(min_val, max_val + 1, 
                                      size=(population_size, n_variables))
        
        # Storage for convergence tracking
        convergence_history = []
        
        # Main evolution loop
        for generation in range(n_generations):
            # Evaluate population
            objectives = np.array([evaluate_func(ind) for ind in population])
            
            # Fast non-dominated sorting
            fronts = self._fast_non_dominated_sort(objectives)
            
            # Calculate crowding distance for each front
            for front in fronts:
                self._crowding_distance_assignment(objectives[front])
            
            # Track convergence
            pareto_front_idx = fronts[0]
            pareto_objectives = objectives[pareto_front_idx]
            
            convergence_history.append({
                'generation': generation,
                'pareto_size': len(pareto_front_idx),
                'avg_cost': np.mean(pareto_objectives[:, 0]),
                'avg_latency': np.mean(pareto_objectives[:, 1]),
                'avg_performance': np.mean(-pareto_objectives[:, 2]),  # Convert back to positive
            })
            
            if generation % 10 == 0:
                print(f"Generation {generation}/{n_generations} - "
                      f"Pareto size: {len(pareto_front_idx)}")
            
            # Generate offspring
            offspring = self._generate_offspring(
                population, objectives, fronts,
                crossover_prob, mutation_prob,
                min_val, max_val
            )
            
            # Combine parent and offspring populations
            combined_pop = np.vstack([population, offspring])
            combined_obj = np.array([evaluate_func(ind) for ind in combined_pop])
            
            # Survival selection
            population = self._environmental_selection(
                combined_pop, combined_obj, population_size
            )
        
        # Final evaluation
        final_objectives = np.array([evaluate_func(ind) for ind in population])
        fronts = self._fast_non_dominated_sort(final_objectives)
        pareto_front_idx = fronts[0]
        
        # Store results
        self.population = population
        self.objectives = final_objectives
        
        self.results = {
            'pareto_front': population[pareto_front_idx],
            'pareto_objectives': final_objectives[pareto_front_idx],
            'all_solutions': population,
            'all_objectives': final_objectives,
            'convergence': convergence_history
        }
        
        return self.results
    
    def _fast_non_dominated_sort(self, objectives: np.ndarray) -> List[np.ndarray]:
        """
        Fast non-dominated sorting.
        
        Args:
            objectives: Objective values array (n_pop, n_obj)
        
        Returns:
            List of fronts (each front is array of indices)
        """
        n = len(objectives)
        
        # Initialize
        domination_count = np.zeros(n, dtype=int)  # Number of solutions dominating i
        dominated_solutions = [[] for _ in range(n)]  # Solutions dominated by i
        fronts = [[]]
        
        # Find domination relationships
        for i in range(n):
            for j in range(i + 1, n):
                if self.dominates(objectives[i], objectives[j]):
                    dominated_solutions[i].append(j)
                    domination_count[j] += 1
                elif self.dominates(objectives[j], objectives[i]):
                    dominated_solutions[j].append(i)
                    domination_count[i] += 1
        
        # First front: solutions with domination_count == 0
        for i in range(n):
            if domination_count[i] == 0:
                fronts[0].append(i)
        
        # Find subsequent fronts
        k = 0
        while k < len(fronts) and len(fronts[k]) > 0:
            next_front = []
            for i in fronts[k]:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            
            if len(next_front) > 0:
                fronts.append(next_front)
            k += 1
        
        # Remove empty last front if exists
        if fronts and len(fronts[-1]) == 0:
            fronts.pop()
        
        return [np.array(front) for front in fronts]
    
    def _crowding_distance_assignment(self, objectives: np.ndarray) -> np.ndarray:
        """
        Calculate crowding distance for solutions.
        
        Args:
            objectives: Objective values for solutions in a front
        
        Returns:
            Array of crowding distances
        """
        n = len(objectives)
        n_obj = objectives.shape[1]
        
        distance = np.zeros(n)
        
        for m in range(n_obj):
            # Sort by objective m
            sorted_idx = np.argsort(objectives[:, m])
            
            # Boundary solutions get infinite distance
            distance[sorted_idx[0]] = float('inf')
            distance[sorted_idx[-1]] = float('inf')
            
            # Calculate distance for middle solutions
            obj_range = objectives[sorted_idx[-1], m] - objectives[sorted_idx[0], m]
            
            if obj_range > 0:
                for i in range(1, n - 1):
                    distance[sorted_idx[i]] += (
                        (objectives[sorted_idx[i + 1], m] - 
                         objectives[sorted_idx[i - 1], m]) / obj_range
                    )
        
        return distance
    
    def _generate_offspring(self, population: np.ndarray, 
                           objectives: np.ndarray,
                           fronts: List[np.ndarray],
                           crossover_prob: float,
                           mutation_prob: float,
                           min_val: int,
                           max_val: int) -> np.ndarray:
        """Generate offspring through tournament selection, crossover, and mutation."""
        n_pop = len(population)
        n_var = population.shape[1]
        offspring = []
        
        while len(offspring) < n_pop:
            # Tournament selection
            parent1 = self._tournament_selection(population, objectives, fronts)
            parent2 = self._tournament_selection(population, objectives, fronts)
            
            # Crossover
            if np.random.random() < crossover_prob:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            child1 = self._mutate(child1, mutation_prob, min_val, max_val)
            child2 = self._mutate(child2, mutation_prob, min_val, max_val)
            
            offspring.append(child1)
            if len(offspring) < n_pop:
                offspring.append(child2)
        
        return np.array(offspring)
    
    def _tournament_selection(self, population: np.ndarray,
                             objectives: np.ndarray,
                             fronts: List[np.ndarray],
                             tournament_size: int = 2) -> np.ndarray:
        """Select individual using binary tournament."""
        # Pick random individuals
        candidates = np.random.choice(len(population), tournament_size, replace=False)
        
        # Find which front each candidate belongs to
        candidate_ranks = []
        for idx in candidates:
            for rank, front in enumerate(fronts):
                if idx in front:
                    candidate_ranks.append(rank)
                    break
        
        # Select based on rank (lower is better)
        best_rank = min(candidate_ranks)
        best_candidates = [candidates[i] for i, r in enumerate(candidate_ranks) if r == best_rank]
        
        if len(best_candidates) == 1:
            return population[best_candidates[0]].copy()
        
        # If tie, select based on crowding distance
        front_idx = fronts[best_rank]
        front_objectives = objectives[front_idx]
        distances = self._crowding_distance_assignment(front_objectives)
        
        # Map back to candidate indices
        candidate_distances = []
        for c in best_candidates:
            pos = np.where(front_idx == c)[0][0]
            candidate_distances.append(distances[pos])
        
        best = best_candidates[np.argmax(candidate_distances)]
        return population[best].copy()
    
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Single-point crossover."""
        n = len(parent1)
        point = np.random.randint(1, n)
        
        child1 = np.concatenate([parent1[:point], parent2[point:]])
        child2 = np.concatenate([parent2[:point], parent1[point:]])
        
        return child1, child2
    
    def _mutate(self, individual: np.ndarray, mutation_prob: float,
                min_val: int, max_val: int) -> np.ndarray:
        """Uniform mutation."""
        mutated = individual.copy()
        
        for i in range(len(mutated)):
            if np.random.random() < mutation_prob:
                mutated[i] = np.random.randint(min_val, max_val + 1)
        
        return mutated
    
    def _environmental_selection(self, population: np.ndarray,
                                objectives: np.ndarray,
                                target_size: int) -> np.ndarray:
        """Select survivors for next generation."""
        fronts = self._fast_non_dominated_sort(objectives)
        
        selected = []
        for front in fronts:
            if len(selected) + len(front) <= target_size:
                selected.extend(front)
            else:
                # Need to select partial front based on crowding distance
                remaining = target_size - len(selected)
                front_objectives = objectives[front]
                distances = self._crowding_distance_assignment(front_objectives)
                
                # Select individuals with largest crowding distance
                sorted_idx = np.argsort(distances)[::-1]
                selected.extend(front[sorted_idx[:remaining]])
                break
        
        return population[selected]
    
    def get_pareto_front(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get Pareto front from last run."""
        if self.results is None:
            raise ValueError("No results available. Run optimize() first.")
        
        return self.results['pareto_front'], self.results['pareto_objectives']
