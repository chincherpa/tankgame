"""
Tankgame Save/Load System
Handles game state persistence.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

# Default saves directory
SAVES_DIR = Path(__file__).parent.parent / 'saves'


def ensure_saves_dir() -> None:
    """Ensure the saves directory exists."""
    SAVES_DIR.mkdir(exist_ok=True)


def get_save_path(filename: str) -> Path:
    """Get the full path to a save file."""
    ensure_saves_dir()
    if not filename.endswith('.json'):
        filename += '.json'
    return SAVES_DIR / filename


def save_exists(filename: str) -> bool:
    """Check if a save file exists."""
    return get_save_path(filename).exists()


def list_saves() -> List[Dict[str, str]]:
    """
    List all available save files.
    
    Returns:
        List of dicts with 'filename', 'timestamp', and 'display_name'
    """
    ensure_saves_dir()
    saves = []
    
    for file in SAVES_DIR.glob('*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            saves.append({
                'filename': file.stem,
                'timestamp': data.get('timestamp', 'Unknown'),
                'mode': data.get('mode', 'Unknown'),
                'players': ', '.join(data.get('player_names', [])),
            })
        except (json.JSONDecodeError, KeyError):
            # Skip corrupted saves
            continue
    
    # Sort by timestamp, newest first
    saves.sort(key=lambda x: x['timestamp'], reverse=True)
    return saves


def save_game(game: 'Game', filename: str) -> bool:
    """
    Save the current game state.
    
    Args:
        game: The game instance to save
        filename: Name for the save file
        
    Returns:
        True if save successful
    """
    try:
        save_data = {
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'mode': game.mode,
            'player_names': [t.name for t in game.tanks.values()],
            'current_player_idx': game.current_player_idx,
            'tanks': {
                tank_id: tank.to_dict() 
                for tank_id, tank in game.tanks.items()
            },
        }
        
        path = get_save_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f'\n✓ Spiel gespeichert: {filename}')
        return True
        
    except Exception as e:
        print(f'\n✗ Fehler beim Speichern: {e}')
        return False


def load_game(filename: str) -> Optional[dict]:
    """
    Load a saved game state.
    
    Args:
        filename: Name of the save file
        
    Returns:
        Save data dict or None if failed
    """
    try:
        path = get_save_path(filename)
        
        if not path.exists():
            print(f'\n✗ Spielstand nicht gefunden: {filename}')
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Version check
        version = data.get('version', '1.0')
        if version.split('.')[0] != '2':
            print(f'\n⚠️ Alter Spielstand (v{version}), möglicherweise inkompatibel.')
        
        return data
        
    except json.JSONDecodeError:
        print(f'\n✗ Spielstand beschädigt: {filename}')
        return None
    except Exception as e:
        print(f'\n✗ Fehler beim Laden: {e}')
        return None


def delete_save(filename: str) -> bool:
    """
    Delete a save file.
    
    Args:
        filename: Name of the save file
        
    Returns:
        True if deletion successful
    """
    try:
        path = get_save_path(filename)
        if path.exists():
            path.unlink()
            print(f'\n✓ Spielstand gelöscht: {filename}')
            return True
        else:
            print(f'\n✗ Spielstand nicht gefunden: {filename}')
            return False
    except Exception as e:
        print(f'\n✗ Fehler beim Löschen: {e}')
        return False
