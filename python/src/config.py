"""
Tankgame Configuration
Contains all game settings, items, and predefined tanks.
"""

from typing import Dict, Tuple, Any

# Game Settings
SETTINGS: Dict[str, int] = {
    'probability_to_miss': 20,
    'probability_of_malfunction': 15,
    'credits': 0,
    'base_dodge_chance': 5,
}

# Debug mode - set to True to skip animations and speed up gameplay
DEBUG: bool = False

# Shop Items
# Format: id -> (name, description, value, price, attribute)
ITEMS: Dict[str, Tuple[str, str, int, int, str]] = {
    '1': ('Armor+10', 'Increase armor', 10, 3, 'armor'),
    '2': ('Armor+20', 'Increase armor', 20, 5, 'armor'),
    '3': ('Ammo+2', 'Add ammunition', 2, 3, 'ammo'),
    '4': ('Repair', 'Decrease malfunction chance', 1, 2, 'malfunction'),
}

# Predefined Tanks
# Format: id -> (name, (armor, ammo, power, dmg_mitigation))
PREDEFINED_TANKS: Dict[str, Tuple[str, Tuple[int, int, int, int]]] = {
    '1': ('Heavy Tank', (120, 7, 15, 13)),
    '2': ('Middle Tank', (110, 9, 14, 11)),
    '3': ('Light Tank', (95, 11, 12, 9)),
    '4': ('UltraLight Tank', (80, 15, 10, 7)),
}

# Attribute modification factors for custom tanks
ATTRIBUTE_FACTORS: Dict[str, int] = {
    'Armor': 5,
    'Ammo': 1,
    'Power': 1,
    'Dmg_mitigation': 1,
}

# Base stats for custom tank creation
BASE_STATS: Dict[str, int] = {
    'armor': 100,
    'ammo': 10,
    'power': 10,
    'dmg_mitigation': 10,
}

# Points available for custom tank creation
CUSTOM_TANK_POINTS: int = 20
