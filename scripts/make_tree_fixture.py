"""Write tests/fixtures/genre_tree.json: distances and trees from analysis.py, for the JS engine test.

genre_engine.test.mjs rebuilds the same matrix and trees from genre_data.json in node and compares them;
tests/test_tree_fixture.py checks that this fixture still matches the Python code.

Run: python scripts/make_tree_fixture.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from analysis import build_upgma_tree, create_distance_matrix, create_phylogenetic_tree  # noqa: E402
from genre_database import load_genre_data  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "genre_tree.json"
WEIGHT_SETS = [(0.4, 0.3, 0.3), (1.0, 0.0, 0.0), (0.1, 0.2, 0.7)]
SMALL = {  # the regression case from test_merged_cluster_keeps_matrix_row
    "A": {"date": 1800, "parents": [], "characteristics": ["x", "y"]},
    "D": {"date": 1810, "parents": [], "characteristics": ["x", "y"]},
    "B": {"date": 2000, "parents": [], "characteristics": ["p", "q"]},
    "C": {"date": 2005, "parents": [], "characteristics": ["p", "q"]},
}
HAND = [[0, 2, 4, 10], [2, 0, 4, 10], [4, 4, 0, 6], [10, 10, 6, 0]]  # test_upgma_hand_worked


def node_dict(n):
    out = {"name": n.name, "branch_length": n.branch_length, "height": n.height}
    if n.children:
        out["children"] = [node_dict(c) for c in n.children]
    return out


def make():
    data = load_genre_data()
    names, matrix = create_distance_matrix(data)
    n = len(names)
    return {
        "names": names,
        "condensed": [float(matrix[i, j]) for i in range(n) for j in range(i + 1, n)],
        "trees": [{"weights": list(w), "tree": node_dict(create_phylogenetic_tree(data, w))} for w in WEIGHT_SETS],
        "small": {"data": SMALL, "tree": node_dict(create_phylogenetic_tree(SMALL))},
        "upgma_hand": {"matrix": HAND, "tree": node_dict(build_upgma_tree(list("ABCD"), np.array(HAND, float)))},
    }


if __name__ == "__main__":
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(make(), separators=(",", ":")))
    print(f"wrote {FIXTURE} ({FIXTURE.stat().st_size / 1e3:.0f} kB)")
