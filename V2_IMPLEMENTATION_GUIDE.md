# Version 2 Implementation Guide: Global Normalization Approach

## အကျဉ်းချုပ်

Version 2 က **Global Normalization** approach ကို သုံးပြီး algorithm selection နဲ့ solution ranking လုပ်ပါတယ်။ Version 1 (main.py) ရဲ့ normalization ပြဿနာများကို ဖြေရှင်းပေးပါတယ်။

---

## ဘာတွေ ပြောင်းလဲခဲ့လဲ?

### 1. ဖိုင်များ ဆောက်သွင်းခဲ့တာများ

#### **utils/preferences_v2.py** - အသစ် ဆောက်ခဲ့တယ်

```python
class AlgorithmSelectorV2:
    """Global normalization ကို သုံးတဲ့ algorithm selector"""

    def select_best_solutions_globally(self, algorithm_results, top_k=15):
        """
        Algorithm အားလုံးရဲ့ solutions တွေကို global normalization နဲ့ rank လုပ်ပြီး
        top K solutions ကို ရွေးချယ်တယ်။
        """
```

**အဓိက ပြောင်းလဲချက်များ:**
- ✅ **Global min/max ကို သုံးတယ်** - algorithm တစ်ခုချင်းစီ သီးခြား မဟုတ်ဘူး
- ✅ **Top K solutions selection** - မျိုးသုံးစွဲသူ သတ်မှတ်နိုင်တယ် (default: 15)
- ✅ **Algorithm distribution tracking** - top solutions ထဲမှာ ဘယ် algorithm က ဘယ်နှခု ရှိတယ်ဆိုတာ ပြတယ်
- ✅ **Top 3 recommendations** - user ကို အသင့်တော်ဆုံး 3 ခု ပြတယ်

---

#### **main_v2.py** - main.py ကို copy လုပ်ပြီး ပြုပြင်ခဲ့တယ်

**အဓိက ပြောင်းလဲချက်များ:**
- ✅ `preferences_v2` import လုပ်ထားတယ်
- ✅ `--top-k` argument ထည့်ထားတယ် (default: 15)
- ✅ Output directory က `results_v2` ဖြစ်တယ်
- ✅ Global normalization analysis နဲ့ top solutions table ပြတယ်
- ✅ Top 3 deployment configurations ကို အသေးစိတ် ပြတယ်

---

### 2. လုပ်ဆောင်ချက်များ ပြောင်းလဲမှု

#### **Version 1 (main.py) Approach:**

```
Algorithm တစ်ခုချင်းစီ run မယ်
  ↓
Algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်မယ်
  ↓
Algorithm တစ်ခုချင်းစီရဲ့ average score တွက်မယ်
  ↓
Best algorithm ရွေးမယ်
  ↓
Best algorithm ရဲ့ best solution တစ်ခုပဲ ပြမယ်
```

**ပြဿနာ:**
- ❌ Algorithm တွေကို unfair comparison လုပ်တယ်
- ❌ Absolute values ကို ဆုံးရှုံးစေတယ်
- ❌ Top solutions အများကြီး မပြဘူး

---

#### **Version 2 (main_v2.py) Approach:**

```
Algorithm အားလုံး run မယ်
  ↓
Solutions အားလုံး (e.g., 150) ကို စုစည်းမယ်
  ↓
GLOBAL min/max ကို ရှာမယ် (combined objectives ကနေ)
  ↓
Solutions အားလုံးကို global min/max နဲ့ normalize လုပ်မယ်
  ↓
User preferences နဲ့ weighted scores တွက်မယ်
  ↓
Top K solutions (e.g., 15) ကို rank အလိုက် ရွေးမယ်
  ↓
Algorithm distribution ပြမယ် (e.g., MOEAD: 8, NSGA2: 4, SPEA2: 3)
  ↓
Top 3 recommendations ကို deployment configs နဲ့တကွ ပြမယ်
```

**အားသာချက်:**
- ✅ Fair algorithm comparison - global scale သုံးတယ်
- ✅ Absolute performance differences ကို preserve လုပ်တယ်
- ✅ Top 15 solutions ကို user ကို ပြတယ်
- ✅ Algorithm distribution ကို analysis လုပ်တယ်

---

## အသေးစိတ် Technical Implementation

### 1. Global Normalization Process

**Code location:** `utils/preferences_v2.py:72-100`

```python
def select_best_solutions_globally(self, algorithm_results, top_k=15):
    # Step 1: Combine ALL Pareto fronts
    all_objectives = []
    solution_metadata = []

    for algo_name, results in algorithm_results.items():
        all_objectives.append(results['pareto_objectives'])
        # Track which solution came from which algorithm
        for i in range(len(results['pareto_objectives'])):
            solution_metadata.append({
                'algorithm': algo_name,
                'original_index': i
            })

    combined_objectives = np.vstack(all_objectives)
    # Shape: (total_solutions, 3) - ဥပမာ (30, 3) or (150, 3)

    # Step 2: Find GLOBAL min/max
    global_min = np.min(combined_objectives, axis=0)
    global_max = np.max(combined_objectives, axis=0)

    # Step 3: Normalize using GLOBAL scale
    range_vals = global_max - global_min
    combined_normalized = (combined_objectives - global_min) / range_vals

    # Step 4: Calculate weighted scores for ALL solutions
    weighted_scores = (
        combined_normalized[:, 0] * self.preferences.cost_weight +
        combined_normalized[:, 1] * self.preferences.latency_weight +
        combined_normalized[:, 2] * self.preferences.performance_weight
    )

    # Step 5: Select top K
    top_k_indices = np.argsort(weighted_scores)[:top_k]

    # Step 6: Extract solution info and track algorithm distribution
    top_solutions = []
    algorithm_distribution = {}

    for rank, idx in enumerate(top_k_indices, 1):
        meta = solution_metadata[idx]
        algo_name = meta['algorithm']

        # Count algorithm distribution
        if algo_name not in algorithm_distribution:
            algorithm_distribution[algo_name] = 0
        algorithm_distribution[algo_name] += 1

        top_solutions.append({
            'rank': rank,
            'algorithm': algo_name,
            'original_index': meta['original_index'],
            'objectives': combined_objectives[idx],
            'normalized': combined_normalized[idx],
            'weighted_score': weighted_scores[idx]
        })

    return {
        'top_solutions': top_solutions,
        'algorithm_distribution': algorithm_distribution,
        ...
    }
```

---

### 2. Algorithm Distribution Analysis

**သင့်မေးခွန်း:** "ဘယ် algorithm ကနေ ဘယ်နှခု ထွက်တယ်ဆိုတာ ပြချင်တယ်"

**Implementation:**

```python
algorithm_distribution = {}

for sol in top_solutions:
    algo_name = sol['algorithm']
    if algo_name not in algorithm_distribution:
        algorithm_distribution[algo_name] = 0
    algorithm_distribution[algo_name] += 1

# Example result:
# {
#   'moead': 8,
#   'nsga2': 4,
#   'spea2': 3
# }
```

**Output Example:**

```
Algorithm Distribution in Top 15 Solutions:
----------------------------------------------------------------------
🏆 MOEAD   :  8 solutions ( 53.3%)
   NSGA2   :  4 solutions ( 26.7%)
   SPEA2   :  3 solutions ( 20.0%)
```

---

### 3. Top Solutions Table

**Code location:** `main_v2.py:373-384`

```python
print(f"{'Rank':<6} {'Algorithm':<10} {'Cost':>10} {'Latency':>10} "
      f"{'Performance':>12} {'Score':>8}")
print("-" * 70)

for sol in selection_result['top_solutions']:
    obj = sol['objectives']
    print(f"#{sol['rank']:<5} {sol['algorithm'].upper():<10} "
          f"${obj[0]:>9.4f} {obj[1]:>9.2f}ms "
          f"{-obj[2]:>11.0f} {sol['weighted_score']:>8.4f}")
```

**Output Example:**

```
Rank   Algorithm        Cost    Latency  Performance    Score
----------------------------------------------------------------------
#1     MOEAD      $   0.8421      2.30ms       28450   0.0823
#2     MOEAD      $   0.9156      3.10ms       27823   0.1045
#3     NSGA2      $   0.7834      1.50ms       25678   0.1234
#4     MOEAD      $   1.1234      4.20ms       29800   0.1456
...
#15    SPEA2      $   2.3456     12.30ms       15234   0.5678
```

---

### 4. Top 3 Deployment Configurations

**သင့်မေးခွန်း:** "Top 3 ကို deployment configuration နဲ့တကွ ပြချင်တယ်"

**Implementation:**

```python
for i in range(min(3, len(selection_result['top_solutions']))):
    sol_info = selection_result['top_solutions'][i]
    algo_name = sol_info['algorithm']
    original_idx = sol_info['original_index']

    # Get actual solution from original algorithm result
    pareto_front = all_results[algo_name]['pareto_front']
    solution = pareto_front[original_idx]

    print(f"\n🏆 Rank #{sol_info['rank']}: {algo_name.upper()}")
    print("-" * 70)

    # Decode solution to show instance assignments
    summary = evaluator.get_solution_summary(solution.tolist())
    for assignment in summary['assignments']:
        print(f"  {assignment['service']:12s} -> {assignment['instance']}")
```

**Output Example:**

```
🏆 Rank #1: MOEAD (Weighted Score: 0.0823)
----------------------------------------------------------------------
  frontend     -> aws:us-east-1:t3.large
  backend      -> gcp:us-central1:n2-standard-4
  database     -> aws:us-east-1:r6i.2xlarge
  cache        -> gcp:us-central1:n2-standard-2
  worker       -> aws:us-east-1:c6i.xlarge

🏆 Rank #2: MOEAD (Weighted Score: 0.1045)
----------------------------------------------------------------------
  frontend     -> aws:us-east-1:t3.xlarge
  backend      -> gcp:us-central1:c3-standard-4
  database     -> aws:us-east-1:r6i.2xlarge
  cache        -> gcp:us-central1:n2-standard-2
  worker       -> aws:us-east-1:c6i.xlarge

🏆 Rank #3: NSGA2 (Weighted Score: 0.1234)
----------------------------------------------------------------------
  frontend     -> gcp:us-central1:n2-standard-2
  backend      -> aws:us-east-1:c6i.2xlarge
  database     -> aws:us-east-1:r7i.2xlarge
  cache        -> gcp:us-central1:n2-standard-2
  worker       -> gcp:us-central1:n2-standard-2
```

---

## Command Usage - Version 1 vs Version 2 နှိုင်းယှဉ်ချက်

### Version 1 (main.py)

```bash
python main.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct
```

**Output:**
- `results/` directory
- Best algorithm တစ်ခု
- Best solution တစ်ခု
- Per-algorithm normalization

---

### Version 2 (main_v2.py)

```bash
python main_v2.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct \
  --top-k 15
```

**Output:**
- `results_v2/` directory
- Top 15 solutions (global normalization)
- Algorithm distribution analysis
- Top 3 detailed configurations
- Global normalization report

---

## နှစ်ခု နှိုင်းယှဉ်ချက် Table

| Feature | Version 1 (main.py) | Version 2 (main_v2.py) |
|---------|---------------------|------------------------|
| **Normalization** | Per-algorithm (သီးခြား) | Global (စုစည်းထား) |
| **Solutions ပြတာ** | Best 1 only | Top 15 (customizable) |
| **Algorithm distribution** | ❌ မပြဘူး | ✅ ပြတယ် |
| **Fair comparison** | ❌ Unfair | ✅ Fair |
| **Absolute values** | ❌ Lost | ✅ Preserved |
| **Top 3 configs** | ❌ တစ်ခုပဲ | ✅ သုံးခု အသေးစိတ် |
| **Output directory** | `results/` | `results_v2/` |
| **Commands** | တူညီတယ် | တူညီတယ် + `--top-k` |

---

## ဥပမာ Workflow

### အဆင့် 1: Version 1 Run မယ်

```bash
python main.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct
```

**ရလဒ်:**
```
results/
  nsga2/
    pareto_front.png
    solutions.csv
    convergence.png
  moead/
    ...
  spea2/
    ...
  algorithm_selection.txt  ← Best algorithm + best solution
```

---

### အဆင့် 2: Version 2 Run မယ် (same parameters)

```bash
python main_v2.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct \
  --top-k 15
```

**ရလဒ်:**
```
results_v2/
  nsga2/
    pareto_front.png
    solutions.csv
    convergence.png
  moead/
    ...
  spea2/
    ...
  global_normalization_results.txt  ← Global analysis + top 15 + top 3 configs
```

---

### အဆင့် 3: နှစ်ခု နှိုင်းယှဉ်မယ်

```bash
# Version 1 results
cat results/algorithm_selection.txt

# Version 2 results
cat results_v2/global_normalization_results.txt

# Compare:
# - Which algorithm won?
# - What's the best solution?
# - How different are the approaches?
```

---

## ဘာကြောင့် Version 2 က ပိုကောင်းလဲ?

### 1. Fair Algorithm Comparison

**Version 1:**
```
NSGA2 cost range: $0.21 - $5.81 → Normalize to [0, 1]
MOEAD cost range: $0.50 - $3.20 → Normalize to [0, 1]

နှစ်ခုလုံး [0, 1] range ရပေမယ့် တကယ့် absolute values မတူဘူး။
```

**Version 2:**
```
Global cost range: $0.21 - $5.81 (from all algorithms)

NSGA2 best: $0.21 → Normalized: 0.00
MOEAD best: $0.50 → Normalized: 0.05

Absolute difference ကို preserve လုပ်တယ်!
```

---

### 2. More Solution Choices

**Version 1:** Best solution တစ်ခုပဲ ပြတယ်

**Version 2:** Top 15 solutions ပြတယ်, user က ရွေးလို့ရတယ်

---

### 3. Algorithm Insights

**Version 1:** "MOEAD က အကောင်းဆုံး" ဆိုတာပဲ ပြောတယ်

**Version 2:** "MOEAD က top 15 ထဲမှာ 8 ခု ရှိတယ် (53%), NSGA2 က 4 ခု (27%), SPEA2 က 3 ခု (20%)" ဆိုပြီး အသေးစိတ် analysis ပေးတယ်

---

### 4. User Preference Accuracy

**Version 1:** Per-algorithm normalization က user preferences ကို distort လုပ်တယ်

**Version 2:** Global normalization က user preferences ကို accurately reflect လုပ်တယ်

---

## File Structure

```
multi-cloud-optimization/
├── main.py                          ← Version 1 (original)
├── main_v2.py                       ← Version 2 (global normalization)
├── utils/
│   ├── preferences.py               ← Version 1 selector
│   ├── preferences_v2.py            ← Version 2 selector (global)
│   ├── data_loader.py
│   └── metrics.py
├── results/                         ← Version 1 output
│   ├── nsga2/
│   ├── moead/
│   ├── spea2/
│   └── algorithm_selection.txt
├── results_v2/                      ← Version 2 output
│   ├── nsga2/
│   ├── moead/
│   ├── spea2/
│   └── global_normalization_results.txt
├── NORMALIZATION_EXPLAINED.md       ← Original normalization explanation
├── NORMALIZATION_AND_SELECTION_DEEP_DIVE.md  ← Deep analysis
└── V2_IMPLEMENTATION_GUIDE.md       ← This file
```

---

## Testing & Comparison

### Quick Test

```bash
# Version 1 - Fast test
python main.py \
  --algorithm all \
  --population 10 \
  --generations 5 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct

# Version 2 - Same parameters
python main_v2.py \
  --algorithm all \
  --population 10 \
  --generations 5 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct \
  --top-k 10
```

### Full Experiment

```bash
# Version 1
python main.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct

# Version 2
python main_v2.py \
  --algorithm all \
  --population 50 \
  --generations 100 \
  --cost-weight 15 \
  --latency-weight 5 \
  --performance-weight 80 \
  --pct \
  --top-k 15
```

---

## Key Takeaways

### သင့်ရဲ့ Original Concerns:

1. ✅ **"Normalization က perspective view အကောင်းဆုံးတွေကိုပဲ ယူနေတယ်"**
   - **ဖြေရှင်းချက်:** Global normalization သုံးပြီး absolute values ကို preserve လုပ်တယ်

2. ✅ **"Top 3 ကို ဘယ်လို ရွေးတာလဲ? 150 ထဲကလား 9 ထဲကလား?"**
   - **ဖြေရှင်းချက်:** 150 solutions အားလုံးကို global normalize လုပ်ပြီး top 15 ရွေးတယ်, အဲ့ထဲက top 3 ကို ပြတယ်

3. ✅ **"Algorithm distribution ကို ပြချင်တယ်"**
   - **ဖြေရှင်းချက်:** Top 15 ထဲမှာ ဘယ် algorithm က ဘယ်နှခု ရှိတယ်ဆိုတာ table နဲ့ ပြတယ်

4. ✅ **"V1 နဲ့ V2 ကို compare လုပ်ချင်တယ်"**
   - **ဖြေရှင်းချက်:** main.py မပျက်ဘဲ main_v2.py အသစ် ဆောက်ထားတယ်၊ results/ နဲ့ results_v2/ သီးခြား ရှိတယ်

---

## Conclusion

Version 2 က သင့်ရဲ့ normalization concerns အားလုံးကို ဖြေရှင်းပေးပါတယ်:

- ✅ **Global normalization** - Fair algorithm comparison
- ✅ **Top 15 solutions** - More choices for users
- ✅ **Algorithm distribution** - Insights into which algorithm performs best
- ✅ **Top 3 configurations** - Detailed deployment recommendations
- ✅ **Backward compatible** - Original main.py မပျက်ဘူး, commands တူညီတယ်

**အခု သင့်အနေနဲ့ နှစ်ခုလုံးကို run ပြီး results တွေကို compare လုပ်နိုင်ပါပြီ!** 🚀
