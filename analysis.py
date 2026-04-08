"""
Genre analysis: metrics, clustering, distance calculation, and tree construction.
"""

import numpy as np
import pandas as pd
from collections import defaultdict
import logging

logger = logging.getLogger("GenreAnalysis")


class Node:
    """Node for phylogenetic tree construction."""

    def __init__(self, name, branch_length=0.0):
        self.name = name
        self.children = []
        self.branch_length = branch_length
        self.height = 0.0


def create_distance_matrix(genre_data):
    """
    Create a full distance matrix from the genre database.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        Tuple of (sorted genre names list, numpy distance matrix).
    """
    genres = sorted(list(genre_data.keys()))
    n = len(genres)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            g1, g2 = genres[i], genres[j]

            # Time distance
            time_dist = abs(genre_data[g1]["date"] - genre_data[g2]["date"]) / 1000.0

            # Parent similarity
            parents1 = set(genre_data[g1]["parents"])
            parents2 = set(genre_data[g2]["parents"])
            parent_dist = 1.0
            if parents1 and parents2:
                shared = len(parents1 & parents2)
                total = len(parents1 | parents2)
                if total > 0:
                    parent_dist = 1.0 - (shared / total)

            # Characteristic similarity
            char1 = set(genre_data[g1]["characteristics"])
            char2 = set(genre_data[g2]["characteristics"])
            char_dist = 1.0
            if char1 and char2:
                shared = len(char1 & char2)
                total = len(char1 | char2)
                if total > 0:
                    char_dist = 1.0 - (shared / total)

            # Combine distances
            dist = float((0.4 * time_dist) + (0.3 * parent_dist) + (0.3 * char_dist))
            matrix[i, j] = dist
            matrix[j, i] = dist

    return genres, matrix


def _find_min_pair(matrix):
    """Find the closest pair of clusters in a distance matrix."""
    n = matrix.shape[0]
    min_dist = float("inf")
    min_i, min_j = -1, -1

    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] < min_dist:
                min_dist = matrix[i, j]
                min_i, min_j = i, j

    return min_i, min_j, min_dist


def _update_matrix(old_matrix, i, j):
    """Create new matrix after merging clusters i and j (UPGMA)."""
    n = old_matrix.shape[0]
    new_size = n - 1
    new_matrix = np.zeros((new_size, new_size))

    new_to_old = [k for k in range(n) if k != j]

    for new_i in range(new_size):
        for new_j in range(new_i + 1, new_size):
            old_i = new_to_old[new_i]
            old_j = new_to_old[new_j]

            if old_i == i:
                dist = (old_matrix[i, old_j] + old_matrix[j, old_j]) / 2.0
            elif old_j == i:
                dist = (old_matrix[old_i, i] + old_matrix[old_i, j]) / 2.0
            else:
                dist = old_matrix[old_i, old_j]

            new_matrix[new_i, new_j] = dist
            new_matrix[new_j, new_i] = dist

    return new_matrix


def create_phylogenetic_tree(genre_data):
    """
    Build a UPGMA tree from genre data.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        Root Node of the constructed tree.
    """
    genres, matrix = create_distance_matrix(genre_data)
    nodes = [Node(name) for name in genres]

    while len(nodes) > 1:
        i, j, dist = _find_min_pair(matrix)

        new_node = Node(f"Internal_{len(nodes)}")
        branch_length = dist / 2.0
        nodes[i].branch_length = branch_length - nodes[i].height
        nodes[j].branch_length = branch_length - nodes[j].height

        new_node.children = [nodes[i], nodes[j]]
        new_node.height = branch_length

        nodes.pop(j)
        nodes.pop(i)
        nodes.append(new_node)
        matrix = _update_matrix(matrix, i, j)

    return nodes[0]


def analyze_genre_metrics(genre_data):
    """
    Calculate various metrics about genre evolution.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        Dictionary of metrics.
    """
    return {
        "total_genres": len(genre_data),
        "avg_parents": np.mean(
            [len(data["parents"]) for data in genre_data.values()]
        ),
        "hybrid_genres": [
            genre
            for genre, data in genre_data.items()
            if len(data["parents"]) > 1
        ],
        "major_emergence_periods": _identify_emergence_periods(genre_data),
        "most_influential": _identify_influential_genres(genre_data),
    }


def _identify_emergence_periods(genre_data):
    """Identify major periods of genre emergence."""
    dates = [data["date"] for data in genre_data.values()]
    df = pd.DataFrame(dates, columns=["date"])
    return df.groupby(pd.cut(df["date"], bins=5)).count().to_dict()


def _identify_influential_genres(genre_data):
    """Identify genres that influenced the most other genres."""
    influence_count = defaultdict(int)
    for data in genre_data.values():
        for parent in data["parents"]:
            influence_count[parent] += 1
    return dict(sorted(influence_count.items(), key=lambda x: x[1], reverse=True))


def analyze_genre_characteristics(genre_data):
    """
    Analyze the evolution of genre characteristics over time.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        Dictionary with most_common, earliest, and modern_trends.
    """
    return {
        "most_common": _most_common_characteristics(genre_data),
        "earliest": _earliest_characteristics(genre_data),
        "modern_trends": _modern_characteristics(genre_data),
    }


def _most_common_characteristics(genre_data):
    """Identify most common characteristics across genres."""
    char_count = defaultdict(int)
    for data in genre_data.values():
        for char in data["characteristics"]:
            char_count[char] += 1
    return dict(sorted(char_count.items(), key=lambda x: x[1], reverse=True)[:10])


def _earliest_characteristics(genre_data):
    """Identify earliest appearing characteristics."""
    char_dates = defaultdict(list)
    for data in genre_data.values():
        for char in data["characteristics"]:
            char_dates[char].append(data["date"])
    return {char: min(dates) for char, dates in char_dates.items()}


def _modern_characteristics(genre_data):
    """Identify characteristics common in modern genres (post-2000)."""
    modern_chars = defaultdict(int)
    for data in genre_data.values():
        if data["date"] >= 2000:
            for char in data["characteristics"]:
                modern_chars[char] += 1
    return dict(sorted(modern_chars.items(), key=lambda x: x[1], reverse=True)[:10])
