"""
Genre visualization: timeline graph and phylogenetic tree plotting.
"""

import numpy as np
import logging

try:
    import networkx as nx
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for headless use
    import matplotlib.pyplot as plt
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

logger = logging.getLogger("GenreVisualization")


def create_timeline_graph(genre_data):
    """
    Create a timeline-based network visualization of genre evolution.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        Tuple of (networkx DiGraph, position dict).
    """
    if not HAS_PLOTTING:
        raise ImportError("networkx and matplotlib are required for visualization")

    G = nx.DiGraph()
    pos = {}

    for genre, data in genre_data.items():
        G.add_node(genre, date=data["date"])
        x = (data["date"] + 1000) / 3000
        y = np.random.random()
        pos[genre] = (x, y)

        for parent in data["parents"]:
            G.add_edge(parent, genre)

    return G, pos


def plot_timeline_graph(G, pos, genre_data):
    """
    Plot the timeline-based genre evolution graph.

    Args:
        G: networkx DiGraph from create_timeline_graph.
        pos: Position dict from create_timeline_graph.
        genre_data: Genre database dictionary.

    Returns:
        matplotlib pyplot module (call .savefig() on the result).
    """
    if not HAS_PLOTTING:
        raise ImportError("networkx and matplotlib are required for visualization")

    plt.figure(figsize=(20, 10))

    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=500, alpha=0.7)
    nx.draw_networkx_edges(
        G, pos, edge_color="gray", arrows=True, arrowsize=20,
        connectionstyle="arc3,rad=0.2",
    )
    nx.draw_networkx_labels(G, pos, font_size=6)

    plt.axhline(y=0.5, color="gray", linestyle="--", alpha=0.3)
    dates = sorted(set(data["date"] for data in genre_data.values()))
    for date in dates:
        x = (date + 1000) / 3000
        plt.axvline(x=x, color="gray", linestyle=":", alpha=0.2)
        plt.text(x, -0.1, str(date), rotation=45)

    plt.title("Evolution of Literary Genres Over Time", pad=20)
    plt.axis("off")
    return plt


def plot_phylogenetic_tree(root, genre_data):
    """
    Plot the phylogenetic tree using networkx.

    Args:
        root: Root Node from analysis.create_phylogenetic_tree.
        genre_data: Genre database dictionary.

    Returns:
        matplotlib pyplot module.
    """
    if not HAS_PLOTTING:
        raise ImportError("networkx and matplotlib are required for visualization")

    G = nx.Graph()
    pos = {}
    labels = {}

    def add_nodes(node, x=0, y=0, dx=1, level=0):
        node_id = id(node)
        G.add_node(node_id)
        pos[node_id] = (x, y)
        labels[node_id] = node.name if node.name in genre_data else ""

        n_children = len(node.children)
        if n_children > 0:
            dy = 1.0 / (n_children + 1)
            for i, child in enumerate(node.children, 1):
                child_id = id(child)
                new_y = y + (i * dy - 0.5)
                add_nodes(child, x + dx, new_y, dx / 2, level + 1)
                G.add_edge(node_id, child_id)

    plt.figure(figsize=(15, 10))
    add_nodes(root)

    nx.draw(
        G, pos, labels=labels, with_labels=True,
        node_color="lightblue", node_size=500, font_size=6, font_weight="bold",
    )

    plt.title("Genre Evolution Tree")
    plt.axis("off")
    return plt
