# Multi-Cloud Workload Optimization

Multi-objective optimization for intelligent workload placement across AWS, Azure, and GCP.

## Project Structure

```
multi-cloud-optimization/
├── algorithms/          # Optimization algorithms
│   ├── nsga2.py        # NSGA-II implementation
│   ├── moead.py        # MOEA/D (to be implemented)
│   └── base.py         # Base algorithm interface
├── data/               # Data files (symlinked from ~/thesis/data)
├── models/             # Cloud instance and workload models
│   ├── instance.py     # Cloud instance representation
│   └── workload.py     # Workload requirements
├── utils/              # Helper functions
│   ├── data_loader.py  # Load pricing, latency, performance data
│   └── metrics.py      # Evaluation metrics
├── results/            # Optimization results and visualizations
├── main.py             # Main entry point
└── requirements.txt    # Python dependencies
```

## Objectives

The system optimizes workload placement based on three objectives:

1. **Cost Minimization**: Total cost across all cloud providers
2. **Latency Minimization**: Network latency between services
3. **Performance Maximization**: Compute performance (Geekbench scores)

## Data Sources

- **Pricing**: `~/thesis/data/pricing/cloud-pricing.csv`
- **Network Latency**: `~/thesis/data/network/region-latency.csv`
- **Performance**: `~/thesis/data/performance/geekbench-scores.csv`

## Algorithms

### NSGA-II (Implemented)
Non-dominated Sorting Genetic Algorithm II - classic multi-objective evolutionary algorithm.

### MOEA/D (Planned)
Multi-Objective Evolutionary Algorithm based on Decomposition.

### Future Algorithms
- SPEA2
- IBEA
- Others...

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run NSGA-II optimization
python main.py --algorithm nsga2 --generations 100 --population 50

# Run with specific workload
python main.py --algorithm nsga2 --workload configs/workload1.json

# Compare algorithms
python main.py --compare nsga2,moead --generations 100
```

## Output

Results are saved in `results/` directory:
- Pareto front visualization
- Solution CSV files
- Performance metrics
- Convergence plots
