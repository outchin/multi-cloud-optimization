# Thesis Writing Plan

> **Purpose**: Detailed chapter outline and writing schedule
> **For**: Notion reference & thesis writing guidance
> **Last Updated**: 2026-05-20

---

## Thesis Title

**Multi-Cloud Workload Optimization using Multi-Objective Evolutionary Algorithms: A Comparative Study of NSGA-II, MOEA/D, and SPEA2**

---

## Target Specifications

- **Total Pages**: 80-120 pages (Target: ~100 pages)
- **Timeline**: 6-8 weeks
- **Target Submission**: TBD
- **Format**: Master's Thesis

---

## Chapter Breakdown & Writing Schedule

### Chapter 1: Introduction
**Target Length**: 8-10 pages
**Timeline**: Week 1
**Status**: ⏳ Not Started

#### 1.1 Background & Motivation (2-3 pages)
- Cloud computing evolution
- Multi-cloud adoption trends
- Workload placement challenges
- Conflicting objectives: Cost, Latency, Performance

#### 1.2 Problem Statement (1-2 pages)
- Multi-objective optimization problem
- Why multi-cloud workload placement is hard
- Need for systematic algorithm comparison

#### 1.3 Research Questions (1 page)
1. Which algorithm performs best for multi-cloud workload optimization?
2. How do algorithms compare by workload size?
3. How do algorithms compare by user preference type?
4. Are custom implementations comparable to established libraries?

#### 1.4 Thesis Contributions (2 pages)
1. Custom implementations of NSGA-II, MOEA/D, SPEA2
2. Real-world data integration (empirical latency testing)
3. Comprehensive algorithm comparison (260 test cases)
4. Algorithm selection guidelines
5. Library issue discovery (MOEA/D)

#### 1.5 Thesis Structure (1 page)
- Brief overview of each chapter

**Writing Notes**:
- Start with motivating example (e-commerce microservices)
- Cite cloud adoption statistics
- Emphasize practical contribution

---

### Chapter 2: Literature Review
**Target Length**: 15-20 pages
**Timeline**: Week 2
**Status**: ⏳ Not Started

#### 2.1 Multi-Objective Optimization (3-4 pages)
- Pareto dominance concept
- Pareto front definition
- Multi-objective vs single-objective
- Evaluation metrics (hypervolume, IGD, etc.)

#### 2.2 Evolutionary Algorithms Overview (2-3 pages)
- Genetic algorithms basics
- Genetic operators (selection, crossover, mutation)
- Evolution process
- Why EA for multi-objective optimization

#### 2.3 NSGA-II (3-4 pages)
- History & development (Deb et al. 2002)
- Fast non-dominated sorting (O(MN²))
- Crowding distance for diversity
- Elitist approach
- Applications & success stories

#### 2.4 MOEA/D (3-4 pages)
- Decomposition concept (Zhang & Li 2007)
- Weight vectors (Das-Dennis method)
- Neighborhood structure
- Tchebycheff/weighted sum decomposition
- Advantages for many-objective problems

#### 2.5 SPEA2 (3-4 pages)
- Archive-based approach (Zitzler et al. 2001)
- Strength-based fitness
- k-NN density estimation
- Truncation operator
- Improvements over SPEA

#### 2.6 Cloud Workload Optimization (2-3 pages)
- Existing work in cloud optimization
- Multi-cloud placement studies
- Related evolutionary algorithm applications
- **Gap**: No comprehensive NSGA-II/MOEA/D/SPEA2 comparison for multi-cloud

**Writing Notes**:
- Include algorithm diagrams
- Cite key papers (Deb 2002, Zhang 2007, Zitzler 2001)
- Identify research gap clearly

---

### Chapter 3: Methodology
**Target Length**: 15-18 pages
**Timeline**: Week 3
**Status**: ⏳ Not Started

#### 3.1 Problem Formulation (3-4 pages)
- Decision variables (instance assignments)
- Objectives:
  * Minimize Cost: Σ(hourly_cost)
  * Minimize Latency: Avg(inter-service latency)
  * Maximize Performance: Avg(Geekbench scores)
- Constraints:
  * CPU requirements met
  * RAM requirements met
  * Budget limit
  * Latency threshold

#### 3.2 Data Collection (4-5 pages)
- **Cost Data**:
  * Web crawling methodology
  * AWS, Azure, GCP pricing
  * CSV format & structure

- **Performance Data**:
  * Geekbench benchmark selection
  * Data sources & reliability
  * Instance types covered

- **Latency Data**:
  * **Empirical testing approach** (Critical contribution!)
  * Server deployment (regions used)
  * Testing methodology (ping tests, RTT)
  * Latency matrix structure
  * Results: 1ms (intra-region), 10-50ms (cross-region), 2.5-270ms (cross-cloud)

#### 3.3 User Input Specification (2-3 pages)
- JSON workload template
- Service definitions
- Resource requirements (CPU, RAM)
- User preferences (weights & constraints)

#### 3.4 Algorithm Descriptions (4-5 pages)
- NSGA-II implementation details
- MOEA/D implementation details
- SPEA2 implementation details
- Common components (encoding, crossover, mutation)

#### 3.5 Evaluation Approach (1-2 pages)
- Custom vs library validation
- Comprehensive testing framework
- Win rate determination

**Writing Notes**:
- Include latency testing setup diagram
- Explain JSON format with examples
- Reference data files location

---

### Chapter 4: Implementation
**Target Length**: 12-15 pages
**Timeline**: Week 4
**Status**: ⏳ Not Started

#### 4.1 System Architecture (2-3 pages)
- Overall system design
- Component interaction diagram
- Data flow

#### 4.2 Custom Algorithm Implementations (5-6 pages)
- **NSGA-II** (`algorithms/nsga2.py`, ~373 lines):
  * Fast non-dominated sorting implementation
  * Crowding distance calculation
  * Tournament selection

- **MOEA/D** (`algorithms/moead.py`, ~315 lines):
  * Weight vector generation (Das-Dennis)
  * Neighborhood structure
  * Tchebycheff decomposition

- **SPEA2** (`algorithms/spea2.py`, ~355 lines):
  * Archive management
  * Strength fitness calculation
  * k-NN density & truncation

#### 4.3 Library Implementations (1-2 pages)
- pymoo (NSGA-II, MOEA/D)
- Platypus (SPEA2)
- Adaptation for our problem

#### 4.4 Testing Framework (2-3 pages)
- Workload generator (`workload_generator.py`)
- Preference generator (`preference_generator.py`)
- Automated test runner (`comprehensive_algorithm_tester.py`)
- 260 test case generation

#### 4.5 Implementation Challenges (1-2 pages)
- Algorithm-specific complexities
- Debugging stochastic algorithms
- Solutions applied

**Writing Notes**:
- Include code snippets (key algorithms)
- Reference GitHub repository
- System architecture diagram

---

### Chapter 5: Experimental Setup
**Target Length**: 8-10 pages
**Timeline**: Week 5
**Status**: ⏳ Not Started

#### 5.1 Test Configuration (2-3 pages)
- Algorithm parameters:
  * Population size: 20 (quick), 50-100 (full)
  * Generations: 20 (quick), 100-200 (full)
  * Crossover probability: 0.9
  * Mutation probability: 1/n_variables

#### 5.2 Workload Generation (2-3 pages)
- 4 sizes: Small (2), Medium (3), Large (5), XL (7 services)
- Service types & resource requirements
- Realistic workload patterns

#### 5.3 Preference Combinations (2-3 pages)
- 13 combinations:
  * Cost-focused (4 combinations)
  * Latency-focused (4 combinations)
  * Performance-focused (4 combinations)
  * Balanced (1 combination)

#### 5.4 Validation Methodology (1-2 pages)
- Custom vs library comparison
- Metrics: Pareto size, objective values, standard deviation
- Acceptable variance thresholds

**Writing Notes**:
- Table of test configurations
- Sample workload JSON
- Preference weight distributions

---

### Chapter 6: Results & Analysis
**Target Length**: 20-25 pages
**Timeline**: Weeks 6-7
**Status**: ⏳ Not Started

#### 6.1 Validation Results (5-6 pages)
- **NSGA-II Validation**:
  * Custom vs pymoo comparison
  * 1.39% cost diff, 2.13% perf diff → **Validated**!
  * Pareto front visualizations

- **MOEA/D Validation**:
  * **Critical Finding**: Library convergence failure
  * 77 duplicate solutions vs 20 diverse → **Custom superior**!
  * Detailed analysis

- **SPEA2 Validation**:
  * Custom vs Platypus comparison
  * 6.13% latency diff → **Validated**!
  * Archive dynamics comparison

#### 6.2 Overall Win Rate Analysis (3-4 pages)
- SPEA2: 42.3% (best overall)
- NSGA-II: 38.5% (most versatile)
- MOEA/D: 19.2% (specialized)
- Visualizations: Bar charts, pie charts

#### 6.3 Win Rates by Application Size (4-5 pages)
- Small apps: NSGA-II & MOEA/D tied
- Medium apps: SPEA2 dominates (53.8%)
- Large apps: SPEA2 leads (46.2%)
- Extra-large apps: NSGA-II wins (46.2%)
- Grouped bar charts

#### 6.4 Win Rates by Preference Type (4-5 pages)
- Cost-focused: NSGA-II & SPEA2 tied, MOEA/D fails (0%)
- Latency-focused: NSGA-II leads (58.3%)
- Performance-focused: MOEA/D dominates (50%)
- Balanced: SPEA2 wins (43.8%)
- Heatmap visualization

#### 6.5 Same-Region Bias Analysis (3-4 pages)
- 15-35% solutions show 1ms latency
- All same-region deployment
- Trade-off: Latency optimization vs Multi-cloud diversity
- Discussion of findings

**Writing Notes**:
- Many visualizations (Pareto fronts, bar charts, heatmaps)
- Tables with detailed numbers
- Statistical significance (if time permits)

---

### Chapter 7: Discussion
**Target Length**: 10-12 pages
**Timeline**: Week 8
**Status**: ⏳ Not Started

#### 7.1 Algorithm Selection Guidelines (3-4 pages)
**When to use which algorithm:**
| Scenario | Recommended | Rationale |
|----------|-------------|-----------|
| Small apps | NSGA-II or MOEA/D | Tied performance |
| Medium apps | SPEA2 | 53.8% win rate |
| Large apps | SPEA2 | Best for complex |
| Extra-large apps | NSGA-II | Scales well |
| Cost optimization | NSGA-II or SPEA2 | Both effective |
| Latency optimization | NSGA-II | 58.3% win rate |
| Performance optimization | MOEA/D | 50% win rate |
| Balanced | SPEA2 | Most robust |

#### 7.2 Key Insights (2-3 pages)
- **MOEA/D Specialization**: Why performance-only?
- **SPEA2 Robustness**: Archive approach benefits
- **NSGA-II Versatility**: Why general-purpose works
- **Custom vs Library**: Value of custom implementation

#### 7.3 Same-Region Bias Trade-off (2-3 pages)
- Mathematical optimality vs Real-world diversity
- Future work: Acceptable latency threshold approach
- Multi-cloud benefits beyond latency

#### 7.4 Practical Recommendations (2-3 pages)
- For cloud practitioners
- Algorithm choice decision tree
- Implementation considerations

**Writing Notes**:
- Decision tree diagram
- Practical examples
- Link to research questions

---

### Chapter 8: Conclusion
**Target Length**: 5-7 pages
**Timeline**: Week 8
**Status**: ⏳ Not Started

#### 8.1 Summary of Contributions (2 pages)
- Three custom algorithm implementations
- Real-world data integration (empirical latency!)
- Comprehensive comparison (260 test cases)
- Algorithm selection guidelines
- Library issue discovery

#### 8.2 Research Questions Answered (2 pages)
- RQ1: Which algorithm best? → Depends on scenario!
- RQ2: By workload size? → SPEA2 for medium/large, NSGA-II for XL
- RQ3: By preference? → MOEA/D for performance, NSGA-II for latency, SPEA2 for balanced
- RQ4: Custom vs library? → Yes, validated! Custom MOEA/D even better!

#### 8.3 Limitations (1 page)
- Test scale (52 cases run, 260 framework ready)
- Single-cloud regions (AWS/GCP/Azure)
- Static latency data (not real-time)
- Simplified workload model

#### 8.4 Future Work (1-2 pages)
- Acceptable latency threshold implementation
- 4th objective (diversity)
- More cloud providers & regions
- Real-time latency monitoring
- Workload migration optimization
- Conference/journal publication

**Writing Notes**:
- Revisit Introduction
- Ensure all RQs answered
- Limitations are honest but not undermining

---

### Chapter 9: References
**Target**: 40-60 references
**Status**: Ongoing collection

#### Key References (Must Include):
1. Deb et al. (2002) - NSGA-II
2. Zhang & Li (2007) - MOEA/D
3. Zitzler et al. (2001) - SPEA2
4. pymoo library paper (Blank & Deb, 2020)
5. Cloud optimization papers
6. Multi-objective optimization texts
7. Geekbench documentation
8. AWS/Azure/GCP technical docs

---

### Appendices
**Target Length**: 10-15 pages

#### Appendix A: Algorithm Pseudocode
- NSGA-II pseudocode
- MOEA/D pseudocode
- SPEA2 pseudocode

#### Appendix B: Detailed Results Tables
- All 52 test case results
- Pareto front data
- Statistical summaries

#### Appendix C: Test Workloads
- Sample workload JSONs
- Workload specifications

#### Appendix D: Source Code Snippets
- Key implementation snippets
- GitHub repository reference

---

## Writing Schedule (8-Week Plan)

### Week 1: Introduction
- ✅ Monday-Tuesday: Outline & Background
- ✅ Wednesday-Thursday: Problem Statement & RQs
- ✅ Friday-Sunday: Contributions & Structure

### Week 2: Literature Review
- Monday-Tuesday: Multi-objective optimization & EA overview
- Wednesday-Thursday: NSGA-II & MOEA/D
- Friday-Sunday: SPEA2 & Cloud optimization

### Week 3: Methodology
- Monday-Tuesday: Problem formulation
- Wednesday-Thursday: Data collection (highlight empirical latency!)
- Friday-Sunday: User input & Algorithm descriptions

### Week 4: Implementation
- Monday-Tuesday: Architecture & Custom implementations
- Wednesday-Thursday: Library implementations & Testing framework
- Friday-Sunday: Challenges & wrap-up

### Week 5: Experimental Setup
- Monday-Tuesday: Test configuration & Workload generation
- Wednesday-Thursday: Preference combinations & Validation methodology
- Friday-Sunday: Review & refinement

### Week 6: Results Part 1
- Monday-Tuesday: Validation results (all 3 algorithms)
- Wednesday-Thursday: Overall win rates & By size
- Friday-Sunday: Continue & refine

### Week 7: Results Part 2 & Discussion
- Monday-Tuesday: By preference & Same-region bias
- Wednesday-Thursday: Discussion & Guidelines
- Friday-Sunday: Insights & Recommendations

### Week 8: Conclusion & Finalization
- Monday-Tuesday: Conclusion chapter
- Wednesday-Thursday: Appendices & References
- Friday-Sunday: Full thesis review & formatting

---

## Daily Writing Goals

### Daily Target: 3-5 pages/day
- Morning session: 2-3 pages (writing)
- Afternoon session: 1-2 pages (editing/figures)
- Evening: Review & plan tomorrow

### Weekly Target: 12-15 pages/week

---

## Writing Tips & Reminders

### Structure:
- Each section: Context → Detail → Conclusion
- Each chapter: Introduction → Body → Summary
- Transitions between sections smooth

### Style:
- Academic tone, clear language
- Myanmar technical terms in English
- Active voice preferred
- Past tense for work done, present for general truths

### Figures:
- Pareto front visualizations
- Bar charts (win rates)
- Heatmaps (algorithm × scenario)
- System architecture diagrams
- Algorithm flow diagrams
- Timeline/Gantt chart

### Tables:
- Algorithm comparison summary
- Win rate breakdown
- Test configuration parameters
- Validation results

---

## Files to Reference While Writing

### For Methodology & Implementation:
- `algorithms/nsga2.py`
- `algorithms/moead.py`
- `algorithms/spea2.py`
- `ALGORITHMS.md`
- `IMPLEMENTATION.md`

### For Results:
- `ALGORITHM_VALIDATION_REPORT.md`
- `RESEARCH_FINDINGS_SUMMARY.md`
- `ALGORITHM_COMPARISON_REPORT.txt`
- `PROFESSOR_MEETING_REPORT.md`

### For Context:
- `PROJECT_CONTEXT.md`
- `CURRENT_STATUS.md`
- `DECISION_LOG.md`
- `DIFFICULTIES_ENCOUNTERED.md`

---

## Success Criteria

### Minimum Requirements:
- ✅ All research questions answered
- ✅ All chapters complete
- ✅ 80+ pages
- ✅ 40+ references
- ✅ Clear contribution

### Excellence Indicators:
- 🎯 100+ pages with appendices
- 🎯 50+ references
- 🎯 High-quality visualizations
- 🎯 Clear practical guidelines
- 🎯 Publication-ready quality

---

**For Notion**: Use this for writing progress tracking
**Status**: ⏳ Ready to start writing!
**Last Updated**: May 20, 2026
