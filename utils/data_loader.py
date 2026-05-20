"""Data loader for pricing, latency, and performance data."""

import csv
import os
from pathlib import Path
from typing import List, Dict, Tuple
from models.instance import CloudInstance


class DataLoader:
    """Load and parse cloud data from CSV files."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize data loader.
        
        Args:
            data_dir: Path to data directory. Defaults to ~/thesis/data
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/thesis/data")
        
        self.data_dir = Path(data_dir)
        self.pricing_file = self.data_dir / "pricing" / "cloud-pricing.csv"
        self.latency_file = self.data_dir / "network" / "region-latency.csv"
        self.performance_file = self.data_dir / "performance" / "geekbench-scores.csv"
        
        # Caches
        self._pricing_cache = None
        self._latency_cache = None
        self._performance_cache = None
    
    def load_pricing(self) -> Dict[Tuple[str, str, str], float]:
        """
        Load pricing data.
        
        Returns:
            Dictionary mapping (provider, region, instance_type) -> hourly_cost
        """
        if self._pricing_cache is not None:
            return self._pricing_cache
        
        pricing = {}
        
        with open(self.pricing_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows or rows where provider is missing
                if not row.get('provider') or not row['provider'].strip():
                    continue
                
                # Skip comments
                if row['provider'].startswith('#'):
                    continue
                
                key = (row['provider'], row['region'], row['instance_type'])
                pricing[key] = float(row['hourly_cost'])
        
        self._pricing_cache = pricing
        return pricing
    
    def load_latency_matrix(self) -> Dict[Tuple[str, str], float]:
        """
        Load network latency data.
        
        Returns:
            Dictionary mapping (from_region, to_region) -> latency_ms
        """
        if self._latency_cache is not None:
            return self._latency_cache
        
        latency = {}
        
        with open(self.latency_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows or rows where from_region is missing
                if not row.get('from_region') or not row['from_region'].strip():
                    continue
                
                # Skip comments
                if row['from_region'].startswith('#'):
                    continue
                
                from_region = f"{row['from_provider']}:{row['from_region']}"
                to_region = f"{row['to_provider']}:{row['to_region']}"
                
                key = (from_region, to_region)
                latency[key] = float(row['avg_latency_ms'])
        
        self._latency_cache = latency
        return latency
    
    def load_performance(self) -> Dict[Tuple[str, str, str], Tuple[int, int]]:
        """
        Load performance data (Geekbench scores).
        
        Returns:
            Dictionary mapping (provider, region, instance_type) -> (single_core, multi_core)
        """
        if self._performance_cache is not None:
            return self._performance_cache
        
        performance = {}
        
        with open(self.performance_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows or rows where provider is missing
                if not row.get('provider') or not row['provider'].strip():
                    continue
                
                # Skip comments
                if row['provider'].startswith('#'):
                    continue
                
                key = (row['provider'], row['region'], row['instance_type'])
                single_core = int(row['single_core_score'])
                multi_core = int(row['multi_core_score'])
                performance[key] = (single_core, multi_core)
        
        self._performance_cache = performance
        return performance
    
    def load_all_instances(self) -> List[CloudInstance]:
        """
        Load all cloud instances with integrated data.
        
        Returns:
            List of CloudInstance objects with pricing, performance, and latency data
        """
        pricing = self.load_pricing()
        latency_matrix = self.load_latency_matrix()
        performance = self.load_performance()
        
        instances = []
        
        # Read instance specs from performance file (most complete)
        with open(self.performance_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows
                if not row.get('provider') or not row['provider'].strip():
                    continue
                
                # Skip comments
                if row['provider'].startswith('#'):
                    continue
                
                provider = row['provider']
                region = row['region']
                instance_type = row['instance_type']
                
                key = (provider, region, instance_type)
                
                # Get pricing (default to 0 if not found)
                hourly_cost = pricing.get(key, 0.0)
                
                # Get performance
                single_core, multi_core = performance[key]
                
                # Build latency map for this instance's region
                instance_region = f"{provider}:{region}"
                latency_map = {}
                for (from_reg, to_reg), latency in latency_matrix.items():
                    if from_reg == instance_region:
                        latency_map[to_reg] = latency
                
                # Create instance
                instance = CloudInstance(
                    provider=provider,
                    region=region,
                    instance_type=instance_type,
                    vcpus=int(row['vcpus']),
                    ram_gb=float(row['ram_gb']),
                    architecture=row['architecture'],
                    hourly_cost=hourly_cost,
                    single_core_score=single_core,
                    multi_core_score=multi_core,
                    latency_map=latency_map
                )
                
                instances.append(instance)
        
        return instances
    
    def filter_instances(self, instances: List[CloudInstance], 
                        providers: List[str] = None,
                        regions: List[str] = None,
                        min_vcpus: int = None,
                        max_vcpus: int = None,
                        min_ram_gb: float = None,
                        max_cost: float = None) -> List[CloudInstance]:
        """
        Filter instances based on criteria.
        
        Args:
            instances: List of instances to filter
            providers: List of allowed providers
            regions: List of allowed regions
            min_vcpus: Minimum vCPUs
            max_vcpus: Maximum vCPUs
            min_ram_gb: Minimum RAM
            max_cost: Maximum hourly cost
        
        Returns:
            Filtered list of instances
        """
        filtered = instances
        
        if providers:
            filtered = [i for i in filtered if i.provider in providers]
        
        if regions:
            filtered = [i for i in filtered if i.region in regions]
        
        if min_vcpus:
            filtered = [i for i in filtered if i.vcpus >= min_vcpus]
        
        if max_vcpus:
            filtered = [i for i in filtered if i.vcpus <= max_vcpus]
        
        if min_ram_gb:
            filtered = [i for i in filtered if i.ram_gb >= min_ram_gb]
        
        if max_cost:
            filtered = [i for i in filtered if i.hourly_cost <= max_cost]
        
        return filtered
