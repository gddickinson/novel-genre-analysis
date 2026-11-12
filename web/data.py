"""Data for the web API, built from the repo's own code and files (nothing here adds genre facts).

- genres(): genre_data.json via genre_database.load_genre_data, as a sorted list with children and guide links.
- tree_dict(): analysis.create_phylogenetic_tree as nested JSON.
- analysis_summary(): analysis.analyze_genre_metrics / analyze_genre_characteristics made JSON-safe.
- guides() / guide(slug): the committed Markdown writing guides in guides/.
"""
import re
from functools import lru_cache
from pathlib import Path

from analysis import (
    DEFAULT_WEIGHTS,
    analyze_genre_characteristics,
    analyze_genre_metrics,
    create_phylogenetic_tree,
)
from genre_database import load_genre_data, validate_parent_references

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

# Navigation links from a guide to genre entries of exactly the same name in genre_data.json (both spellings of
# climate fiction exist in the data). Guides with no same-named genre entry are not linked.
GUIDE_GENRES = {
    "adventure": ["Adventure Fiction"], "climate-fiction": ["Climate Fiction", "Cli-Fi"],
    "cozy-mystery": ["Cozy Mystery"], "crime-fiction": ["Crime Fiction"], "fantasy": ["Fantasy"],
    "gothic-fiction": ["Gothic Fiction"], "historical-fiction": ["Historical Fiction"], "horror": ["Horror"],
    "literary-fiction": ["Literary Fiction"], "magical-realism": ["Magical Realism"], "mystery": ["Mystery"],
    "new-weird": ["New Weird"], "noir-hardboiled": ["Noir"], "romance": ["Romance"],
    "science-fiction": ["Science Fiction"], "thriller": ["Thriller"], "urban-fantasy": ["Urban Fantasy"],
    "western": ["Western"],
}


@lru_cache(maxsize=1)
def raw():
    return load_genre_data()


def guide_slugs():
    return sorted(p.name[: -len("-guide.md")] for p in GUIDES.glob("*-guide.md"))


def genre_guides():
    """{genre name: guide slug} for genres that have a same-named guide."""
    names = set(raw())
    slugs = set(guide_slugs())
    return {g: s for s, gs in GUIDE_GENRES.items() if s in slugs for g in gs if g in names}


def genres():
    data, links = raw(), genre_guides()
    children = {name: [] for name in data}
    for name, d in data.items():
        for p in d["parents"]:
            children.setdefault(p, []).append(name)
    return [
        {"name": n, "date": data[n]["date"], "parents": data[n]["parents"],
         "characteristics": data[n]["characteristics"], "children": sorted(children.get(n, [])),
         "guide": links.get(n)}
        for n in sorted(data)
    ]


def _node(n):
    out = {"name": n.name, "branch_length": n.branch_length, "height": n.height}
    if n.children:
        out["children"] = [_node(c) for c in n.children]
    return out


def tree_dict(weights=DEFAULT_WEIGHTS):
    return _node(create_phylogenetic_tree(raw(), tuple(weights)))


def analysis_summary():
    data = raw()
    m = analyze_genre_metrics(data)
    c = analyze_genre_characteristics(data)
    periods = m["major_emergence_periods"]["date"]
    return {
        "total_genres": int(m["total_genres"]),
        "avg_parents": float(m["avg_parents"]),
        "hybrid_genres": sorted(m["hybrid_genres"]),
        "emergence_periods": [{"from": float(iv.left), "to": float(iv.right), "count": int(n)}
                              for iv, n in sorted(periods.items(), key=lambda kv: kv[0].left)],
        "most_influential": [[k, int(v)] for k, v in m["most_influential"].items()],
        "most_common": [[k, int(v)] for k, v in c["most_common"].items()],
        "earliest": sorted(([k, int(v)] for k, v in c["earliest"].items()), key=lambda kv: (kv[1], kv[0])),
        "modern_trends": [[k, int(v)] for k, v in c["modern_trends"].items()],
        "dangling_parents": [list(t) for t in validate_parent_references(data)],
        "weights": list(DEFAULT_WEIGHTS),
    }


def _title(md):
    first = md.lstrip().splitlines()[0] if md.strip() else ""
    t = re.sub(r"^#+\s*", "", first)
    return re.sub(r"^Comprehensive Guide to Writing\s+", "", t) or "Guide"


def guides():
    out = []
    rev = {}
    for g, s in genre_guides().items():
        rev.setdefault(s, []).append(g)
    for s in guide_slugs():
        md = (GUIDES / f"{s}-guide.md").read_text(encoding="utf-8")
        out.append({"slug": s, "title": _title(md), "words": len(md.split()),
                    "sections": sum(1 for line in md.splitlines() if line.startswith("## ")),
                    "genres": sorted(rev.get(s, []))})
    return out


def guide(slug):
    if slug not in guide_slugs():
        return None
    md = (GUIDES / f"{slug}-guide.md").read_text(encoding="utf-8")
    return {"slug": slug, "title": _title(md), "markdown": md}
