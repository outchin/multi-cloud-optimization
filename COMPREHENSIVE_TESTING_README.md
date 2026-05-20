# Comprehensive Algorithm Testing Framework

ဒီ framework က Custom နဲ့ Library implementations တွေကို systematic testing လုပ်ပြီး compare လုပ်တဲ့ အပိုင်းဖြစ်ပါတယ်။

## Overview

Framework မှာ အဓိက components ၃ ခု ပါဝင်ပါတယ်:

1. **Workload Generator** (`workload_generator.py`) - Different sizes နဲ့ configurations များ generate လုပ်ပါတယ်
2. **Preference Generator** (`preference_generator.py`) - User preference combinations များ generate လုပ်ပါတယ်
3. **Comprehensive Tester** (`comprehensive_algorithm_tester.py`) - Algorithm တွေကို test run လုပ်ပြီး compare လုပ်ပါတယ်
4. **Master Script** (`run_comprehensive_tests.py`) - အားလုံးကို orchestrate လုပ်ပါတယ်

## Quick Start

### Option 1: Run Everything (Full Pipeline)

```bash
# Small test (3 workloads × 10 preferences = 30 tests × 6 algorithms = 180 runs)
python3 run_comprehensive_tests.py \
  --sizes small \
  --services 3 5 \
  --latency-profiles moderate \
  --preference-mode preset \
  --population 20 \
  --generations 50

# Medium test (~100 tests)
python3 run_comprehensive_tests.py \
  --sizes small medium \
  --services 3 5 7 \
  --latency-profiles moderate relaxed \
  --preference-mode diverse \
  --preference-count 20 \
  --population 50 \
  --generations 100

# Full comprehensive test (~200-300 tests)
python3 run_comprehensive_tests.py \
  --sizes tiny small medium large xlarge \
  --services 3 5 7 \
  --latency-profiles strict moderate relaxed \
  --preference-mode diverse \
  --preference-count 50 \
  --population 50 \
  --generations 100
```

### Option 2: Step by Step

#### Step 1: Generate Workloads

```bash
# Generate test workloads
python3 workload_generator.py \
  --output-dir test_workloads \
  --sizes small medium large \
  --services 3 5 7 \
  --latency strict moderate relaxed
```

**Workload Sizes:**
- `tiny`: 1-2 vCPU, 1-2 GB RAM, 500-1500 score
- `small`: 1-2 vCPU, 2-4 GB RAM, 1000-2500 score
- `medium`: 2-4 vCPU, 4-8 GB RAM, 2000-4500 score
- `large`: 4-8 vCPU, 8-16 GB RAM, 4000-8000 score
- `xlarge`: 8-16 vCPU, 16-32 GB RAM, 8000-15000 score

**Latency Profiles:**
- `strict`: 5-20ms inter-service latency
- `moderate`: 30-80ms inter-service latency
- `relaxed`: 80-250ms inter-service latency

#### Step 2: Generate Preferences

```bash
# Preset profiles (10 predefined combinations)
python3 preference_generator.py \
  --output-dir test_preferences \
  --mode preset

# Diverse set (custom count)
python3 preference_generator.py \
  --output-dir test_preferences \
  --mode diverse \
  --count 50

# Systematic (all combinations with step=10)
python3 preference_generator.py \
  --output-dir test_preferences \
  --mode systematic
```

**Preset Profiles:**
- Cost-focused (60%, 30%, 10%)
- Latency-focused (10%, 60%, 30%)
- Performance-focused (10%, 30%, 60%)
- Balanced (33%, 33%, 34%)
- Cost-Latency (50%, 50%, 0%)
- And more...

#### Step 3: Run Tests

```bash
python3 comprehensive_algorithm_tester.py \
  --workload-dir test_workloads \
  --preference-file test_preferences/preferences_diverse_50.json \
  --population 50 \
  --generations 100 \
  --output-dir comprehensive_test_results

# For quick testing, limit number of cases
python3 comprehensive_algorithm_tester.py \
  --workload-dir test_workloads \
  --preference-file test_preferences/preferences_preset.json \
  --population 20 \
  --generations 50 \
  --limit 10
```

## Output Files

### Test Results Directory Structure

```
comprehensive_test_results/
├── test_results.csv              # Main results CSV
├── test_results_detailed.json    # Detailed JSON results
└── test_summary.txt              # Summary report
```

### CSV Columns

Main columns:
- `Test_ID` - Unique test case ID
- `Workload_Name` - Workload name
- `Size_Category` - tiny/small/medium/large/xlarge
- `Num_Services` - Number of services (3, 5, 7, etc.)
- `Latency_Profile` - strict/moderate/relaxed
- `Pref_Cost%`, `Pref_Latency%`, `Pref_Performance%` - User preferences
- `Winner_Algorithm` - Best performing algorithm
- `Winner_Implementation` - custom or library
- `Winner_Score` - Weighted score
- `Winner_Cost`, `Winner_Latency`, `Winner_Performance` - Best solution metrics

Algorithm-specific columns (for each of 6 algorithms):
- `{algo}_pareto_size` - Size of Pareto front
- `{algo}_exec_time` - Execution time (seconds)
- `{algo}_best_score` - Best weighted score
- `{algo}_best_cost`, `{algo}_best_latency`, `{algo}_best_performance` - Best solution metrics

### Summary Report

Summary report (:test_summary.txt`) မှာ:
- Winner distribution by algorithm
- Winner distribution by implementation type (custom vs library)
- Overall statistics

## Usage Examples

### Example 1: Quick Test (10-15 minutes)

```bash
python3 run_comprehensive_tests.py \
  --sizes small \
  --services 3 \
  --latency-profiles moderate \
  --preference-mode preset \
  --population 20 \
  --generations 30 \
  --test-limit 5
```

### Example 2: Moderate Test (1-2 hours)

```bash
python3 run_comprehensive_tests.py \
  --sizes small medium \
  --services 3 5 \
  --latency-profiles moderate relaxed \
  --preference-mode diverse \
  --preference-count 20 \
  --population 50 \
  --generations 50
```

### Example 3: Full Comprehensive Test (4-8 hours)

```bash
python3 run_comprehensive_tests.py \
  --sizes tiny small medium large xlarge \
  --services 3 5 7 \
  --latency-profiles strict moderate relaxed \
  --preference-mode diverse \
  --preference-count 50 \
  --population 50 \
  --generations 100
```

### Example 4: Reuse Existing Workloads/Preferences

```bash
# Only generate new data
python3 run_comprehensive_tests.py \
  --sizes small medium \
  --services 5 \
  --preference-mode diverse \
  --preference-count 30 \
  --only-generate

# Then run tests using existing data
python3 run_comprehensive_tests.py \
  --skip-workload-gen \
  --skip-preference-gen \
  --population 50 \
  --generations 100
```

## Algorithms Tested

**Custom Implementations:**
1. NSGA-II Custom (`algorithms/nsga2.py`)
2. MOEA/D Custom (`algorithms/moead.py`)
3. SPEA2 Custom (`algorithms/spea2.py`)

**Library Implementations:**
1. NSGA-II Pymoo (`algorithms_library/nsga2_pymoo.py`)
2. MOEA/D Pymoo (`algorithms_library/moead_pymoo.py`)
3. SPEA2 Platypus (`algorithms_library/spea2_platypus.py`)

## Winner Determination

Winner ကို user preferences အပေါ် မူတည်ပြီး weighted score နဲ့ ဆုံးဖြတ်ပါတယ်:

```
weighted_score = (cost_weight × normalized_cost) +
                 (latency_weight × normalized_latency) +
                 (performance_weight × (1 - normalized_performance))
```

**Lowest weighted score = Winner** (သေးငယ်ရင် ပိုကောင်းတယ်)

## Test Case Calculation

Total test cases = `num_sizes × num_service_counts × num_latency_profiles × num_preferences`

Example:
- 5 sizes × 3 service counts × 3 latency profiles × 50 preferences = **2,250 test cases**
- Each test case runs **6 algorithms** (3 custom + 3 library)
- Total algorithm runs = **13,500 runs**

## Performance Tips

1. **Start small**: --test-limit 10 နဲ့ အရင် စမ်းကြည့်ပါ
2. **Reduce population/generations**: --population 20 --generations 30 သုံးပါ
3. **Use preset preferences**: --preference-mode preset (10 preferences only)
4. **Limit workload variations**: --sizes small --services 3 တစ်ခုတည်း သုံးပါ

## Troubleshooting

### Problem: "No compatible instances found"
**Solution**: Workload requirements က cloud instances တွေနဲ့ မကိုက်ဘူး။ Size category ကို ပြောင်းကြည့်ပါ။

### Problem: Tests taking too long
**Solution**:
- `--test-limit` သုံးပြီး test cases ကို limit လုပ်ပါ
- Population/generations ကို လျှော့ပါ
- Workload/preference combinations ကို လျှော့ပါ

### Problem: Memory issues
**Solution**:
- Workload sizes ကို သေးငယ်အောင် လုပ်ပါ (tiny/small only)
- Test cases ကို batch လုပ်ပါ (--test-limit သုံးပြီး)

## Data Analysis

CSV results ကို analysis လုပ်ဖို့:

```python
import pandas as pd

# Load results
df = pd.read_csv('comprehensive_test_results/test_results.csv')

# Winner by algorithm
print(df['Winner_Algorithm'].value_counts())

# Winner by implementation
df['Winner_Impl'] = df['Winner_Implementation']
print(df['Winner_Impl'].value_counts())

# Winner by size category
print(df.groupby('Size_Category')['Winner_Algorithm'].value_counts())

# Winner by preference profile
print(df.groupby(['Pref_Cost%', 'Pref_Latency%'])['Winner_Algorithm'].value_counts())
```

## Next Steps

1. Run quick test ကို အရင် စမ်းကြည့်ပါ
2. Results ကို ကြည့်ပြီး validate လုပ်ပါ
3. Parameters adjust လုပ်ပါ
4. Full comprehensive test ကို run ပါ
5. Results analyze လုပ်ပြီး thesis paper မှာ သုံးပါ

## Questions?

ပြဿနာ တွေ့ရင် error message နဲ့ တကွ မေးပါ။ Good luck!
