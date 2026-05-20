"""User preference handling and algorithm selection."""

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


class AlgorithmSelector:
    """Select best algorithm based on user preferences."""

    def __init__(self, preferences: UserPreferences):
        """
        Initialize algorithm selector.

        Args:
            preferences: User preferences for objectives
        """
        self.preferences = preferences

    def normalize_objectives(self, objectives: np.ndarray) -> np.ndarray:
        """
        Normalize objectives to [0, 1] range using min-max normalization.

        Args:
            objectives: Array of shape (n_solutions, 3) with [cost, latency, -performance]

        Returns:
            Normalized objectives in [0, 1] range
        """
        normalized = np.zeros_like(objectives, dtype=float)

        for i in range(objectives.shape[1]):
            min_val = np.min(objectives[:, i])
            max_val = np.max(objectives[:, i])

            if np.isclose(min_val, max_val):
                # All values are the same, set to 0.5
                normalized[:, i] = 0.5
            else:
                # Min-max normalization
                normalized[:, i] = (objectives[:, i] - min_val) / (max_val - min_val)

        return normalized

    def calculate_weighted_score(self, objectives: np.ndarray) -> float:
        """
        Calculate weighted score for a set of objectives.

        Lower is better (minimization).

        Args:
            objectives: Pareto objectives array (n_solutions, 3)
                       [cost, latency, -performance]

        Returns:
            Weighted score (lower is better)
        """
        # Normalize objectives to [0, 1]
        normalized = self.normalize_objectives(objectives)

        # For each solution, calculate weighted sum
        weighted_scores = (
            normalized[:, 0] * self.preferences.cost_weight +      # cost (minimize)
            normalized[:, 1] * self.preferences.latency_weight +   # latency (minimize)
            normalized[:, 2] * self.preferences.performance_weight # -performance (minimize, so actually maximizing performance)
        )

        # Return average weighted score across all Pareto solutions
        return np.mean(weighted_scores)

    def find_best_solution(self, objectives: np.ndarray) -> Tuple[int, float]:
        """
        Find the best solution from Pareto front based on user preferences.

        Args:
            objectives: Pareto objectives array (n_solutions, 3)

        Returns:
            (best_index, best_score) where best_index is the index of best solution
        """
        # Normalize objectives
        normalized = self.normalize_objectives(objectives)

        # Calculate weighted score for each solution
        scores = (
            normalized[:, 0] * self.preferences.cost_weight +
            normalized[:, 1] * self.preferences.latency_weight +
            normalized[:, 2] * self.preferences.performance_weight
        )

        # Find best (minimum) score
        best_idx = np.argmin(scores)
        best_score = scores[best_idx]

        return best_idx, best_score

    def select_best_algorithm(self, algorithm_results: Dict[str, Dict]) -> Dict:
        """
        Select the best algorithm based on user preferences.

        Args:
            algorithm_results: Dictionary mapping algorithm name to results
                              Each result should have 'pareto_objectives' key

        Returns:
            Dictionary with:
                - 'best_algorithm': Name of best algorithm
                - 'scores': Dictionary of algorithm scores
                - 'rankings': Dictionary of algorithm rankings
                - 'best_solution': Best solution from best algorithm
                - 'analysis': Detailed analysis
        """
        scores = {}

        # Calculate weighted score for each algorithm
        for algo_name, results in algorithm_results.items():
            pareto_objectives = results['pareto_objectives']
            scores[algo_name] = self.calculate_weighted_score(pareto_objectives)

        # Rank algorithms (lower score is better)
        rankings = {}
        sorted_algos = sorted(scores.items(), key=lambda x: x[1])
        for rank, (algo_name, score) in enumerate(sorted_algos, 1):
            rankings[algo_name] = rank

        # Best algorithm has lowest score
        best_algorithm = sorted_algos[0][0]
        best_algo_results = algorithm_results[best_algorithm]

        # Find best solution from best algorithm
        best_sol_idx, best_sol_score = self.find_best_solution(
            best_algo_results['pareto_objectives']
        )

        # Create analysis
        analysis = self._create_analysis(
            algorithm_results, scores, rankings, best_algorithm,
            best_sol_idx, best_sol_score
        )

        return {
            'best_algorithm': best_algorithm,
            'scores': scores,
            'rankings': rankings,
            'best_solution_index': best_sol_idx,
            'best_solution_score': best_sol_score,
            'analysis': analysis
        }

    def _create_analysis(self, algorithm_results: Dict, scores: Dict,
                        rankings: Dict, best_algorithm: str,
                        best_sol_idx: int, best_sol_score: float) -> str:
        """Create detailed analysis text."""
        lines = []
        lines.append("=" * 70)
        lines.append("ALGORITHM SELECTION BASED ON USER PREFERENCES")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"User Preferences: {self.preferences}")
        lines.append("")
        lines.append("Algorithm Performance Scores (lower is better):")
        lines.append("-" * 70)

        # Show scores in ranked order
        sorted_algos = sorted(scores.items(), key=lambda x: x[1])
        for rank, (algo_name, score) in enumerate(sorted_algos, 1):
            pareto_size = len(algorithm_results[algo_name]['pareto_objectives'])
            marker = "🏆" if algo_name == best_algorithm else "  "
            lines.append(f"{marker} #{rank} {algo_name.upper():8s} - Score: {score:.4f} "
                        f"(Pareto size: {pareto_size})")

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"RECOMMENDED ALGORITHM: {best_algorithm.upper()}")
        lines.append("=" * 70)
        lines.append("")

        # Get best solution details
        best_objectives = algorithm_results[best_algorithm]['pareto_objectives'][best_sol_idx]
        cost = best_objectives[0]
        latency = best_objectives[1]
        performance = -best_objectives[2]  # Convert back to positive

        lines.append(f"Best Solution from {best_algorithm.upper()} (index {best_sol_idx}):")
        lines.append(f"  Cost:        ${cost:.4f}/hour (weight: {self.preferences.cost_weight:.1%})")
        lines.append(f"  Latency:     {latency:.2f} ms (weight: {self.preferences.latency_weight:.1%})")
        lines.append(f"  Performance: {performance:.0f} (weight: {self.preferences.performance_weight:.1%})")
        lines.append(f"  Weighted Score: {best_sol_score:.4f}")
        lines.append("")

        # Show why this algorithm is best
        lines.append("Why this algorithm?")
        lines.append("-" * 70)

        best_score = scores[best_algorithm]
        score_diffs = {
            algo: ((score - best_score) / best_score * 100)
            for algo, score in scores.items()
            if algo != best_algorithm
        }

        if score_diffs:
            lines.append(f"{best_algorithm.upper()} achieved the lowest weighted score based on")
            lines.append(f"your preferences. It performs better than:")
            for algo, diff in sorted(score_diffs.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  - {algo.upper()}: {diff:.1f}% better")

        lines.append("")
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
