"""
Unit tests for Game class.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import Game
from src.tank import Tank


class TestGameCreation:
    """Test game initialization."""
    
    def test_game_creation_pvp(self):
        """Test creating a PvP game."""
        game = Game(mode='pvp')
        
        assert game.mode == 'pvp'
        assert game.tanks == {}
        assert game.is_running is True
    
    def test_game_creation_pvc(self):
        """Test creating a PvC game."""
        game = Game(mode='pvc')
        
        assert game.mode == 'pvc'
        assert game.tanks == {}
    
    def test_game_default_mode_is_pvp(self):
        """Test default game mode is PvP."""
        game = Game()
        
        assert game.mode == 'pvp'


class TestGameAliveCount:
    """Test alive tank counting."""
    
    def test_get_alive_count_all_alive(self):
        """Test counting when all tanks alive."""
        game = Game()
        game.tanks = {
            '1': Tank('Tank1', 100, 10, 15, 10),
            '2': Tank('Tank2', 100, 10, 15, 10),
        }
        
        assert game.get_alive_count() == 2
    
    def test_get_alive_count_one_dead(self):
        """Test counting with one dead tank."""
        game = Game()
        game.tanks = {
            '1': Tank('Tank1', 100, 10, 15, 10),
            '2': Tank('Tank2', 100, 10, 15, 10),
        }
        game.tanks['1'].alive = False
        
        assert game.get_alive_count() == 1
    
    def test_get_alive_count_all_dead(self):
        """Test counting when all tanks dead."""
        game = Game()
        game.tanks = {
            '1': Tank('Tank1', 100, 10, 15, 10),
            '2': Tank('Tank2', 100, 10, 15, 10),
        }
        game.tanks['1'].alive = False
        game.tanks['2'].alive = False
        
        assert game.get_alive_count() == 0
    
    def test_get_alive_count_empty(self):
        """Test counting with no tanks."""
        game = Game()
        
        assert game.get_alive_count() == 0


class TestGamePlayerManagement:
    """Test player turn management."""
    
    def test_get_current_tank(self):
        """Test getting current player's tank."""
        game = Game()
        tank1 = Tank('Tank1', 100, 10, 15, 10)
        tank2 = Tank('Tank2', 100, 10, 15, 10)
        game.tanks = {'1': tank1, '2': tank2}
        game._player_order = ['1', '2']
        game.current_player_idx = 0
        
        assert game.get_current_tank() == tank1
    
    def test_get_opponent_tank(self):
        """Test getting opponent's tank."""
        game = Game()
        tank1 = Tank('Tank1', 100, 10, 15, 10)
        tank2 = Tank('Tank2', 100, 10, 15, 10)
        game.tanks = {'1': tank1, '2': tank2}
        game._player_order = ['1', '2']
        game.current_player_idx = 0
        
        assert game.get_opponent_tank() == tank2
    
    def test_next_player_advances(self):
        """Test next player advances turn."""
        game = Game()
        tank1 = Tank('Tank1', 100, 10, 15, 10)
        tank2 = Tank('Tank2', 100, 10, 15, 10)
        game.tanks = {'1': tank1, '2': tank2}
        game._player_order = ['1', '2']
        game.current_player_idx = 0
        
        game.next_player()
        
        assert game.current_player_idx == 1
    
    def test_next_player_wraps_around(self):
        """Test next player wraps to first player."""
        game = Game()
        tank1 = Tank('Tank1', 100, 10, 15, 10)
        tank2 = Tank('Tank2', 100, 10, 15, 10)
        game.tanks = {'1': tank1, '2': tank2}
        game._player_order = ['1', '2']
        game.current_player_idx = 1
        
        game.next_player()
        
        assert game.current_player_idx == 0
    
    def test_next_player_skips_dead(self):
        """Test next player skips dead tanks."""
        game = Game()
        tank1 = Tank('Tank1', 100, 10, 15, 10)
        tank2 = Tank('Tank2', 100, 10, 15, 10)
        tank3 = Tank('Tank3', 100, 10, 15, 10)
        game.tanks = {'1': tank1, '2': tank2, '3': tank3}
        game._player_order = ['1', '2', '3']
        game.current_player_idx = 0
        tank2.alive = False  # Tank 2 is dead
        
        game.next_player()
        
        # Should skip tank 2 and go to tank 3
        assert game.current_player_idx == 2


class TestGameSaveLoad:
    """Test game save/load functionality."""
    
    def test_from_save_restores_mode(self):
        """Test loading restores game mode."""
        save_data = {
            'mode': 'pvc',
            'current_player_idx': 1,
            'tanks': {
                '1': {
                    'name': 'Player',
                    'armor': 80,
                    'ammo': 8,
                    'power': 15,
                    'dmg_mitigation': 5,
                    'alive': True,
                    'ARMORSTART': 100,
                },
                '2': {
                    'name': 'Computer',
                    'armor': 90,
                    'ammo': 6,
                    'power': 12,
                    'dmg_mitigation': 8,
                    'alive': True,
                    'ARMORSTART': 100,
                }
            }
        }
        
        game = Game.from_save(save_data)
        
        assert game.mode == 'pvc'
        assert game.current_player_idx == 1
        assert len(game.tanks) == 2
    
    def test_from_save_restores_tanks(self):
        """Test loading restores tank states."""
        save_data = {
            'mode': 'pvp',
            'current_player_idx': 0,
            'tanks': {
                '1': {
                    'name': 'Tank1',
                    'armor': 50,
                    'ammo': 5,
                    'power': 15,
                    'dmg_mitigation': 3,
                    'alive': True,
                    'ARMORSTART': 100,
                    'shots': 10,
                    'hits': 5,
                }
            }
        }
        
        game = Game.from_save(save_data)
        
        tank = game.tanks['1']
        assert tank.name == 'Tank1'
        assert tank.armor == 50
        assert tank.shots == 10


class TestRandomTankCreation:
    """Test random tank generation."""
    
    def test_create_random_tank_generates_valid_stats(self):
        """Test random tank has valid stats."""
        game = Game()
        
        armor, ammo, power, dmg_mit = game._create_random_tank()
        
        # Check that stats are positive and reasonable
        assert armor >= 100  # Base is 100
        assert ammo >= 10    # Base is 10
        assert power >= 10   # Base is 10
        assert dmg_mit >= 10 # Base is 10
    
    def test_create_random_tank_varies(self):
        """Test random tanks have variation."""
        game = Game()
        
        tanks = [game._create_random_tank() for _ in range(10)]
        
        # At least some should be different
        unique_tanks = set(tanks)
        assert len(unique_tanks) > 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
