"""
Unit tests for Shop class.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shop import Shop
from src.tank import Tank
from src.config import ITEMS


class TestShopCreation:
    """Test shop initialization."""
    
    def test_shop_has_items(self):
        """Test shop loads items from config."""
        shop = Shop()
        
        assert shop.items == ITEMS
        assert len(shop.items) > 0
    
    def test_shop_items_have_required_fields(self):
        """Test each item has required fields."""
        shop = Shop()
        
        for item_id, item_data in shop.items.items():
            assert len(item_data) == 5  # name, desc, value, price, attribute
            name, desc, value, price, attr = item_data
            assert isinstance(name, str)
            assert isinstance(desc, str)
            assert isinstance(value, int)
            assert isinstance(price, int)
            assert attr in ['armor', 'ammo', 'malfunction']


class TestShopBuy:
    """Test purchase mechanics."""
    
    def test_buy_armor_increases_armor(self):
        """Test buying armor item increases tank armor."""
        shop = Shop()
        tank = Tank("ShopTank", 100, 10, 15, 10)
        tank.credits = 10  # Enough credits
        initial_armor = tank.armor
        
        result = shop.buy(tank, '1')  # Armor+10
        
        assert result is True
        assert tank.armor == initial_armor + 10
    
    def test_buy_ammo_increases_ammo(self):
        """Test buying ammo increases tank ammo."""
        shop = Shop()
        tank = Tank("AmmoTank", 100, 10, 15, 10)
        tank.credits = 10
        initial_ammo = tank.ammo
        
        result = shop.buy(tank, '3')  # Ammo+2
        
        assert result is True
        assert tank.ammo == initial_ammo + 2
    
    def test_buy_deducts_credits(self):
        """Test purchase deducts correct credit amount."""
        shop = Shop()
        tank = Tank("CreditTank", 100, 10, 15, 10)
        tank.credits = 10
        
        shop.buy(tank, '1')  # Armor+10 costs 3 credits
        
        assert tank.credits == 7
    
    def test_buy_fails_insufficient_credits(self):
        """Test purchase fails without enough credits."""
        shop = Shop()
        tank = Tank("PoorTank", 100, 10, 15, 10)
        tank.credits = 1  # Not enough for anything
        initial_armor = tank.armor
        
        result = shop.buy(tank, '2')  # Armor+20 costs 5
        
        assert result is False
        assert tank.armor == initial_armor
        assert tank.credits == 1  # Credits unchanged
    
    def test_buy_invalid_item(self):
        """Test purchasing invalid item fails."""
        shop = Shop()
        tank = Tank("InvalidTank", 100, 10, 15, 10)
        tank.credits = 10
        
        result = shop.buy(tank, '99')  # Invalid item ID
        
        assert result is False
    
    def test_buy_repair_reduces_malfunction(self):
        """Test repair item reduces malfunction chance."""
        shop = Shop()
        tank = Tank("RepairTank", 100, 10, 15, 10)
        tank.credits = 10
        tank.malfunction = 20
        
        result = shop.buy(tank, '4')  # Repair item
        
        assert result is True
        assert tank.malfunction == 19
    
    def test_malfunction_cannot_go_negative(self):
        """Test malfunction doesn't go below 0."""
        shop = Shop()
        tank = Tank("LowMalfTank", 100, 10, 15, 10)
        tank.credits = 10
        tank.malfunction = 0
        
        shop.buy(tank, '4')  # Repair when at 0
        
        assert tank.malfunction == 0


class TestShopDisplay:
    """Test shop display functions."""
    
    @patch('src.shop.ui.display_shop')
    def test_display_calls_ui(self, mock_display):
        """Test display method calls UI function."""
        shop = Shop()
        tank = Tank("DisplayTank", 100, 10, 15, 10)
        
        shop.display(tank)
        
        mock_display.assert_called_once_with(tank)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
