# Decision Log

> **Purpose**: Key decisions made throughout the thesis project
> **For**: Notion reference (Chat will use this to populate Notion)
> **Last Updated**: 2026-05-20

---

## Project Decisions Timeline

### Decision 1: Algorithm Scope Expansion
**Phase**: Project Inception & Research
**Context**: ပထမဆုံး NSGA-II တစ်ခုတည်း implement လုပ်ဖို့သာ စဉ်းစားခဲ့တယ်

**Options Considered**:
1. NSGA-II only (original plan)
2. NSGA-II + one more algorithm
3. NSGA-II + MOEA/D + SPEA2 (three algorithms)

**Decision**: သုံးခု လုံး implement လုပ်မယ်

**Rationale**:
- Literature review လုပ်တုန်း similar algorithms (MOEA/D, SPEA2) တွေ တွေ့ခဲ့တယ်
- Comprehensive comparison လုပ်ရင် research value ပိုများမယ်
- Each algorithm က different approaches သုံးတယ် (Pareto-dominance vs Decomposition vs Archive-based)
- Thesis contribution လည်း stronger ဖြစ်မယ်

**Impact**:
- ✅ Research depth increased significantly
- ✅ Algorithm selection guidelines ရရှိခဲ့တယ်
- ⚠️ Implementation time increased (~3x work)
- ✅ Found library MOEA/D issue (bonus discovery!)

**Status**: ✅ Completed - All three algorithms implemented & validated

---

### Decision 2: Custom vs Library Implementation Approach
**Phase**: Algorithm Implementation
**Context**: Algorithms တွေကို library သုံးမလား ကိုယ်တိုင် scratch က ရေးမလား

**Options Considered**:
1. Use existing libraries only (pymoo, Platypus)
2. Custom implementations only
3. **Both custom AND library implementations**

**Decision**: Both လုပ်မယ် - Custom ရေးပြီး library နဲ့ validate လုပ်မယ်

**Rationale**:
- Custom implementation က algorithm understanding ကို deep ဖြစ်စေတယ်
- Library comparison က correctness validation ပေးတယ်
- ကိုယ့်ရဲ့ code က correct ဆိုတာ prove လုပ်နိုင်တယ်
- Black-box library မသုံးတာက thesis မှာ ပိုကောင်းတယ်

**Impact**:
- ✅ All custom implementations validated!
- ✅ Found MOEA/D library convergence issue
- ✅ Custom MOEA/D proven **superior** to library
- ✅ Deep algorithm understanding achieved
- ⚠️ Extra implementation & testing time required

**Status**: ✅ Completed - Validation report written (ALGORITHM_VALIDATION_REPORT.md)

---

### Decision 3: Data Collection Methodology
**Phase**: Data Collection
**Context**: ဘယ် data တွေကို ဘယ်လို collect လုပ်မလဲ

#### 3a. Cost Data
**Decision**: Web crawling from cloud provider websites

**Rationale**:
- Real pricing data လိုတယ်
- Cloud providers တွေက pricing APIs မထောက်ပံ့ဘူး (or limited)
- Crawling က actual, up-to-date data ပေးတယ်

**Implementation**: AWS, Azure, GCP pricing pages ကနေ CSV files တွေ create လုပ်ခဲ့တယ်

#### 3b. Performance Data
**Decision**: Geekbench scores ကို official sources ကနေ collect လုပ်မယ်

**Rationale**:
- Geekbench က industry-standard benchmark
- Instance types အားလုံး အတွက် available
- Consistent, comparable metrics

**Implementation**: Geekbench websites ကနေ data download လုပ်ပြီး CSV files သိမ်းခဲ့တယ်

#### 3c. Latency Data
**Decision**: **Deploy real servers and empirically test latency**

**Rationale**:
- Theoretical latency estimates က မလုံလောက်ဘူး
- Real inter-cloud, inter-region latency patterns လိုတယ်
- Empirical data က research credibility increase လုပ်တယ်

**Implementation**:
- AWS, GCP, Azure regions တွေမှာ test servers deploy လုပ်ခဲ့တယ်
- Servers အချင်းချင်း connection latency measure လုပ်ခဲ့တယ်
- Results: Intra-region (1ms), Cross-region (10-50ms), Cross-cloud (2.5-270ms)

**Impact**:
- ✅ Real-world latency data ရခဲ့တယ် - research credibility high!
- ✅ Same-region bias discovery ရခဲ့တယ်
- ⚠️ Server costs & setup time required
- ✅ Thesis contribution: Empirical latency testing

**Status**: ✅ Completed - CSV files in `data/network/`

---

### Decision 4: User Input Specification Format
**Phase**: User Input Design
**Context**: Users တွေက workload requirements ကို ဘယ်လို specify လုပ်မလဲ

**Options Considered**:
1. Command-line arguments
2. Python dictionaries
3. **JSON configuration files**
4. YAML files

**Decision**: JSON workload templates

**Rationale**:
- JSON က human-readable and machine-parsable
- Service definitions, resource requirements, preferences clear ဖြစ်တယ်
- Easy to generate test workloads programmatically
- Standard format, widely supported

**Implementation**: `configs/sample_workload.json` template created

**Impact**:
- ✅ Clean, extensible input system
- ✅ Easy to generate 260+ test workloads
- ✅ Clear separation: workload specs vs user preferences

**Status**: ✅ Completed - Working well

---

### Decision 5: Testing Framework Design
**Phase**: Testing Framework
**Context**: ဘယ်လို comprehensive testing framework ဆောက်မလဲ

**Decision**: Automated test generator with systematic coverage

**Components**:
1. **Workload Generator**: 4 sizes (small=2, medium=3, large=5, XL=7 services)
2. **Preference Generator**: 13 combinations (cost-focused, latency-focused, performance-focused, balanced)
3. **Test Runner**: Runs all algorithms × all workloads × all preferences
4. **Win Rate Analyzer**: Determines which algorithm wins for each scenario

**Rationale**:
- Manual testing မလုံလောက်ဘူး
- Systematic coverage လိုတယ် (size × preference combinations)
- Statistical significance အတွက် multiple instances လိုတယ်
- Reproducibility essential

**Implementation**:
- `workload_generator.py` - Generate test workloads
- `preference_generator.py` - Generate preference combinations
- `comprehensive_algorithm_tester.py` - Run full suite
- Framework generates 260 test cases (4 sizes × 13 prefs × 5 instances)

**Impact**:
- ✅ Comprehensive testing achieved (52+ test cases executed)
- ✅ Algorithm strengths clearly identified
- ✅ Statistical analysis possible
- ✅ Reproducible results

**Status**: ✅ Completed - Framework working perfectly

---

### Decision 6: Validation Strategy
**Phase**: Validation
**Date Evidence**: April 30, 2026 (from validation report)
**Context**: ဘယ်လို custom implementations တွေ correct ဆိုတာ prove လုပ်မလဲ

**Decision**: Compare against established Python libraries (pymoo, Platypus)

**Rationale**:
- Library implementations က peer-reviewed, widely used
- Validation against "ground truth"
- Differences ရှိရင် stochastic nature vs implementation error သိနိုင်တယ်

**Libraries Used**:
- pymoo (NSGA-II, MOEA/D) - Developed with K. Deb (NSGA-II creator!)
- Platypus (SPEA2)

**Impact**:
- ✅ NSGA-II validated (1.39% cost diff, 2.13% performance diff)
- ✅ MOEA/D custom **superior** to library! (Library convergence failure discovered)
- ✅ SPEA2 validated (6.13% latency diff)
- ✅ High confidence in custom implementations
- ✅ Research contribution: Library issue discovery

**Status**: ✅ Completed - Validation report published

---

### Decision 7: Same-Region Bias - What to Do?
**Phase**: Analysis
**Date Evidence**: April 27, 2026 (from RESEARCH_FINDINGS_SUMMARY.md)
**Context**: Algorithms တွေက 15-35% same-region (1ms latency) solutions ပေးတယ်

**Problem**: Mathematically optimal but reduces multi-cloud diversity

**Options Considered**:
1. **Add diversity as 4th objective** (Maximize cloud/region diversity)
   - Pros: Explicit encouragement, theoretically elegant
   - Cons: 4D Pareto front (complex), difficult to visualize

2. **Acceptable latency threshold approach** (Recommended in PROFESSOR_MEETING_REPORT.md)
   - Treat latencies < 50ms as equally acceptable (penalty = 0)
   - Latencies > 50ms get quadratic penalty
   - Pros: Real-world aligned, automatic diversity, maintains 3 objectives
   - Cons: Threshold selection subjective

3. Do nothing - Document as algorithmic behavior
   - Pros: No extra work
   - Cons: Missed opportunity for improvement

**Decision**: **Document finding, suggest threshold approach for future work**

**Rationale**:
- Implementation phase already complete
- Threshold approach က novel contribution ဖြစ်နိုင်တယ်
- Thesis မှာ trade-off discussion လုပ်ဖို့ good material
- Future work section မှာ recommendation အနေနဲ့ ထည့်မယ်

**Impact**:
- ✅ Research insight documented
- ✅ Thesis discussion material
- ✅ Future work direction clear
- 📝 Not implemented yet (scope limitation)

**Status**: ✅ Documented - Future work candidate

---

### Decision 8: Thesis Workflow Infrastructure
**Phase**: Thesis Preparation
**Date**: May 20, 2026
**Context**: Thesis ရေးဖို့ ဘယ်လို workflow setup လုပ်မလဲ

**Decision**: GitHub + Notion + Claude Code integrated workflow

**Components**:
1. **GitHub as single source of truth**
   - Code, data, documentation, context files
   - Version control, reproducibility

2. **Context files for Claude Code**
   - PROJECT_CONTEXT.md - Project overview, structure
   - CURRENT_STATUS.md - Daily status tracking
   - Auto-loaded when using `thesis-code` alias

3. **Notion for planning & human-readable docs**
   - Strategic planning, knowledge base
   - Daily logs, decisions, insights
   - Claude Chat integration (via Notion MCP)

4. **Shell aliases for quick access**
   - `thesis-code` - Start Claude Code with context
   - `thesis-status` - View current status
   - `thesis-commit` - Quick commit & push

**Rationale**:
- Long-term thesis project needs organization
- Context files prevent "context loss" between sessions
- Notion provides human-friendly planning space
- Aliases save time daily

**Impact**:
- ✅ Context files created & working
- ✅ Workflow guides written
- ✅ Setup script ready (`configs/setup_thesis_alias.sh`)
- 🚧 Notion setup pending
- ✅ Ready for thesis writing phase

**Status**: 🚧 95% Complete - Almost ready

---

## Decision Categories

### Strategic Decisions
1. ✅ Algorithm scope expansion (3 algorithms)
2. ✅ Custom + library approach
3. ✅ Empirical latency testing

### Technical Decisions
4. ✅ JSON workload format
5. ✅ Automated testing framework design
6. ✅ Library validation strategy

### Research Decisions
7. ✅ Same-region bias handling (documented for future work)

### Workflow Decisions
8. 🚧 Thesis workflow infrastructure (GitHub + Notion + Claude Code)

---

## Key Learnings from Decisions

### What Worked Well ✅
- **Three algorithms**: Rich comparison data, clear algorithm selection guidelines
- **Custom implementations**: Deep understanding, found library issues
- **Empirical latency testing**: Real data adds credibility
- **Comprehensive testing framework**: Systematic, reproducible results
- **Library validation**: Proof of correctness

### What Was Challenging ⚠️
- **Time investment**: Three algorithms took ~3x time (but worth it!)
- **Server costs**: Latency testing required cloud resources
- **Stochastic variance**: Understanding 20-30% differences as "normal"

### Unexpected Discoveries 🎯
- **Library MOEA/D failure**: Custom implementation superior!
- **Same-region bias**: Trade-off between latency & diversity
- **MOEA/D specialization**: Only good for performance maximization

---

## Decisions Pending (Future Work)

1. **Latency threshold implementation**: If project extended
2. **Additional benchmarks**: More cloud providers, regions
3. **Real workload testing**: Deploy actual microservices
4. **Thesis publication**: Conference or journal paper

---

**For Notion**: Copy this to "Decisions & Design" section
**Status**: ✅ Complete decision log
**Next**: Use this when discussing thesis methodology & design choices
