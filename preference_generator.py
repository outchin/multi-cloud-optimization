"""
User Preference Generator for Comprehensive Testing
Generates various user preference combinations.
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict
import itertools


class PreferenceGenerator:
    """Generate user preference combinations for testing."""

    # Predefined preference profiles
    PRESET_PROFILES = {
        'cost_focused': (60, 30, 10),      # Cost, Latency, Performance
        'latency_focused': (10, 60, 30),
        'performance_focused': (10, 30, 60),
        'balanced': (33, 33, 34),
        'cost_latency': (50, 50, 0),
        'cost_performance': (50, 0, 50),
        'latency_performance': (0, 50, 50),
        'extreme_cost': (80, 15, 5),
        'extreme_latency': (5, 80, 15),
        'extreme_performance': (5, 15, 80),
    }

    def __init__(self):
        """Initialize preference generator."""
        self.generated_preferences = []

    @staticmethod
    def validate_preference(cost_pct: float, latency_pct: float,
                          performance_pct: float) -> bool:
        """
        Validate that preference percentages sum to 100.

        Args:
            cost_pct: Cost percentage (0-100)
            latency_pct: Latency percentage (0-100)
            performance_pct: Performance percentage (0-100)

        Returns:
            True if valid, False otherwise
        """
        total = cost_pct + latency_pct + performance_pct
        return abs(total - 100.0) < 0.01

    def generate_systematic_preferences(self, step: int = 10) -> List[Tuple[int, int, int]]:
        """
        Generate systematic preference combinations.

        Args:
            step: Step size for percentage variations (default: 10)

        Returns:
            List of (cost_pct, latency_pct, performance_pct) tuples
        """
        preferences = []

        # Generate all combinations where percentages sum to 100
        for cost_pct in range(0, 101, step):
            for latency_pct in range(0, 101, step):
                performance_pct = 100 - cost_pct - latency_pct
                if 0 <= performance_pct <= 100:
                    preferences.append((cost_pct, latency_pct, performance_pct))

        return preferences

    def generate_focused_preferences(self, primary_range: Tuple[int, int],
                                    secondary_step: int = 10) -> List[Tuple[int, int, int]]:
        """
        Generate preferences with one dominant objective.

        Args:
            primary_range: Range for primary objective (min_pct, max_pct)
            secondary_step: Step size for secondary objectives

        Returns:
            List of preference tuples
        """
        preferences = []
        min_pct, max_pct = primary_range

        # Cost-focused
        for cost_pct in range(min_pct, max_pct + 1, secondary_step):
            for latency_pct in range(0, 101 - cost_pct, secondary_step):
                performance_pct = 100 - cost_pct - latency_pct
                if performance_pct >= 0:
                    preferences.append((cost_pct, latency_pct, performance_pct))

        # Latency-focused
        for latency_pct in range(min_pct, max_pct + 1, secondary_step):
            for cost_pct in range(0, 101 - latency_pct, secondary_step):
                performance_pct = 100 - cost_pct - latency_pct
                if performance_pct >= 0:
                    preferences.append((cost_pct, latency_pct, performance_pct))

        # Performance-focused
        for performance_pct in range(min_pct, max_pct + 1, secondary_step):
            for cost_pct in range(0, 101 - performance_pct, secondary_step):
                latency_pct = 100 - cost_pct - performance_pct
                if latency_pct >= 0:
                    preferences.append((cost_pct, latency_pct, performance_pct))

        # Remove duplicates
        preferences = list(set(preferences))
        return preferences

    def generate_preset_profiles(self) -> List[Tuple[str, Tuple[int, int, int]]]:
        """
        Generate predefined preference profiles.

        Returns:
            List of (profile_name, (cost_pct, latency_pct, performance_pct)) tuples
        """
        return [(name, prefs) for name, prefs in self.PRESET_PROFILES.items()]

    def generate_diverse_preferences(self, count: int = 50) -> List[Tuple[int, int, int]]:
        """
        Generate diverse preference combinations using strategic sampling.

        Args:
            count: Target number of diverse preferences

        Returns:
            List of preference tuples
        """
        import random
        random.seed(42)  # For reproducibility

        preferences = set()

        # Add preset profiles first
        for _, prefs in self.PRESET_PROFILES.items():
            preferences.add(prefs)

        # Add corner cases
        corners = [
            (100, 0, 0), (0, 100, 0), (0, 0, 100),  # Single objective
            (50, 50, 0), (50, 0, 50), (0, 50, 50),  # Two objectives
            (33, 33, 34),  # Balanced
        ]
        preferences.update(corners)

        # Add systematic grid (step = 20)
        for cost in range(0, 101, 20):
            for latency in range(0, 101, 20):
                perf = 100 - cost - latency
                if 0 <= perf <= 100:
                    preferences.add((cost, latency, perf))

        # Add random samples to reach target count
        while len(preferences) < count:
            cost = random.randint(0, 100)
            latency = random.randint(0, 100 - cost)
            perf = 100 - cost - latency
            if perf >= 0:
                preferences.add((cost, latency, perf))

        return sorted(list(preferences))

    def save_preferences_to_file(self, preferences: List[Tuple[int, int, int]],
                                output_path: str):
        """
        Save preference combinations to JSON file.

        Args:
            preferences: List of preference tuples
            output_path: Output file path
        """
        pref_list = []
        for i, (cost, lat, perf) in enumerate(preferences, 1):
            pref_list.append({
                'preference_id': i,
                'cost_weight': cost,
                'latency_weight': lat,
                'performance_weight': perf,
                'profile': self._classify_profile(cost, lat, perf)
            })

        output = {
            'total_preferences': len(pref_list),
            'preferences': pref_list
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Saved {len(pref_list)} preferences to {output_path}")

    def _classify_profile(self, cost: int, lat: int, perf: int) -> str:
        """
        Classify preference into a profile category.

        Args:
            cost, lat, perf: Preference percentages

        Returns:
            Profile category name
        """
        max_val = max(cost, lat, perf)

        if max_val >= 60:
            if cost == max_val:
                return 'cost_focused'
            elif lat == max_val:
                return 'latency_focused'
            else:
                return 'performance_focused'
        elif abs(cost - lat) <= 10 and abs(lat - perf) <= 10:
            return 'balanced'
        elif cost >= 40 and lat >= 40:
            return 'cost_latency'
        elif cost >= 40 and perf >= 40:
            return 'cost_performance'
        elif lat >= 40 and perf >= 40:
            return 'latency_performance'
        else:
            return 'mixed'

    def generate_and_save_comprehensive_set(self, output_dir: str = 'test_preferences',
                                           mode: str = 'diverse',
                                           count: int = 50) -> str:
        """
        Generate and save comprehensive preference set.

        Args:
            output_dir: Output directory
            mode: Generation mode ('diverse', 'systematic', 'preset')
            count: Target count for diverse mode

        Returns:
            Path to generated file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if mode == 'diverse':
            preferences = self.generate_diverse_preferences(count)
            filename = f'preferences_diverse_{count}.json'
        elif mode == 'systematic':
            preferences = self.generate_systematic_preferences(step=10)
            filename = 'preferences_systematic_step10.json'
        elif mode == 'preset':
            preset_list = self.generate_preset_profiles()
            preferences = [prefs for _, prefs in preset_list]
            filename = 'preferences_preset.json'
        else:
            raise ValueError(f"Unknown mode: {mode}")

        filepath = output_path / filename
        self.save_preferences_to_file(preferences, str(filepath))

        self.generated_preferences = preferences

        # Generate summary
        summary_path = output_path / f"preference_summary_{mode}.txt"
        with open(summary_path, 'w') as f:
            f.write("PREFERENCE GENERATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Mode: {mode}\n")
            f.write(f"Total preferences: {len(preferences)}\n\n")

            # Count by profile
            profiles = {}
            for pref in preferences:
                profile = self._classify_profile(*pref)
                profiles[profile] = profiles.get(profile, 0) + 1

            f.write("Distribution by profile:\n")
            for profile, count in sorted(profiles.items()):
                f.write(f"  {profile:20s}: {count:3d}\n")

            f.write("\nSample preferences:\n")
            for i, (cost, lat, perf) in enumerate(preferences[:10], 1):
                profile = self._classify_profile(cost, lat, perf)
                f.write(f"  {i:2d}. Cost:{cost:3d}% Lat:{lat:3d}% Perf:{perf:3d}%  ({profile})\n")

        print(f"Summary saved to: {summary_path}")

        return str(filepath)


def main():
    """Generate test preferences."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate user preference combinations')
    parser.add_argument('--output-dir', default='test_preferences',
                       help='Output directory')
    parser.add_argument('--mode', default='diverse',
                       choices=['diverse', 'systematic', 'preset'],
                       help='Generation mode')
    parser.add_argument('--count', type=int, default=50,
                       help='Number of preferences (for diverse mode)')

    args = parser.parse_args()

    generator = PreferenceGenerator()
    generator.generate_and_save_comprehensive_set(
        output_dir=args.output_dir,
        mode=args.mode,
        count=args.count
    )


if __name__ == '__main__':
    main()
