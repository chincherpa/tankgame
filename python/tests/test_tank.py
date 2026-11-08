"""
Unit tests for Tank class.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tank import Tank
from src.config import SETTINGS


class TestTankCreation:
    """Test tank initialization."""
    
    def test_tank_creation_basic(self):
        """Test basic tank creation with all parameters."""
        tank = Tank("TestTank", 100, 10, 15, 10)
        
        assert tank.name == "TestTank"
        assert tank.armor == 100
        assert tank.ammo == 10
        assert tank.power == 15
        assert tank.dmg_mitigation == 10
        assert tank.alive is True
    
    def test_tank_creation_with_dodge(self):
        """Test tank creation with custom dodge chance."""
        tank = Tank("DodgyTank", 100, 10, 15, 10, dodge_chance=25)
        
        assert tank.dodge_chance == 25
    
    def test_tank_creation_default_dodge(self):
        """Test tank creation uses default dodge chance."""
        tank = Tank("NormalTank", 100, 10, 15, 10)
        
        assert tank.dodge_chance == SETTINGS['base_dodge_chance']
    
    def test_tank_creation_initializes_stats(self):
        """Test that all statistics start at zero."""
        tank = Tank("StatTank", 100, 10, 15, 10)
        
        assert tank.shots == 0
        assert tank.hits == 0
        assert tank.misses == 0
        assert tank.malfuncs == 0
        assert tank.dmg == 0
        assert tank.dodges == 0
    
    def test_tank_armorstart_saved(self):
        """Test that initial armor is saved for percentage calculations."""
        tank = Tank("ArmorTank", 150, 10, 15, 10)
        
        assert tank.ARMORSTART == 150


class TestTankHit:
    """Test tank damage mechanics."""
    
    def test_hit_reduces_armor(self):
        """Test that being hit reduces armor."""
        tank = Tank("HitTank", 100, 10, 15, 0)  # 0 mitigation
        initial_armor = tank.armor
        
        tank.hit(20)
        
        assert tank.armor < initial_armor
    
    def test_hit_with_mitigation(self):
        """Test damage mitigation reduces damage."""
        tank = Tank("MitiTank", 100, 10, 15, 50)  # 50% mitigation
        
        tank.hit(20)  # Should only take 10 damage
        
        assert tank.armor == 90
    
    def test_hit_reduces_mitigation(self):
        """Test that being hit reduces damage mitigation."""
        tank = Tank("MitiTank", 100, 10, 15, 10)
        
        tank.hit(10)
        
        assert tank.dmg_mitigation == 9
    
    def test_hit_increases_malfunction(self):
        """Test that being hit increases malfunction chance."""
        tank = Tank("MalfTank", 100, 10, 15, 10)
        initial_malf = tank.malfunction
        
        tank.hit(10)
        
        assert tank.malfunction == initial_malf + 1
    
    def test_hit_tracks_damage(self):
        """Test that total damage is tracked."""
        tank = Tank("DmgTank", 100, 10, 15, 0)
        
        tank.hit(15)
        tank.hit(10)
        
        assert tank.dmg == 25
    
    def test_hit_counts_hits(self):
        """Test that hits are counted."""
        tank = Tank("CountTank", 100, 10, 15, 0)
        
        tank.hit(5)
        tank.hit(5)
        tank.hit(5)
        
        assert tank.hits == 3
    
    def test_armor_cannot_go_negative(self):
        """Test that armor doesn't go below zero."""
        tank = Tank("NegTank", 10, 10, 15, 0)
        
        tank.hit(100)  # Way more damage than armor
        
        assert tank.armor == 0
    
    def test_mitigation_cannot_go_negative(self):
        """Test that mitigation doesn't go below zero."""
        tank = Tank("MitiNegTank", 100, 10, 15, 1)
        
        tank.hit(5)
        tank.hit(5)  # Second hit should take mitigation to 0
        
        assert tank.dmg_mitigation == 0


class TestTankExplosion:
    """Test tank destruction mechanics."""
    
    def test_explode_sets_alive_false(self):
        """Test that explosion kills tank."""
        tank = Tank("ExplodeTank", 100, 10, 15, 0)
        
        tank.explode()
        
        assert tank.alive is False
    
    def test_zero_armor_triggers_explosion(self):
        """Test that zero armor causes explosion."""
        tank = Tank("ZeroTank", 10, 10, 15, 0)
        
        tank.hit(10)  # Exactly enough to hit zero
        
        assert tank.alive is False
    
    def test_overkill_triggers_explosion(self):
        """Test that overkill damage causes explosion."""
        tank = Tank("OverkillTank", 10, 10, 15, 0)
        
        tank.hit(100)  # Way more than armor
        
        assert tank.alive is False


class TestTankSerialization:
    """Test save/load functionality."""
    
    def test_to_dict(self):
        """Test tank serialization."""
        tank = Tank("SaveTank", 100, 10, 15, 10, dodge_chance=8)
        tank.shots = 5
        tank.hits = 3
        
        data = tank.to_dict()
        
        assert data['name'] == "SaveTank"
        assert data['armor'] == 100
        assert data['shots'] == 5
        assert data['hits'] == 3
        assert data['dodge_chance'] == 8
    
    def test_from_dict(self):
        """Test tank deserialization."""
        data = {
            'name': 'LoadTank',
            'armor': 80,
            'ammo': 8,
            'power': 12,
            'dmg_mitigation': 5,
            'dodge_chance': 15,
            'shots': 10,
            'hits': 7,
            'alive': True,
            'ARMORSTART': 100,
        }
        
        tank = Tank.from_dict(data)
        
        assert tank.name == 'LoadTank'
        assert tank.armor == 80
        assert tank.ammo == 8
        assert tank.shots == 10
        assert tank.dodge_chance == 15
    
    def test_roundtrip_serialization(self):
        """Test that save/load preserves all data."""
        original = Tank("RoundTripTank", 120, 15, 18, 12, dodge_chance=10)
        original.shots = 7
        original.hits = 4
        original.dmg = 45
        original.credits = 5
        
        data = original.to_dict()
        restored = Tank.from_dict(data)
        
        assert restored.name == original.name
        assert restored.armor == original.armor
        assert restored.shots == original.shots
        assert restored.hits == original.hits
        assert restored.dmg == original.dmg
        assert restored.credits == original.credits


class TestTankString:
    """Test string representation."""
    
    def test_str_alive_tank(self):
        """Test string for alive tank."""
        tank = Tank("StringTank", 100, 10, 15, 10)
        
        result = str(tank)
        
        assert "StringTank" in result
        assert "100%" in result  # Full armor
    
    def test_str_dead_tank(self):
        """Test string for dead tank."""
        tank = Tank("DeadTank", 100, 10, 15, 10)
        tank.alive = False
        
        result = str(tank)
        
        assert "zerstört" in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
