"""
Workload Generator for Comprehensive Testing
Generates workload variations of different sizes and complexities.
"""

import json
import os
from pathlib import Path
from typing import List, Dict


class WorkloadGenerator:
    """Generate workload configurations for testing."""

    # Application size categories
    SIZE_SPECS = {
        'tiny': {
            'vcpu_range': (1, 2),
            'ram_range': (1, 2),
            'score_range': (500, 1500),
            'latency_strict': (5, 15),
            'latency_moderate': (20, 40),
            'latency_relaxed': (50, 100)
        },
        'small': {
            'vcpu_range': (1, 2),
            'ram_range': (2, 4),
            'score_range': (1000, 2500),
            'latency_strict': (10, 20),
            'latency_moderate': (30, 60),
            'latency_relaxed': (80, 150)
        },
        'medium': {
            'vcpu_range': (2, 4),
            'ram_range': (4, 8),
            'score_range': (2000, 4500),
            'latency_strict': (15, 30),
            'latency_moderate': (40, 80),
            'latency_relaxed': (100, 200)
        },
        'large': {
            'vcpu_range': (4, 8),
            'ram_range': (8, 16),
            'score_range': (4000, 8000),
            'latency_strict': (20, 40),
            'latency_moderate': (50, 100),
            'latency_relaxed': (120, 250)
        },
        'xlarge': {
            'vcpu_range': (8, 16),
            'ram_range': (16, 32),
            'score_range': (8000, 15000),
            'latency_strict': (30, 50),
            'latency_moderate': (60, 120),
            'latency_relaxed': (150, 300)
        }
    }

    # Service templates (typical microservices)
    SERVICE_TEMPLATES = {
        'web': ['frontend', 'web_server', 'nginx', 'load_balancer'],
        'api': ['api_gateway', 'rest_api', 'graphql_api'],
        'backend': ['backend', 'application_server', 'business_logic'],
        'auth': ['auth_service', 'identity_service', 'oauth_server'],
        'database': ['database', 'postgres', 'mysql', 'mongo'],
        'cache': ['cache', 'redis', 'memcached'],
        'queue': ['worker_queue', 'message_queue', 'job_processor'],
        'storage': ['file_storage', 'object_storage', 's3_service'],
        'search': ['search_service', 'elasticsearch', 'search_engine'],
        'analytics': ['analytics_service', 'metrics_collector', 'logger']
    }

    def __init__(self):
        """Initialize workload generator."""
        self.generated_workloads = []

    def generate_service(self, service_type: str, size_category: str,
                        service_name: str, latency_profile: str = 'moderate') -> Dict:
        """
        Generate a single service specification.

        Args:
            service_type: Type of service (web, api, backend, etc.)
            size_category: Size category (tiny, small, medium, large, xlarge)
            service_name: Name for the service
            latency_profile: Latency strictness (strict, moderate, relaxed)

        Returns:
            Service specification dictionary
        """
        import random

        specs = self.SIZE_SPECS[size_category]

        # Adjust specs based on service type
        if service_type in ['database', 'backend']:
            vcpu = max(specs['vcpu_range'])
            ram = max(specs['ram_range'])
            score = int(specs['score_range'][1] * 0.9)
        elif service_type in ['cache', 'queue']:
            vcpu = min(specs['vcpu_range']) + 1
            ram = int((specs['ram_range'][0] + specs['ram_range'][1]) / 2)
            score = int((specs['score_range'][0] + specs['score_range'][1]) / 2)
        else:  # web, api, auth, etc.
            vcpu = min(specs['vcpu_range']) + 1
            ram = min(specs['ram_range']) + 1
            score = int(specs['score_range'][0] * 1.2)

        service = {
            'name': service_name,
            'vcpu_min': vcpu,
            'ram_gb_min': ram,
            'min_multi_core_score': score
        }

        return service

    def generate_workload(self, workload_id: int, size_category: str,
                         num_services: int, latency_profile: str,
                         service_mix: List[str] = None) -> Dict:
        """
        Generate a complete workload configuration.

        Args:
            workload_id: Unique ID for the workload
            size_category: Size category (tiny, small, medium, large, xlarge)
            num_services: Number of services in the workload
            latency_profile: Latency strictness (strict, moderate, relaxed)
            service_mix: List of service types to include (optional)

        Returns:
            Workload configuration dictionary
        """
        import random

        if service_mix is None:
            # Default service mix for typical application
            service_mix = ['web', 'api', 'backend', 'auth', 'database', 'cache', 'queue']

        # Ensure we don't exceed available service types
        num_services = min(num_services, len(service_mix))
        selected_types = service_mix[:num_services]

        services = []
        service_names = []

        # Generate services
        for i, svc_type in enumerate(selected_types):
            templates = self.SERVICE_TEMPLATES[svc_type]
            service_name = templates[0]  # Use first template name

            # Ensure unique names
            if service_name in service_names:
                service_name = f"{service_name}_{i}"
            service_names.append(service_name)

            service = self.generate_service(svc_type, size_category, service_name, latency_profile)
            services.append(service)

        # Add latency requirements (inter-service dependencies)
        specs = self.SIZE_SPECS[size_category]
        latency_key = f'latency_{latency_profile}'
        lat_min, lat_max = specs[latency_key]

        for i, service in enumerate(services):
            # Add latency requirements to some services
            if i < len(services) - 1:  # Not the last service
                latency_reqs = {}

                # Connect to 1-3 other services
                num_connections = min(random.randint(1, 3), len(services) - i - 1)
                target_indices = random.sample(range(i + 1, len(services)), num_connections)

                for target_idx in target_indices:
                    target_name = services[target_idx]['name']
                    latency_value = random.randint(lat_min, lat_max)
                    latency_reqs[target_name] = latency_value

                if latency_reqs:
                    service['latency_requirements'] = latency_reqs

        # Determine max cost based on size
        cost_multipliers = {
            'tiny': 1.0,
            'small': 2.0,
            'medium': 4.0,
            'large': 8.0,
            'xlarge': 12.0
        }
        base_cost = 1.5  # Base cost per service
        max_cost = base_cost * num_services * cost_multipliers[size_category]

        workload = {
            'name': f"Workload_{workload_id}_{size_category}_{num_services}svc_{latency_profile}lat",
            'services': services,
            'max_total_cost_per_hour': round(max_cost, 2),
            'prefer_single_provider': False,
            'prefer_single_region': False,
            'metadata': {
                'workload_id': workload_id,
                'size_category': size_category,
                'num_services': num_services,
                'latency_profile': latency_profile
            }
        }

        return workload

    def generate_test_suite(self, output_dir: str = 'test_workloads',
                           sizes: List[str] = None,
                           service_counts: List[int] = None,
                           latency_profiles: List[str] = None) -> List[str]:
        """
        Generate a comprehensive test suite of workloads.

        Args:
            output_dir: Directory to save workload files
            sizes: List of size categories to generate
            service_counts: List of service counts to generate
            latency_profiles: List of latency profiles to generate

        Returns:
            List of generated workload file paths
        """
        import random

        if sizes is None:
            sizes = ['tiny', 'small', 'medium', 'large', 'xlarge']

        if service_counts is None:
            service_counts = [3, 5, 7]

        if latency_profiles is None:
            latency_profiles = ['strict', 'moderate', 'relaxed']

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        workload_id = 1
        generated_files = []

        print(f"Generating test workloads...")
        print(f"Sizes: {sizes}")
        print(f"Service counts: {service_counts}")
        print(f"Latency profiles: {latency_profiles}")
        print()

        for size in sizes:
            for num_svc in service_counts:
                for lat_profile in latency_profiles:
                    # Generate workload
                    workload = self.generate_workload(
                        workload_id=workload_id,
                        size_category=size,
                        num_services=num_svc,
                        latency_profile=lat_profile
                    )

                    # Save to file
                    filename = f"workload_{workload_id:03d}_{size}_{num_svc}svc_{lat_profile}.json"
                    filepath = output_path / filename

                    with open(filepath, 'w') as f:
                        json.dump(workload, f, indent=2)

                    generated_files.append(str(filepath))
                    self.generated_workloads.append(workload)

                    print(f"Generated: {filename}")
                    workload_id += 1

        print(f"\nTotal workloads generated: {len(generated_files)}")

        # Generate summary
        summary_path = output_path / "workload_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("WORKLOAD GENERATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total workloads: {len(generated_files)}\n")
            f.write(f"Size categories: {', '.join(sizes)}\n")
            f.write(f"Service counts: {', '.join(map(str, service_counts))}\n")
            f.write(f"Latency profiles: {', '.join(latency_profiles)}\n\n")
            f.write("Generated files:\n")
            for fp in generated_files:
                f.write(f"  - {Path(fp).name}\n")

        print(f"\nSummary saved to: {summary_path}")

        return generated_files


def main():
    """Generate test workloads."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate test workloads')
    parser.add_argument('--output-dir', default='test_workloads',
                       help='Output directory for workloads')
    parser.add_argument('--sizes', nargs='+',
                       choices=['tiny', 'small', 'medium', 'large', 'xlarge'],
                       help='Size categories to generate')
    parser.add_argument('--services', nargs='+', type=int,
                       help='Service counts to generate (e.g., 3 5 7)')
    parser.add_argument('--latency', nargs='+',
                       choices=['strict', 'moderate', 'relaxed'],
                       help='Latency profiles to generate')

    args = parser.parse_args()

    generator = WorkloadGenerator()
    generator.generate_test_suite(
        output_dir=args.output_dir,
        sizes=args.sizes,
        service_counts=args.services,
        latency_profiles=args.latency
    )


if __name__ == '__main__':
    main()
