"""
Enumerations used in the game.
"""
from enum import Enum

class GameState(Enum):
    """Game state enumeration."""
    INTRO = "intro"
    MENU = "menu"
    OPTIONS = "options"
    GAMEPLAY = "gameplay"

class AnimationType(Enum):
    """Animation type enumeration."""
    NONE = "none"
    CARD_MOVE = "card_move"
    DAMAGE = "damage"
    HEAL = "heal"
    PULSE = "pulse"
    FADE = "fade"
    SHAKE = "shake"

class Suit(Enum):
    """Card suit enumeration."""
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class CardType(Enum):
    """Card type enumeration."""
    HEALTH = "Health Potion"
    WEAPON = "Weapon"
    MONSTER = "Monster"