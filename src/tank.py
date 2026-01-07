"""
Tankgame Tank Class
Represents a tank with all its attributes and combat methods.
"""

import random
from time import sleep
from typing import Optional

from .config import SETTINGS, DEBUG
from . import ui


class Tank:
    """
    Represents a tank in the game.
    
    Attributes:
        name: Name of the tank/player
        armor: Current armor points
        ammo: Remaining ammunition
        power: Damage per shot
        dmg_mitigation: Percentage of damage reduction
        miss: Probability to miss (%)
        malfunction: Probability of malfunction (%)
        credits: Currency for shop purchases
        alive: Whether the tank is alive
        dodge_chance: Probability to dodge incoming attacks (%)
        ARMORSTART: Initial armor for percentage calculations
        shots: Total shots fired
        hits: Times this tank was hit
        malfuncs: Number of malfunctions
        dmg: Total damage received
        misses: Number of missed shots
    """
    
    def __init__(
        self, 
        name: str, 
        armor: int, 
        ammo: int, 
        power: int, 
        dmg_mitigation: int,
        dodge_chance: Optional[int] = None
    ):
        self.name = name
        self.armor = armor
        self.ammo = ammo
        self.power = power
        self.dmg_mitigation = dmg_mitigation
        self.dodge_chance = dodge_chance if dodge_chance is not None else SETTINGS['base_dodge_chance']
        
        # From settings
        self.miss = SETTINGS['probability_to_miss']
        self.malfunction = SETTINGS['probability_of_malfunction']
        self.credits = SETTINGS['credits']
        
        # State
        self.alive = True
        self.ARMORSTART = armor
        
        # Statistics
        self.shots = 0
        self.hits = 0
        self.malfuncs = 0
        self.dmg = 0
        self.misses = 0
        self.dodges = 0
    
    def __str__(self) -> str:
        """Return string representation of tank status."""
        if self.alive:
            armor_percent = int((self.armor / self.ARMORSTART) * 100)
            return (
                f"{self.name} hat {armor_percent}% Panzerung und {self.ammo} Munition "
                f"({self.power} Power).\n"
                f"• Schadensreduktion: {self.dmg_mitigation}%\n"
                f"• Fehlschuss-Chance: {self.miss}%\n"
                f"• Fehlfunktions-Chance: {self.malfunction}%\n"
                f"• Ausweich-Chance: {self.dodge_chance}%"
            )
        else:
            return f"{self.name} wurde zerstört!"
    
    def to_dict(self) -> dict:
        """Convert tank to dictionary for saving."""
        return {
            'name': self.name,
            'armor': self.armor,
            'ammo': self.ammo,
            'power': self.power,
            'dmg_mitigation': self.dmg_mitigation,
            'dodge_chance': self.dodge_chance,
            'miss': self.miss,
            'malfunction': self.malfunction,
            'credits': self.credits,
            'alive': self.alive,
            'ARMORSTART': self.ARMORSTART,
            'shots': self.shots,
            'hits': self.hits,
            'malfuncs': self.malfuncs,
            'dmg': self.dmg,
            'misses': self.misses,
            'dodges': self.dodges,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Tank':
        """Create tank from dictionary."""
        tank = cls(
            name=data['name'],
            armor=data['armor'],
            ammo=data['ammo'],
            power=data['power'],
            dmg_mitigation=data['dmg_mitigation'],
            dodge_chance=data.get('dodge_chance', SETTINGS['base_dodge_chance'])
        )
        tank.miss = data.get('miss', SETTINGS['probability_to_miss'])
        tank.malfunction = data.get('malfunction', SETTINGS['probability_of_malfunction'])
        tank.credits = data.get('credits', SETTINGS['credits'])
        tank.alive = data.get('alive', True)
        tank.ARMORSTART = data.get('ARMORSTART', tank.armor)
        tank.shots = data.get('shots', 0)
        tank.hits = data.get('hits', 0)
        tank.malfuncs = data.get('malfuncs', 0)
        tank.dmg = data.get('dmg', 0)
        tank.misses = data.get('misses', 0)
        tank.dodges = data.get('dodges', 0)
        return tank
    
    def check_malfunction(self) -> bool:
        """
        Check if tank has a malfunction.
        
        Returns:
            True if malfunction occurred
        """
        roll = random.randint(1, 100)
        if roll <= self.malfunction:
            self.malfuncs += 1
            ui.animate_malfunction(self.name)
            return True
        return False
    
    def try_dodge(self) -> bool:
        """
        Attempt to dodge an incoming attack.
        
        Returns:
            True if dodge successful
        """
        roll = random.randint(1, 100)
        if roll <= self.dodge_chance:
            self.dodges += 1
            ui.animate_dodge(self.name)
            return True
        return False
    
    def fire_at(self, target: 'Tank') -> str:
        """
        Fire at a target tank.
        
        Args:
            target: The tank to fire at
            
        Returns:
            'hit', 'miss', or 'dodge'
        """
        self.shots += 1
        self.ammo -= 1
        
        # Animate shooting
        ui.animate_shooting(self.name, target.name)
        
        if not DEBUG:
            ui.print_slow('/' + '─' * 20 + '\\')
        
        # Check if attacker misses
        hit_roll = random.randint(1, 100)
        if hit_roll <= self.miss:
            self.misses += 1
            ui.animate_miss()
            if not DEBUG:
                sleep(0.5)
            return 'miss'
        
        # Check if target dodges
        if target.try_dodge():
            return 'dodge'
        
        # Hit confirmed
        self.credits += 1
        target.hit(self.power)
        return 'hit'
    
    def hit(self, power: int) -> None:
        """
        Process being hit by an attack.
        
        Args:
            power: The attack power
        """
        self.hits += 1
        
        # Calculate damage with mitigation
        damage = int(power * (100 - self.dmg_mitigation) / 100)
        self.dmg += damage
        self.armor -= damage
        
        if self.armor < 0:
            self.armor = 0
        
        # Reduce mitigation
        self.dmg_mitigation = max(0, self.dmg_mitigation - 1)
        
        # Increase malfunction chance
        self.malfunction += 1
        
        # Show hit animation
        ui.animate_hit(self.name, damage)
        
        # Check for destruction
        if self.armor == 0:
            self.explode()
    
    def explode(self) -> None:
        """Handle tank destruction."""
        self.alive = False
        ui.animate_explosion(self.name)


# Allow running this file for testing
if __name__ == '__main__':
    print('\n⚠️ This file should not be run directly.')
    print('Use: python -m src.main\n')
