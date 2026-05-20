# Quick Start Guide

## Installation

```bash
# Navigate to project directory
cd /Users/zawwaisoe/Desktop/Master_Thesis/Labs/multi-cloud-optimization

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Data Setup

Data is symlinked from `~/thesis/data`:
- **Pricing**: `~/thesis/data/pricing/cloud-pricing.csv`
- **Latency**: `~/thesis/data/network/region-latency.csv`
- **Performance**: `~/thesis/data/performance/geekbench-scores.csv`

The symlink is already created. If you need to recreate it:
```bash
ln -s ~/thesis/data data
```

## Running Optimization

### Quick Run (Sample Workload)
```bash
# Use the run.sh script
./run.sh

# Or manually:
python main.py --algorithm nsga2 --population 50 --generations 100
```

### Custom Workload
```bash
python main.py \
  --algorithm nsga2 \
  --workload configs/sample_workload.json \
  --population 100 \
  --generations 200 \
  --output-dir results/experiment1
```

### Parameters

- `--algorithm`: Algorithm to use (nsga2, moead)
- `--workload`: Path to workload JSON file
- `--population`: Population size (default: 50)
- `--generations`: Number of generations (default: 100)
- `--output-dir`: Output directory (default: results)

## Output Files

After running, check the `results/` directory:

1. **pareto_front_nsga2.png** - 2D projections of Pareto front
2. **solutions_nsga2.csv** - All Pareto solutions with instance assignments
3. **convergence_nsga2.png** - Convergence curves over generations
4. **results_nsga2.json** - Raw results data

## Example Workload Configuration

Create a JSON file in `configs/`:

```json
{
  "name": "My Workload",
  "services": [
    {
      "name": "frontend",
      "vcpu_min": 2,
      "ram_gb_min": 4,
      "min_multi_core_score": 2000,
      "latency_requirements": {
        "backend": 50
      }
    },
    {
      "name": "backend",
      "vcpu_min": 4,
      "ram_gb_min": 8,
      "min_multi_core_score": 4000,
      "latency_requirements": {
        "database": 20
      }
    },
    {
      "name": "database",
      "vcpu_min": 4,
      "ram_gb_min": 16
    }
  ],
  "max_total_cost_per_hour": 5.0
}
```

## Understanding Results

### Objectives (all minimization)

1. **Cost**: Total hourly cost ($/hour)
2. **Latency**: Average network latency between services (ms)
3. **Performance**: Negative of average Geekbench score (negated for minimization)

### Pareto Front

The Pareto front contains non-dominated solutions where:
- No solution is strictly better in all objectives
- Each solution represents a trade-off

### Choosing a Solution

From the Pareto front, select based on priorities:
- **Cost-focused**: Lowest cost solution
- **Performance-focused**: Highest performance (most negative in objective)
- **Balanced**: Middle ground solutions

## Adding New Algorithms

1. Create new file in `algorithms/` (e.g., `spea2.py`)
2. Inherit from `OptimizationAlgorithm` base class
3. Implement `optimize()` and `get_pareto_front()` methods
4. Update `main.py` to include new algorithm

See `algorithms/moead.py` for template.

## Modifying Data

If you want to update the cloud data:
```bash
# Edit pricing
nano ~/thesis/data/pricing/cloud-pricing.csv

# Edit latency
nano ~/thesis/data/network/region-latency.csv

# Edit performance
nano ~/thesis/data/performance/geekbench-scores.csv
```

Changes will be automatically picked up in next run.

## Troubleshooting

**No compatible instances found:**
- Check service requirements (vCPU, RAM, performance scores)
- Verify data files contain matching instances

**Poor convergence:**
- Increase population size
- Increase number of generations
- Check constraint feasibility

**Memory issues:**
- Reduce population size
- Filter instances more aggressively
- Use smaller workloads for testing

## Next Steps

1. ✅ Run with sample workload
2. Create your own workload configurations
3. Experiment with population/generation sizes
4. Implement MOEA/D algorithm
5. Add visualization improvements
6. Compare multiple algorithms
