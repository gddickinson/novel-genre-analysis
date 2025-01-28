# Literary Genre Evolution Analyzer

A comprehensive Python tool for analyzing and visualizing the evolution of literary genres throughout history. This project combines network analysis, phylogenetic tree construction, and detailed genre characteristics to provide insights into how literary genres have emerged, evolved, and influenced each other over time.

## Overview

The Literary Genre Evolution Analyzer is a collaboration with Anthropic's Claude AI, aiming to create a data-driven understanding of literary genre evolution. The project maps over 120 genres from ancient forms to contemporary developments, analyzing their relationships, characteristics, and evolutionary patterns.

### Key Features

- **Timeline Visualization**: Creates a network graph showing genre evolution over time
- **Phylogenetic Analysis**: Generates evolutionary trees using UPGMA clustering
- **Characteristic Analysis**: Tracks the emergence and prevalence of genre features
- **Comprehensive Genre Database**: Contains detailed information about 120+ literary genres
- **Genre Writing Guides**: Includes detailed guides for writing in specific genres

## Visualizations

The project generates two main visualizations:

1. **Timeline Graph** (`genre_timeline.png`):
   - Shows chronological evolution of genres
   - Displays parent-child relationships
   - Includes time markers for historical context

2. **Phylogenetic Tree** (`genre_phylogeny.png`):
   - Illustrates genre clustering based on similarities
   - Shows evolutionary relationships
   - Highlights genre family groupings

## Installation

```bash
git clone https://github.com/gddickinson/genre-evolution.git
cd genre-evolution
pip install -r requirements.txt
```

### Dependencies

- NetworkX
- Matplotlib
- NumPy
- Pandas
- SciPy

## Usage

```python
from genre_evolution import GenreEvolution

# Create analyzer instance
analyzer = GenreEvolution()

# Generate visualizations
analyzer.create_timeline_graph()
analyzer.create_phylogenetic_tree()

# Analyze genre characteristics
metrics = analyzer.analyze_genre_metrics()
characteristics = analyzer.analyze_genre_characteristics()
```

## Project Structure

```
├── genre-evolution.py     # Main analysis code
├── genre_timeline.png     # Timeline visualization
├── genre_phylogeny.png    # Evolutionary tree visualization
├── guides/               # Writing guides for different genres
│   ├── mystery-guide.md
│   ├── cozy-mystery-guide.md
│   └── ...
└── README.md
```

## Genre Analysis

The project analyzes genres across multiple dimensions:

- **Temporal Evolution**: Tracks when genres emerged and how they developed
- **Parent-Child Relationships**: Maps how genres influenced and spawned new genres
- **Characteristic Inheritance**: Analyzes how genre features are passed down and modified
- **Hybridization Patterns**: Studies how genres combine to form new subgenres

## Writing Guides

The repository includes detailed guides for writing in various genres, covering:
- Genre conventions and expectations
- Structural elements
- Character development
- Plot progression
- Market considerations

## Methodology

The analysis uses several computational approaches:

1. **Distance Calculation**:
   - Temporal distance (40% weight)
   - Parent similarity (30% weight)
   - Characteristic similarity (30% weight)

2. **Tree Construction**:
   - UPGMA (Unweighted Pair Group Method with Arithmetic Mean)
   - Hierarchical clustering
   - Distance-based phylogenetic analysis

## Contributing

Contributions are welcome! Please feel free to submit pull requests with:
- Additional genres
- Updated characteristics
- New writing guides
- Analysis improvements
- Visualization enhancements

## Contact

- George Dickinson (george.dickinson@gmail.com)
- GitHub: [@gddickinson](https://github.com/gddickinson)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Claude AI (Anthropic) for collaboration on analysis and guide creation
- NetworkX team for graph visualization capabilities
- Academic sources for genre history and characteristics

## Future Development

Planned improvements include:
- Interactive web visualization
- Additional genre guides
- Enhanced clustering algorithms
- Cultural influence mapping
- Geographic distribution analysis

