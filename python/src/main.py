#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tankgame - A terminal-based tank combat game.

Usage:
    python -m src.main
    
Or from the project root:
    python run.py
"""

from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import DEBUG
from .game import Game
from .utils import safe_choice_input, safe_int_input, clear_screen
from . import save_system
from . import ui

console = Console()


def display_main_menu() -> None:
    """Display the main menu."""
    console.print(Panel(
        "[bold cyan]🎮 TANKGAME[/bold cyan]\n\n"
        "Ein Terminal-basiertes Panzer-Kampfspiel",
        border_style="cyan"
    ))
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="bold yellow")
    table.add_column("Beschreibung")
    
    table.add_row("[P]", "Player vs Player")
    table.add_row("[C]", "Player vs Computer")
    table.add_row("[L]", "Spielstand laden")
    table.add_row("[I]", "Anleitung")
    table.add_row("[Q]", "Beenden")
    
    console.print(table)
    console.print()


def display_load_menu() -> None:
    """Display saved games."""
    saves = save_system.list_saves()
    
    if not saves:
        console.print("\n[yellow]Keine Spielstände vorhanden.[/yellow]\n")
        return
    
    table = Table(title="📁 Spielstände", show_header=True)
    table.add_column("#", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Datum")
    table.add_column("Modus")
    table.add_column("Spieler")
    
    for i, save in enumerate(saves, 1):
        timestamp = save['timestamp'][:19].replace('T', ' ')
        table.add_row(
            str(i),
            save['filename'],
            timestamp,
            save['mode'].upper(),
            save['players']
        )
    
    console.print(table)


def load_game_menu() -> Game | None:
    """Show load game menu and return loaded game."""
    saves = save_system.list_saves()
    
    if not saves:
        display_load_menu()
        return None
    
    display_load_menu()
    
    choice = safe_int_input(
        '\nSpielstand auswählen (0 zum Abbrechen): ',
        valid_range=range(0, len(saves) + 1),
        default=0
    )
    
    if choice is None or choice == 0:
        return None
    
    filename = saves[choice - 1]['filename']
    save_data = save_system.load_game(filename)
    
    if save_data:
        console.print(f"\n[green]✓ Spielstand '{filename}' geladen![/green]\n")
        sleep(1)
        return Game.from_save(save_data)
    
    return None


def main() -> None:
    """Main entry point."""
    while True:
        clear_screen()
        display_main_menu()
        
        choice = safe_choice_input(
            'Auswahl: ',
            ['p', 'c', 'l', 'i', 'q']
        )
        
        if choice == 'q':
            console.print("\n[cyan]Auf Wiedersehen! 👋[/cyan]\n")
            break
        
        elif choice == 'i':
            clear_screen()
            ui.display_instructions()
            input('\nDrücke Enter...')
        
        elif choice == 'l':
            clear_screen()
            game = load_game_menu()
            if game:
                game.run()
        
        elif choice == 'p':
            # PvP Mode
            num_players = safe_int_input(
                '\nAnzahl Spieler (2-8): ',
                valid_range=range(2, 9),
                default=2
            ) or 2
            
            game = Game(mode='pvp')
            game.setup_pvp(num_players)
            game.run()
        
        elif choice == 'c':
            # PvC Mode
            game = Game(mode='pvc')
            game.setup_pvc()
            game.run()


if __name__ == '__main__':
    main()
