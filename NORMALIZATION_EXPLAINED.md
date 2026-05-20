# Normalization in Multi-Objective Optimization

## Why Normalization is Critical

In multi-objective optimization, we deal with multiple objectives that have **different units and scales**:

- **Cost**: Measured in dollars per hour ($0.21 - $5.81)
- **Latency**: Measured in milliseconds (1.0 - 17.2 ms)
- **Performance**: Measured in Geekbench scores (2005 - 39800)

### The Problem Without Normalization

If we directly apply user preference weights to raw values, the objective with the largest numerical range will **dominate** the weighted score, regardless of the user's actual preferences.

**Example:**

User preferences: Cost 15%, Latency 5%, Performance 80%

Solution A:
- Cost: $0.50
- Latency: 5 ms
- Performance: 35000

**Without normalization:**
```
Weighted Score = (0.50 × 0.15) + (5 × 0.05) + (35000 × 0.80)
               = 0.075 + 0.25 + 28000
               = 28000.325
```

The performance value (35000) completely **dominates** the score, making cost and latency weights meaningless.

Solution B:
- Cost: $5.00 (10× worse)
- Latency: 15 ms (3× worse)
- Performance: 36000 (only 2.9% better)

```
Weighted Score = (5.00 × 0.15) + (15 × 0.05) + (36000 × 0.80)
               = 0.75 + 0.75 + 28800
               = 28801.5
```

Despite being significantly worse in cost and latency, Solution B has a higher score simply because the large performance numbers overshadow everything else. **This defeats the purpose of user preferences.**

---

## The Solution: Min-Max Normalization

### Mathematical Formula

```
Normalized_value = (Value - Min) / (Max - Min)
```

Where:
- **Value**: The actual objective value for a solution
- **Min**: The minimum value across all solutions for this objective
- **Max**: The maximum value across all solutions for this objective

### Result

All objectives are transformed to a **0 to 1 range**, where:
- **0.0** = Best possible value (minimum for cost/latency, maximum for performance)
- **1.0** = Worst possible value (maximum for cost/latency, minimum for performance)

---

## Step-by-Step Normalization Process

### Step 1: Identify the Range for Each Objective

From all solutions in the Pareto front, find the minimum and maximum values:

**Example dataset:**

| Solution | Cost   | Latency | Performance |
|----------|--------|---------|-------------|
| 1        | $0.21  | 1.0 ms  | 2005        |
| 2        | $2.50  | 8.5 ms  | 15000       |
| 3        | $5.81  | 17.2 ms | 39800       |

**Ranges:**
- Cost: Min = $0.21, Max = $5.81
- Latency: Min = 1.0 ms, Max = 17.2 ms
- Performance: Min = 2005, Max = 39800

---

### Step 2: Apply Min-Max Normalization

Transform each value to the 0-1 range using the formula.

#### Cost Normalization

```
Solution 1: (0.21 - 0.21) / (5.81 - 0.21) = 0.00 / 5.60 = 0.00 ✓ (Best)
Solution 2: (2.50 - 0.21) / (5.81 - 0.21) = 2.29 / 5.60 = 0.41
Solution 3: (5.81 - 0.21) / (5.81 - 0.21) = 5.60 / 5.60 = 1.00 (Worst)
```

#### Latency Normalization

```
Solution 1: (1.0 - 1.0) / (17.2 - 1.0) = 0.0 / 16.2 = 0.00 ✓ (Best)
Solution 2: (8.5 - 1.0) / (17.2 - 1.0) = 7.5 / 16.2 = 0.46
Solution 3: (17.2 - 1.0) / (17.2 - 1.0) = 16.2 / 16.2 = 1.00 (Worst)
```

#### Performance Normalization (Special Case)

**Important:** Performance is stored as **-performance** in the objectives array because we minimize all objectives. Higher performance is better, so we negate it.

Stored values: -2005, -15000, -39800

Range: Min = -39800, Max = -2005

```
Solution 1 (-2005):  (-2005 - (-39800)) / ((-2005) - (-39800)) = 37795 / 37795 = 1.00 (Worst - low performance)
Solution 2 (-15000): (-15000 - (-39800)) / ((-2005) - (-39800)) = 24800 / 37795 = 0.66
Solution 3 (-39800): (-39800 - (-39800)) / ((-2005) - (-39800)) = 0 / 37795 = 0.00 ✓ (Best - high performance)
```

---

### Step 3: Calculate Weighted Score

Now that all objectives are in the 0-1 range, we can meaningfully apply user preference weights.

**User preferences:** Cost 15%, Latency 5%, Performance 80%

**Solution 3 (normalized):**
- Normalized cost: 1.00
- Normalized latency: 1.00
- Normalized -performance: 0.00

```
Weighted Score = (1.00 × 0.15) + (1.00 × 0.05) + (0.00 × 0.80)
               = 0.15 + 0.05 + 0.00
               = 0.20
```

**Solution 1 (normalized):**
- Normalized cost: 0.00
- Normalized latency: 0.00
- Normalized -performance: 1.00

```
Weighted Score = (0.00 × 0.15) + (0.00 × 0.05) + (1.00 × 0.80)
               = 0.00 + 0.00 + 0.80
               = 0.80
```

**Solution 2 (normalized):**
- Normalized cost: 0.41
- Normalized latency: 0.46
- Normalized -performance: 0.66

```
Weighted Score = (0.41 × 0.15) + (0.46 × 0.05) + (0.66 × 0.80)
               = 0.0615 + 0.023 + 0.528
               = 0.6125
```

**Ranking (lower is better):**
1. Solution 3: 0.20 ← **Winner** (high performance aligns with 80% preference)
2. Solution 2: 0.61
3. Solution 1: 0.80

---

## Mathematical Interpretation

### What Does Normalization Do?

The formula `(Value - Min) / (Max - Min)` performs two operations:

#### 1. **Shift to Zero** (Value - Min)

Subtracting the minimum shifts the entire range so it starts at 0.

**Before:** Cost range = $0.21 to $5.81
**After shift:** 0.00 to 5.60

#### 2. **Scale to One** (Divide by Range)

Dividing by the range `(Max - Min)` scales the values to the 0-1 interval.

**After shift:** 0.00 to 5.60
**After scaling:** 0.00 / 5.60 = 0.0 to 5.60 / 5.60 = 1.0

### Linear Transformation

Normalization is a **linear transformation** that preserves the relative distances between values.

If Cost A is 50% between min and max, its normalized value will be 0.5.

**Geometric interpretation:**
```
Original scale:
$0.21 ------------ $3.01 ------------ $5.81
  |                  |                  |
 Min             Midpoint             Max

Normalized scale:
 0.0 -------------- 0.5 -------------- 1.0
  |                  |                  |
 Best            Moderate            Worst
```

---

## Why 0-to-1 Range?

### Comparability

Once normalized, all objectives are **dimensionless** and **comparable**:

- Before: "$3 vs 10ms" → Cannot compare (different units)
- After: "0.5 vs 0.6" → Comparable (both are proportions)

### Meaningful Weights

User preference weights (e.g., 15%, 5%, 80%) now have **true meaning**:

- Without normalization: Large values dominate regardless of weights
- With normalization: Weights accurately reflect user priorities

### Fair Contribution

Each objective contributes to the final score **proportionally** to its weight:

```
Score = Σ (normalized_objective_i × weight_i)
```

All normalized values are in [0, 1], so no single objective can dominate due to scale.

---

## Summary

### Problem
Different objectives have different scales (dollars, milliseconds, scores), causing **scale dominance** when calculating weighted scores.

### Solution
**Min-Max Normalization** transforms all objectives to a **uniform 0-1 scale**, ensuring user preference weights are applied **fairly and meaningfully**.

### Formula
```
Normalized = (Value - Min) / (Max - Min)
```

### Steps
1. Find min and max for each objective across all solutions
2. Apply normalization formula to each objective value
3. Calculate weighted score using normalized values and user weights
4. Lower weighted score = better solution (given user preferences)

### Result
User preferences are **accurately reflected** in algorithm selection and solution ranking, regardless of the original measurement scales.
