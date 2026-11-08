"""
Tankgame UI Module
Handles all terminal output, tables, and animations.
"""

import sys
from time import sleep
from typing import Dict, List, Optional, TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from crayons import yellow, red

from .config import DEBUG, ITEMS, PREDEFINED_TANKS

if TYPE_CHECKING:
    from .tank import Tank

console = Console()


def print_slow(text: str, delay: float = 0.05) -> None:
    """Print text character by character."""
    for letter in text:
        print(letter, end='', flush=True)
        sleep(delay)
    print()


def print_red_banner(message: str, char: str = '#', width: int = 30) -> None:
    """Print a message in a red banner."""
    padding = (width - len(message)) // 2
    border = char * width
    padded_message = char * padding + message + char * padding
    
    # Adjust for odd lengths
    if len(padded_message) < width:
        padded_message += char
        
    print(red(border))
    print(red(padded_message))
    print(red(border))


def display_tank_table(tanks: Dict[str, 'Tank'], show_stats: bool = False) -> None:
    """
    Display a formatted table of all tanks.
    
    Args:
        tanks: Dictionary of tank_id -> Tank
        show_stats: If True, show detailed statistics
    """
    table = Table(title="🎮 Tanks", show_header=True, header_style="bold cyan")
    
    # Basic columns
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold")
    table.add_column("Armor", justify="center")
    table.add_column("Ammo", justify="center")
    table.add_column("Power", justify="center")
    table.add_column("Dmg Mit.", justify="center")
    table.add_column("Miss%", justify="center")
    table.add_column("Malf.%", justify="center")
    table.add_column("Credits", justify="center")
    table.add_column("Dodge%", justify="center")
    
    if show_stats:
        table.add_column("Shots", justify="center")
        table.add_column("Hits", justify="center")
        table.add_column("Misses", justify="center")
        table.add_column("Dmg", justify="center")
    
    for idx, (tank_id, tank) in enumerate(tanks.items(), 1):
        # Color coding
        if tank.alive:
            name_style = "green" if tank.armor > tank.ARMORSTART * 0.5 else "yellow"
        else:
            name_style = "red"
            
        armor_style = "green"
        if tank.armor < tank.ARMORSTART * 0.5:
            armor_style = "yellow"
        if tank.armor < tank.ARMORSTART * 0.25:
            armor_style = "red"
        
        row = [
            str(idx),
            Text(tank.name, style=name_style),
            Text(str(tank.armor), style=armor_style),
            str(tank.ammo),
            str(tank.power),
            f"{tank.dmg_mitigation}%",
            f"{tank.miss}%",
            f"{tank.malfunction}%",
            str(tank.credits),
            f"{tank.dodge_chance}%",
        ]
        
        if show_stats:
            row.extend([
                str(tank.shots),
                str(tank.hits),
                str(tank.misses),
                str(tank.dmg),
            ])
        
        table.add_row(*row)
    
    console.print(table)


def display_shop(player: 'Tank') -> None:
    """Display the shop menu."""
    console.print(Panel(str(player), title=f"🎖️ {player.name}", border_style="blue"))
    
    table = Table(title="🛒 Shop", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Item", style="bold")
    table.add_column("Effect")
    table.add_column("Value", justify="center")
    table.add_column("Price", justify="center", style="yellow")
    
    for item_id, item_data in ITEMS.items():
        name, desc, value, price, _ = item_data
        affordable = "✓" if player.credits >= price else "✗"
        table.add_row(item_id, name, desc, f"+{value}", f"{price} 💰 {affordable}")
    
    table.add_row("─", "───", "───", "───", "───")
    table.add_row("0", "Cancel", "", "", "")
    
    console.print(table)
    console.print(f"\n[bold]Deine Credits:[/bold] [yellow]{player.credits}[/yellow] 💰\n")


def display_tank_selection() -> None:
    """Display the tank selection menu."""
    table = Table(title="🎯 Select Tank", show_header=True, header_style="bold green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold")
    table.add_column("Armor", justify="center")
    table.add_column("Ammo", justify="center")
    table.add_column("Power", justify="center")
    table.add_column("Dmg Mit.", justify="center")
    
    for tank_id, (name, stats) in PREDEFINED_TANKS.items():
        armor, ammo, power, dmg_mit = stats
        table.add_row(tank_id, name, str(armor), str(ammo), str(power), f"{dmg_mit}%")
    
    table.add_row("─", "───", "───", "───", "───", "───")
    table.add_row("0", "Cancel", "", "", "", "")
    
    console.print(table)


def animate_shooting(attacker: str, target: str) -> None:
    """Display shooting animation."""
    if DEBUG:
        return
        
    console.print(f"\n[bold]{attacker}[/bold] zielt auf [bold]{target}[/bold]'s Panzer!", style="yellow")
    
    with console.status("[bold green]Berechne Schuss...") as status:
        sleep(0.5)
        for phase in ["Ziele...", "Feuer!", "💥"]:
            status.update(f"[bold green]{phase}")
            sleep(0.3)


def animate_hit(tank_name: str, damage: int) -> None:
    """Display hit animation."""
    print_red_banner(f" BOOM! - {tank_name} wurde getroffen! ", "#", 50)
    print_red_banner(f" -{damage} Armor! ", "#", 50)


def animate_miss() -> None:
    """Display miss animation."""
    print_red_banner(" MISS ", "#", 30)


def animate_malfunction(tank_name: str) -> None:
    """Display malfunction animation."""
    console.print(f"\n[bold red]⚠️ Oh nein, {tank_name} hat eine Fehlfunktion![/bold red]\n")


def animate_dodge(tank_name: str) -> None:
    """Display dodge animation."""
    console.print(f"\n[bold cyan]💨 {tank_name} weicht aus![/bold cyan]\n")


def animate_explosion(tank_name: str) -> None:
    """Display explosion animation."""
    if not DEBUG:
        sleep(0.5)
    print_red_banner(f" KAWOOM! - {tank_name} explodiert! ", "#", 50)
    if not DEBUG:
        sleep(0.5)
    print_red_banner(f" {tank_name} wurde zerstört! ", "#", 50)


def display_winner(winner_name: str, is_computer: bool = False) -> None:
    """Display winner announcement."""
    if is_computer:
        console.print("\n[bold red]😢 Oh nein, du hast verloren![/bold red]")
        console.print("[bold red]Der Computer gewinnt![/bold red]\n")
    else:
        console.print(f"\n[bold green]🎉 {winner_name} ist der Gewinner - WOOHOO! 🎉[/bold green]\n")


def display_instructions() -> None:
    """Display game instructions."""
    instructions = """
[bold cyan]🎮 TANKGAME - Anleitung[/bold cyan]

Jeder Panzer hat diese Attribute:
  • [bold]Armor[/bold]     : Panzerung, wird bei Treffern reduziert
  • [bold]Ammo[/bold]      : Anzahl Munition, -1 pro Schuss
  • [bold]Power[/bold]     : Schaden pro Schuss
  • [bold]Dmg Mit.[/bold]  : Schadensreduktion (%), -1 pro Treffer
  • [bold]Miss[/bold]      : Fehlschuss-Wahrscheinlichkeit
  • [bold]Malfunction[/bold]: Fehlfunktions-Wahrscheinlichkeit
  • [bold]Credits[/bold]   : Währung für den Shop
  • [bold]Dodge[/bold]     : Ausweich-Wahrscheinlichkeit

[bold yellow]Aktionen pro Runde:[/bold yellow]
  [S] Shoot   - Auf Gegner schießen
  [B] Buy     - Shop öffnen
  [N] Nothing - Warten (+1 Credit)
"""
    console.print(Panel(instructions, border_style="cyan"))


def display_turn(player_name: str, is_computer: bool = False) -> None:
    """Display whose turn it is."""
    if is_computer:
        console.print("\n[bold red]🤖 Computer ist am Zug[/bold red]\n")
    else:
        console.print(f"\n[bold green]➡️ {player_name} ist am Zug[/bold green]\n")
