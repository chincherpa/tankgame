"""
Tankgame Game Logic
Main game controller handling game flow and player turns.
"""

import random
from time import sleep
from typing import Dict, Optional, List, Tuple

from rich.console import Console

from .config import (
    DEBUG, PREDEFINED_TANKS, ATTRIBUTE_FACTORS, 
    BASE_STATS, CUSTOM_TANK_POINTS, SETTINGS
)
from .tank import Tank
from .shop import shop
from . import ui
from .utils import (
    safe_int_input, safe_choice_input, represents_int, 
    spinning_cursor, get_4_randoms, clear_screen
)
from . import save_system

console = Console()


class Game:
    """
    Main game controller.
    
    Attributes:
        mode: Game mode ('pvp' or 'pvc')
        tanks: Dictionary of tank_id -> Tank
        current_player_idx: Index of current player
        is_running: Whether game is still running
    """
    
    def __init__(self, mode: str = 'pvp'):
        self.mode = mode
        self.tanks: Dict[str, Tank] = {}
        self.current_player_idx: int = 0
        self.is_running: bool = True
        self._player_order: List[str] = []
    
    @classmethod
    def from_save(cls, save_data: dict) -> 'Game':
        """
        Create a game instance from save data.
        
        Args:
            save_data: Dictionary from save file
            
        Returns:
            Restored Game instance
        """
        game = cls(mode=save_data.get('mode', 'pvp'))
        game.current_player_idx = save_data.get('current_player_idx', 0)
        
        for tank_id, tank_data in save_data.get('tanks', {}).items():
            game.tanks[tank_id] = Tank.from_dict(tank_data)
        
        game._player_order = list(game.tanks.keys())
        return game
    
    def setup_pvp(self, num_players: int = 2) -> None:
        """
        Set up a Player vs Player game.
        
        Args:
            num_players: Number of players
        """
        clear_screen()
        
        for i in range(1, num_players + 1):
            name = input(f'\nName von Spieler {i}? ').strip() or f'Spieler {i}'
            
            clear_screen()
            print(f'\n{name}, wähle deinen Panzer:\n')
            
            attributes = self._select_or_create_tank(name)
            if attributes:
                tank_id = str(i)
                self.tanks[tank_id] = Tank(name, *attributes)
                self._player_order.append(tank_id)
            
            clear_screen()
        
        self.current_player_idx = 0
    
    def setup_pvc(self) -> None:
        """Set up a Player vs Computer game."""
        clear_screen()
        
        name = input('\nDein Name? ').strip() or 'Spieler'
        
        print(f'\n{name}, wähle deinen Panzer:\n')
        attributes = self._select_or_create_tank(name)
        
        if attributes:
            self.tanks['1'] = Tank(name, *attributes)
            self._player_order.append('1')
        
        # Generate computer tank
        print()
        spinning_cursor(3, "Generiere Computer-Panzer...")
        
        comp_attrs = self._create_random_tank()
        self.tanks['2'] = Tank('Computer', *comp_attrs)
        self._player_order.append('2')
        
        clear_screen()
    
    def _select_or_create_tank(self, player_name: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Let player select a predefined tank or create custom.
        
        Returns:
            Tuple of (armor, ammo, power, dmg_mitigation) or None
        """
        while True:
            choice = safe_choice_input(
                f'\n{player_name}: [P]redefinierter Panzer oder [M]odifiziert? ',
                ['p', 'm']
            )
            
            if choice == 'm':
                return self._create_custom_tank(player_name)
            elif choice == 'p':
                result = self._select_predefined_tank()
                if result:
                    return result
            else:
                return None
    
    def _select_predefined_tank(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Display tank selection and return chosen tank stats.
        
        Returns:
            Tank stats tuple or None if cancelled
        """
        ui.display_tank_selection()
        
        choice = safe_int_input(
            '\nPanzer auswählen: ',
            valid_range=range(0, len(PREDEFINED_TANKS) + 1),
            default=0
        )
        
        if choice is None or choice == 0:
            return None
        
        tank_key = str(choice)
        if tank_key in PREDEFINED_TANKS:
            return PREDEFINED_TANKS[tank_key][1]
        
        return None
    
    def _create_custom_tank(self, player_name: str) -> Tuple[int, int, int, int]:
        """
        Let player distribute points to create a custom tank.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Tank stats tuple
        """
        points = CUSTOM_TANK_POINTS
        stats = dict(BASE_STATS)
        
        while points > 0:
            clear_screen()
            print(f'\n{player_name}, dein Panzer hat:\n')
            print(f'  Armor:          {stats["armor"]} ({ATTRIBUTE_FACTORS["Armor"]} pro Punkt)')
            print(f'  Ammo:           {stats["ammo"]} ({ATTRIBUTE_FACTORS["Ammo"]} pro Punkt)')
            print(f'  Power:          {stats["power"]} ({ATTRIBUTE_FACTORS["Power"]} pro Punkt)')
            print(f'  Dmg Mitigation: {stats["dmg_mitigation"]} ({ATTRIBUTE_FACTORS["Dmg_mitigation"]} pro Punkt)')
            print(f'\nVerfügbare Punkte: {points}\n')
            
            # Armor
            if points > 0:
                armor_pts = safe_int_input(
                    f'Punkte für ARMOR ({points}p übrig)? ',
                    valid_range=range(0, points + 1),
                    default=0
                ) or 0
                points -= armor_pts
                stats['armor'] += armor_pts * ATTRIBUTE_FACTORS['Armor']
            
            # Ammo
            if points > 0:
                ammo_pts = safe_int_input(
                    f'Punkte für AMMO ({points}p übrig)? ',
                    valid_range=range(0, points + 1),
                    default=0
                ) or 0
                points -= ammo_pts
                stats['ammo'] += ammo_pts * ATTRIBUTE_FACTORS['Ammo']
            
            # Power
            if points > 0:
                power_pts = safe_int_input(
                    f'Punkte für POWER ({points}p übrig)? ',
                    valid_range=range(0, points + 1),
                    default=0
                ) or 0
                points -= power_pts
                stats['power'] += power_pts * ATTRIBUTE_FACTORS['Power']
            
            # Damage mitigation (use remaining points)
            if points > 0:
                dmg_pts = safe_int_input(
                    f'Punkte für DMG MITIGATION ({points}p übrig)? ',
                    valid_range=range(0, points + 1),
                    default=0
                ) or 0
                points -= dmg_pts
                stats['dmg_mitigation'] += dmg_pts * ATTRIBUTE_FACTORS['Dmg_mitigation']
        
        print(f'\n✓ Panzer erstellt!')
        if not DEBUG:
            sleep(1)
        
        return (stats['armor'], stats['ammo'], stats['power'], stats['dmg_mitigation'])
    
    def _create_random_tank(self) -> Tuple[int, int, int, int]:
        """Create a random tank with randomly distributed points."""
        points = get_4_randoms(CUSTOM_TANK_POINTS)
        
        armor = BASE_STATS['armor'] + points[0] * ATTRIBUTE_FACTORS['Armor']
        ammo = BASE_STATS['ammo'] + points[1] * ATTRIBUTE_FACTORS['Ammo']
        power = BASE_STATS['power'] + points[2] * ATTRIBUTE_FACTORS['Power']
        dmg_mit = BASE_STATS['dmg_mitigation'] + points[3] * ATTRIBUTE_FACTORS['Dmg_mitigation']
        
        return (armor, ammo, power, dmg_mit)
    
    def get_alive_count(self) -> int:
        """Return number of alive tanks."""
        return sum(1 for t in self.tanks.values() if t.alive)
    
    def get_current_tank(self) -> Tank:
        """Get the current player's tank."""
        tank_id = self._player_order[self.current_player_idx]
        return self.tanks[tank_id]
    
    def get_opponent_tank(self) -> Tank:
        """Get opponent tank (for 2-player games)."""
        opponent_idx = (self.current_player_idx + 1) % len(self._player_order)
        tank_id = self._player_order[opponent_idx]
        return self.tanks[tank_id]
    
    def next_player(self) -> None:
        """Advance to next player, skipping dead tanks."""
        attempts = 0
        while attempts < len(self._player_order):
            self.current_player_idx = (self.current_player_idx + 1) % len(self._player_order)
            if self.get_current_tank().alive:
                return
            attempts += 1
    
    def run(self) -> None:
        """Main game loop."""
        while self.is_running and self.get_alive_count() > 1:
            clear_screen()
            ui.display_tank_table(self.tanks)
            
            if self.mode == 'pvp':
                self._play_pvp_turn()
            else:
                self._play_pvc_turn()
            
            if not DEBUG:
                sleep(1)
        
        # Game over
        self._show_game_over()
    
    def _play_pvp_turn(self) -> None:
        """Handle a PvP turn."""
        current = self.get_current_tank()
        
        if not current.alive:
            self.next_player()
            return
        
        ui.display_turn(current.name)
        
        action = safe_choice_input(
            '[S]chießen, [B]uying, [N]ichts tun, [Q]uit? ',
            ['s', 'b', 'n', 'q', 'save']
        )
        
        if action == 'q':
            self.is_running = False
            return
        
        if action == 'save':
            filename = input('Dateiname zum Speichern: ').strip() or 'quicksave'
            save_system.save_game(self, filename)
            if not DEBUG:
                sleep(1)
            return
        
        if action == 'b':
            shop.run(current)
        elif action == 's':
            self._handle_shoot(current)
        elif action == 'n':
            self._do_nothing(current)
        
        self.next_player()
    
    def _play_pvc_turn(self) -> None:
        """Handle a PvC turn."""
        current = self.get_current_tank()
        
        if not current.alive:
            self.next_player()
            return
        
        is_computer = current.name == 'Computer'
        ui.display_turn(current.name, is_computer)
        
        if is_computer:
            self._computer_turn()
        else:
            self._player_turn()
        
        self.next_player()
    
    def _player_turn(self) -> None:
        """Handle human player's turn in PvC mode."""
        current = self.get_current_tank()
        
        action = safe_choice_input(
            '[S]chießen, [B]uying, [N]ichts tun, [Q]uit? ',
            ['s', 'b', 'n', 'q', 'save']
        )
        
        if action == 'q':
            self.is_running = False
            return
        
        if action == 'save':
            filename = input('Dateiname zum Speichern: ').strip() or 'quicksave'
            save_system.save_game(self, filename)
            return
        
        if action == 'b':
            shop.run(current)
        elif action == 's':
            self._handle_shoot(current)
        elif action == 'n':
            self._do_nothing(current)
    
    def _computer_turn(self) -> None:
        """Handle computer's turn."""
        computer = self.get_current_tank()
        player = self.get_opponent_tank()
        
        if not DEBUG:
            sleep(0.5)
        
        # Simple AI: always shoot if possible
        if computer.ammo > 0:
            if computer.check_malfunction():
                if not DEBUG:
                    sleep(1)
                return
            
            computer.fire_at(player)
        else:
            self._do_nothing(computer)
    
    def _handle_shoot(self, attacker: Tank) -> None:
        """Handle shooting action."""
        if attacker.ammo <= 0:
            print('\n⚠️ Keine Munition mehr!')
            go_shop = safe_choice_input('Im Shop kaufen? [j/n] ', ['j', 'n'])
            if go_shop == 'j':
                shop.run(attacker)
            return
        
        # Check for malfunction
        if attacker.check_malfunction():
            if not DEBUG:
                sleep(1)
            return
        
        # Get target (for 2 players, auto-target opponent)
        if len(self.tanks) == 2:
            target = self.get_opponent_tank()
        else:
            target = self._select_target(attacker)
            if not target:
                return
        
        # Fire!
        attacker.fire_at(target)
    
    def _select_target(self, attacker: Tank) -> Optional[Tank]:
        """Let player select a target tank."""
        valid_targets = []
        
        for tank_id, tank in self.tanks.items():
            if tank != attacker and tank.alive:
                valid_targets.append(tank_id)
        
        if not valid_targets:
            print('\nKeine gültigen Ziele!')
            return None
        
        print('\nVerfügbare Ziele:')
        for i, tank_id in enumerate(valid_targets, 1):
            print(f'  {i}. {self.tanks[tank_id].name}')
        
        choice = safe_int_input(
            'Ziel auswählen: ',
            valid_range=range(1, len(valid_targets) + 1)
        )
        
        if choice is None:
            return None
        
        return self.tanks[valid_targets[choice - 1]]
    
    def _do_nothing(self, tank: Tank) -> None:
        """Handle 'do nothing' action."""
        tank.credits += 1
        print(f'\n{tank.name} wartet und erhält 1 Credit.')
        if not DEBUG:
            sleep(0.5)
    
    def _show_game_over(self) -> None:
        """Display game over screen."""
        clear_screen()
        
        # Find winner
        winner = None
        for tank in self.tanks.values():
            if tank.alive:
                winner = tank
                break
        
        if winner:
            if self.mode == 'pvc':
                ui.display_winner(winner.name, is_computer=(winner.name == 'Computer'))
            else:
                ui.display_winner(winner.name)
        
        # Show final stats
        ui.display_tank_table(self.tanks, show_stats=True)
        
        input('\nDrücke Enter zum Beenden...')
