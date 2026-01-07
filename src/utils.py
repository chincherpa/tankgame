"""
Tankgame Utilities
Helper functions for input validation, random generation, etc.
"""

import random
import sys
from time import sleep
from typing import List, Optional, Tuple


def safe_int_input(
    prompt: str, 
    valid_range: Optional[range] = None, 
    default: Optional[int] = None,
    allow_empty: bool = True
) -> Optional[int]:
    """
    Safely get integer input from user with validation.
    
    Args:
        prompt: The prompt to display
        valid_range: Optional range of valid values
        default: Default value if input is empty
        allow_empty: Whether empty input is allowed
        
    Returns:
        The validated integer or default value
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                if allow_empty:
                    return default
                print("Eingabe erforderlich.")
                continue
                
            num = int(value)
            
            if valid_range is not None and num not in valid_range:
                print(f"Bitte eine Zahl zwischen {valid_range.start} und {valid_range.stop - 1} eingeben.")
                continue
                
            return num
            
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
            return None


def safe_choice_input(
    prompt: str,
    valid_choices: List[str],
    case_sensitive: bool = False
) -> Optional[str]:
    """
    Get a choice from a list of valid options.
    
    Args:
        prompt: The prompt to display
        valid_choices: List of valid choice strings
        case_sensitive: Whether comparison should be case-sensitive
        
    Returns:
        The selected choice or None if cancelled
    """
    while True:
        try:
            value = input(prompt).strip()
            
            if not case_sensitive:
                value = value.lower()
                valid_lower = [c.lower() for c in valid_choices]
                if value in valid_lower:
                    return value
            else:
                if value in valid_choices:
                    return value
                    
            print(f"Ungültige Auswahl. Erlaubt: {', '.join(valid_choices)}")
            
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
            return None


def represents_int(s: str) -> bool:
    """Check if a string represents an integer."""
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False


def spinning_cursor(duration: int, value: str = '') -> None:
    """
    Display a spinning cursor animation.
    
    Args:
        duration: Number of cycles
        value: Text to display next to cursor
    """
    for _ in range(duration):
        for cursor in '|/-\\':
            sleep(0.1)
            sys.stdout.write(f'\r{cursor} {value}')
            sys.stdout.flush()
    print()  # New line after animation


def get_4_randoms(target_sum: int) -> Tuple[int, int, int, int]:
    """
    Generate 4 random numbers that sum to target_sum.
    
    Args:
        target_sum: The target sum for all 4 numbers
        
    Returns:
        Tuple of 4 random integers
    """
    # More efficient algorithm than brute force
    points = [0, 0, 0, 0]
    for _ in range(target_sum):
        idx = random.randint(0, 3)
        points[idx] += 1
    return tuple(points)  # type: ignore


def clear_screen() -> None:
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
