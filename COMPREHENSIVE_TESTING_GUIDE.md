# Comprehensive Algorithm Testing Guide

## Overview

This document describes the comprehensive testing framework created to analyze which multi-objective optimization algorithm (NSGA-II, MOEA/D, or SPEA2) performs best under different conditions.

## Research Questions

1. **Which algorithm is most effective overall?**
2. **Does algorithm performance vary by application size?**
   - Small (2 services)
   - Medium (3 services)
   - Large (5 services)
   - Extra-Large (7 services)
3. **Does algorithm performance vary by user preferences?**
   - Cost-focused (cost weight >= 50%)
   - Latency-focused (latency weight >= 50%)
   - Performance-focused (performance weight >= 50%)
   - Balanced (no single objective >= 50%)

## Test Configuration

### Application Sizes

| Size | Services | CPU Range | RAM Range | Description |
|------|----------|-----------|-----------|-------------|
| Small | 2 | 1-2 cores | 2-4 GB | Microservice, simple app |
| Medium | 3 | 2-4 cores | 4-8 GB | Standard web application |
| Large | 5 | 4-8 cores | 8-16 GB | Complex enterprise app |
| Extra-Large | 7 | 8-16 cores | 16-32 GB | Data-intensive application |

### User Preference Combinations

13 different preference combinations are tested:

#### Balanced
- (33%, 33%, 34%) - Equal importance to all objectives

#### Cost-Focused
- (70%, 15%, 15%) - Heavily cost-optimized
- (60%, 20%, 20%) - Cost-preferred
- (50%, 25%, 25%) - Cost-dominant

#### Latency-Focused
- (15%, 70%, 15%) - Heavily latency-optimized
- (20%, 60%, 20%) - Latency-preferred
- (25%, 50%, 25%) - Latency-dominant

#### Performance-Focused
- (15%, 15%, 70%) - Heavily performance-optimized
- (20%, 20%, 60%) - Performance-preferred
- (25%, 25%, 50%) - Performance-dominant

#### Two-Objective Focused
- (45%, 45%, 10%) - Cost + Latency balanced
- (45%, 10%, 45%) - Cost + Performance balanced
- (10%, 45%, 45%) - Latency + Performance balanced

### Total Test Cases

With default settings:
- 4 application sizes
- 13 preference combinations
- 3 instances per configuration
- **Total: 156 test cases**

Each test case runs all 3 algorithms (NSGA-II, MOEAD, SPEA2), so **468 algorithm runs** in total.

## Running the Tests

### Quick Test (Sample)
```bash
python3 comprehensive_test_generator.py \
    --tests-per-config 1 \
    --population 20 \
    --generations 20 \
    --output-dir test_sample_results
```
This runs 52 tests (4 sizes × 13 preferences × 1 instance).

### Full Test Suite
```bash
python3 comprehensive_test_generator.py \
    --tests-per-config 3 \
    --population 50 \
    --generations 100 \
    --output-dir comprehensive_test_results
```
This runs 156 tests with proper population/generation settings for quality results.

### High-Quality Test (Research Grade)
```bash
python3 comprehensive_test_generator.py \
    --tests-per-config 5 \
    --population 100 \
    --generations 200 \
    --output-dir research_results
```
This runs 260 tests with high-quality settings suitable for thesis/publication.

## Output Files

The test generator creates:

1. **`all_results.json`** - Complete detailed results including:
   - Test configurations
   - Algorithm performance metrics
   - Pareto front sizes
   - Objective value ranges
   - Best solutions for each test

2. **`summary.csv`** - Concise results table with:
   - Test ID and configuration
   - User preferences
   - Best algorithm for each test
   - Best solution objectives (cost, latency, performance)

3. **`results_interim_N.json`** - Incremental saves every 10 tests (for recovery if interrupted)

## Understanding Results

### Algorithm Win Rate
The analysis shows:
- How many tests each algorithm won overall
- Win percentage by application size
- Win percentage by preference type

### Example Output
```
ANALYSIS SUMMARY
======================================================================

Algorithm Performance:
  NSGA2: 85/156 tests (54.5%)
  MOEAD: 45/156 tests (28.8%)
  SPEA2: 26/156 tests (16.7%)

Performance by Application Size:

  SMALL:
    NSGA2: 25/39 (64.1%)
    MOEAD: 10/39 (25.6%)
    SPEA2: 4/39 (10.3%)

  LARGE:
    MOEAD: 20/39 (51.3%)
    NSGA2: 15/39 (38.5%)
    SPEA2: 4/39 (10.3%)

Performance by Preference Type:

  Cost-focused:
    NSGA2: 30/48 (62.5%)
    MOEAD: 12/48 (25.0%)
    SPEA2: 6/48 (12.5%)

  Latency-focused:
    MOEAD: 25/48 (52.1%)
    NSGA2: 18/48 (37.5%)
    SPEA2: 5/48 (10.4%)
```

## Key Findings Template

After running the full test suite, analyze:

1. **Overall Winner**: Which algorithm wins most tests?
2. **Size-Specific Performance**:
   - Does NSGA-II dominate small applications?
   - Does MOEA/D excel at large applications?
3. **Preference-Specific Performance**:
   - Which algorithm is best for cost optimization?
   - Which handles latency requirements best?
   - Which maximizes performance?
4. **Trade-offs**:
   - Pareto front size comparison
   - Solution diversity analysis
   - Convergence speed differences

## Next Steps for Thesis

1. Run the full test suite with `--tests-per-config 5`
2. Analyze the results using the CSV file
3. Create visualizations:
   - Bar charts of algorithm win rates
   - Heatmaps of performance by size and preference
   - Box plots of objective value distributions
4. Document findings in thesis:
   - Which algorithm to recommend for which scenario
   - Statistical significance tests (chi-square, etc.)
   - Discussion of why certain algorithms excel in certain conditions

## Implementation Details

### Workload Generation
- Services are generated with randomized but realistic specifications
- CPU and RAM vary within size-category ranges
- Latency requirements are added between dependent services (10-100ms)
- Minimum performance scores are estimated based on CPU count

### Evaluation Method
- Uses global normalization for fair algorithm comparison
- Evaluates all 3 algorithms on identical workload configurations
- Selects best algorithm based on weighted score matching user preferences
- Records detailed statistics for post-analysis

### Reproducibility
- Uses fixed random seed (default: 42)
- All test configurations are saved in output files
- Incremental saving prevents data loss from interruptions

## Troubleshooting

### Tests Running Slowly
Reduce:
- `--population` (try 20 for quick tests, 50 for quality)
- `--generations` (try 20 for quick tests, 100 for quality)
- `--tests-per-config` (try 1 for quick tests, 3-5 for quality)

### Memory Issues
- Process tests in batches by modifying the script
- Save results more frequently
- Use smaller population sizes

### Unexpected Results
- Check `all_results.json` for detailed algorithm statistics
- Verify compatible instances are being found
- Review Pareto front sizes (should be > 1)

## References

This testing framework supports the research questions in:
- Thesis: "Multi-Cloud Workload Optimization Using Multi-Objective Evolutionary Algorithms"
- Algorithms: NSGA-II, MOEA/D, SPEA2
- Objectives: Cost minimization, Latency minimization, Performance maximization
