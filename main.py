#!/usr/bin/env python3
"""
Literary Genre Evolution Analyzer - CLI entry point.

Loads genre data, generates visualizations, and prints analysis results.
"""

import sys
import logging

from genre_database import load_genre_data, validate_parent_references
from analysis import (
    create_phylogenetic_tree,
    analyze_genre_metrics,
    analyze_genre_characteristics,
)

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GenreEvolution")


def main():
    """Run the full genre evolution analysis pipeline."""
    # Load genre data from JSON
    genre_data = load_genre_data()

    # Validate parent references
    dangling = validate_parent_references(genre_data)
    if dangling:
        logger.warning(f"Found {len(dangling)} dangling parent references")

    # Try to generate visualizations (requires networkx + matplotlib)
    try:
        from visualization import (
            create_timeline_graph,
            plot_timeline_graph,
            plot_phylogenetic_tree,
        )

        # Timeline graph
        G, pos = create_timeline_graph(genre_data)
        timeline_plt = plot_timeline_graph(G, pos, genre_data)
        timeline_plt.savefig("genre_timeline.png", bbox_inches="tight", dpi=300)
        logger.info("Saved genre_timeline.png")

        # Phylogenetic tree
        tree = create_phylogenetic_tree(genre_data)
        tree_plt = plot_phylogenetic_tree(tree, genre_data)
        tree_plt.savefig("genre_phylogeny.png", bbox_inches="tight", dpi=300)
        logger.info("Saved genre_phylogeny.png")

    except ImportError as e:
        logger.warning(f"Visualization skipped (missing dependency): {e}")
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")

    # Analyze metrics and characteristics
    metrics = analyze_genre_metrics(genre_data)
    char_analysis = analyze_genre_characteristics(genre_data)

    # Print results
    print(f"\nGenre Evolution Analysis:")
    print(f"\nTotal number of genres: {metrics['total_genres']}")
    print(f"Average number of parent genres: {metrics['avg_parents']:.2f}")

    print("\nMost Common Characteristics:")
    for char, count in char_analysis["most_common"].items():
        print(f"- {char}: {count} genres")

    print("\nEarliest Genre Characteristics:")
    earliest = sorted(char_analysis["earliest"].items(), key=lambda x: x[1])
    for char, date in earliest[:10]:
        print(f"- {char}: {date} BCE/CE")

    print("\nMost Common Modern Characteristics (post-2000):")
    for char, count in char_analysis["modern_trends"].items():
        print(f"- {char}: {count} genres")


if __name__ == "__main__":
    main()
