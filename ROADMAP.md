# Literary Genre Evolution Analyzer — Roadmap

## Current State
A single large file (`genre-evolution.py`) containing the entire `GenreEvolution` class with 120+ genre definitions, network graph construction, phylogenetic tree building (using BioPython UPGMA), and matplotlib visualizations. Has a `guides/` directory with writing guides and an `old/` directory with previous versions. The genre database is comprehensive but hardcoded as a Python dictionary. No tests, no packaging, single-file architecture.

## Short-term Improvements
- [ ] Split `genre-evolution.py` into modules: `genre_data.py` (genre database), `analysis.py` (metrics, clustering), `visualization.py` (plotting), `main.py` (CLI)
- [ ] Move the genre database from a hardcoded dict to a JSON or YAML file for easier editing
- [ ] Add a `requirements.txt` (networkx, matplotlib, numpy, pandas, scipy, biopython)
- [ ] Add input validation for genre parent references — ensure no dangling parent links
- [ ] Add docstrings to `create_timeline_graph()`, `create_phylogenetic_tree()`, and analysis methods
- [ ] Handle the BioPython import gracefully — provide a fallback or clear error if not installed

## Feature Enhancements
- [ ] Add an interactive HTML visualization using pyvis or plotly for the genre network
- [ ] Add genre search and filtering: find genres by characteristic, time period, or parent
- [ ] Generate genre comparison reports (e.g., "how does Gothic Horror differ from Cosmic Horror?")
- [ ] Add a genre recommendation feature: given a set of characteristics, suggest matching genres
- [ ] Support user-contributed genres via a simple JSON schema for community additions
- [ ] Add temporal animation showing genre emergence over centuries
- [ ] Export genre relationship data as GraphML for use in Gephi or Cytoscape

## Long-term Vision
- [ ] Build a web app (Streamlit or Dash) for interactive genre exploration
- [ ] Integrate with book APIs (Open Library, Google Books) to correlate genre popularity with publication data
- [ ] Add geographic/cultural origin tracking for genres
- [ ] Train a text classifier to predict genre from book excerpts using the characteristic database
- [ ] Support collaborative editing of the genre database with version control

## Technical Debt
- [ ] Clean up or remove the `old/` directory — archive it outside the main project
- [ ] The phylogenetic tree construction assumes all genres can be compared — add distance validation
- [ ] Replace hardcoded visualization parameters (figure sizes, font sizes, colors) with a config
- [ ] Add unit tests for distance calculation, tree construction, and genre metric analysis
- [ ] The `Node` inner class duplicates BioPython's Clade — evaluate whether it is still needed
- [ ] Add proper `__main__.py` entry point instead of script-level execution
