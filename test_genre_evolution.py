#!/usr/bin/env python3
"""
Test suite for the Literary Genre Evolution Analyzer.
Covers data loading, distance calculation, tree construction, and metric analysis.
"""

import unittest
import os
import sys
import json
import tempfile

# Ensure project root is on path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from genre_database import load_genre_data, validate_parent_references
from analysis import (
    create_distance_matrix,
    create_phylogenetic_tree,
    analyze_genre_metrics,
    analyze_genre_characteristics,
    Node,
)


class TestGenreDatabase(unittest.TestCase):
    """Tests for genre_database.py."""

    def test_load_genre_data(self):
        """Genre data loads and contains expected keys."""
        data = load_genre_data()
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 50)
        # Spot-check a well-known genre
        self.assertIn("Science Fiction", data)
        self.assertIn("date", data["Science Fiction"])
        self.assertIn("parents", data["Science Fiction"])
        self.assertIn("characteristics", data["Science Fiction"])

    def test_load_from_custom_path(self):
        """Loading from a custom JSON path works."""
        sample = {"TestGenre": {"date": 2000, "parents": [], "characteristics": ["test"]}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample, f)
            tmppath = f.name
        try:
            data = load_genre_data(tmppath)
            self.assertIn("TestGenre", data)
        finally:
            os.unlink(tmppath)

    def test_validate_parent_references_clean(self):
        """Default data should have no dangling parent references."""
        data = load_genre_data()
        dangling = validate_parent_references(data)
        self.assertEqual(dangling, [], f"Dangling refs found: {dangling}")

    def test_validate_detects_missing_parent(self):
        """Validator catches references to non-existent parents."""
        data = {"A": {"date": 2000, "parents": ["NonExistent"], "characteristics": []}}
        dangling = validate_parent_references(data)
        self.assertEqual(len(dangling), 1)
        self.assertEqual(dangling[0], ("A", "NonExistent"))


class TestDistanceMatrix(unittest.TestCase):
    """Tests for distance matrix construction."""

    def test_distance_matrix_shape(self):
        """Matrix should be square with size = number of genres."""
        data = load_genre_data()
        genres, matrix = create_distance_matrix(data)
        n = len(genres)
        self.assertEqual(matrix.shape, (n, n))

    def test_distance_matrix_symmetric(self):
        """Distance matrix should be symmetric."""
        data = load_genre_data()
        _, matrix = create_distance_matrix(data)
        self.assertTrue((matrix == matrix.T).all())

    def test_distance_matrix_zero_diagonal(self):
        """Diagonal should be all zeros."""
        data = load_genre_data()
        _, matrix = create_distance_matrix(data)
        for i in range(matrix.shape[0]):
            self.assertAlmostEqual(matrix[i, i], 0.0)

    def test_distance_matrix_nonnegative(self):
        """All distances should be non-negative."""
        data = load_genre_data()
        _, matrix = create_distance_matrix(data)
        self.assertTrue((matrix >= 0).all())


class TestPhylogeneticTree(unittest.TestCase):
    """Tests for tree construction."""

    def test_tree_builds_without_error(self):
        """Tree construction completes on a small subset."""
        small_data = {
            "A": {"date": 1800, "parents": [], "characteristics": ["x", "y"]},
            "B": {"date": 1900, "parents": ["A"], "characteristics": ["y", "z"]},
            "C": {"date": 2000, "parents": ["A"], "characteristics": ["x", "z"]},
        }
        root = create_phylogenetic_tree(small_data)
        self.assertIsInstance(root, Node)
        # Root should have children
        self.assertGreater(len(root.children), 0)

    def test_node_attributes(self):
        """Node has expected attributes."""
        node = Node("test", branch_length=1.5)
        self.assertEqual(node.name, "test")
        self.assertEqual(node.branch_length, 1.5)
        self.assertEqual(node.children, [])


class TestMetrics(unittest.TestCase):
    """Tests for metric analysis."""

    def test_genre_metrics(self):
        """analyze_genre_metrics returns expected keys."""
        data = load_genre_data()
        metrics = analyze_genre_metrics(data)
        self.assertIn("total_genres", metrics)
        self.assertIn("avg_parents", metrics)
        self.assertIn("hybrid_genres", metrics)
        self.assertIn("most_influential", metrics)
        self.assertEqual(metrics["total_genres"], len(data))

    def test_characteristic_analysis(self):
        """analyze_genre_characteristics returns expected keys."""
        data = load_genre_data()
        char_analysis = analyze_genre_characteristics(data)
        self.assertIn("most_common", char_analysis)
        self.assertIn("earliest", char_analysis)
        self.assertIn("modern_trends", char_analysis)
        self.assertGreater(len(char_analysis["most_common"]), 0)

    def test_hybrid_genres_have_multiple_parents(self):
        """All hybrid genres should have > 1 parent."""
        data = load_genre_data()
        metrics = analyze_genre_metrics(data)
        for genre in metrics["hybrid_genres"]:
            self.assertGreater(len(data[genre]["parents"]), 1)


if __name__ == "__main__":
    unittest.main()
