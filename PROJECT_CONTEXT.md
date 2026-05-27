# Multi-Cloud Workload Optimization - Project Context

> **Purpose**: This file provides context for Claude Code and other AI assistants
> **Auto-loaded**: When you start `thesis-code`, this file is automatically read
> **Last Updated**: 2026-05-20

---

## 📌 Project Overview

**Title**: Multi-Cloud Workload Optimization using Multi-Objective Evolutionary Algorithms

**Description**: A Master's thesis implementation that optimizes workload placement across AWS, Azure, and GCP using three state-of-the-art multi-objective evolutionary algorithms (MOEAs).

**Objectives** (3 conflicting objectives):
1. **Cost Minimization** - Total hourly cost across all cloud providers
2. **Latency Minimization** - Average network latency between services
3. **Performance Maximization** - Average compute performance (Geekbench scores)

**Approach**: Custom implementations of NSGA-II, MOEA/D, and SPEA2 algorithms from scratch (not using black-box libraries).

---

## 📂 Directory Structure

```
multi-cloud-optimization/
├── configs/                          # Configuration files
│   └── Thesis_Workflow_Visual_Guide.md  # Workflow documentation
│
├── algorithms/                       # Core algorithm implementations
│   ├── nsga2.py                     # NSGA-II (~373 lines)
│   ├── moead.py                     # MOEA/D (~315 lines)
│   └── spea2.py                     # SPEA2 (~355 lines)
│
├── algorithms_library/               # Library-based implementations (for comparison)
│   ├── nsga2_library.py
│   ├── moead_library.py
│   └── spea2_library.py
│
├── models/                          # Data models
│   ├── instance.py                  # Cloud instance model
│   └── workload.py                  # Workload requirements model
│
├── utils/                           # Utility functions
│   ├── data_loader.py              # Load pricing, latency, performance data
│   ├── metrics.py                  # Evaluation metrics & objectives
│   ├── visualization.py            # Plotting utilities
│   └── dominance.py                # Pareto dominance utilities
│
├── data/                           # Data files (symlinked)
│   ├── pricing/                    # Cloud pricing data
│   ├── network/                    # Inter-region latency data
│   └── performance/                # Geekbench scores
│
├── test_workloads/                 # Generated test workloads
├── test_preferences/               # Generated user preferences
├── results/                        # Algorithm outputs & visualizations
│
├── main.py                         # Main entry point (v1)
├── main_v2.py                      # Main entry point (v2 - improved)
├── main_v3.py                      # Main entry point (v3 - latest)
│
├── workload_generator.py           # Generate test workloads
├── preference_generator.py         # Generate user preferences
├── compare_implementations.py      # Compare custom vs library
├── comprehensive_algorithm_tester.py  # Full testing suite
│
├── CURRENT_STATUS.md               # Daily status tracking (UPDATE THIS!)
├── PROJECT_CONTEXT.md              # This file (Claude Code context)
│
└── Documentation files:
    ├── ALGORITHMS.md               # Algorithm details & comparisons
    ├── IMPLEMENTATION.md           # Implementation guidelines
    ├── QUICKSTART.md              # Quick start guide
    ├── COMPREHENSIVE_TESTING_GUIDE.md
    ├── COMPREHENSIVE_TESTING_README.md
    └── [Other .md files]           # Research notes, meeting reports
```

---

## 🧬 Implemented Algorithms

### 1. NSGA-II (Non-dominated Sorting Genetic Algorithm II)
- **File**: `algorithms/nsga2.py`
- **Status**: ✅ Fully implemented & tested
- **Key Features**:
  - Fast non-dominated sorting (O(MN²))
  - Crowding distance for diversity
  - Elitist selection
  - Tournament selection
- **Best for**: General multi-objective problems (2-3 objectives)
- **Reference**: Deb et al. (2002)

### 2. MOEA/D (Multi-Objective EA based on Decomposition)
- **File**: `algorithms/moead.py`
- **Status**: ✅ Fully implemented & tested
- **Key Features**:
  - Decomposition-based approach
  - Weight vectors (Das-Dennis method)
  - Neighborhood structure
  - Tchebycheff decomposition
- **Best for**: Many-objective problems, fast convergence
- **Reference**: Zhang & Li (2007)

### 3. SPEA2 (Strength Pareto Evolutionary Algorithm 2)
- **File**: `algorithms/spea2.py`
- **Status**: ✅ Fully implemented & tested
- **Key Features**:
  - External archive
  - Strength-based fitness
  - k-NN density estimation
  - Truncation operator
- **Best for**: Irregular Pareto fronts, fine-grained fitness
- **Reference**: Zitzler et al. (2001)

---

## 🔧 Technical Details

### Encoding
- **Representation**: Integer array `[inst₁, inst₂, ..., instₙ]`
- Each gene represents instance assignment for a workload
- Instance IDs map to cloud providers (AWS, Azure, GCP)

### Genetic Operators
- **Crossover**: Single-point crossover (probability: 0.9)
- **Mutation**: Uniform mutation (probability: 1/n_variables)
- **Selection**: Tournament selection (NSGA-II, SPEA2), Neighborhood (MOEA/D)

### Objectives
```python
# Minimize cost, latency; Maximize performance
objectives = (cost, latency, -performance)  # Note: performance is negated
```

### Constraints
- **Budget constraint**: Total cost ≤ user budget
- **Latency constraint**: Max latency ≤ user threshold
- **Performance constraint**: Min performance ≥ user requirement
- **Handling**: Infeasible solutions get penalty in objective values

---

## 🚀 Common Commands

### Running Algorithms

```bash
# Single algorithm
python main_v3.py --algorithm nsga2 --population 50 --generations 100
python main_v3.py --algorithm moead --population 50 --generations 100
python main_v3.py --algorithm spea2 --population 50 --generations 100

# All algorithms (comparison)
python main_v3.py --algorithm all --population 50 --generations 100

# Or use convenience script
./run-all.sh
```

### Generate Test Data

```bash
# Generate workloads
python workload_generator.py --count 10

# Generate preferences
python preference_generator.py --count 5
```

### Testing & Comparison

```bash
# Compare custom vs library implementations
python compare_implementations.py

# Comprehensive testing
python comprehensive_algorithm_tester.py

# Run comprehensive test suite
python run_comprehensive_tests.py
```

### Git Workflow

```bash
# Daily morning routine
git pull
cat CURRENT_STATUS.md

# Daily evening routine
git add .
git commit -m "Description of today's work"
git push
```

---

## 📦 Dependencies

```
Python >= 3.8
numpy
matplotlib
pygmo (optional - for comparison only)
```

Install:
```bash
pip install -r requirements.txt
```

Or with venv:
```bash
source venv/bin/activate  # Or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📐 Coding Conventions

### File Organization
- `algorithms/` - Core algorithm implementations (MODIFY CAREFULLY)
- `utils/` - Helper functions (MODIFY AS NEEDED)
- `models/` - Data structures (RARELY MODIFY)
- `data/` - Data files (READ-ONLY)

### Naming Conventions
- Classes: `PascalCase` (e.g., `NSGA2`, `MOEADAlgorithm`)
- Functions: `snake_case` (e.g., `fast_non_dominated_sort`, `crowding_distance`)
- Variables: `snake_case` (e.g., `population_size`, `pareto_front`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_GENERATIONS`, `DEFAULT_POPULATION`)

### Documentation
- All functions must have docstrings
- Complex algorithms should have inline comments explaining the steps
- Reference paper equations/algorithms in comments when applicable

### Testing
- Always test after major changes
- Compare results with library implementations when possible
- Validate against known benchmarks

---

## 🎯 Current Phase: Thesis Writing Preparation

### What's Done
- ✅ All three algorithms implemented from scratch
- ✅ Custom and library implementations
- ✅ Comprehensive testing framework
- ✅ Real-world data integration
- ✅ Results generation and visualization

### What's Next
- 🚧 Thesis workflow setup
- 📝 Thesis structure planning
- 📝 Related work research
- 📝 Writing chapters

### Important Files to Track
- **CURRENT_STATUS.md** - Update this DAILY (morning & evening)
- **PROJECT_CONTEXT.md** - Update when project structure changes
- **Results files** - Track in git, reference in thesis

---

## 💡 Important Notes for Claude Code

### When Implementing Features
1. **Always check CURRENT_STATUS.md first** to understand what's being worked on
2. **Follow existing code style** - Look at `algorithms/nsga2.py` as reference
3. **Test thoroughly** - Compare with library implementations when possible
4. **Document well** - Add docstrings and inline comments
5. **Update CURRENT_STATUS.md** - Reflect progress and issues

### When Debugging
1. Check if similar functionality exists in other algorithms
2. Verify data loading is correct (pricing, latency, performance)
3. Validate constraint handling
4. Compare intermediate results with library implementations

### When Asked About Project
1. Read CURRENT_STATUS.md to get latest status
2. Check specific algorithm files for implementation details
3. Reference ALGORITHMS.md for algorithm comparisons
4. Look at test results in results/ directories

### File Modification Guidelines
- **Safe to modify**: `main_*.py`, `workload_generator.py`, `preference_generator.py`, documentation files
- **Modify carefully**: `algorithms/*.py`, `utils/*.py`
- **Rarely modify**: `models/*.py`, `algorithms_library/*.py`
- **Never modify**: `data/` files

---

## 🔗 Related Files

### For Understanding Algorithms
- `ALGORITHMS.md` - Detailed algorithm explanations
- `algorithms/nsga2.py` - NSGA-II implementation
- `algorithms/moead.py` - MOEA/D implementation
- `algorithms/spea2.py` - SPEA2 implementation

### For Understanding Implementation
- `IMPLEMENTATION.md` - Implementation guidelines
- `V2_IMPLEMENTATION_GUIDE.md` - Version 2 improvements
- `NORMALIZATION_EXPLAINED.md` - Normalization techniques

### For Understanding Testing
- `COMPREHENSIVE_TESTING_GUIDE.md` - Testing documentation
- `COMPREHENSIVE_TESTING_README.md` - Testing README
- `ALGORITHM_VALIDATION_REPORT.md` - Validation results

### For Understanding Results
- `ALGORITHM_COMPARISON_REPORT.txt` - Custom vs Library comparison
- `PROFESSOR_MEETING_REPORT.md` - Meeting notes
- `RESEARCH_FINDINGS_SUMMARY.md` - Research insights

---

## 🎓 Thesis Context

**Student**: Zaw Wai Soe
**Student ID**: 680531027
**Program**: Master's Thesis
**Topic**: Multi-Cloud Workload Optimization using MOEAs
**Supervisor**: Assist Prof: Ratsameetip Wita

**Key Contributions**:
1. Custom implementations of NSGA-II, MOEA/D, SPEA2 from scratch
2. Real-world cloud data integration (AWS, Azure, GCP)
3. Comprehensive comparison and validation
4. Practical application to multi-cloud workload optimization problem

**Phase Status**:
- Implementation Phase: ✅ Complete
- Testing Phase: ✅ Complete
- Workflow Setup: 🚧 In Progress
- Thesis Writing: 📅 Starting Soon

---

## 🔄 Workflow Integration

### Daily Workflow
1. **Morning** (5 min):
   - Open terminal: `cat CURRENT_STATUS.md`
   - Update today's plan in CURRENT_STATUS.md
   - Commit: `git add CURRENT_STATUS.md && git commit -m "Daily plan" && git push`

2. **During Work**:
   - Use `thesis-code` alias to start Claude Code (auto-loads this file)
   - Update CURRENT_STATUS.md as you make progress
   - Commit frequently

3. **Evening** (5 min):
   - Review work: `git status`
   - Commit changes: `git add . && git commit -m "Today's work" && git push`
   - Update CURRENT_STATUS.md with tomorrow's plan

### Claude Code Session
```bash
# Start new session
thesis-code "Continue thesis work"

# Claude Code automatically reads:
# - PROJECT_CONTEXT.md (this file)
# - CURRENT_STATUS.md (daily status)
```

### Claude Chat (Notion)
- Use for strategic planning and discussions
- Notion pages sync with GitHub context files
- Access via Notion MCP in Claude Chat

---

## 📞 Contact & Resources

### Useful Links
- GitHub Repo: [Link will be added]
- Notion Workspace: [Link will be added]
- Cloud Pricing Data: AWS, Azure, GCP pricing pages
- Algorithm Papers: See References section in ALGORITHMS.md

### Support
- For algorithm questions: Check ALGORITHMS.md
- For implementation questions: Check IMPLEMENTATION.md
- For testing questions: Check COMPREHENSIVE_TESTING_GUIDE.md
- For workflow questions: Check configs/Thesis_Workflow_Visual_Guide.md

---

**Remember**: This file helps Claude Code understand your project context.
**Keep it updated** when you make structural changes to the project!
