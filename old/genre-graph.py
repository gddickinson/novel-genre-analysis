import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def create_genre_graph():
    # Create directed graph
    G = nx.DiGraph()
    
    # Define main genres and their relationships
    genres = {
        # Major Traditional Categories
        "Literary Fiction": [],
        "Genre Fiction": ["Literary Fiction"],  # Can have literary elements
        
        # Major Genre Fiction Categories
        "Romance": ["Genre Fiction"],
        "Mystery": ["Genre Fiction"],
        "Science Fiction": ["Genre Fiction"],
        "Fantasy": ["Genre Fiction"],
        "Horror": ["Genre Fiction"],
        "Historical Fiction": ["Genre Fiction"],
        "Thriller": ["Genre Fiction"],
        "Western": ["Genre Fiction"],
        
        # Romance Subgenres
        "Contemporary Romance": ["Romance"],
        "Historical Romance": ["Romance", "Historical Fiction"],
        "Paranormal Romance": ["Romance", "Fantasy"],
        "Romantic Suspense": ["Romance", "Thriller"],
        "Erotic Romance": ["Romance"],
        
        # Mystery Subgenres
        "Cozy Mystery": ["Mystery"],
        "Hard-Boiled": ["Mystery"],
        "Police Procedural": ["Mystery"],
        "Amateur Sleuth": ["Mystery"],
        "True Crime": ["Mystery", "Non-Fiction"],
        
        # Science Fiction Subgenres
        "Hard SF": ["Science Fiction"],
        "Space Opera": ["Science Fiction"],
        "Cyberpunk": ["Science Fiction"],
        "Post-Apocalyptic": ["Science Fiction"],
        "Military SF": ["Science Fiction"],
        
        # Fantasy Subgenres
        "Epic Fantasy": ["Fantasy"],
        "Urban Fantasy": ["Fantasy"],
        "Dark Fantasy": ["Fantasy", "Horror"],
        "Portal Fantasy": ["Fantasy"],
        "Magical Realism": ["Fantasy", "Literary Fiction"],
        
        # Horror Subgenres
        "Gothic Horror": ["Horror"],
        "Supernatural Horror": ["Horror"],
        "Psychological Horror": ["Horror", "Thriller"],
        "Cosmic Horror": ["Horror", "Science Fiction"],
        
        # Historical Fiction Subgenres
        "Alternative History": ["Historical Fiction", "Science Fiction"],
        "Historical Mystery": ["Historical Fiction", "Mystery"],
        "Historical Romance": ["Historical Fiction", "Romance"],
        "Biblical Fiction": ["Historical Fiction"],
        
        # Thriller Subgenres
        "Psychological Thriller": ["Thriller"],
        "Legal Thriller": ["Thriller"],
        "Medical Thriller": ["Thriller"],
        "Technothriller": ["Thriller", "Science Fiction"],
        
        # Cross-Genre Categories
        "Young Adult": [],  # Can apply to any genre
        "New Adult": [],    # Can apply to any genre
        "Middle Grade": [], # Can apply to any genre
        
        # Other Important Categories
        "Non-Fiction": [],
        "Poetry": [],
        "Drama": [],
        "Experimental": ["Literary Fiction"],
    }
    
    # Add nodes and edges
    for genre, parents in genres.items():
        G.add_node(genre)
        for parent in parents:
            G.add_edge(parent, genre)
    
    return G

def plot_genre_graph(G):
    plt.figure(figsize=(20, 20))
    
    # Use hierarchical layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=2000, alpha=0.7)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                          arrows=True, arrowsize=20)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title("Literary Genres and Their Relationships", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    return plt

# Create and plot the graph
G = create_genre_graph()
plt = plot_genre_graph(G)

# Additional analysis functions
def get_genre_statistics(G):
    """Calculate various statistics about the genre network"""
    stats = {
        "Total Genres": G.number_of_nodes(),
        "Total Relationships": G.number_of_edges(),
        "Most Connected Genres": sorted(
            [(n, G.degree(n)) for n in G.nodes()],
            key=lambda x: x[1],
            reverse=True
        )[:5],
        "Pure Genres": [n for n in G.nodes() if G.in_degree(n) == 0],
        "Hybrid Genres": [n for n in G.nodes() if G.in_degree(n) > 1]
    }
    return stats

def print_genre_stats(stats):
    """Print formatted genre statistics"""
    print("\nGenre Network Statistics:")
    print(f"Total number of genres: {stats['Total Genres']}")
    print(f"Total number of relationships: {stats['Total Relationships']}")
    print("\nMost connected genres:")
    for genre, connections in stats['Most Connected Genres']:
        print(f"- {genre}: {connections} connections")
    print("\nPure genres (no parent genres):")
    for genre in stats['Pure Genres']:
        print(f"- {genre}")
    print("\nHybrid genres (multiple parent genres):")
    for genre in stats['Hybrid Genres']:
        print(f"- {genre}")

# Calculate and print statistics
stats = get_genre_statistics(G)
print_genre_stats(stats)
