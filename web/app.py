"""FastAPI web app for Genre Phylogeny: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8170, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
The tree and distances are also computed in the browser by static/genre_engine.js (a port of analysis.py, node-tested
against it), so the static site can rebuild the tree with other weights.
"""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web import data  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Genre Phylogeny")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    g = data.genres()
    traits = {c for x in g for c in x["characteristics"]}
    return {
        "title": "Genre Phylogeny", "genres": len(g), "traits": len(traits),
        "shared_traits": sum(1 for t in traits if sum(t in x["characteristics"] for x in g) > 1),
        "roots": sum(1 for x in g if not x["parents"]), "hybrids": sum(1 for x in g if len(x["parents"]) > 1),
        "guides": len(data.guide_slugs()), "earliest": min(x["date"] for x in g), "latest": max(x["date"] for x in g),
    }


@app.get("/api/genres")
def genres():
    """Every genre: date, parents, characteristics, children and guide link."""
    return data.genres()


@app.get("/api/analysis")
def analysis():
    """analysis.py metrics and characteristic trends."""
    return data.analysis_summary()


@app.get("/api/tree")
def tree(w_time: float = Query(0.4, ge=0), w_parent: float = Query(0.3, ge=0), w_char: float = Query(0.3, ge=0)):
    """The tree from analysis.create_phylogenetic_tree with the given distance weights (default: the repo's)."""
    return data.tree_dict((w_time, w_parent, w_char))


@app.get("/api/guides")
def guides():
    """The writing guides in guides/ (title, word count, linked genres)."""
    return data.guides()


@app.get("/api/guides/{slug}")
def guide(slug: str):
    """One guide's Markdown."""
    g = data.guide(slug)
    if g is None:
        raise HTTPException(404, f"no guide {slug!r}")
    return g


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/genres", "/analysis", "/tree", "/guides"] + [f"/guides/{s}" for s in data.guide_slugs()]
