# Literary Genre Evolution Analyzer - Interface Map

## Module Overview

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point; loads data, runs analysis, generates visualizations |
| `genre_database.py` | Loads genre data from JSON, validates parent references |
| `genre_data.json` | Genre database: 120+ genres with dates, parents, characteristics |
| `analysis.py` | Distance matrix, UPGMA tree construction, metric analysis |
| `visualization.py` | Timeline graph and phylogenetic tree plotting (networkx + matplotlib) |
| `genre-evolution.py` | Original monolithic file (retained for reference) |
| `test_genre_evolution.py` | Test suite for data loading, distance, tree, and metrics |
| `_archive/` | Previous versions of the code |

## Key Classes and Functions

### genre_database.py
- `load_genre_data(path=None)` - loads genre dict from JSON
- `validate_parent_references(genre_data)` - returns list of dangling parent refs

### analysis.py
- `Node` - tree node class with name, children, branch_length, height
- `create_distance_matrix(genre_data)` - returns (genre_names, numpy_matrix)
- `create_phylogenetic_tree(genre_data)` - UPGMA tree construction, returns root Node
- `analyze_genre_metrics(genre_data)` - total genres, avg parents, hybrid genres, influential
- `analyze_genre_characteristics(genre_data)` - most common, earliest, modern trends

### visualization.py
- `create_timeline_graph(genre_data)` - returns (DiGraph, positions)
- `plot_timeline_graph(G, pos, genre_data)` - renders timeline plot
- `plot_phylogenetic_tree(root, genre_data)` - renders tree plot

## Data Flow
```
genre_data.json -> genre_database.py (load + validate)
                -> analysis.py (metrics + tree)
                -> visualization.py (plots)
                -> main.py (orchestrate all)
```
