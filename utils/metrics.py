"""Evaluation metrics for optimization solutions."""

from typing import List, Tuple
import numpy as np
from models.instance import CloudInstance
from models.workload import Workload


class SolutionEvaluator:
    """Evaluate solutions based on multiple objectives."""
    
    def __init__(self, workload: Workload, instances: List[CloudInstance], normalize: bool = True):
        """
        Initialize evaluator.
        
        Args:
            workload: Workload to be deployed
            instances: Available cloud instances
            normalize: Whether to normalize objectives to [0, 1] range
        """
        self.workload = workload
        self.instances = instances
        self.num_services = len(workload.services)
        self.normalize = normalize
        
        # Compute normalization bounds if enabled
        if self.normalize:
            self._compute_normalization_bounds()
    
    def _compute_normalization_bounds(self):
        """Compute min/max bounds for objective normalization."""
        # Cost bounds: min/max instance costs
        min_cost = min(inst.hourly_cost for inst in self.instances) * self.num_services
        max_cost = max(inst.hourly_cost for inst in self.instances) * self.num_services
        
        # Latency bounds: 1ms (same region) to 100ms (realistic cross-cloud max)
        min_latency = 1.0
        max_latency = 100.0
        
        # Performance bounds: min/max instance performance
        min_perf = min(inst.multi_core_score for inst in self.instances) * self.num_services
        max_perf = max(inst.multi_core_score for inst in self.instances) * self.num_services
        
        self.bounds = {
            'cost': (min_cost, max_cost),
            'latency': (min_latency, max_latency),
            'performance': (min_perf, max_perf)
        }
    
    def decode_solution(self, solution: List[int]) -> List[CloudInstance]:
        """
        Decode solution chromosome to instance assignments.
        
        Args:
            solution: List of instance indices (one per service)
        
        Returns:
            List of CloudInstance assignments
        """
        return [self.instances[idx] for idx in solution]
    
    def evaluate(self, solution: List[int]) -> Tuple[float, float, float]:
        """
        Evaluate solution on all objectives.
        
        Args:
            solution: List of instance indices
        
        Returns:
            Tuple of (total_cost, avg_latency, neg_performance)
            Note: All objectives are minimization (performance is negated)
            If normalize=True, objectives are scaled to [0, 1]
        """
        assignments = self.decode_solution(solution)
        
        cost = self.calculate_cost(assignments)
        latency = self.calculate_latency(assignments)
        performance = self.calculate_performance(assignments)
        
        # Normalize if enabled
        if self.normalize:
            cost = self._normalize(cost, self.bounds['cost'])
            latency = self._normalize(latency, self.bounds['latency'])
            performance = self._normalize(performance, self.bounds['performance'])
        
        # Return as minimization objectives
        # Performance is negated so we minimize negative performance (= maximize performance)
        return (cost, latency, -performance)
    
    def _normalize(self, value: float, bounds: Tuple[float, float]) -> float:
        """
        Normalize value to [0, 1] range.
        
        Args:
            value: Value to normalize
            bounds: (min, max) tuple
        
        Returns:
            Normalized value in [0, 1]
        """
        min_val, max_val = bounds
        if max_val - min_val == 0:
            return 0.0
        return (value - min_val) / (max_val - min_val)
    
    def calculate_cost(self, assignments: List[CloudInstance]) -> float:
        """
        Calculate total hourly cost.
        
        Args:
            assignments: Instance assignments for each service
        
        Returns:
            Total hourly cost
        """
        return sum(instance.hourly_cost for instance in assignments)
    
    def calculate_latency(self, assignments: List[CloudInstance]) -> float:
        """
        Calculate average network latency between services.
        
        Args:
            assignments: Instance assignments for each service
        
        Returns:
            Average latency in milliseconds
        """
        total_latency = 0.0
        pair_count = 0
        
        # Calculate latency for all service pairs
        for i in range(len(assignments)):
            service_i = self.workload.services[i]
            instance_i = assignments[i]
            
            # Check if this service has latency requirements to others
            for j, service_j in enumerate(self.workload.services):
                if i == j:
                    continue
                
                instance_j = assignments[j]
                
                # Get latency between the two regions
                from_region = f"{instance_i.provider}:{instance_i.region}"
                to_region = f"{instance_j.provider}:{instance_j.region}"
                
                latency = instance_i.get_latency_to(to_region)
                
                # If no latency data (same region), assume 1ms
                if latency is None:
                    if from_region == to_region:
                        latency = 1.0
                    else:
                        # Missing data - use reasonable penalty (100ms instead of 200ms)
                        # This is realistic for long-distance cross-cloud connections
                        latency = 100.0
                
                total_latency += latency
                pair_count += 1
        
        if pair_count == 0:
            return 0.0
        
        return total_latency / pair_count
    
    def calculate_performance(self, assignments: List[CloudInstance]) -> float:
        """
        Calculate aggregate performance score.
        
        Args:
            assignments: Instance assignments for each service
        
        Returns:
            Aggregate performance (higher is better)
        """
        # Use average multi-core score as performance metric
        total_score = sum(instance.multi_core_score for instance in assignments)
        return total_score / len(assignments)
    
    def calculate_diversity(self, assignments: List[CloudInstance]) -> float:
        """
        Calculate deployment diversity (multi-cloud distribution).
        
        Args:
            assignments: Instance assignments for each service
        
        Returns:
            Diversity score (0 = all same provider, 1 = max diversity)
        """
        providers = set(inst.provider for inst in assignments)
        regions = set(f"{inst.provider}:{inst.region}" for inst in assignments)
        
        # Normalize by maximum possible diversity
        max_providers = min(3, len(assignments))  # AWS, Azure, GCP
        max_regions = len(assignments)
        
        provider_diversity = (len(providers) - 1) / (max_providers - 1) if max_providers > 1 else 0
        region_diversity = (len(regions) - 1) / (max_regions - 1) if max_regions > 1 else 0
        
        # Average of both
        return (provider_diversity + region_diversity) / 2.0
    
    def is_feasible(self, solution: List[int]) -> bool:
        """
        Check if solution meets all constraints.
        
        Args:
            solution: List of instance indices
        
        Returns:
            True if solution is feasible
        """
        assignments = self.decode_solution(solution)
        
        # Check if each instance meets its service requirements
        for i, (service, instance) in enumerate(zip(self.workload.services, assignments)):
            if not service.is_compatible_with(instance):
                return False
        
        # Check global cost constraint
        if self.workload.max_total_cost_per_hour:
            total_cost = self.calculate_cost(assignments)
            if total_cost > self.workload.max_total_cost_per_hour:
                return False
        
        # Check latency requirements between services
        for i, service_i in enumerate(self.workload.services):
            instance_i = assignments[i]
            
            for target_service, max_latency in service_i.latency_requirements.items():
                # Find the target service index
                target_idx = None
                for j, service_j in enumerate(self.workload.services):
                    if service_j.name == target_service:
                        target_idx = j
                        break
                
                if target_idx is not None:
                    instance_j = assignments[target_idx]
                    from_region = f"{instance_i.provider}:{instance_i.region}"
                    to_region = f"{instance_j.provider}:{instance_j.region}"
                    
                    latency = instance_i.get_latency_to(to_region)
                    if latency is None:
                        if from_region == to_region:
                            latency = 1.0
                        else:
                            latency = 100.0
                    
                    if latency > max_latency:
                        return False
        
        return True
    
    def get_solution_summary(self, solution: List[int]) -> dict:
        """
        Get detailed summary of a solution.
        
        Args:
            solution: List of instance indices
        
        Returns:
            Dictionary with solution details
        """
        assignments = self.decode_solution(solution)
        objectives = self.evaluate(solution)
        
        # Get raw (non-normalized) values for display
        cost_raw = self.calculate_cost(assignments)
        latency_raw = self.calculate_latency(assignments)
        performance_raw = self.calculate_performance(assignments)
        diversity = self.calculate_diversity(assignments)
        
        return {
            'cost': cost_raw,
            'latency': latency_raw,
            'performance': performance_raw,
            'diversity': diversity,
            'assignments': [
                {
                    'service': service.name,
                    'instance': instance.full_name,
                    'cost': instance.hourly_cost,
                    'vcpus': instance.vcpus,
                    'ram_gb': instance.ram_gb,
                    'multi_core_score': instance.multi_core_score
                }
                for service, instance in zip(self.workload.services, assignments)
            ],
            'feasible': self.is_feasible(solution)
        }
