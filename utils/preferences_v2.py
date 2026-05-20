"""User preference handling and algorithm selection with GLOBAL NORMALIZATION."""

import numpy as np
from typing import Dict, List, Tuple


class UserPreferences:
    """Handle user preferences for multi-objective optimization."""

    def __init__(self, cost_weight: float = 1/3, latency_weight: float = 1/3,
                 performance_weight: float = 1/3):
        """
        Initialize user preferences.

        Args:
            cost_weight: Weight for cost objective (0-1)
            latency_weight: Weight for latency objective (0-1)
            performance_weight: Weight for performance objective (0-1)

        Note:
            Weights should sum to 1.0
        """
        total = cost_weight + latency_weight + performance_weight
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.cost_weight = cost_weight
        self.latency_weight = latency_weight
        self.performance_weight = performance_weight

    def __repr__(self):
        return (f"UserPreferences(cost={self.cost_weight:.2%}, "
                f"latency={self.latency_weight:.2%}, "
                f"performance={self.performance_weight:.2%})")

    @classmethod
    def from_percentages(cls, cost_pct: float, latency_pct: float,
                        performance_pct: float):
        """
        Create preferences from percentages (0-100).

        Args:
            cost_pct: Cost importance (0-100)
            latency_pct: Latency importance (0-100)
            performance_pct: Performance importance (0-100)

        Example:
            >>> prefs = UserPreferences.from_percentages(40, 40, 20)
            >>> prefs.cost_weight
            0.4
        """
        total = cost_pct + latency_pct + performance_pct
        if not np.isclose(total, 100.0):
            raise ValueError(f"Percentages must sum to 100, got {total}")

        return cls(
            cost_weight=cost_pct / 100.0,
            latency_weight=latency_pct / 100.0,
            performance_weight=performance_pct / 100.0
        )


class AlgorithmSelectorV2:
    """
    Select best algorithm using GLOBAL NORMALIZATION.

    This version addresses the normalization concerns by using a combined
    Pareto front from all algorithms to establish global min/max values.
    """

    def __init__(self, preferences: UserPreferences):
        """
        Initialize algorithm selector.

        Args:
            preferences: User preferences for objectives
        """
        self.preferences = preferences

    def select_best_solutions_globally(self, algorithm_results: Dict[str, Dict],
                                       top_k: int = 15) -> Dict:
        """
        Select top K solutions from ALL algorithms using global normalization.

        This is the main improvement over the original approach:
        - Combines all Pareto fronts into one pool
        - Uses GLOBAL min/max for normalization (not per-algorithm)
        - Ranks ALL solutions fairly based on user preferences
        - Returns top K solutions with their source algorithms

        Args:
            algorithm_results: Dictionary mapping algorithm name to results
            top_k: Number of top solutions to return (default: 15)

        Returns:
            Dictionary with:
                - 'top_solutions': List of top K solution info
                - 'global_min': Global minimum values for each objective
                - 'global_max': Global maximum values for each objective
                - 'algorithm_distribution': Count of solutions per algorithm
                - 'best_algorithm': Algorithm with most solutions in top K
                - 'analysis': Detailed analysis text
        """
        # Step 1: Combine all Pareto fronts
        all_objectives = []
        all_solutions = []
        solution_metadata = []  # (algo_name, solution_index)

        for algo_name, results in algorithm_results.items():
            pareto_obj = results['pareto_objectives']
            pareto_sol = results['pareto_front']

            all_objectives.append(pareto_obj)
            all_solutions.append(pareto_sol)

            for i in range(len(pareto_obj)):
                solution_metadata.append({
                    'algorithm': algo_name,
                    'original_index': i
                })

        combined_objectives = np.vstack(all_objectives)
        combined_solutions = np.vstack(all_solutions)

        # Step 2: Find GLOBAL min and max across ALL solutions
        global_min = np.min(combined_objectives, axis=0)
        global_max = np.max(combined_objectives, axis=0)

        # Step 3: Normalize ALL solutions using GLOBAL min/max
        range_vals = global_max - global_min
        range_vals[range_vals == 0] = 1.0  # Avoid division by zero

        combined_normalized = (combined_objectives - global_min) / range_vals

        # Step 4: Calculate weighted scores for ALL solutions
        weighted_scores = (
            combined_normalized[:, 0] * self.preferences.cost_weight +
            combined_normalized[:, 1] * self.preferences.latency_weight +
            combined_normalized[:, 2] * self.preferences.performance_weight
        )

        # Step 5: Find top K solutions
        top_k_indices = np.argsort(weighted_scores)[:top_k]

        # Step 6: Extract top K solution information
        top_solutions = []
        algorithm_distribution = {}

        for rank, idx in enumerate(top_k_indices, 1):
            meta = solution_metadata[idx]
            algo_name = meta['algorithm']
            original_idx = meta['original_index']

            # Count algorithm distribution
            if algo_name not in algorithm_distribution:
                algorithm_distribution[algo_name] = 0
            algorithm_distribution[algo_name] += 1

            top_solutions.append({
                'rank': rank,
                'algorithm': algo_name,
                'original_index': original_idx,
                'solution': combined_solutions[idx],
                'objectives': combined_objectives[idx],
                'normalized': combined_normalized[idx],
                'weighted_score': weighted_scores[idx]
            })

        # Step 7: Determine best algorithm (most solutions in top K)
        best_algorithm = max(algorithm_distribution.items(),
                           key=lambda x: x[1])[0]

        # Step 8: Create analysis
        analysis = self._create_global_analysis(
            top_solutions, algorithm_distribution, best_algorithm,
            global_min, global_max, algorithm_results
        )

        return {
            'top_solutions': top_solutions,
            'global_min': global_min,
            'global_max': global_max,
            'algorithm_distribution': algorithm_distribution,
            'best_algorithm': best_algorithm,
            'analysis': analysis
        }

    def _create_global_analysis(self, top_solutions: List[Dict],
                                algorithm_distribution: Dict,
                                best_algorithm: str,
                                global_min: np.ndarray,
                                global_max: np.ndarray,
                                algorithm_results: Dict) -> str:
        """Create detailed analysis text for global normalization approach."""
        lines = []
        lines.append("=" * 70)
        lines.append("GLOBAL NORMALIZATION - TOP SOLUTIONS ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"User Preferences: {self.preferences}")
        lines.append("")

        # Global ranges
        lines.append("Global Objective Ranges (across all algorithms):")
        lines.append("-" * 70)
        lines.append(f"  Cost:        ${global_min[0]:.4f} - ${global_max[0]:.4f}/hour")
        lines.append(f"  Latency:     {global_min[1]:.2f} - {global_max[1]:.2f} ms")
        lines.append(f"  Performance: {-global_max[2]:.0f} - {-global_min[2]:.0f}")
        lines.append("")

        # Total solutions analyzed
        total_solutions = sum(len(r['pareto_objectives'])
                            for r in algorithm_results.values())
        lines.append(f"Total Solutions Analyzed: {total_solutions}")
        lines.append(f"Top Solutions Selected: {len(top_solutions)}")
        lines.append("")

        # Algorithm distribution
        lines.append("Algorithm Distribution in Top Solutions:")
        lines.append("-" * 70)
        sorted_dist = sorted(algorithm_distribution.items(),
                           key=lambda x: x[1], reverse=True)
        for algo_name, count in sorted_dist:
            percentage = (count / len(top_solutions)) * 100
            marker = "🏆" if algo_name == best_algorithm else "  "
            lines.append(f"{marker} {algo_name.upper():8s}: {count:2d} solutions "
                        f"({percentage:5.1f}%)")
        lines.append("")

        # Best algorithm
        lines.append("=" * 70)
        lines.append(f"BEST ALGORITHM: {best_algorithm.upper()}")
        lines.append("=" * 70)
        best_count = algorithm_distribution[best_algorithm]
        best_pct = (best_count / len(top_solutions)) * 100
        lines.append(f"{best_algorithm.upper()} contributed {best_count} out of "
                    f"{len(top_solutions)} top solutions ({best_pct:.1f}%)")
        lines.append("")

        # Top 3 recommendations
        lines.append("=" * 70)
        lines.append("TOP 3 RECOMMENDED SOLUTIONS")
        lines.append("=" * 70)
        lines.append("")

        for i in range(min(3, len(top_solutions))):
            sol = top_solutions[i]
            obj = sol['objectives']
            norm = sol['normalized']

            lines.append(f"Rank #{sol['rank']}: {sol['algorithm'].upper()} "
                        f"(Solution {sol['original_index']})")
            lines.append(f"  Cost:            ${obj[0]:.4f}/hour "
                        f"(normalized: {norm[0]:.3f}, weight: {self.preferences.cost_weight:.1%})")
            lines.append(f"  Latency:         {obj[1]:.2f} ms "
                        f"(normalized: {norm[1]:.3f}, weight: {self.preferences.latency_weight:.1%})")
            lines.append(f"  Performance:     {-obj[2]:.0f} "
                        f"(normalized: {norm[2]:.3f}, weight: {self.preferences.performance_weight:.1%})")
            lines.append(f"  Weighted Score:  {sol['weighted_score']:.4f} (lower is better)")
            lines.append("")

        lines.append("=" * 70)
        lines.append("Why Global Normalization?")
        lines.append("-" * 70)
        lines.append("This approach uses GLOBAL min/max values from all algorithms,")
        lines.append("ensuring fair comparison and preventing per-algorithm bias.")
        lines.append("Solutions are ranked purely on user preferences across the")
        lines.append("entire solution space, not within individual algorithm fronts.")
        lines.append("=" * 70)

        return "\n".join(lines)


def interactive_preference_input() -> UserPreferences:
    """
    Interactive command-line input for user preferences.

    Returns:
        UserPreferences object
    """
    print("\n" + "=" * 70)
    print("USER PREFERENCE INPUT")
    print("=" * 70)
    print("\nPlease specify the importance of each objective (as percentages).")
    print("The three values must sum to 100%.\n")

    while True:
        try:
            cost_pct = float(input("Cost importance (0-100): "))
            latency_pct = float(input("Latency importance (0-100): "))
            performance_pct = float(input("Performance importance (0-100): "))

            # Validate
            if any(x < 0 or x > 100 for x in [cost_pct, latency_pct, performance_pct]):
                print("❌ All values must be between 0 and 100. Please try again.\n")
                continue

            total = cost_pct + latency_pct + performance_pct
            if not np.isclose(total, 100.0):
                print(f"❌ Values must sum to 100, got {total}. Please try again.\n")
                continue

            # Create preferences
            prefs = UserPreferences.from_percentages(cost_pct, latency_pct, performance_pct)

            # Confirm
            print(f"\nPreferences set: {prefs}")
            confirm = input("Confirm? (y/n): ").lower().strip()
            if confirm in ['y', 'yes']:
                return prefs
            else:
                print("\nLet's try again...\n")

        except ValueError as e:
            print(f"❌ Invalid input: {e}. Please try again.\n")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user.")
            exit(1)
