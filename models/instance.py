"""Cloud instance representation."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CloudInstance:
    """Represents a cloud instance with its specifications and metrics."""
    
    provider: str  # aws, azure, gcp
    region: str
    instance_type: str
    vcpus: int
    ram_gb: float
    architecture: str  # x86_64, arm64
    
    # Pricing
    hourly_cost: float
    
    # Performance
    single_core_score: int
    multi_core_score: int
    
    # Network latency to other regions (will be populated from latency matrix)
    latency_map: dict = None
    
    def __post_init__(self):
        """Initialize latency map if not provided."""
        if self.latency_map is None:
            self.latency_map = {}
    
    @property
    def full_name(self) -> str:
        """Get full identifier of the instance."""
        return f"{self.provider}:{self.region}:{self.instance_type}"
    
    @property
    def performance_per_dollar(self) -> float:
        """Calculate performance per dollar metric."""
        if self.hourly_cost == 0:
            return float('inf')
        return self.multi_core_score / self.hourly_cost
    
    @property
    def performance_per_vcpu(self) -> float:
        """Calculate performance per vCPU."""
        if self.vcpus == 0:
            return 0
        return self.multi_core_score / self.vcpus
    
    def get_latency_to(self, target_region: str) -> Optional[float]:
        """Get network latency to target region in milliseconds."""
        return self.latency_map.get(target_region)
    
    def __str__(self) -> str:
        return (f"{self.full_name} | "
                f"{self.vcpus}vCPU {self.ram_gb}GB | "
                f"${self.hourly_cost:.4f}/hr | "
                f"Score: {self.multi_core_score}")
    
    def __repr__(self) -> str:
        return f"CloudInstance({self.full_name})"
