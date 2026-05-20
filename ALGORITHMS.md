# Implemented Algorithms

## Overview

Three state-of-the-art multi-objective evolutionary algorithms (MOEAs) are implemented:

1. **NSGA-II** - Non-dominated Sorting Genetic Algorithm II
2. **MOEA/D** - Multi-Objective Evolutionary Algorithm based on Decomposition
3. **SPEA2** - Strength Pareto Evolutionary Algorithm 2

All algorithms are implemented **from scratch** (not using libraries) for full control and customization.

---

## 1. NSGA-II

**File**: `algorithms/nsga2.py`  
**Lines**: ~373 lines

### Key Features
- **Fast non-dominated sorting** - O(MN²) complexity
- **Crowding distance** - Maintains diversity
- **Elitist selection** - Best solutions always survive
- **Tournament selection** - Rank + crowding distance

### Parameters
- Population size: 50 (default)
- Crossover probability: 0.9
- Mutation probability: 1/n_variables
- Tournament size: 2

### Strengths
✅ Well-established (most cited MOEA)  
✅ Good convergence properties  
✅ Maintains diversity well  
✅ Works well for 2-3 objectives  

### Reference
> Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE Transactions on Evolutionary Computation, 6(2), 182-197.

---

## 2. MOEA/D

**File**: `algorithms/moead.py`  
**Lines**: ~315 lines

### Key Features
- **Decomposition-based** - Converts multi-objective to scalar subproblems
- **Weight vectors** - Uniformly distributed using simplex lattice
- **Neighborhood structure** - Cooperative evolution
- **Tchebycheff decomposition** - Handles non-convex Pareto fronts

### Parameters
- Population size: 50 (= number of subproblems)
- Neighborhood size: 20
- Decomposition method: Tchebycheff
- Crossover: Single-point
- Mutation probability: 1/n_variables

### Strengths
✅ Good for many-objective problems  
✅ Fast convergence  
✅ Efficient use of population  
✅ Good distribution along Pareto front  

### Reference
> Zhang, Q., & Li, H. (2007). MOEA/D: A multiobjective evolutionary algorithm based on decomposition. IEEE Transactions on Evolutionary Computation, 11(6), 712-731.

---

## 3. SPEA2

**File**: `algorithms/spea2.py`  
**Lines**: ~355 lines

### Key Features
- **External archive** - Stores non-dominated solutions separately
- **Strength-based fitness** - Considers dominance relationships
- **Density estimation** - k-th nearest neighbor distance
- **Truncation operator** - Maintains archive diversity

### Parameters
- Population size: 50
- Archive size: 50 (equal to population)
- k-th neighbor: √N
- Binary tournament selection
- Crossover: Single-point
- Mutation probability: 1/n_variables

### Strengths
✅ Fine-grained fitness assignment  
✅ Good diversity preservation  
✅ Robust archive maintenance  
✅ Works well for irregular Pareto fronts  

### Reference
> Zitzler, E., Laumanns, M., & Thiele, L. (2001). SPEA2: Improving the strength Pareto evolutionary algorithm. TIK-report, 103.

---

## Algorithm Comparison

| Feature | NSGA-II | MOEA/D | SPEA2 |
|---------|---------|--------|-------|
| **Approach** | Dominance + crowding | Decomposition | Strength + density |
| **Population** | Single | Single | Population + Archive |
| **Selection** | Tournament | Neighborhood | Binary tournament |
| **Diversity** | Crowding distance | Weight vectors | k-NN density |
| **Best for** | General problems | Many objectives | Irregular fronts |
| **Complexity** | O(MN²) | O(N²) | O(N²log N) |
| **Memory** | N solutions | N solutions | 2N solutions |

---

## Usage

### Run Single Algorithm
```bash
# NSGA-II
python main.py --algorithm nsga2 --population 50 --generations 100

# MOEA/D
python main.py --algorithm moead --population 50 --generations 100

# SPEA2
python main.py --algorithm spea2 --population 50 --generations 100
```

### Run All Three for Comparison
```bash
python main.py --algorithm all --population 50 --generations 100
```

Or use the convenience script:
```bash
./run-all.sh
```

---

## Output Structure

When running all algorithms:
```
results/
├── nsga2/
│   ├── pareto_front.png
│   ├── solutions.csv
│   ├── convergence.png
│   └── results.json
├── moead/
│   ├── pareto_front.png
│   ├── solutions.csv
│   ├── convergence.png
│   └── results.json
└── spea2/
    ├── pareto_front.png
    ├── solutions.csv
    ├── convergence.png
    └── results.json
```

---

## Implementation Details

### Common Components (All Algorithms)
- **Encoding**: Integer array [inst₁, inst₂, ..., instₙ]
- **Crossover**: Single-point crossover
- **Mutation**: Uniform mutation (random reset)
- **Constraints**: Handled during evaluation (infeasible solutions get penalty)

### Algorithm-Specific Components

**NSGA-II**:
- Fast non-dominated sort: Fronts [F₀, F₁, F₂, ...]
- Crowding distance: Boundary = ∞, others = normalized spacing
- Environmental selection: Front rank first, then crowding distance

**MOEA/D**:
- Weight generation: Simplex lattice (Das-Dennis for 3D)
- Neighborhood: k-nearest neighbors in weight space
- Scalar fitness: `max{wᵢ × |fᵢ - zᵢ*|}`
- Update: Replace neighbors if better on their subproblem

**SPEA2**:
- Strength: Number of solutions dominated
- Raw fitness: Sum of dominators' strengths
- Density: 1/(σₖ + 2) where σₖ is k-NN distance
- Truncation: Remove most crowded iteratively

---

## Performance Metrics

All algorithms optimize three objectives:
1. **Cost** (minimize) - Total hourly cost
2. **Latency** (minimize) - Average inter-service latency
3. **Performance** (maximize) - Average Geekbench score

### Evaluation Metrics
- **Pareto front size** - Number of non-dominated solutions
- **Convergence** - Tracking over generations
- **Diversity** - Spread of solutions
- **Quality** - Objective ranges

---

## Expected Results

Based on 100 generations, population 50:

| Algorithm | Pareto Size | Convergence | Diversity | Execution Time |
|-----------|-------------|-------------|-----------|----------------|
| NSGA-II | 30-50 | Good | Excellent | ~90s |
| MOEA/D | 40-50 | Excellent | Good | ~80s |
| SPEA2 | 35-50 | Good | Excellent | ~100s |

**Note**: Results may vary based on problem complexity and randomness.

---

## Customization

### Adding New Objectives
Edit `utils/metrics.py`:
```python
def evaluate(self, solution):
    cost = self.calculate_cost(assignments)
    latency = self.calculate_latency(assignments)
    performance = self.calculate_performance(assignments)
    # Add new objective:
    reliability = self.calculate_reliability(assignments)
    
    return (cost, latency, -performance, -reliability)
```

### Tuning Parameters
- **Population size**: 20-100 (larger = more diversity, slower)
- **Generations**: 50-200 (more = better convergence, slower)
- **MOEA/D neighbors**: 10-30 (balance exploration/exploitation)
- **SPEA2 archive**: Equal to pop or larger

---

## Validation

All three algorithms have been:
- ✅ Implemented from scratch (no black-box libraries)
- ✅ Tested with real cloud data (pricing, latency, performance)
- ✅ Validated against published papers
- ✅ Compared for consistency

---

## Future Work

Potential extensions:
1. **NSGA-III** - For many-objective (4+ objectives)
2. **IBEA** - Indicator-based EA
3. **SMS-EMOA** - S-metric selection
4. **MOEA/DD** - Diversity-based MOEA/D
5. **Parallel execution** - Multi-threading for faster evaluation

---

**Last Updated**: March 25, 2025  
**Status**: All three algorithms implemented and tested ✅
