"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -------------------------------------------------------------------------------------------
import json  # noqa: E402

from analysis import create_phylogenetic_tree  # noqa: E402
from genre_database import load_genre_data  # noqa: E402


def test_info_counts_match_data():
    data = load_genre_data()
    s = client.get("/api/info").json()
    assert s["genres"] == len(data)
    assert s["traits"] == len({c for g in data.values() for c in g["characteristics"]})
    assert s["guides"] == len(list((ROOT / "guides").glob("*-guide.md")))


def test_genres_are_the_data_unchanged():
    data = load_genre_data()
    rows = client.get("/api/genres").json()
    assert [r["name"] for r in rows] == sorted(data)
    for r in rows:
        d = data[r["name"]]
        assert (r["date"], r["parents"], r["characteristics"]) == (d["date"], d["parents"], d["characteristics"])
        for c in r["children"]:
            assert r["name"] in data[c]["parents"]
        if r["guide"]:
            assert (ROOT / "guides" / f"{r['guide']}-guide.md").exists()


def _leaves(n):
    return [n["name"]] if "children" not in n else [x for c in n["children"] for x in _leaves(c)]


def test_tree_endpoint_is_the_python_tree():
    t = client.get("/api/tree").json()
    assert sorted(_leaves(t)) == sorted(load_genre_data())
    assert t["height"] == create_phylogenetic_tree(load_genre_data()).height
    t2 = client.get("/api/tree?w_time=1&w_parent=0&w_char=0").json()
    assert t2["height"] != t["height"]
    assert client.get("/api/tree?w_time=-1").status_code == 422


def test_guides():
    gs = client.get("/api/guides").json()
    assert gs and all(g["words"] > 100 for g in gs)
    g = client.get("/api/guides/mystery").json()
    assert g["markdown"].startswith("# ")
    assert client.get("/api/guides/nope").status_code == 404
    assert client.get("/api/guides/..%2FREADME").status_code == 404


def test_analysis_is_json_of_python_metrics():
    a = client.get("/api/analysis").json()
    assert a["total_genres"] == len(load_genre_data())
    assert sum(p["count"] for p in a["emergence_periods"]) == a["total_genres"]
    assert a["dangling_parents"] == []


def test_tree_fixture_is_current():
    """tests/fixtures/genre_tree.json (used by the node test) still matches analysis.py (rtol 1e-9)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_tree_fixture
    fresh = make_tree_fixture.make()
    saved = json.loads(make_tree_fixture.FIXTURE.read_text())
    assert saved["names"] == fresh["names"]
    assert saved["condensed"] == pytest.approx(fresh["condensed"], rel=1e-9, abs=1e-12)

    def same(a, b):
        assert a["name"] == b["name"]
        assert a["branch_length"] == pytest.approx(b["branch_length"], rel=1e-9, abs=1e-12)
        assert ("children" in a) == ("children" in b)
        for x, y in zip(a.get("children", []), b.get("children", [])):
            same(x, y)
    for s, f in zip(saved["trees"], fresh["trees"]):
        same(s["tree"], f["tree"])
    same(saved["small"]["tree"], fresh["small"]["tree"])
    same(saved["upgma_hand"]["tree"], fresh["upgma_hand"]["tree"])
