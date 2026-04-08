"""
Genre database loader.

Loads genre definitions from genre_data.json and provides validation utilities.
"""

import json
import os
import logging

logger = logging.getLogger("GenreDatabase")

_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genre_data.json")


def load_genre_data(path=None):
    """
    Load the genre database from a JSON file.

    Args:
        path: Optional path to JSON file. Defaults to genre_data.json in project root.

    Returns:
        Dictionary mapping genre names to their data (date, parents, characteristics).
    """
    path = path or _DATA_FILE
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} genres from {path}")
    return data


def validate_parent_references(genre_data):
    """
    Validate that all parent references point to existing genres.

    Args:
        genre_data: Genre database dictionary.

    Returns:
        List of (genre, missing_parent) tuples for any dangling references.
    """
    all_names = set(genre_data.keys())
    dangling = []
    for genre, data in genre_data.items():
        for parent in data.get("parents", []):
            if parent not in all_names:
                dangling.append((genre, parent))
    if dangling:
        for genre, parent in dangling:
            logger.warning(f"Genre '{genre}' references missing parent '{parent}'")
    return dangling
