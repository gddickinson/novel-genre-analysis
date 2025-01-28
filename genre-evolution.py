# Literary Genre Evolution Analyzer
# Comprehensive analysis of literary genre evolution using network and phylogenetic approaches

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from io import StringIO
import pandas as pd
from collections import defaultdict

class GenreEvolution:
    class Node:
        def __init__(self, name, branch_length=0.0):
            self.name = name
            self.children = []
            self.branch_length = branch_length
            self.height = 0.0

    def __init__(self):
        # Dictionary of genres with their approximate emergence dates, parent genres, and key characteristics
        self.genre_data = {
            # Base Genres (ensuring all parent references exist)
            "Alternative History": {"date": 1900, "parents": ["Historical Fiction"],
                "characteristics": ["divergent timeline", "historical change points", "speculative outcomes"]},
            "Mystery": {"date": 1841, "parents": ["Detective Fiction"],
                "characteristics": ["crime solving", "investigation", "suspense"]},
            "Non-Fiction": {"date": -3000, "parents": [],
                "characteristics": ["factual content", "research based", "educational purpose"]},

            # Ancient Forms
            "Oral Epic": {"date": -2000, "parents": [],
                "characteristics": ["oral tradition", "heroic deeds", "supernatural elements", "episodic structure",
                                  "divine intervention", "formulaic phrases", "mnemonic devices"]},
            "Epic Poetry": {"date": -800, "parents": ["Oral Epic"], "characteristics": ["written form", "verse", "heroic journey"]},
            "Lyric Poetry": {"date": -600, "parents": [], "characteristics": ["personal expression", "musical accompaniment"]},
            "Drama": {"date": -534, "parents": [], "characteristics": ["performed", "dialogue", "conflict"]},
            "Myth": {"date": -3000, "parents": [], "characteristics": ["supernatural beings", "origin stories", "moral lessons"]},
            "Folk Tale": {"date": -2000, "parents": ["Myth"], "characteristics": ["oral tradition", "common people", "moral lessons"]},

            # Medieval and Renaissance
            "Romance": {"date": 1150, "parents": ["Epic Poetry"], "characteristics": ["courtly love", "chivalry", "adventures"]},
            "Mystery Play": {"date": 1200, "parents": ["Drama"], "characteristics": ["religious themes", "moral instruction"]},
            "Allegory": {"date": 1200, "parents": [], "characteristics": ["symbolic meaning", "moral teaching"]},
            "Pastoral": {"date": 1400, "parents": ["Lyric Poetry"], "characteristics": ["rural life", "nature", "simplicity"]},

            # Early Modern
            "Gothic Fiction": {"date": 1764, "parents": ["Romance"], "characteristics": ["supernatural", "horror", "romance"]},
            "Thriller": {"date": 1850, "parents": [], "characteristics": ["suspense", "tension", "danger"]},
            "Historical Fiction": {"date": 1814, "parents": [], "characteristics": ["historical setting", "period detail"]},
            "Sensation Novel": {"date": 1860, "parents": ["Gothic Fiction"], "characteristics": ["shocking revelations", "social scandal"]},
            "Detective Fiction": {"date": 1841, "parents": [], "characteristics": ["crime solving", "clues", "investigation"]},

            # Victorian Era
            "Penny Dreadful": {"date": 1830, "parents": ["Gothic Fiction"], "characteristics": ["sensational", "serialized", "cheap publication"]},
            "Social Novel": {"date": 1840, "parents": [], "characteristics": ["social criticism", "reform themes"]},
            "Scientific Romance": {"date": 1880, "parents": ["Romance"], "characteristics": ["scientific speculation", "future societies"]},

            # Early 20th Century
            "Science Fiction": {"date": 1818, "parents": ["Gothic Fiction", "Scientific Romance"], "characteristics": ["scientific elements", "future", "technology"]},
            "Horror": {"date": 1764, "parents": ["Gothic Fiction"], "characteristics": ["fear", "supernatural", "psychological tension"]},
            "Fantasy": {"date": 1858, "parents": ["Romance", "Gothic Fiction"], "characteristics": ["magic", "otherworld", "heroic quest"]},
            "Western": {"date": 1860, "parents": ["Historical Fiction"], "characteristics": ["frontier life", "conflict", "justice"]},
            "Hard SF": {"date": 1920, "parents": ["Science Fiction"], "characteristics": ["scientific accuracy", "technological focus"]},
            "Space Opera": {"date": 1928, "parents": ["Science Fiction"], "characteristics": ["space adventure", "interstellar travel"]},
            "Sword & Sorcery": {"date": 1932, "parents": ["Fantasy"], "characteristics": ["heroic combat", "magic", "adventure"]},
            "Noir": {"date": 1930, "parents": ["Detective Fiction"], "characteristics": ["cynicism", "moral ambiguity", "urban setting"]},

            # Mid 20th Century
            "Cosmic Horror": {"date": 1928, "parents": ["Horror", "Science Fiction"], "characteristics": ["cosmic dread", "unknowable entities"]},
            "High Fantasy": {"date": 1954, "parents": ["Fantasy"], "characteristics": ["secondary world", "epic conflict", "magic systems"]},
            "Military SF": {"date": 1959, "parents": ["Science Fiction"], "characteristics": ["military conflict", "future warfare"]},
            "New Wave SF": {"date": 1964, "parents": ["Science Fiction"], "characteristics": ["literary style", "social issues", "psychological focus"]},
            "Magical Realism": {"date": 1967, "parents": ["Literary Fiction", "Fantasy"], "characteristics": ["realistic setting", "magical elements"]},

            # Late 20th Century
            "Cyberpunk": {"date": 1984, "parents": ["Science Fiction"], "characteristics": ["high tech", "low life", "corporate power"]},
            "Urban Fantasy": {"date": 1986, "parents": ["Fantasy", "Horror"], "characteristics": ["modern setting", "hidden magic"]},
            "Steampunk": {"date": 1987, "parents": ["Science Fiction", "Historical Fiction"], "characteristics": ["Victorian aesthetic", "alternative technology"]},
            "Splatterpunk": {"date": 1986, "parents": ["Horror"], "characteristics": ["graphic violence", "social commentary"]},
            "Paranormal Romance": {"date": 1990, "parents": ["Romance", "Fantasy"], "characteristics": ["supernatural elements", "romantic focus"]},
            "Biopunk": {"date": 1990, "parents": ["Science Fiction", "Cyberpunk"], "characteristics": ["biotechnology", "genetic engineering"]},

            # Contemporary (21st Century)
            "New Weird": {"date": 2000, "parents": ["Fantasy", "Horror", "Science Fiction"], "characteristics": ["genre-blending", "surreal elements"]},
            "Climate Fiction": {"date": 2000, "parents": ["Science Fiction"], "characteristics": ["climate change", "environmental focus"]},
            "LitRPG": {"date": 2010, "parents": ["Fantasy", "Science Fiction"], "characteristics": ["game mechanics", "progression"]},
            "Solar Punk": {"date": 2012, "parents": ["Science Fiction"], "characteristics": ["sustainable future", "optimistic outlook"]},
            "Hopepunk": {"date": 2017, "parents": ["Science Fiction", "Fantasy"], "characteristics": ["resistance", "optimism", "community"]},

            # Mystery/Crime Subgenres
            "Cozy Mystery": {"date": 1920, "parents": ["Detective Fiction"], "characteristics": ["amateur sleuth", "small community"]},
            "Police Procedural": {"date": 1945, "parents": ["Detective Fiction"], "characteristics": ["police work", "realism"]},
            "Legal Thriller": {"date": 1987, "parents": ["Thriller", "Detective Fiction"], "characteristics": ["legal system", "courtroom drama"]},
            "Nordic Noir": {"date": 1990, "parents": ["Noir", "Police Procedural"], "characteristics": ["scandinavian setting", "social criticism"]},

            # Romance Subgenres
            "Regency Romance": {"date": 1935, "parents": ["Romance", "Historical Fiction"], "characteristics": ["regency period", "social manners"]},
            "Contemporary Romance": {"date": 1950, "parents": ["Romance"], "characteristics": ["modern setting", "realistic relationships"]},
            "Romantic Suspense": {"date": 1960, "parents": ["Romance", "Thriller"], "characteristics": ["danger", "romance", "suspense"]},
            "Erotic Romance": {"date": 1970, "parents": ["Romance"], "characteristics": ["explicit content", "relationship focus"]},

            # Horror Subgenres
            "Psychological Horror": {"date": 1959, "parents": ["Horror"], "characteristics": ["mental tension", "unreliable narrator"]},
            "Folk Horror": {"date": 1968, "parents": ["Horror"], "characteristics": ["rural setting", "ancient evil", "isolation"]},
            "Body Horror": {"date": 1975, "parents": ["Horror"], "characteristics": ["physical transformation", "grotesque"]},
            "Found Footage": {"date": 1999, "parents": ["Horror"], "characteristics": ["documentary style", "realism"]},

            # Fantasy Subgenres
            "Dark Fantasy": {"date": 1973, "parents": ["Fantasy", "Horror"], "characteristics": ["grim themes", "horror elements"]},
            "Portal Fantasy": {"date": 1950, "parents": ["Fantasy"], "characteristics": ["world transition", "discovery"]},
            "Contemporary Fantasy": {"date": 1965, "parents": ["Fantasy"], "characteristics": ["modern setting", "hidden magic"]},
            "Grimdark": {"date": 2000, "parents": ["Dark Fantasy"], "characteristics": ["moral ambiguity", "violence", "cynicism"]},

            # Literary Categories
            "Literary Fiction": {"date": 1900, "parents": [], "characteristics": ["character focus", "stylistic innovation"]},

            # Additional Base Genres (to ensure all parents are present)
            "Adventure Fiction": {"date": 1850, "parents": [], "characteristics": ["action", "exploration", "risk"]},
            "Crime Fiction": {"date": 1841, "parents": ["Detective Fiction"], "characteristics": ["criminal activity", "investigation"]},
            "Modernism": {"date": 1910, "parents": ["Literary Fiction"], "characteristics": ["experimentation", "stream of consciousness"]},
            "Postmodernism": {"date": 1945, "parents": ["Literary Fiction", "Modernism"], "characteristics": ["metafiction", "irony"]},
            "Experimental Fiction": {"date": 1960, "parents": ["Literary Fiction"], "characteristics": ["unconventional form", "innovation"]},

            # Science Fiction Branch
            "Military SF": {"date": 1959, "parents": ["Science Fiction"],
                "characteristics": ["military hierarchy", "future warfare", "advanced weapons", "space combat",
                                  "military ethics", "team dynamics"]},
            "Post-Cyberpunk": {"date": 1995, "parents": ["Cyberpunk"],
                "characteristics": ["technological optimism", "social change", "transhuman elements"]},
            "Nanopunk": {"date": 1995, "parents": ["Science Fiction", "Cyberpunk"],
                "characteristics": ["nanotechnology", "molecular engineering", "post-scarcity themes"]},
            "Atompunk": {"date": 2000, "parents": ["Science Fiction"],
                "characteristics": ["atomic age aesthetic", "retro-futurism", "1950s optimism"]},
            "Dieselpunk": {"date": 2001, "parents": ["Science Fiction", "Alternative History"],
                "characteristics": ["1920s-1950s aesthetic", "industrial technology", "war themes"]},
            "Clockpunk": {"date": 1990, "parents": ["Science Fiction", "Historical Fiction"],
                "characteristics": ["renaissance tech", "mechanical devices", "historical settings"]},
            "Solarpunk": {"date": 2012, "parents": ["Science Fiction"],
                "characteristics": ["environmental sustainability", "social justice", "optimistic future"]},
            "Lunarpunk": {"date": 2020, "parents": ["Science Fiction", "Solarpunk"],
                "characteristics": ["nocturnal society", "darkness themes", "sustainable night living"]},

            # Fantasy Branch
            "Arcanepunk": {"date": 2010, "parents": ["Fantasy", "Science Fiction"],
                "characteristics": ["industrialized magic", "magical technology", "urban setting"]},
            "Flintlock Fantasy": {"date": 2000, "parents": ["Fantasy", "Historical Fiction"],
                "characteristics": ["gunpowder weapons", "military themes", "historical parallel"]},
            "Silk Road Fantasy": {"date": 2015, "parents": ["Fantasy", "Historical Fiction"],
                "characteristics": ["Asian settings", "trade routes", "cultural exchange"]},
            "Tribal Fantasy": {"date": 2010, "parents": ["Fantasy"],
                "characteristics": ["indigenous cultures", "nature magic", "oral traditions"]},
            "Celtic Fantasy": {"date": 1980, "parents": ["Fantasy"],
                "characteristics": ["Celtic mythology", "fae creatures", "druidic magic"]},
            "Arthurian Fantasy": {"date": 1960, "parents": ["Fantasy", "Historical Fiction"],
                "characteristics": ["Arthurian legend", "medieval setting", "chivalric codes"]},

            # Horror Branch
            "Eco-Horror": {"date": 1970, "parents": ["Horror"],
                "characteristics": ["environmental threats", "nature revenge", "ecological disaster"]},
            "Survival Horror": {"date": 1980, "parents": ["Horror"],
                "characteristics": ["isolation", "resource management", "immediate threats"]},
            "Gothic Horror": {"date": 1764, "parents": ["Horror", "Gothic Fiction"],
                "characteristics": ["ancient secrets", "family curses", "haunted locations"]},
            "Quiet Horror": {"date": 1980, "parents": ["Horror"],
                "characteristics": ["subtle dread", "psychological focus", "understated supernatural"]},
            "Cosmic Horror": {"date": 1928, "parents": ["Horror", "Science Fiction"],
                "characteristics": ["cosmic dread", "unknowable entities", "human insignificance"]},

            # Mystery/Crime Branch
            "Tech Noir": {"date": 1985, "parents": ["Noir", "Science Fiction"],
                "characteristics": ["future dystopia", "detective story", "technological anxiety"]},
            "Forensic Thriller": {"date": 1990, "parents": ["Thriller", "Police Procedural"],
                "characteristics": ["scientific investigation", "forensic detail", "serial crimes"]},
            "Domestic Noir": {"date": 2010, "parents": ["Noir", "Psychological Thriller"],
                "characteristics": ["domestic setting", "unreliable narrator", "personal threats"]},
            "Historical Mystery": {"date": 1970, "parents": ["Mystery", "Historical Fiction"],
                "characteristics": ["period setting", "historical accuracy", "period detective work"]},
            "Medical Thriller": {"date": 1975, "parents": ["Thriller"],
                "characteristics": ["medical setting", "health threats", "scientific accuracy"]},

            # Romance Branch
            "Time Travel Romance": {"date": 1990, "parents": ["Romance", "Science Fiction"],
                "characteristics": ["temporal displacement", "historical settings", "paradox elements"]},
            "Gothic Romance": {"date": 1780, "parents": ["Romance", "Gothic Fiction"],
                "characteristics": ["mysterious past", "gloomy setting", "romantic suspense"]},
            "Sports Romance": {"date": 1980, "parents": ["Romance"],
                "characteristics": ["athletic setting", "competition", "team dynamics"]},
            "Medical Romance": {"date": 1960, "parents": ["Romance"],
                "characteristics": ["hospital setting", "medical drama", "professional conflicts"]},

            # Contemporary/Literary
            "Autofiction": {"date": 1977, "parents": ["Literary Fiction"],
                "characteristics": ["autobiographical elements", "fictional techniques", "self-reflection"]},
            "Hypertext Fiction": {"date": 1990, "parents": ["Experimental Fiction"],
                "characteristics": ["non-linear", "interactive elements", "digital medium"]},
            "Cli-Fi": {"date": 2000, "parents": ["Science Fiction", "Literary Fiction"],
                "characteristics": ["climate change", "environmental crisis", "social impact"]},
            "Biographical Fiction": {"date": 1930, "parents": ["Historical Fiction", "Literary Fiction"],
                "characteristics": ["historical figures", "factual basis", "creative interpretation"]},

            # Cross-Genre Innovations
            "Weird West": {"date": 1972, "parents": ["Western", "Horror", "Fantasy"],
                "characteristics": ["frontier setting", "supernatural elements", "western tropes"]},
            "Science Fantasy": {"date": 1950, "parents": ["Science Fiction", "Fantasy"],
                "characteristics": ["mixed magic/technology", "genre blending", "speculative elements"]},
            "Contemporary Fairytale": {"date": 1990, "parents": ["Fantasy", "Literary Fiction"],
                "characteristics": ["fairytale retelling", "modern setting", "mythic elements"]},
            "Supernatural Thriller": {"date": 1970, "parents": ["Thriller", "Horror"],
                "characteristics": ["supernatural threats", "fast pace", "suspense elements"]},

            # Age Category Cross-Sections
            "Young Adult Romance": {"date": 1980, "parents": ["Romance"],
                "characteristics": ["coming of age", "first love", "teen protagonist"]},
            "Middle Grade Fantasy": {"date": 1950, "parents": ["Fantasy"],
                "characteristics": ["young protagonist", "magical discovery", "age-appropriate content"]},
            "New Adult Urban Fantasy": {"date": 2010, "parents": ["Urban Fantasy"],
                "characteristics": ["college-age protagonist", "adult themes", "urban setting"]},

            # Additional Thriller Subgenres
            "Psychological Thriller": {"date": 1960, "parents": ["Thriller"],
                "characteristics": ["psychological manipulation", "unreliable narrator", "mental tension"]},
            "Action Thriller": {"date": 1960, "parents": ["Thriller", "Adventure Fiction"],
                "characteristics": ["fast pace", "physical danger", "action sequences"]},
            "Espionage Thriller": {"date": 1903, "parents": ["Thriller"],
                "characteristics": ["espionage", "political intrigue", "covert operations"]},
            "Political Thriller": {"date": 1950, "parents": ["Thriller"],
                "characteristics": ["political intrigue", "conspiracy", "power dynamics"]},

            # Additional Modern Genres
            "Bizarro Fiction": {"date": 1999, "parents": ["Experimental Fiction"],
                "characteristics": ["absurdism", "extreme situations", "satirical elements"]},
            "Silkpunk": {"date": 2015, "parents": ["Science Fiction", "Historical Fiction"],
                "characteristics": ["East Asian elements", "biomechanical technology", "classical Asian aesthetics"]},
            "Gothic Science Fiction": {"date": 1818, "parents": ["Gothic Fiction", "Science Fiction"],
                "characteristics": ["scientific horror", "dark atmosphere", "technological dread"]},

            # Additional Romance Subgenres
            "Workplace Romance": {"date": 1980, "parents": ["Contemporary Romance"],
                "characteristics": ["office setting", "professional conflict", "workplace dynamics"]},
            "Holiday Romance": {"date": 1940, "parents": ["Contemporary Romance"],
                "characteristics": ["seasonal setting", "festive themes", "holiday traditions"]},

            # Additional Fantasy Subgenres
            "Mythic Fiction": {"date": 1990, "parents": ["Fantasy", "Literary Fiction"],
                "characteristics": ["mythological elements", "contemporary setting", "symbolic meaning"]},
            "Wuxia": {"date": 1900, "parents": ["Fantasy", "Adventure Fiction"],
                "characteristics": ["martial arts", "Chinese culture", "honor codes"]},
            "Xuanhuan": {"date": 2000, "parents": ["Fantasy", "Wuxia"],
                "characteristics": ["eastern fantasy", "cultivation", "power progression"]},

            # Additional Horror Subgenres
            "Slasher": {"date": 1970, "parents": ["Horror"],
                "characteristics": ["serial killer", "pursuit", "survival"]},
            "Haunted House": {"date": 1820, "parents": ["Gothic Horror"],
                "characteristics": ["haunted location", "supernatural presence", "psychological terror"]},

            # Additional Science Fiction Subgenres
            "First Contact": {"date": 1940, "parents": ["Science Fiction"],
                "characteristics": ["alien encounter", "cultural exchange", "scientific discovery"]},
            "Generation Ship": {"date": 1950, "parents": ["Science Fiction"],
                "characteristics": ["enclosed society", "long space journey", "social evolution"]},

            # Recent Emerging Genres
            "Cozy Fantasy": {"date": 2020, "parents": ["Fantasy"],
                "characteristics": ["low stakes", "comfort focus", "peaceful resolution"]},
            "Gamelit": {"date": 2015, "parents": ["LitRPG"],
                "characteristics": ["game elements", "real world setting", "progression system"]},
            "Slice of Life Fantasy": {"date": 2018, "parents": ["Fantasy"],
                "characteristics": ["everyday magic", "minimal conflict", "character focus"]},
            "Noblebright": {"date": 2015, "parents": ["Fantasy"],
                "characteristics": ["optimistic tone", "moral clarity", "positive change"]},

            # Academic and Educational Fiction
            "Campus Novel": {"date": 1950, "parents": ["Literary Fiction"],
                "characteristics": ["academic setting", "intellectual themes", "university life"]},
            "Academic Mystery": {"date": 1930, "parents": ["Mystery", "Campus Novel"],
                "characteristics": ["university setting", "academic intrigue", "scholarly detection"]}

    }

    def create_timeline_graph(self):
        """Create a timeline-based network visualization of genre evolution"""
        G = nx.DiGraph()

        # Add nodes with temporal positions
        pos = {}
        for genre, data in self.genre_data.items():
            G.add_node(genre, date=data["date"])
            # Normalize dates for visualization
            x = (data["date"] + 1000) / 3000  # Adjust scaling as needed
            y = np.random.random()  # Random y position for better visualization
            pos[genre] = (x, y)

            # Add edges from parents
            for parent in data["parents"]:
                G.add_edge(parent, genre)

        return G, pos

    def plot_timeline_graph(self, G, pos):
        """Plot the timeline-based genre evolution graph"""
        plt.figure(figsize=(20, 10))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                             node_size=1000, alpha=0.7)

        # Draw edges with curved arrows
        nx.draw_networkx_edges(G, pos, edge_color='gray',
                             arrows=True, arrowsize=20,
                             connectionstyle="arc3,rad=0.2")

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8)

        # Add timeline
        plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3)
        dates = sorted(set(data["date"] for data in self.genre_data.values()))
        for date in dates:
            x = (date + 1000) / 3000
            plt.axvline(x=x, color='gray', linestyle=':', alpha=0.2)
            plt.text(x, -0.1, str(date), rotation=45)

        plt.title("Evolution of Literary Genres Over Time", pad=20)
        plt.axis('off')
        return plt

    def create_distance_matrix(self):
        """Create a full distance matrix as numpy array"""
        genres = sorted(list(self.genre_data.keys()))
        n = len(genres)
        matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i+1, n):
                g1, g2 = genres[i], genres[j]

                # Calculate distance components
                time_dist = abs(self.genre_data[g1]["date"] - self.genre_data[g2]["date"]) / 1000.0

                # Parent similarity
                parents1 = set(self.genre_data[g1]["parents"])
                parents2 = set(self.genre_data[g2]["parents"])
                parent_dist = 1.0
                if parents1 and parents2:
                    shared = len(parents1 & parents2)
                    total = len(parents1 | parents2)
                    if total > 0:
                        parent_dist = 1.0 - (shared / total)

                # Characteristic similarity
                char1 = set(self.genre_data[g1]["characteristics"])
                char2 = set(self.genre_data[g2]["characteristics"])
                char_dist = 1.0
                if char1 and char2:
                    shared = len(char1 & char2)
                    total = len(char1 | char2)
                    if total > 0:
                        char_dist = 1.0 - (shared / total)

                # Combine distances
                dist = float((0.4 * time_dist) + (0.3 * parent_dist) + (0.3 * char_dist))
                matrix[i, j] = dist
                matrix[j, i] = dist

        return genres, matrix

    def find_min_pair(self, matrix):
        """Find the closest pair of clusters"""
        n = matrix.shape[0]
        min_dist = float('inf')
        min_i, min_j = -1, -1

        for i in range(n):
            for j in range(i+1, n):
                if matrix[i, j] < min_dist:
                    min_dist = matrix[i, j]
                    min_i, min_j = i, j

        return min_i, min_j, min_dist

    def update_matrix(self, old_matrix, i, j):
        """Create new matrix after merging clusters i and j"""
        n = old_matrix.shape[0]
        new_size = n - 1
        new_matrix = np.zeros((new_size, new_size))

        # Create mapping for indices
        new_to_old = []
        for k in range(n):
            if k != j:  # Skip the index being removed
                new_to_old.append(k)

        # Fill in new distances
        for new_i in range(new_size):
            for new_j in range(new_i+1, new_size):
                old_i = new_to_old[new_i]
                old_j = new_to_old[new_j]

                if old_i == i:  # This is the merged cluster
                    dist = (old_matrix[i, old_j] + old_matrix[j, old_j]) / 2.0
                else:
                    if old_j == i:  # This is the merged cluster
                        dist = (old_matrix[old_i, i] + old_matrix[old_i, j]) / 2.0
                    else:
                        dist = old_matrix[old_i, old_j]

                new_matrix[new_i, new_j] = dist
                new_matrix[new_j, new_i] = dist

        return new_matrix

    def create_phylogenetic_tree(self):
        """Build a UPGMA tree from genre data"""
        genres, matrix = self.create_distance_matrix()
        nodes = [self.Node(name) for name in genres]

        while len(nodes) > 1:
            # Find closest pair
            i, j, dist = self.find_min_pair(matrix)

            # Create new node
            new_node = self.Node(f"Internal_{len(nodes)}")

            # Set branch lengths
            branch_length = dist / 2.0
            nodes[i].branch_length = branch_length - nodes[i].height
            nodes[j].branch_length = branch_length - nodes[j].height

            # Add children
            new_node.children = [nodes[i], nodes[j]]
            new_node.height = branch_length

            # Update nodes list and distance matrix
            nodes.pop(j)  # Remove larger index first
            nodes.pop(i)
            nodes.append(new_node)
            matrix = self.update_matrix(matrix, i, j)

        return nodes[0]

    def plot_phylogenetic_tree(self, root):
        """Plot the tree using networkx"""
        G = nx.Graph()
        pos = {}
        labels = {}

        def add_nodes(node, x=0, y=0, dx=1, level=0):
            """Recursively add nodes to the graph"""
            node_id = id(node)
            G.add_node(node_id)
            pos[node_id] = (x, y)
            labels[node_id] = node.name if node.name in self.genre_data else ""

            n_children = len(node.children)
            if n_children > 0:
                dy = 1.0 / (n_children + 1)
                for i, child in enumerate(node.children, 1):
                    child_id = id(child)
                    new_y = y + (i * dy - 0.5)
                    add_nodes(child, x + dx, new_y, dx/2, level+1)
                    G.add_edge(node_id, child_id)

        plt.figure(figsize=(15, 10))
        add_nodes(root)

        nx.draw(G, pos,
                labels=labels,
                with_labels=True,
                node_color='lightblue',
                node_size=2000,
                font_size=8,
                font_weight='bold')

        plt.title("Genre Evolution Tree")
        plt.axis('off')
        return plt

    def analyze_genre_metrics(self):
        """Calculate various metrics about genre evolution"""
        metrics = {
            "total_genres": len(self.genre_data),
            "avg_parents": np.mean([len(data["parents"]) for data in self.genre_data.values()]),
            "hybrid_genres": [genre for genre, data in self.genre_data.items()
                            if len(data["parents"]) > 1],
            "major_emergence_periods": self._identify_emergence_periods(),
            "most_influential": self._identify_influential_genres()
        }
        return metrics

    def _identify_emergence_periods(self):
        """Identify major periods of genre emergence"""
        dates = [data["date"] for data in self.genre_data.values()]
        df = pd.DataFrame(dates, columns=['date'])
        return df.groupby(pd.cut(df['date'], bins=5)).count().to_dict()

    def _identify_influential_genres(self):
        """Identify genres that influenced the most other genres"""
        influence_count = defaultdict(int)
        for data in self.genre_data.values():
            for parent in data["parents"]:
                influence_count[parent] += 1
        return dict(sorted(influence_count.items(), key=lambda x: x[1], reverse=True))

    def analyze_genre_characteristics(self):
        """Analyze the evolution of genre characteristics over time"""
        # Collect all unique characteristics
        all_characteristics = set()
        for data in self.genre_data.values():
            all_characteristics.update(data["characteristics"])

        # Track characteristic emergence over time
        characteristic_timeline = defaultdict(list)
        for genre, data in self.genre_data.items():
            year = data["date"]
            for char in data["characteristics"]:
                characteristic_timeline[char].append(year)

        # Analyze characteristic patterns
        characteristic_analysis = {
            "most_common": self._most_common_characteristics(),
            "earliest": self._earliest_characteristics(),
            "modern_trends": self._modern_characteristics()
        }

        return characteristic_analysis

    def _most_common_characteristics(self):
        """Identify most common characteristics across genres"""
        char_count = defaultdict(int)
        for data in self.genre_data.values():
            for char in data["characteristics"]:
                char_count[char] += 1
        return dict(sorted(char_count.items(), key=lambda x: x[1], reverse=True)[:10])

    def _earliest_characteristics(self):
        """Identify earliest appearing characteristics"""
        char_dates = defaultdict(list)
        for data in self.genre_data.values():
            for char in data["characteristics"]:
                char_dates[char].append(data["date"])
        return {char: min(dates) for char, dates in char_dates.items()}

    def _modern_characteristics(self):
        """Identify characteristics common in modern genres (post-2000)"""
        modern_chars = defaultdict(int)
        for data in self.genre_data.values():
            if data["date"] >= 2000:
                for char in data["characteristics"]:
                    modern_chars[char] += 1
        return dict(sorted(modern_chars.items(), key=lambda x: x[1], reverse=True)[:10])

# Create and use the analyzer
analyzer = GenreEvolution()

try:
    # Generate timeline visualization
    G, pos = analyzer.create_timeline_graph()
    timeline_plt = analyzer.plot_timeline_graph(G, pos)
    timeline_plt.savefig('genre_timeline.png', bbox_inches='tight', dpi=300)

    # Generate phylogenetic tree
    tree = analyzer.create_phylogenetic_tree()
    tree_plt = analyzer.plot_phylogenetic_tree(tree)
    tree_plt.savefig('genre_phylogeny.png', bbox_inches='tight', dpi=300)

    # Analyze metrics and characteristics
    metrics = analyzer.analyze_genre_metrics()
    char_analysis = analyzer.analyze_genre_characteristics()

    # Print analysis results
    print("\nGenre Evolution Analysis:")
    print(f"\nTotal number of genres: {metrics['total_genres']}")
    print(f"Average number of parent genres: {metrics['avg_parents']:.2f}")

    print("\nMost Common Characteristics:")
    for char, count in char_analysis['most_common'].items():
        print(f"- {char}: {count} genres")

    print("\nEarliest Genre Characteristics:")
    earliest = sorted(char_analysis['earliest'].items(), key=lambda x: x[1])
    for char, date in earliest[:10]:
        print(f"- {char}: {date} BCE/CE")

    print("\nMost Common Modern Characteristics (post-2000):")
    for char, count in char_analysis['modern_trends'].items():
        print(f"- {char}: {count} genres")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    raise  # Re-raise the exception for debugging
