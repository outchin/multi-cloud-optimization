# NSGA-II Algorithm အသေးစိတ် ရှင်းလင်းချက်

## NSGA-II ဆိုတာ ဘာလဲ?

**NSGA-II** = **Non-dominated Sorting Genetic Algorithm II**

Multi-objective optimization problems တွေကို ဖြေရှင်းဖို့ အသုံးပြုတဲ့ evolutionary algorithm တစ်ခုဖြစ်ပါတယ်။ Deb et al. (2002) က တီထွင်ခဲ့တာဖြစ်ပြီး NSGA (original version) ကို ပိုကောင်းအောင် တိုးတက်ထားတာဖြစ်ပါတယ်။

---

## အဓိက Concepts များ

### 1. Multi-Objective Optimization

**ပြဿနာ:**
- Single objective မဟုတ်ဘဲ objectives အများကြီး ရှိတယ်
- ဥပမာ: Cost minimize လုပ်ချင်တယ်, Latency minimize လုပ်ချင်တယ်, Performance maximize လုပ်ချင်တယ်
- Objectives တွေ conflict ဖြစ်တယ် (e.g., cost နည်းရင် performance နည်းတယ်)

**အဖြေ:**
- Single "best" solution မရှိဘူး
- **Pareto optimal solutions** အစုတစ်စု ရှိတယ်
- User က သူ့ရဲ့ preferences အပေါ် မူတည်ပြီး ရွေးနိုင်တယ်

---

### 2. Pareto Dominance

**Dominance ဆိုတာ ဘာလဲ?**

Solution A က solution B ကို **dominate** လုပ်တယ် ဆိုတာ:
1. A က objectives အားလုံးမှာ B ထက် **ပိုမဆိုးဘူး** (≤)
2. A က objectives အနည်းဆုံး တစ်ခုမှာ B ထက် **strictly ပိုကောင်းတယ်** (<)

**ဥပမာ:**

| Solution | Cost ($) | Latency (ms) | Performance |
|----------|----------|--------------|-------------|
| A        | 1.0      | 5.0          | 10000       |
| B        | 1.5      | 6.0          | 9000        |
| C        | 0.8      | 7.0          | 11000       |

**Analysis:**
- **A dominates B**: A က cost, latency, performance အားလုံးမှာ ပိုကောင်းတယ်
- **A does NOT dominate C**: A က latency ပိုကောင်းပေမယ့် cost နဲ့ performance မှာ ပိုဆိုးတယ်
- **C does NOT dominate A**: C က cost နဲ့ performance ပိုကောင်းပေမယ့် latency မှာ ပိုဆိုးတယ်

**Pareto Optimal (Non-dominated):** ဘယ် solution ကမှ dominate မလုပ်နိုင်တဲ့ solution

ဒီ example မှာ **A နဲ့ C နှစ်ခုလုံး Pareto optimal** ဖြစ်တယ် (သူတို့က တစ်ယောက်ကို တစ်ယောက် dominate မလုပ်နိုင်ဘူး)။

---

### 3. Pareto Front

**Pareto Front** = Pareto optimal solutions အားလုံးရဲ့ အစု

Objective space မှာ plot လုပ်လိုက်ရင် "front" (မျဉ်းကွေး) ပုံစံ ဖြစ်တယ်။

```
Performance
    ↑
    |     C  ●
    |         ╲
    |          ╲ A
    |           ●╲
    |             ╲
    |              ●─── Pareto Front
    |               ╲ B
    |                ●
    |________________→ Cost
```

**ရည်မှန်းချက်:** Algorithm ကို run တဲ့အခါ **diverse Pareto front** ကို ရှာချင်တယ်။

---

## NSGA-II ရဲ့ အဓိက Features

### 1. Fast Non-dominated Sorting
- Population ကို fronts အလိုက် သီးခြား ခွဲတယ်
- Front 1: Non-dominated solutions (အကောင်းဆုံး)
- Front 2: Front 1 ကို ဖယ်ရှားရင် non-dominated ဖြစ်တဲ့ solutions
- Front 3, 4, ... အဆင့်ဆင့်
- **Complexity:** O(MN²) - M = objectives, N = population size

### 2. Crowding Distance
- Same front ထဲမှာ ရှိတဲ့ solutions တွေကို diversity maintain လုပ်ဖို့
- Solution တစ်ခုရဲ့ နှစ်ဘက် neighbors တွေ ဘယ်လောက် ဝေးလဲဆိုတာ တိုင်းတယ်
- Larger distance = more isolated = ပိုကောင်းတယ် (diversity အတွက်)

### 3. Elitism
- Parent နဲ့ offspring ကို combine လုပ်ပြီး အကောင်းဆုံးကို ရွေးတယ်
- Good solutions တွေ ဆုံးရှုံးသွားခြင်း မရှိဘူး

---

## NSGA-II Algorithm အဆင့်များ

### Overview Flow

```
1. Initialize Random Population (P₀)
   ↓
2. Evaluate Objectives
   ↓
3. Loop for G generations:
   │
   ├─ 3.1. Fast Non-dominated Sorting
   │      └─ Rank solutions into fronts (F₁, F₂, F₃, ...)
   │
   ├─ 3.2. Crowding Distance Assignment
   │      └─ Calculate diversity metric
   │
   ├─ 3.3. Tournament Selection
   │      └─ Select parents based on rank + crowding distance
   │
   ├─ 3.4. Crossover
   │      └─ Create offspring from parents
   │
   ├─ 3.5. Mutation
   │      └─ Introduce variation
   │
   ├─ 3.6. Combine Parent + Offspring (Pₜ + Qₜ = Rₜ)
   │      └─ Size = 2N
   │
   └─ 3.7. Environmental Selection
          └─ Select best N solutions for next generation
   ↓
4. Return Pareto Front (F₁)
```

---

## အဆင့် ၁: Initialization (Population ဖန်တီးခြင်း)

**ဘာလုပ်တာလဲ:**
- Random solutions (individuals) အစုတစ်စု ဖန်တီးတယ်
- Population size N ရွေးတယ် (ဥပမာ 50, 100)

**Code:**
```python
# algorithms/nsga2.py:48-50
population = np.random.randint(min_val, max_val + 1,
                              size=(population_size, n_variables))
```

**ဥပမာ:**
```
Services: [frontend, backend, database]  (n_variables = 3)
Instances: 0-72                         (73 compatible instances)
Population size: 4

Population (random):
Individual 0: [12, 45, 33]  → frontend=instance_12, backend=instance_45, database=instance_33
Individual 1: [5,  67, 21]
Individual 2: [34, 12, 55]
Individual 3: [8,  29, 41]
```

---

## အဆင့် ၂: Evaluation (Objectives တွက်ချက်ခြင်း)

**ဘာလုပ်တာလဲ:**
- Individual တစ်ခုချင်းစီအတွက် objective values တွေ တွက်တယ်
- ကျွန်တော်တို့မှာ: [cost, latency, -performance]

**Code:**
```python
# algorithms/nsga2.py:58
objectives = np.array([evaluate_func(ind) for ind in population])
```

**ဥပမာ:**
```
Individual 0: [12, 45, 33] → Evaluate
  - Cost: $2.34/hour
  - Latency: 8.5 ms
  - Performance: 15000
  → Objectives: [2.34, 8.5, -15000]  (negative performance for minimization)

All objectives:
[[2.34,  8.5, -15000],   # Individual 0
 [1.45, 12.0, -12000],   # Individual 1
 [3.20,  5.0, -20000],   # Individual 2
 [2.10,  9.0, -14000]]   # Individual 3
```

---

## အဆင့် ၃: Fast Non-dominated Sorting

### 3.1. Concept

Population ကို **fronts** (ranks) အလိုက် ခွဲတယ်:
- **Front 1 (F₁):** Non-dominated solutions (ဘယ်သူမှ dominate မလုပ်ထားဘူး)
- **Front 2 (F₂):** F₁ ကို ဖယ်ရှားရင် non-dominated ဖြစ်တဲ့ solutions
- **Front 3 (F₃), ...**

### 3.2. Algorithm

**Step-by-step:**

1. **Domination relationships ရှာခြင်း:**
   - Individual i တစ်ခုချင်းစီအတွက်:
     - `domination_count[i]`: i ကို dominate လုပ်ထားတဲ့ solutions အရေအတွက်
     - `dominated_solutions[i]`: i က dominate လုပ်ထားတဲ့ solutions များ

2. **Front 1 ရှာခြင်း:**
   - `domination_count[i] == 0` ဆိုရင် Front 1 မှာ ထည့်တယ်

3. **Subsequent fronts ရှာခြင်း:**
   - Front k ထဲက solution တစ်ခုချင်းစီအတွက်:
     - သူက dominate လုပ်ထားတဲ့ solutions တွေရဲ့ domination_count ကို 1 လျှော့တယ်
     - domination_count == 0 ဖြစ်သွားရင် next front မှာ ထည့်တယ်

### 3.3. Code

```python
# algorithms/nsga2.py:118-168
def _fast_non_dominated_sort(self, objectives):
    n = len(objectives)

    domination_count = np.zeros(n, dtype=int)
    dominated_solutions = [[] for _ in range(n)]
    fronts = [[]]

    # Find domination relationships
    for i in range(n):
        for j in range(i + 1, n):
            if self.dominates(objectives[i], objectives[j]):
                dominated_solutions[i].append(j)
                domination_count[j] += 1
            elif self.dominates(objectives[j], objectives[i]):
                dominated_solutions[j].append(i)
                domination_count[i] += 1

    # First front
    for i in range(n):
        if domination_count[i] == 0:
            fronts[0].append(i)

    # Subsequent fronts
    k = 0
    while k < len(fronts) and len(fronts[k]) > 0:
        next_front = []
        for i in fronts[k]:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)

        if len(next_front) > 0:
            fronts.append(next_front)
        k += 1

    return fronts
```

### 3.4. ဥပမာ

**Population (4 individuals):**

| ID | Cost | Latency | Perf | Objectives |
|----|------|---------|------|------------|
| 0  | 2.34 | 8.5     | 15k  | [2.34, 8.5, -15000] |
| 1  | 1.45 | 12.0    | 12k  | [1.45, 12.0, -12000] |
| 2  | 3.20 | 5.0     | 20k  | [3.20, 5.0, -20000] |
| 3  | 2.10 | 9.0     | 14k  | [2.10, 9.0, -14000] |

**Dominance Analysis:**

```
Compare 0 vs 1:
  Cost:   2.34 > 1.45  (1 better)
  Lat:    8.5  < 12.0  (0 better)
  Perf: -15k   < -12k  (0 better, lower negative = higher performance)
  → 0 does NOT dominate 1, 1 does NOT dominate 0

Compare 0 vs 2:
  Cost:   2.34 < 3.20  (0 better)
  Lat:    8.5  > 5.0   (2 better)
  Perf: -15k   > -20k  (2 better)
  → 0 does NOT dominate 2, 2 does NOT dominate 0

Compare 0 vs 3:
  Cost:   2.34 > 2.10  (3 better)
  Lat:    8.5  < 9.0   (0 better)
  Perf: -15k   < -14k  (0 better)
  → 0 does NOT dominate 3, 3 does NOT dominate 0

Compare 1 vs 2:
  Cost:   1.45 < 3.20  (1 better)
  Lat:    12.0 > 5.0   (2 better)
  Perf: -12k   > -20k  (2 better)
  → 1 does NOT dominate 2, 2 does NOT dominate 1

Compare 1 vs 3:
  Cost:   1.45 < 2.10  (1 better)
  Lat:    12.0 > 9.0   (3 better)
  Perf: -12k   > -14k  (3 better)
  → 1 does NOT dominate 3, 3 does NOT dominate 1

Compare 2 vs 3:
  Cost:   3.20 > 2.10  (3 better)
  Lat:    5.0  < 9.0   (2 better)
  Perf: -20k   < -14k  (2 better)
  → 2 does NOT dominate 3, 3 does NOT dominate 2
```

**Domination Count:**
- Individual 0: domination_count = 0 → **Front 1**
- Individual 1: domination_count = 0 → **Front 1**
- Individual 2: domination_count = 0 → **Front 1**
- Individual 3: domination_count = 0 → **Front 1**

**Result:**
```
Front 1: [0, 1, 2, 3]  ← All are non-dominated!
```

**Real-world example (larger population):**

Imagine population size = 10:

```
Front 1: [0, 2, 5, 7]      ← Best solutions
Front 2: [1, 4, 8]         ← Dominated only by Front 1
Front 3: [3, 6, 9]         ← Dominated by Front 1 & 2
```

---

## အဆင့် ၄: Crowding Distance Assignment

### 4.1. Concept

**ဘာကြောင့် လိုအပ်လဲ?**
- Same front ထဲမှာ solutions အများကြီး ရှိနိုင်တယ်
- Diversity ထိန်းဖို့ **sparse regions** (ကွဲကွာနေတဲ့ နေရာ) ထဲက solutions တွေကို ရွေးချင်တယ်

**Crowding Distance ဆိုတာ:**
- Solution တစ်ခုရဲ့ neighbor solutions တွေနဲ့ ဘယ်လောက် ဝေးလဲဆိုတာ
- Large distance = isolated = diversity အတွက် ကောင်းတယ်

### 4.2. Algorithm

**Step-by-step:**

1. Front ထဲက solutions အားလုံးကို sort လုပ်တယ် (objective တစ်ခုချင်းစီအတွက်)
2. Boundary solutions (အစ နဲ့ အဆုံး) ကို **infinite distance** ပေးတယ် (အမြဲ ထိန်းသိမ်းမယ်)
3. Middle solutions တွေအတွက် distance တွက်တယ်:
   ```
   distance[i] += (f[i+1] - f[i-1]) / (f_max - f_min)
   ```
4. Objectives အားလုံးမှာ ထပ်တူ လုပ်ပြီး distance ပေါင်းတယ်

### 4.3. Code

```python
# algorithms/nsga2.py:170-203
def _crowding_distance_assignment(self, objectives):
    n = len(objectives)
    n_obj = objectives.shape[1]

    distance = np.zeros(n)

    for m in range(n_obj):
        # Sort by objective m
        sorted_idx = np.argsort(objectives[:, m])

        # Boundary solutions get infinite distance
        distance[sorted_idx[0]] = float('inf')
        distance[sorted_idx[-1]] = float('inf')

        # Calculate distance for middle solutions
        obj_range = objectives[sorted_idx[-1], m] - objectives[sorted_idx[0], m]

        if obj_range > 0:
            for i in range(1, n - 1):
                distance[sorted_idx[i]] += (
                    (objectives[sorted_idx[i + 1], m] -
                     objectives[sorted_idx[i - 1], m]) / obj_range
                )

    return distance
```

### 4.4. ဥပမာ

**Front 1 ထဲမှာ 5 solutions ရှိတယ်:**

| ID | Cost | Latency | Perf |
|----|------|---------|------|
| 0  | 1.0  | 10.0    | 8000 |
| 1  | 2.0  | 7.0     | 12000 |
| 2  | 3.0  | 5.0     | 15000 |
| 3  | 4.0  | 3.0     | 18000 |
| 4  | 5.0  | 1.0     | 20000 |

**Objective 1: Cost**

Sort by cost: [0, 1, 2, 3, 4]
- Distance[0] = ∞ (boundary)
- Distance[4] = ∞ (boundary)
- Distance[1] += (3.0 - 1.0) / (5.0 - 1.0) = 2.0 / 4.0 = 0.5
- Distance[2] += (4.0 - 2.0) / (5.0 - 1.0) = 2.0 / 4.0 = 0.5
- Distance[3] += (5.0 - 3.0) / (5.0 - 1.0) = 2.0 / 4.0 = 0.5

**Objective 2: Latency**

Sort by latency: [4, 3, 2, 1, 0]
- Distance[4] = ∞ (already)
- Distance[0] = ∞ (already)
- Distance[3] += (5.0 - 1.0) / (10.0 - 1.0) = 4.0 / 9.0 = 0.44
- Distance[2] += (7.0 - 3.0) / (10.0 - 1.0) = 4.0 / 9.0 = 0.44
- Distance[1] += (10.0 - 5.0) / (10.0 - 1.0) = 5.0 / 9.0 = 0.56

**Objective 3: Performance**

Sort by -perf: [0, 1, 2, 3, 4]
- Distance[0] = ∞ (already)
- Distance[4] = ∞ (already)
- Distance[1] += (-12k - (-8k)) / (-20k - (-8k)) = -4k / -12k = 0.33
- Distance[2] += (-15k - (-12k)) / (-20k - (-8k)) = -3k / -12k = 0.25
- Distance[3] += (-18k - (-15k)) / (-20k - (-8k)) = -3k / -12k = 0.25

**Final Crowding Distances:**
- Distance[0] = ∞
- Distance[1] = 0.5 + 0.56 + 0.33 = **1.39**
- Distance[2] = 0.5 + 0.44 + 0.25 = **1.19**
- Distance[3] = 0.5 + 0.44 + 0.25 = **1.19**
- Distance[4] = ∞

**Interpretation:**
- Solutions 0 နဲ့ 4 က boundary ဖြစ်တဲ့အတွက် အမြဲ ထိန်းသိမ်းမယ်
- Solution 1 က middle solutions ထဲမှာ အများဆုံး isolated ဖြစ်တယ် (1.39)
- Solutions 2 နဲ့ 3 က ပိို crowded ဖြစ်တယ် (1.19)

---

## အဆင့် ၅: Tournament Selection (Parent ရွေးချယ်ခြင်း)

### 5.1. Concept

**ဘာကြောင့် လိုအပ်လဲ?**
- Offspring ဖန်တီးဖို့ parent solutions နှစ်ခု လိုတယ်
- အကောင်းဆုံး solutions တွေကို ရွေးချင်တယ်

**Tournament Selection:**
- Random candidates နှစ်ခု ရွေးတယ်
- Best ကို ရွေးတယ် based on:
  1. **Rank (Front):** Lower rank ပိုကောင်းတယ် (Front 1 > Front 2)
  2. **Crowding Distance:** Tie ဖြစ်ရင် larger distance ပိုကောင်းတယ်

### 5.2. Code

```python
# algorithms/nsga2.py:238-273
def _tournament_selection(self, population, objectives, fronts):
    # Pick 2 random individuals
    candidates = np.random.choice(len(population), 2, replace=False)

    # Find which front each belongs to
    candidate_ranks = []
    for idx in candidates:
        for rank, front in enumerate(fronts):
            if idx in front:
                candidate_ranks.append(rank)
                break

    # Select based on rank
    best_rank = min(candidate_ranks)
    best_candidates = [candidates[i] for i, r in enumerate(candidate_ranks) if r == best_rank]

    if len(best_candidates) == 1:
        return population[best_candidates[0]].copy()

    # If tie, select based on crowding distance
    front_idx = fronts[best_rank]
    front_objectives = objectives[front_idx]
    distances = self._crowding_distance_assignment(front_objectives)

    # Select candidate with larger distance
    best = best_candidates[np.argmax([distances[...]])]
    return population[best].copy()
```

### 5.3. ဥပမာ

**Population:**
```
Front 1: [0, 2, 5]     (best)
Front 2: [1, 4, 8]
Front 3: [3, 6, 9]
```

**Tournament 1:**
- Candidates: [2, 8]
- Ranks: [0 (Front 1), 1 (Front 2)]
- Winner: **Individual 2** (lower rank)

**Tournament 2:**
- Candidates: [0, 5]
- Ranks: [0 (Front 1), 0 (Front 1)]  ← Tie!
- Calculate crowding distances for Front 1: [∞, 1.5, 2.0]
  - Individual 0: distance = ∞
  - Individual 5: distance = 2.0
- Winner: **Individual 0** (larger distance)

---

## အဆင့် ၆: Crossover (မျိုးပွား ခြင်း)

### 6.1. Concept

**ဘာလုပ်တာလဲ?**
- Parent နှစ်ခုကနေ offspring နှစ်ခု ဖန်တီးတယ်
- Parents တွေရဲ့ genetic information ကို mix လုပ်တယ်

**Single-point Crossover:**
- Random cutting point တစ်ခု ရွေးတယ်
- Point အရှေ့က parent 1, အနောက်က parent 2 ကို ယူပြီး child 1 ဖန်တီးတယ်
- အပြောင်းအလှန် လုပ်ပြီး child 2 ဖန်တီးတယ်

### 6.2. Code

```python
# algorithms/nsga2.py:275-283
def _crossover(self, parent1, parent2):
    n = len(parent1)
    point = np.random.randint(1, n)

    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])

    return child1, child2
```

### 6.3. ဥပမာ

**Parents:**
```
Parent 1: [12, 45, 33, 8,  29]
Parent 2: [5,  67, 21, 34, 12]
```

**Crossover point = 2:**

```
         ↓ cutting point
Parent 1: [12, 45 | 33, 8, 29]
Parent 2: [5,  67 | 21, 34, 12]

Child 1:  [12, 45 | 21, 34, 12]  ← Take from P1[:2] + P2[2:]
Child 2:  [5,  67 | 33, 8,  29]  ← Take from P2[:2] + P1[2:]
```

**Crossover probability:**
- Typically 0.9 (90%)
- Random number < 0.9 ဆိုရင် crossover လုပ်တယ်
- မဟုတ်ရင် parents ကို တိုက်ရိုက် copy လုပ်တယ်

---

## အဆင့် ၇: Mutation (ပြောင်းလဲခြင်း)

### 7.1. Concept

**ဘာကြောင့် လိုအပ်လဲ?**
- Genetic diversity ထိန်းဖို့
- Local optima ကနေ ထွက်ဖို့
- New solutions explore လုပ်ဖို့

**Uniform Mutation:**
- Gene တစ်ခုချင်းစီကို mutation probability နဲ့ စစ်တယ်
- Mutate ဖြစ်ရင် random value အသစ် သတ်မှတ်တယ်

### 7.2. Code

```python
# algorithms/nsga2.py:285-294
def _mutate(self, individual, mutation_prob, min_val, max_val):
    mutated = individual.copy()

    for i in range(len(mutated)):
        if np.random.random() < mutation_prob:
            mutated[i] = np.random.randint(min_val, max_val + 1)

    return mutated
```

### 7.3. ဥပမာ

**Before mutation:**
```
Child: [12, 45, 21, 34, 12]
```

**Mutation probability = 0.2 (1/5):**

```
Gene 0 (12): random(0,1) = 0.45 > 0.2 → No mutation
Gene 1 (45): random(0,1) = 0.15 < 0.2 → Mutate! → New value: 67
Gene 2 (21): random(0,1) = 0.78 > 0.2 → No mutation
Gene 3 (34): random(0,1) = 0.12 < 0.2 → Mutate! → New value: 8
Gene 4 (12): random(0,1) = 0.92 > 0.2 → No mutation
```

**After mutation:**
```
Child: [12, 67, 21, 8, 12]
       ────  ↑      ↑
       Same  Changed Changed
```

**Mutation probability:**
- Default: `1 / n_variables`
- ဥပမာ: 5 services ဆိုရင် 1/5 = 0.2 (20%)

---

## အဆင့် ၈: Environmental Selection (Survivor ရွေးချယ်ခြင်း)

### 8.1. Concept

**ပြဿနာ:**
- Parent population: N individuals
- Offspring population: N individuals
- Combined: 2N individuals
- Next generation အတွက် N individuals ပဲ လိုတယ်

**ဘယ်လို ရွေးမလဲ?**
1. Fast non-dominated sorting လုပ်တယ်
2. Front 1 ကို ပထမ ထည့်တယ်
3. ပြည့်သွားတဲ့ထိ နောက် fronts တွေ ဆက်ထည့်တယ်
4. နောက်ဆုံး front က partially ထည့်ရရင် **crowding distance** အပေါ် မူတည်ပြီး ရွေးတယ်

### 8.2. Code

```python
# algorithms/nsga2.py:296-317
def _environmental_selection(self, population, objectives, target_size):
    fronts = self._fast_non_dominated_sort(objectives)

    selected = []
    for front in fronts:
        if len(selected) + len(front) <= target_size:
            # Add entire front
            selected.extend(front)
        else:
            # Partial front: select based on crowding distance
            remaining = target_size - len(selected)
            front_objectives = objectives[front]
            distances = self._crowding_distance_assignment(front_objectives)

            # Select individuals with largest crowding distance
            sorted_idx = np.argsort(distances)[::-1]  # Descending order
            selected.extend(front[sorted_idx[:remaining]])
            break

    return population[selected]
```

### 8.3. ဥပမာ

**Combined population (2N = 20):**
```
Front 1: [0, 2, 5, 7, 9]       (5 individuals)
Front 2: [1, 4, 8, 11, 14]     (5 individuals)
Front 3: [3, 6, 10, 13]        (4 individuals)
Front 4: [12, 15, 16, 17, 18, 19]  (6 individuals)
```

**Target size: N = 10**

**Selection process:**

1. **Add Front 1:** 5 individuals → Total: 5 (< 10, ဆက်ထည့်မယ်)
2. **Add Front 2:** 5 individuals → Total: 10 (= 10, ပြီးပြီ!)

**Selected individuals:** [0, 2, 5, 7, 9, 1, 4, 8, 11, 14]

---

**Another example (partial front):**

**Target size: N = 12**

1. **Add Front 1:** 5 individuals → Total: 5
2. **Add Front 2:** 5 individuals → Total: 10
3. **Front 3:** 4 individuals → Total would be 14 (> 12)
   - Need only 2 more individuals from Front 3
   - Calculate crowding distances for Front 3:
     ```
     Individual 3:  distance = 2.5
     Individual 6:  distance = 1.8
     Individual 10: distance = 3.0
     Individual 13: distance = 2.2
     ```
   - Sort by distance (descending): [10, 3, 13, 6]
   - Select top 2: [10, 3]

**Final selected:** [0, 2, 5, 7, 9, 1, 4, 8, 11, 14, 10, 3]

---

## NSGA-II လုပ်ဆောင်ချက် အပြည့်အစုံ ဥပမာ

### Generation 0

**Step 1: Initialize population (N = 6)**
```
Population:
  0: [12, 45, 33]
  1: [5,  67, 21]
  2: [34, 12, 55]
  3: [8,  29, 41]
  4: [23, 50, 18]
  5: [15, 38, 62]
```

**Step 2: Evaluate objectives**
```
Objectives (cost, latency, -perf):
  0: [2.34,  8.5, -15000]
  1: [1.45, 12.0, -12000]
  2: [3.20,  5.0, -20000]
  3: [2.10,  9.0, -14000]
  4: [2.80,  7.0, -16000]
  5: [2.90, 10.5, -13000]
```

**Step 3: Fast non-dominated sorting**
```
Front 1: [1, 2, 4]   ← Non-dominated
Front 2: [0, 3, 5]   ← Dominated by Front 1
```

**Step 4: Crowding distance**
```
Front 1 distances: [∞, 1.5, ∞]
Front 2 distances: [2.0, 1.8, 2.2]
```

**Step 5-7: Generate offspring (N = 6)**
```
Tournament selection → Crossover → Mutation → Offspring:
  6: [23, 67, 21]
  7: [5,  50, 55]
  8: [12, 29, 33]
  9: [34, 38, 18]
  10: [15, 12, 62]
  11: [8,  45, 41]
```

**Step 8: Evaluate offspring**
```
Offspring objectives:
  6: [2.50,  9.0, -14500]
  7: [1.80,  8.0, -17000]
  8: [2.20,  7.5, -15500]
  9: [3.00,  6.0, -19000]
  10: [2.70, 11.0, -13500]
  11: [2.00,  8.8, -14200]
```

**Step 9: Combine parent + offspring (2N = 12)**
```
Combined: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

**Step 10: Environmental selection (select N = 6)**
```
Fast non-dominated sort on combined:
  Front 1: [1, 2, 4, 7, 9]   (5 individuals)
  Front 2: [0, 3, 8, 11]     (4 individuals)
  Front 3: [5, 6, 10]        (3 individuals)

Selected (6 needed):
  - Add Front 1: 5 individuals → Total: 5
  - Front 2: 4 individuals → Would be 9 (> 6)
    - Need only 1 from Front 2
    - Crowding distances: [2.0, 1.8, 2.5, 1.5]
    - Select highest: Individual 8 (distance 2.5)

Next generation: [1, 2, 4, 7, 9, 8]
```

### Generation 1

Repeat steps 5-10...

---

## Parameters (ကန့်သတ်ချက်များ)

### 1. Population Size (N)

**ဘာလဲ?** Generation တစ်ခုမှာ ရှိမယ့် individuals အရေအတွက်

**Typical values:** 50-100 (can be higher for complex problems)

**Trade-offs:**
- **Small N:** Fast, but poor exploration
- **Large N:** Better exploration, but slower

**Our implementation:**
```python
population_size = 50  # Default
```

---

### 2. Number of Generations (G)

**ဘာလဲ?** Evolution cycles အရေအတွက်

**Typical values:** 100-500

**Trade-offs:**
- **Few generations:** Fast, but may not converge
- **Many generations:** Better convergence, but slower

**Our implementation:**
```python
n_generations = 100  # Default
```

---

### 3. Crossover Probability (Pc)

**ဘာလဲ?** Parent နှစ်ခုကို crossover လုပ်မယ့် probability

**Typical values:** 0.8-0.95

**Default:**
```python
crossover_prob = 0.9  # 90%
```

---

### 4. Mutation Probability (Pm)

**ဘာလဲ?** Gene တစ်ခုချင်းစီကို mutate လုပ်မယ့် probability

**Typical values:** 1/n_variables

**Default:**
```python
mutation_prob = 1.0 / n_variables  # e.g., 1/5 = 0.2 for 5 services
```

---

## NSGA-II ကို ဘယ်အခါ သုံးသင့်လဲ?

### အသုံးပြုသင့်တဲ့ အခြေအနေများ

✅ **Multi-objective problems:**
- Objectives 2-3 ခု ရှိတဲ့အခါ (ပိုများရင်လည်း အဆင်ပြေတယ်)
- Objectives တွေ conflict ဖြစ်တယ်

✅ **Diverse Pareto front လိုချင်တဲ့အခါ:**
- User က solutions အများကြီးထဲက ရွေးချင်တဲ့အခါ

✅ **Complex solution space:**
- Non-linear, non-convex problems
- Discrete variables (like instance selection)

✅ **No gradient information:**
- Objective functions တွေ differentiable မဟုတ်ရင်

---

### မသုံးသင့်တဲ့ အခြေအနေများ

❌ **Single objective:**
- Simple GA ပိုကောင်းတယ်

❌ **Many objectives (> 5):**
- NSGA-III သို့မဟုတ် many-objective algorithms ပိုကောင်းတယ်

❌ **Very large populations needed:**
- Slower algorithms, consider MOEA/D

---

## NSGA-II ရဲ့ အားသာချက်များ

### ✅ Advantages

1. **Elitism:** Good solutions မဆုံးရှုံးဘူး
2. **Diversity maintenance:** Crowding distance က diverse front ကို maintain လုပ်တယ်
3. **Fast:** O(MN²) complexity (reasonable)
4. **Well-studied:** Widely used, lots of research
5. **Parameter insensitive:** Default parameters က ကောင်းကောင်း အလုပ်လုပ်တယ်

---

### ❌ Disadvantages

1. **O(MN²) complexity:** Large populations မှာ နှေးတယ်
2. **Many objectives:** 3+ objectives မှာ crowding distance က ineffective ဖြစ်တယ်
3. **Parameter setting:** Still needs population size, generations tuning

---

## Real-world Performance

### ကျွန်တော်တို့ရဲ့ Multi-cloud Problem မှာ

**Problem:**
- 5 services
- 73 compatible instances
- 3 objectives (cost, latency, performance)

**Parameters:**
```python
population_size = 50
n_generations = 100
crossover_prob = 0.9
mutation_prob = 0.2  # 1/5
```

**Typical results:**
```
Generation 0:   Pareto size: 12
Generation 50:  Pareto size: 18
Generation 100: Pareto size: 22

Final Pareto front: 22 diverse solutions
Cost range: $0.67 - $3.56/hour
Latency range: 1.0 - 18.4 ms
Performance range: 4518 - 17618
```

---

## Comparison with Other Algorithms

| Feature | NSGA-II | MOEA/D | SPEA2 |
|---------|---------|--------|-------|
| **Approach** | Pareto ranking | Decomposition | Archive |
| **Diversity** | Crowding dist | Weight vectors | Nearest neighbor |
| **Complexity** | O(MN²) | O(MN²) | O(MN³) |
| **Best for** | 2-3 objectives | Many objectives | Archive quality |
| **Convergence** | Good | Good | Very good |
| **Implementation** | Straightforward | Complex | Moderate |

---

## Code Structure Summary

```python
class NSGA2:
    def optimize():
        # 1. Initialize population
        population = random_init()

        # 2. Main loop
        for generation in range(n_generations):
            # 2.1. Evaluate
            objectives = evaluate(population)

            # 2.2. Non-dominated sorting
            fronts = fast_non_dominated_sort(objectives)

            # 2.3. Crowding distance
            for front in fronts:
                crowding_distance_assignment(front)

            # 2.4. Generate offspring
            offspring = []
            while len(offspring) < N:
                # Selection
                parent1 = tournament_selection()
                parent2 = tournament_selection()

                # Crossover
                child1, child2 = crossover(parent1, parent2)

                # Mutation
                child1 = mutate(child1)
                child2 = mutate(child2)

                offspring.extend([child1, child2])

            # 2.5. Combine
            combined = population + offspring

            # 2.6. Environmental selection
            population = environmental_selection(combined, N)

        # 3. Return Pareto front
        return population[front_1]
```

---

## Summary

### NSGA-II အကျဉ်းချုပ်

**ဘာလဲ?**
- Multi-objective evolutionary algorithm
- Pareto dominance concept ကို သုံးတယ်

**အဓိက Components:**
1. **Fast non-dominated sorting** - Solutions ကို fronts အလိုက် rank လုပ်တယ်
2. **Crowding distance** - Diversity maintain လုပ်တယ်
3. **Elitism** - Good solutions ထိန်းသိမ်းတယ်
4. **Tournament selection** - Parents ရွေးတယ်
5. **Crossover & mutation** - Offspring ဖန်တီးတယ်
6. **Environmental selection** - Next generation ရွေးတယ်

**ဘယ်အခါ သုံးမလဲ?**
- Multi-objective problems (2-3 objectives)
- Diverse Pareto front လိုချင်တဲ့အခါ
- Complex, discrete optimization

**အားသာချက်:**
- Elitism, diversity, well-studied

**အားနည်းချက်:**
- O(MN²) complexity, many-objective problems မှာ နည်းတယ်

---

## Next Steps

သင့်အနေနဲ့ အခု NSGA-II ကို နားလည်ပြီဆိုရင်:

1. ✅ **MOEA/D ကို လေ့လာမယ်** (decomposition-based approach)
2. ✅ **SPEA2 ကို လေ့လာမယ်** (archive-based approach)
3. ✅ **Algorithms တွေကို compare လုပ်မယ်**

---

## References

- Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE Transactions on Evolutionary Computation, 6(2), 182-197.
- Implementation: `algorithms/nsga2.py`
- Usage: `main_v2.py --algorithm nsga2`

---

**ပြီးပါပြီ! NSGA-II အကြောင်း အသေးစိတ် သိပြီဖြစ်ပါတယ်။** 🎉
