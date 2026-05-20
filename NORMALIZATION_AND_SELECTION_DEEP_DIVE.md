# Normalization နဲ့ Solution Selection အသေးစိတ် ရှင်းလင်းချက်

## အဓိက မေးခွန်းနှစ်ခု

### မေးခွန်း ၁: Normalization က သူ့ရဲ့ perspective view အကောင်းဆုံးတွေကိုပဲ ထုတ်နေတယ်မဟုတ်လား?

**အဖြေ: မှန်ပါတယ်။ ဒါက တကယ့်ကို အရေးကြီးတဲ့ ပြဿနာ တစ်ခုပါ။**

### မေးခွန်း ၂: Algorithm သုံးခုက ထွက်လာတဲ့ solutions တွေကို ဘယ်လို combine လုပ်ပြီး top 3 ရွေးတာလဲ?

**အဖြေ: လက်ရှိ implementation မှာ တွေ့ရှိရတဲ့ ပြဿနာ ရှိတယ်။**

---

## Part 1: Normalization ရဲ့ အားနည်းချက်

### လက်ရှိ Implementation ကို လေ့လာခြင်း

**Code location:** `utils/preferences.py:75-98`

```python
def normalize_objectives(self, objectives: np.ndarray) -> np.ndarray:
    """Normalize objectives to [0, 1] range using min-max normalization."""
    normalized = np.zeros_like(objectives, dtype=float)

    for i in range(objectives.shape[1]):
        min_val = np.min(objectives[:, i])  # ← အနိမ့်ဆုံး value ကို ရှာတယ်
        max_val = np.max(objectives[:, i])  # ← အမြင့်ဆုံး value ကို ရှာတယ်

        if np.isclose(min_val, max_val):
            normalized[:, i] = 0.5
        else:
            # Min-max normalization
            normalized[:, i] = (objectives[:, i] - min_val) / (max_val - min_val)

    return normalized
```

### ပြဿနာ ဘာလဲ?

Min-max normalization formula:
```
Normalized = (Value - Min) / (Max - Min)
```

**အကောင်းဆုံး value (Min) အတွက်:**
```
Normalized = (Min - Min) / (Max - Min) = 0 / (Max - Min) = 0.00
```

**အဆိုးဆုံး value (Max) အတွက်:**
```
Normalized = (Max - Min) / (Max - Min) = (Max - Min) / (Max - Min) = 1.00
```

**သင့်အနေနဲ့ မှန်ကန်စွာ သတိပြုမိတဲ့ အချက်:**

> "Cost အတွက် အကောင်းဆုံးက အမြဲတမ်း 0.0၊ Performance အတွက် အကောင်းဆုံးက အမြဲတမ်း 0.0၊ Latency အတွက် အကောင်းဆုံးက အမြဲတမ်း 0.0 ဖြစ်နေတယ်။ အဲ့ဒီတော့ ဒီသုံးခု (cost အကောင်းဆုံး solution, performance အကောင်းဆုံး solution, latency အကောင်းဆုံး solution) ကိုပဲ နှိုင်းယှဉ်နေသလို ဖြစ်နေတယ်။"

---

### ဥပမာနဲ့ သရုပ်ပြခြင်း

ဆိုပါစို့ ကျွန်တော်တို့မှာ Algorithm နှစ်ခုရှိတယ်:

#### **NSGA2 ရဲ့ Pareto Front:**

| Solution | Cost ($) | Latency (ms) | Performance |
|----------|----------|--------------|-------------|
| A1       | 0.21     | 1.0          | 2005        |
| A2       | 2.50     | 8.5          | 15000       |
| A3       | 5.81     | 17.2         | 39800       |

**Range:**
- Cost: 0.21 - 5.81 ($5.60 range)
- Latency: 1.0 - 17.2 (16.2 ms range)
- Performance: 2005 - 39800 (37795 score range)

**Normalization ပြီးရင်:**

| Solution | Normalized Cost | Normalized Latency | Normalized Performance |
|----------|-----------------|--------------------|-----------------------|
| A1       | **0.00**        | **0.00**           | 1.00                  |
| A2       | 0.41            | 0.46               | 0.66                  |
| A3       | 1.00            | 1.00               | **0.00**              |

---

#### **MOEA/D ရဲ့ Pareto Front:**

| Solution | Cost ($) | Latency (ms) | Performance |
|----------|----------|--------------|-------------|
| B1       | 0.50     | 2.0          | 5000        |
| B2       | 1.80     | 7.0          | 18000       |
| B3       | 3.20     | 12.5         | 32000       |

**Range:**
- Cost: 0.50 - 3.20 ($2.70 range)
- Latency: 2.0 - 12.5 (10.5 ms range)
- Performance: 5000 - 32000 (27000 score range)

**Normalization ပြီးရင်:**

| Solution | Normalized Cost | Normalized Latency | Normalized Performance |
|----------|-----------------|--------------------|-----------------------|
| B1       | **0.00**        | **0.00**           | 1.00                  |
| B2       | 0.48            | 0.48               | 0.52                  |
| B3       | 1.00            | 1.00               | **0.00**              |

---

### ပြဿနာ ထင်ရှားစေခြင်း

**NSGA2 ရဲ့ cost အကောင်းဆုံး:** $0.21 → Normalized: **0.00**
**MOEA/D ရဲ့ cost အကောင်းဆုံး:** $0.50 → Normalized: **0.00**

**သူတို့နှစ်ခုလုံး normalized value က 0.00 ဖြစ်နေပါတယ်!**

တကယ်တော့:
- NSGA2 က cost မှာ **58% ပိုကောင်းတယ်** ($0.21 vs $0.50)
- ဒါပေမယ့် normalization ပြီးရင် **တူညီသွားတယ်** (0.00 vs 0.00)

**ဒါက အရမ်းကြီးမားတဲ့ ပြဿနာပါ!**

Algorithm တစ်ခုနဲ့ တစ်ခု **တကယ့် absolute values တွေနဲ့ compare လုပ်လို့ မရဘူး**။ သူတို့ရဲ့ **relative positions within their own Pareto fronts** ကိုပဲ compare လုပ်နေတာပါ။

---

## Part 2: လက်ရှိ Algorithm Selection Process

### Code Flow ကို လေ့လာခြင်း

**Code location:** `utils/preferences.py:152-203` နဲ့ `main.py:402-434`

### အဆင့်တစ်ခုချင်းစီ:

#### **အဆင့် ၁: Algorithm တစ်ခုချင်းစီ run ပြီး သူ့ရဲ့ Pareto Front ရတယ်**

```
NSGA2:   50 solutions → Pareto Front (e.g., 12 solutions)
MOEA/D:  50 solutions → Pareto Front (e.g., 15 solutions)
SPEA2:   50 solutions → Pareto Front (e.g., 10 solutions)
```

**စုစုပေါင်း:** 37 Pareto-optimal solutions (သီးခြား Pareto fronts များ)

---

#### **အဆင့် ၂: User Preferences ဖြင့် Algorithm Selection**

**Code location:** `utils/preferences.py:152-203`

```python
def select_best_algorithm(self, algorithm_results: Dict[str, Dict]) -> Dict:
    scores = {}

    # Calculate weighted score for each algorithm
    for algo_name, results in algorithm_results.items():
        pareto_objectives = results['pareto_objectives']
        scores[algo_name] = self.calculate_weighted_score(pareto_objectives)
        # ↑ ဒီမှာ algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်တယ်

    # Rank algorithms (lower score is better)
    best_algorithm = min(scores, key=scores.get)

    # Find best solution from best algorithm
    best_sol_idx, best_sol_score = self.find_best_solution(
        best_algo_results['pareto_objectives']
    )
```

---

#### **အဆင့် ၃: Weighted Score တွက်ချက်ခြင်း**

**Code location:** `utils/preferences.py:100-124`

```python
def calculate_weighted_score(self, objectives: np.ndarray) -> float:
    # Normalize objectives to [0, 1]
    normalized = self.normalize_objectives(objectives)
    # ↑ Algorithm တစ်ခုချင်းစီရဲ့ Pareto front ကို သီးခြား normalize လုပ်တယ်

    # For each solution, calculate weighted sum
    weighted_scores = (
        normalized[:, 0] * self.preferences.cost_weight +
        normalized[:, 1] * self.preferences.latency_weight +
        normalized[:, 2] * self.preferences.performance_weight
    )

    # Return average weighted score across all Pareto solutions
    return np.mean(weighted_scores)
```

---

### လက်ရှိ Approach ရဲ့ Flow:

```
NSGA2 Pareto Front (12 solutions)
  ↓
  Normalize သူ့ရဲ့ own min/max နဲ့ → Normalized values: [0.0 - 1.0]
  ↓
  Calculate weighted scores → Average score: 0.485

MOEA/D Pareto Front (15 solutions)
  ↓
  Normalize သူ့ရဲ့ own min/max နဲ့ → Normalized values: [0.0 - 1.0]
  ↓
  Calculate weighted scores → Average score: 0.523

SPEA2 Pareto Front (10 solutions)
  ↓
  Normalize သူ့ရဲ့ own min/max နဲ့ → Normalized values: [0.0 - 1.0]
  ↓
  Calculate weighted scores → Average score: 0.441

Winner: SPEA2 (lowest average score: 0.441)
```

---

### ပြဿနာ ဘာလဲ?

**၁. Algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်တဲ့အတွက် unfair comparison ဖြစ်တယ်**

ဥပမာ:
- NSGA2: Cost range $0.21 - $5.81 → Normalized to 0.0 - 1.0
- MOEA/D: Cost range $0.50 - $3.00 → Normalized to 0.0 - 1.0

နှစ်ခုလုံး normalized range က တူညီသွားပေမယ့် **တကယ့် absolute values မတူညီဘူး**။

**၂. Average score က Pareto front ရဲ့ "spread" ကို measure လုပ်နေတာ မဟုတ်ဘူး**

Average normalized score က algorithm ရဲ့ **solution diversity** ကို reflect လုပ်တာ မဟုတ်ဘူး။ သူက simply algorithm တစ်ခုချင်းစီရဲ့ normalized values တွေကို average ထုတ်တာပါ။

**မျှော်မှန်းတဲ့အတိုင်း algorithm တိုင်းရဲ့ average normalized score က ခန့်မှန်းခြေအားဖြင့် 0.5 ဝန်းကျင် ဖြစ်သင့်တယ်** (ဘာကြောင့်လဲဆိုတော့ normalized range က 0-1 ဖြစ်ပြီး uniform distribution ဆိုရင် average က 0.5 ဖြစ်တယ်)။

---

### တကယ့်ကို ဖြစ်နေတဲ့ အရာ:

**လက်ရှိ code က Algorithm တစ်ခုချင်းစီရဲ့ Pareto front ထဲက solutions တွေကို သူ့ရဲ့ own min/max နဲ့ normalize လုပ်ပြီး average score တွက်တယ်။**

ဒါက:
- ❌ Algorithm တွေကို absolute performance နဲ့ compare လုပ်လို့ မရဘူး
- ❌ တကယ့် cost, latency, performance values တွေကို ignore လုပ်နေတယ်
- ❌ User preferences ကို accurately reflect လုပ်လို့ မရဘူး

---

## Part 3: အမှန်တကယ် ဘာဖြစ်သင့်လဲ?

### Option 1: Global Normalization (အကြံပြုချက်)

**Concept:** Algorithm အားလုံးကို တစ်ပြိုင်နက် normalize လုပ်တယ်၊ **combined Pareto front** ကို သုံးပြီး global min/max ရှာတယ်။

#### **လုပ်ဆောင်ချက်:**

```python
def select_best_algorithm_global_norm(self, algorithm_results: Dict[str, Dict]) -> Dict:
    # Step 1: Combine all Pareto fronts
    all_objectives = []
    for algo_name, results in algorithm_results.items():
        all_objectives.append(results['pareto_objectives'])

    combined_objectives = np.vstack(all_objectives)
    # Shape: (total_solutions, 3) - ဥပမာ (37, 3)

    # Step 2: Find GLOBAL min and max
    global_min = np.min(combined_objectives, axis=0)
    global_max = np.max(combined_objectives, axis=0)

    # Step 3: Normalize each algorithm using GLOBAL min/max
    scores = {}
    for algo_name, results in algorithm_results.items():
        objectives = results['pareto_objectives']

        # Normalize using global min/max
        normalized = (objectives - global_min) / (global_max - global_min)

        # Calculate weighted scores
        weighted_scores = (
            normalized[:, 0] * self.preferences.cost_weight +
            normalized[:, 1] * self.preferences.latency_weight +
            normalized[:, 2] * self.preferences.performance_weight
        )

        scores[algo_name] = np.mean(weighted_scores)

    # Best algorithm has lowest score
    best_algorithm = min(scores, key=scores.get)

    return best_algorithm, scores
```

---

#### **Global Normalization ရဲ့ အားသာချက်:**

✅ **Algorithm တွေကို fair comparison လုပ်နိုင်တယ်**
- Algorithm အားလုံးက same reference scale (global min/max) ကို သုံးတယ်

✅ **Absolute performance differences ကို preserve လုပ်တယ်**
- NSGA2 က $0.21 ပေးတယ်၊ MOEA/D က $0.50 ပေးတယ်ဆိုရင်၊ normalized values မှာလည်း ဒီ difference က ထင်ရှားတယ်

✅ **User preferences ကို accurately reflect လုပ်တယ်**
- Weights က တကယ့် performance differences ကို reflect လုပ်တယ်

---

#### **ဥပမာနဲ့ သရုပ်ပြခြင်း:**

**Combined Pareto Front:**

| Algorithm | Solution | Cost ($) | Latency (ms) | Performance |
|-----------|----------|----------|--------------|-------------|
| NSGA2     | A1       | 0.21     | 1.0          | 2005        |
| NSGA2     | A2       | 2.50     | 8.5          | 15000       |
| NSGA2     | A3       | 5.81     | 17.2         | 39800       |
| MOEA/D    | B1       | 0.50     | 2.0          | 5000        |
| MOEA/D    | B2       | 1.80     | 7.0          | 18000       |
| MOEA/D    | B3       | 3.20     | 12.5         | 32000       |

**Global Min/Max:**
- Cost: Min = 0.21, Max = 5.81
- Latency: Min = 1.0, Max = 17.2
- Performance: Min = 2005, Max = 39800

**Global Normalization:**

| Algorithm | Solution | Norm Cost | Norm Latency | Norm Perf |
|-----------|----------|-----------|--------------|-----------|
| NSGA2     | A1       | **0.00**  | **0.00**     | 1.00      |
| NSGA2     | A2       | 0.41      | 0.46         | 0.66      |
| NSGA2     | A3       | 1.00      | 1.00         | **0.00**  |
| MOEA/D    | B1       | **0.05**  | 0.06         | 0.92      |
| MOEA/D    | B2       | 0.28      | 0.37         | 0.58      |
| MOEA/D    | B3       | 0.53      | 0.71         | 0.21      |

**အခု NSGA2 A1 နဲ့ MOEA/D B1 ကို နှိုင်းယှဉ်လိုက်ရင်:**
- NSGA2 A1: Normalized cost = **0.00** (best possible)
- MOEA/D B1: Normalized cost = **0.05** (slightly worse)

**တကယ့် difference ကို preserve လုပ်ထားတယ်!**

---

### Option 2: Direct Comparison (Alternative)

**Concept:** Normalization မသုံးဘဲ တန်းရိုက် raw values နဲ့ compare လုပ်တယ်။

ဒါပေမယ့် ဒါက **scale dominance problem** ကို ပြန်ဖြစ်စေတယ် (NORMALIZATION_EXPLAINED.md မှာ ရှင်းပြထားသလို)။

**မသုံးဖို့ အကြံပြုပါတယ်။**

---

### Option 3: Pareto Dominance Count

**Concept:** Algorithm တစ်ခုနဲ့ တစ်ခု compare လုပ်တဲ့အခါ Pareto dominance relationships ကို သုံးတယ်။

```python
def compare_algorithms_by_dominance(results1, results2):
    """Count how many solutions from results1 dominate solutions in results2."""
    dominance_count = 0

    for sol1 in results1['pareto_objectives']:
        for sol2 in results2['pareto_objectives']:
            if dominates(sol1, sol2):
                dominance_count += 1

    return dominance_count

def dominates(obj1, obj2):
    """Check if obj1 dominates obj2 (all objectives better or equal, at least one strictly better)."""
    return (np.all(obj1 <= obj2) and np.any(obj1 < obj2))
```

**အားသာချက်:**
- Normalization မလိုဘူး
- Pareto optimality concept နဲ့ ကိုက်ညီတယ်

**အားနည်းချက်:**
- User preferences ကို directly incorporate လုပ်လို့ မရဘူး
- Complex comparison ဖြစ်တယ်

---

## Part 4: မေးခွန်း ၂ ရဲ့ အဖြေ - Top Solutions ကို ဘယ်လို ရွေးတာလဲ?

### လက်ရှိ Implementation

**Code location:** `main.py:328-357`

```python
# Show top 3 solutions based on user preference (if set)
if user_preferences:
    # Determine which objective user cares most about
    max_weight = max(user_preferences.cost_weight,
                   user_preferences.latency_weight,
                   user_preferences.performance_weight)

    if user_preferences.cost_weight == max_weight:
        sort_criterion = "Cost"
        sorted_indices = np.argsort(pareto_objectives[:, 0])[:3]
    elif user_preferences.latency_weight == max_weight:
        sort_criterion = "Latency"
        sorted_indices = np.argsort(pareto_objectives[:, 1])[:3]
    else:  # performance_weight is max
        sort_criterion = "Performance"
        sorted_indices = np.argsort(pareto_objectives[:, 2])[:3]
```

---

### ဘာဖြစ်နေတာလဲ?

**Single Algorithm Run တဲ့အခါ (e.g., `--algorithm nsga2`):**

1. NSGA2 run ပြီး Pareto front ရတယ် (ဥပမာ 12 solutions)
2. User preferences ကို ကြည့်တယ်:
   - Cost 40%, Latency 40%, Performance 20% ဆိုရင်
   - Max weight က cost (40%) and latency (40%) - tie ဖြစ်တယ်
   - Code က cost ကို ယူတယ် (if-elif structure ကြောင့်)
3. Cost အပေါ် မူတည်ပြီး sort လုပ်ပြီး top 3 ကို ပြတယ်

**ဒါက:**
- ❌ User က cost 40%, latency 40% ထည့်ထားပေမယ့် latency ကို ignore လုပ်တယ်
- ❌ Multi-objective trade-offs ကို consider မလုပ်ဘူး
- ❌ Normalization + weighted sum ကို မသုံးဘူး

---

**Multiple Algorithms Run တဲ့အခါ (e.g., `--algorithm all`):**

1. Algorithm သုံးခု run တယ် → သုံးခု separate Pareto fronts ရတယ်
2. `AlgorithmSelector.select_best_algorithm()` ကို ခေါ်တယ်
3. Algorithm တစ်ခုချင်းစီကို **သီးခြား normalize** လုပ်ပြီး average score တွက်တယ်
4. Best algorithm ကို ရွေးတယ်
5. Best algorithm ရဲ့ Pareto front ထဲက **best solution** ကို ပြန်ရွေးတယ်

**Code location:** `utils/preferences.py:186-188`

```python
# Find best solution from best algorithm
best_sol_idx, best_sol_score = self.find_best_solution(
    best_algo_results['pareto_objectives']
)
```

**`find_best_solution()` က:**
```python
def find_best_solution(self, objectives: np.ndarray) -> Tuple[int, float]:
    # Normalize objectives (သူ့ရဲ့ own min/max နဲ့)
    normalized = self.normalize_objectives(objectives)

    # Calculate weighted score for each solution
    scores = (
        normalized[:, 0] * self.preferences.cost_weight +
        normalized[:, 1] * self.preferences.latency_weight +
        normalized[:, 2] * self.preferences.performance_weight
    )

    # Find best (minimum) score
    best_idx = np.argmin(scores)
    return best_idx, scores[best_idx]
```

---

### အဖြေ: Top 3 ကို ဘယ်လို ရွေးတာလဲ?

**လက်ရှိ implementation မှာ:**

1. **Single algorithm:** User preference ရဲ့ highest weight objective အပေါ် မူတည်ပြီး sort လုပ်ပြီး top 3 ပြတယ်
2. **Multiple algorithms:**
   - Algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်ပြီး average score တွက်တယ်
   - Best algorithm ကို ရွေးတယ်
   - Best algorithm ရဲ့ Pareto front ကို ပြန် normalize လုပ်ပြီး best solution ကို ရွေးတယ်
   - **Top 3 ကို မပြဘူး - best solution တစ်ခုပဲ ပြတယ်** (main.py:416-421)

**ဒီတော့:**
- ❌ 150 solutions အားလုံးကို combined လုပ်ပြီး top 3 မရွေးဘူး
- ❌ Algorithm တစ်ခုချင်းစီက top 3 ကို ရွေးပြီး 9 ခုထဲက best 3 မရွေးဘူး
- ✅ Best algorithm တစ်ခုကို ရွေးပြီး အဲ့ဒီ algorithm ရဲ့ best solution တစ်ခုပဲ ပြတယ်

---

## Part 5: အကြံပြုချက်များ

### Problem 1: Unfair Algorithm Comparison

**လက်ရှိ:**
```python
# Algorithm တစ်ခုချင်းစီကို သီးခြား normalize
for algo in algorithms:
    normalized = normalize(algo.pareto_front)  # သူ့ရဲ့ own min/max
    score[algo] = calculate_score(normalized)
```

**အကြံပြုချက်:**
```python
# Global normalization
all_solutions = combine_all_pareto_fronts(algorithms)
global_min = np.min(all_solutions, axis=0)
global_max = np.max(all_solutions, axis=0)

for algo in algorithms:
    normalized = (algo.pareto_front - global_min) / (global_max - global_min)
    score[algo] = calculate_score(normalized)
```

---

### Problem 2: Single-Objective Sorting for Top Solutions

**လက်ရှိ:**
```python
# Highest weight objective ကိုပဲ သုံးတယ်
if cost_weight == max_weight:
    top_3 = sort_by_cost(solutions)[:3]
```

**အကြံပြုချက်:**
```python
# Normalize ပြီး weighted sum သုံးတယ်
normalized = normalize_with_global_minmax(solutions)
weighted_scores = (
    normalized[:, 0] * cost_weight +
    normalized[:, 1] * latency_weight +
    normalized[:, 2] * performance_weight
)
top_3_indices = np.argsort(weighted_scores)[:3]
```

---

### Problem 3: Only Best Solution Shown (Not Top 3)

**လက်ရှိ:**
```python
# Best solution တစ်ခုပဲ return လုပ်တယ်
best_idx, best_score = find_best_solution(pareto_front)
return best_idx
```

**အကြံပြုချက်:**
```python
# Top 3 solutions return လုပ်တယ်
normalized = normalize(pareto_front)
scores = calculate_weighted_scores(normalized)
top_3_indices = np.argsort(scores)[:3]
return top_3_indices, scores[top_3_indices]
```

---

## Part 6: သင့်ရဲ့ Concerns ကို ပြန်လည် အတည်ပြုခြင်း

### Concern 1: "Normalization က perspective view အကောင်းဆုံးတွေကိုပဲ ထုတ်နေတယ်"

**✅ မှန်ကန်ပါတယ်။**

Min-max normalization က:
- အကောင်းဆုံး value → 0.0
- အဆိုးဆုံး value → 1.0

Algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်တဲ့အခါ:
- Cost အကောင်းဆုံး solution → cost normalized = 0.0
- Performance အကောင်းဆုံး solution → performance normalized = 0.0
- Latency အကောင်းဆုံး solution → latency normalized = 0.0

**ဒါက algorithms တွေကို unfair comparison လုပ်စေတယ်။**

**Solution:** Global normalization သုံးပါ (combined Pareto front ရဲ့ min/max)

---

### Concern 2: "Top 3 ရွေးတဲ့ process က ဘယ်လိုလဲ?"

**✅ သင့်ရဲ့ မေးခွန်း မှန်ကန်ပါတယ်။**

လက်ရှိ implementation မှာ:
- ❌ 150 solutions အားလုံးကို combined မလုပ်ဘူး
- ❌ Algorithm တစ်ခုချင်းစီက top 3 ကို ရွေးပြီး 9 ခုထဲက best 3 မရွေးဘူး
- ✅ Best algorithm တစ်ခုကို ရွေးပြီး အဲ့ဒီ algorithm ရဲ့ **best solution တစ်ခုပဲ** ပြတယ်

**Solution:**
1. Global normalization နဲ့ algorithm ရွေးပါ
2. Best algorithm ရဲ့ Pareto front ကို ပြန် normalize လုပ်ပါ
3. Top 3 solutions ကို weighted scores အပေါ် မူတည်ပြီး ပြပါ

---

## Part 7: Code Example - ပိုကောင်းတဲ့ Approach

### Global Normalization နဲ့ Fair Algorithm Comparison

```python
def select_best_algorithm_v2(self, algorithm_results: Dict[str, Dict]) -> Dict:
    """
    Improved algorithm selection using global normalization.
    """
    # Step 1: Combine all Pareto fronts
    all_objectives = []
    algo_names = []
    algo_solution_counts = []

    for algo_name, results in algorithm_results.items():
        pareto_obj = results['pareto_objectives']
        all_objectives.append(pareto_obj)
        algo_names.append(algo_name)
        algo_solution_counts.append(len(pareto_obj))

    combined_objectives = np.vstack(all_objectives)

    # Step 2: Find GLOBAL min and max
    global_min = np.min(combined_objectives, axis=0)
    global_max = np.max(combined_objectives, axis=0)

    # Step 3: Normalize ALL solutions using global min/max
    range_vals = global_max - global_min
    range_vals[range_vals == 0] = 1.0  # Avoid division by zero

    combined_normalized = (combined_objectives - global_min) / range_vals

    # Step 4: Split back to individual algorithms and calculate scores
    scores = {}
    start_idx = 0

    for algo_name, count in zip(algo_names, algo_solution_counts):
        end_idx = start_idx + count
        algo_normalized = combined_normalized[start_idx:end_idx]

        # Calculate weighted scores for this algorithm's solutions
        weighted_scores = (
            algo_normalized[:, 0] * self.preferences.cost_weight +
            algo_normalized[:, 1] * self.preferences.latency_weight +
            algo_normalized[:, 2] * self.preferences.performance_weight
        )

        # Average score for this algorithm
        scores[algo_name] = np.mean(weighted_scores)

        start_idx = end_idx

    # Step 5: Select best algorithm
    best_algorithm = min(scores, key=scores.get)

    # Step 6: Find top 3 solutions from best algorithm
    best_algo_results = algorithm_results[best_algorithm]
    best_algo_objectives = best_algo_results['pareto_objectives']

    # Normalize best algorithm's solutions using GLOBAL min/max
    best_algo_normalized = (best_algo_objectives - global_min) / range_vals

    # Calculate weighted scores
    best_algo_scores = (
        best_algo_normalized[:, 0] * self.preferences.cost_weight +
        best_algo_normalized[:, 1] * self.preferences.latency_weight +
        best_algo_normalized[:, 2] * self.preferences.performance_weight
    )

    # Get top 3 solutions
    top_3_indices = np.argsort(best_algo_scores)[:3]
    top_3_scores = best_algo_scores[top_3_indices]

    return {
        'best_algorithm': best_algorithm,
        'algorithm_scores': scores,
        'top_3_solution_indices': top_3_indices,
        'top_3_scores': top_3_scores,
        'global_min': global_min,
        'global_max': global_max
    }
```

---

### Usage Example

```python
# User preferences
preferences = UserPreferences.from_percentages(
    cost_pct=15,
    latency_pct=5,
    performance_pct=80
)

# Algorithm results
algorithm_results = {
    'nsga2': {'pareto_objectives': nsga2_pareto_front},
    'moead': {'pareto_objectives': moead_pareto_front},
    'spea2': {'pareto_objectives': spea2_pareto_front}
}

# Select best algorithm with global normalization
selector = AlgorithmSelector(preferences)
result = selector.select_best_algorithm_v2(algorithm_results)

print(f"Best Algorithm: {result['best_algorithm']}")
print(f"Top 3 Solutions:")
for i, (idx, score) in enumerate(zip(result['top_3_solution_indices'],
                                      result['top_3_scores']), 1):
    print(f"  #{i}: Solution {idx}, Weighted Score: {score:.4f}")
```

---

## အကျဉ်းချုပ်

### မေးခွန်း ၁: Normalization က perspective view အကောင်းဆုံးတွေကိုပဲ ယူနေတယ်မဟုတ်လား?

**အဖြေ: မှန်ပါတယ်။** လက်ရှိ implementation က algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်တာကြောင့် unfair comparison ဖြစ်နေတယ်။

**Solution: Global normalization** - combined Pareto front ကို သုံးပြီး global min/max နဲ့ normalize လုပ်ပါ။

---

### မေးခွန်း ၂: Top 3 solutions ကို ဘယ်လို ရွေးတာလဲ?

**အဖြေ:** လက်ရှိ implementation က:
- Single algorithm: Highest weight objective အပေါ် မူတည်ပြီး sort လုပ်တယ်
- Multiple algorithms: Best algorithm ရဲ့ **best solution တစ်ခုပဲ** ပြတယ် (top 3 မဟုတ်ဘူး)

**Solution:** Global normalization + weighted scores နဲ့ top 3 ရွေးပါ။

---

### Key Takeaways

1. **Min-max normalization က အကောင်းဆုံး → 0.0, အဆိုးဆုံး → 1.0 ဖြစ်စေတယ်**
   - ဒါက သင့်ရဲ့ observation မှန်ပါတယ်

2. **Algorithm တစ်ခုချင်းစီကို သီးခြား normalize လုပ်တာ unfair**
   - Absolute values ကို ဆုံးရှုံးစေတယ်
   - Global normalization သုံးပါ

3. **လက်ရှိ top solutions selection မပြည့်စုံဘူး**
   - Single-objective sorting သုံးနေတယ်
   - Weighted multi-objective scoring သုံးသင့်တယ်

4. **Recommendation:**
   - Global normalization ကို implement လုပ်ပါ
   - Top 3 solutions ကို weighted scores နဲ့ ပြပါ
   - Algorithm comparison ကို fair ဖြစ်အောင် လုပ်ပါ

---

## နောက်ထပ် အသေးစိတ် မေးခွန်းများ ရှိပါက

သင့်အနေနဲ့ normalization နဲ့ selection process အကြောင်း နောက်ထပ် သိလိုတာ ရှိပါက ထပ်မေးနိုင်ပါတယ်။ ဒီ document က သင့်ရဲ့ concerns နှစ်ခုလုံးကို အသေးစိတ် ရှင်းပြပြီးပါပြီ။
