"""
Tankgame Shop System
Handles buying items and upgrading tanks.
"""

from typing import Optional
from time import sleep

from .config import ITEMS, DEBUG
from .tank import Tank
from . import ui


class Shop:
    """
    Shop system for purchasing upgrades.
    
    Attributes:
        items: Available items for purchase
    """
    
    def __init__(self):
        self.items = ITEMS
    
    def display(self, player: Tank) -> None:
        """Display the shop interface."""
        ui.display_shop(player)
    
    def buy(self, player: Tank, item_id: str) -> bool:
        """
        Attempt to purchase an item.
        
        Args:
            player: The tank making the purchase
            item_id: ID of the item to buy
            
        Returns:
            True if purchase successful, False otherwise
        """
        if item_id not in self.items:
            print('\nArtikel existiert nicht!')
            return False
        
        name, description, value, price, attribute = self.items[item_id]
        
        if player.credits < price:
            print(f'\nNicht genug Credits für {name}!')
            print(f'{name} kostet {price} Credits.')
            print(f'Du hast {player.credits} Credits.\n')
            return False
        
        # Apply the purchase
        player.credits -= price
        
        if attribute == 'armor':
            player.armor += value
            print(f'\n{player.name} hat {value} Panzerung erhalten.')
        elif attribute == 'ammo':
            player.ammo += value
            print(f'\n{player.name} hat {value} Munition erhalten.')
        elif attribute == 'malfunction':
            player.malfunction = max(0, player.malfunction - value)
            print(f'\n{player.name} hat die Fehlfunktions-Chance um {value}% reduziert.')
        
        print(f'\n✓ {name} für {price} Credits gekauft!')
        
        if not DEBUG:
            sleep(1)
        
        return True
    
    def run(self, player: Tank) -> bool:
        """
        Run the shop interface.
        
        Args:
            player: The tank shopping
            
        Returns:
            True if a purchase was made, False if cancelled
        """
        while True:
            self.display(player)
            
            try:
                choice = input('\nWas möchtest du kaufen? (0 zum Abbrechen)\t').strip()
                
                if not choice:
                    continue
                
                if choice == '0':
                    print('\nAbgebrochen...')
                    if not DEBUG:
                        sleep(0.5)
                    return False
                
                if choice in self.items:
                    if self.buy(player, choice):
                        return True
                else:
                    print('\nUngültige Auswahl!')
                    if not DEBUG:
                        sleep(0.5)
                        
            except KeyboardInterrupt:
                print('\nAbgebrochen.')
                return False


# Singleton shop instance
shop = Shop()
