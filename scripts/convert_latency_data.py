#!/usr/bin/env python3
"""Convert measured latency data to optimization format."""

import csv
import sys

def parse_region(region_str):
    """Parse 'aws-us-east-1' to ('aws', 'us-east-1')."""
    parts = region_str.split('-', 1)
    if len(parts) == 2:
        provider = parts[0]
        region = parts[1]
        return provider, region
    return None, None

def main():
    input_file = '/Users/zawwaisoe/Desktop/Master_Thesis/Labs/latency-measurement/output/latency-matrix.csv'
    output_file = '/Users/zawwaisoe/thesis/data/network/region-latency.csv'
    
    print(f"Converting latency data...")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    
    rows = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_provider, from_region = parse_region(row['source'])
            to_provider, to_region = parse_region(row['target'])
            
            if from_provider and to_provider:
                # Use ping_avg_ms as the latency metric
                latency = float(row['ping_avg_ms'])
                
                rows.append({
                    'from_provider': from_provider,
                    'from_region': from_region,
                    'to_provider': to_provider,
                    'to_region': to_region,
                    'avg_latency_ms': latency,
                    'collection_date': '2025-03-16'
                })
    
    # Add self-references (same region = 1ms)
    unique_regions = set()
    for row in rows:
        unique_regions.add((row['from_provider'], row['from_region']))
    
    for provider, region in unique_regions:
        rows.append({
            'from_provider': provider,
            'from_region': region,
            'to_provider': provider,
            'to_region': region,
            'avg_latency_ms': 1.0,
            'collection_date': '2025-03-16'
        })
    
    # Add estimated Azure latency (based on geographic proximity)
    # Azure eastus is close to AWS us-east-1
    azure_estimates = [
        # Azure to AWS us-east-1 (same region)
        ('azure', 'eastus', 'aws', 'us-east-1', 5.0),
        ('aws', 'us-east-1', 'azure', 'eastus', 5.0),
        # Azure to AWS us-west-2
        ('azure', 'eastus', 'aws', 'us-west-2', 70.0),
        ('aws', 'us-west-2', 'azure', 'eastus', 70.0),
        # Azure to GCP us-east1 (same region)
        ('azure', 'eastus', 'gcp', 'us-east1', 8.0),
        ('gcp', 'us-east1', 'azure', 'eastus', 8.0),
        # Azure to GCP us-west1
        ('azure', 'eastus', 'gcp', 'us-west1', 75.0),
        ('gcp', 'us-west1', 'azure', 'eastus', 75.0),
        # Azure self
        ('azure', 'eastus', 'azure', 'eastus', 1.0),
    ]
    
    for from_p, from_r, to_p, to_r, latency in azure_estimates:
        rows.append({
            'from_provider': from_p,
            'from_region': from_r,
            'to_provider': to_p,
            'to_region': to_r,
            'avg_latency_ms': latency,
            'collection_date': '2025-03-25'
        })
    
    # Add GCP us-central1 estimates (between us-east1 and us-west1)
    gcp_central_estimates = [
        # GCP us-central1 to us-east1
        ('gcp', 'us-central1', 'gcp', 'us-east1', 30.0),
        ('gcp', 'us-east1', 'gcp', 'us-central1', 30.0),
        # GCP us-central1 to us-west1
        ('gcp', 'us-central1', 'gcp', 'us-west1', 35.0),
        ('gcp', 'us-west1', 'gcp', 'us-central1', 35.0),
        # GCP us-central1 self
        ('gcp', 'us-central1', 'gcp', 'us-central1', 1.0),
        # AWS us-east-1 to GCP us-central1
        ('aws', 'us-east-1', 'gcp', 'us-central1', 25.0),
        ('gcp', 'us-central1', 'aws', 'us-east-1', 25.0),
        # AWS us-west-2 to GCP us-central1
        ('aws', 'us-west-2', 'gcp', 'us-central1', 40.0),
        ('gcp', 'us-central1', 'aws', 'us-west-2', 40.0),
        # Azure eastus to GCP us-central1
        ('azure', 'eastus', 'gcp', 'us-central1', 30.0),
        ('gcp', 'us-central1', 'azure', 'eastus', 30.0),
    ]
    
    for from_p, from_r, to_p, to_r, latency in gcp_central_estimates:
        rows.append({
            'from_provider': from_p,
            'from_region': from_r,
            'to_provider': to_p,
            'to_region': to_r,
            'avg_latency_ms': latency,
            'collection_date': '2025-03-25'
        })
    
    # Write output
    with open(output_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'from_provider', 'from_region', 'to_provider', 'to_region',
            'avg_latency_ms', 'collection_date'
        ])
        writer.writeheader()
        
        # Add comment
        f.write('# Real latency measurements from latency-measurement lab\n')
        f.write('# Measured data: AWS and GCP regions (2025-03-16)\n')
        f.write('# Estimated data: Azure and GCP us-central1 (geographic approximation)\n')
        
        for row in rows:
            writer.writerow(row)
    
    print(f"Converted {len(rows)} latency entries")
    print(f"   Real measurements: AWS ↔ GCP regions")
    print(f"   Estimated: Azure, GCP us-central1")

if __name__ == '__main__':
    main()
