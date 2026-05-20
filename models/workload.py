"""Workload representation and requirements."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ServiceRequirement:
    """Requirements for a single service/microservice."""
    
    name: str
    vcpu_min: int
    ram_gb_min: float
    architecture_preference: Optional[str] = None  # x86_64, arm64, or None for any
    
    # Performance requirements
    min_single_core_score: Optional[int] = None
    min_multi_core_score: Optional[int] = None
    
    # Cost constraints
    max_hourly_cost: Optional[float] = None
    
    # Network requirements (latency to other services in ms)
    latency_requirements: dict = None  # {service_name: max_latency_ms}
    
    def __post_init__(self):
        """Initialize latency requirements if not provided."""
        if self.latency_requirements is None:
            self.latency_requirements = {}
    
    def is_compatible_with(self, instance) -> bool:
        """Check if instance meets this service's requirements."""
        # Check vCPU
        if instance.vcpus < self.vcpu_min:
            return False
        
        # Check RAM
        if instance.ram_gb < self.ram_gb_min:
            return False
        
        # Check architecture preference
        if self.architecture_preference and instance.architecture != self.architecture_preference:
            return False
        
        # Check performance requirements
        if self.min_single_core_score and instance.single_core_score < self.min_single_core_score:
            return False
        if self.min_multi_core_score and instance.multi_core_score < self.min_multi_core_score:
            return False
        
        # Check cost constraint
        if self.max_hourly_cost and instance.hourly_cost > self.max_hourly_cost:
            return False
        
        return True


@dataclass
class Workload:
    """Collection of services that need to be deployed."""
    
    name: str
    services: List[ServiceRequirement]
    
    # Global constraints
    max_total_cost_per_hour: Optional[float] = None
    max_total_cost_per_month: Optional[float] = None
    
    # Deployment preferences
    prefer_single_provider: bool = False  # Minimize cross-cloud traffic
    prefer_single_region: bool = False    # Minimize intra-cloud latency
    
    def __len__(self) -> int:
        """Number of services in this workload."""
        return len(self.services)
    
    def get_service(self, name: str) -> Optional[ServiceRequirement]:
        """Get service by name."""
        for service in self.services:
            if service.name == name:
                return service
        return None
    
    @property
    def total_min_vcpus(self) -> int:
        """Total minimum vCPUs required."""
        return sum(s.vcpu_min for s in self.services)
    
    @property
    def total_min_ram_gb(self) -> float:
        """Total minimum RAM required."""
        return sum(s.ram_gb_min for s in self.services)
    
    def __str__(self) -> str:
        return (f"Workload '{self.name}': {len(self)} services, "
                f"min {self.total_min_vcpus} vCPUs, {self.total_min_ram_gb} GB RAM")
