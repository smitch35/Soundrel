"""
Constants used throughout the game.
"""
import pygame

# Window dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Card dimensions
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)

# Fonts
pygame.font.init()  # Initialize font module
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT_MEDIUM = pygame.font.SysFont("Arial", 20)
FONT_LARGE = pygame.font.SysFont("Arial", 24)
FONT_XL = pygame.font.SysFont("Arial", 32)
FONT_TITLE = pygame.font.SysFont("Arial", 64)

# Animation constants
TRANSITION_DURATION = 500  # 500ms for screen transitions
CARD_MOVE_DURATION = 300   # 300ms for card movement
INTRO_DURATION = 3000      # 3000ms for intro screen

# Board zones
class Zone:
    DECK = "deck"
    ROOM = "room"
    WEAPON = "weapon"
    DISCARD = "discard"
    PLAYER = "player"
    RUN_BUTTON = "run_button"
    DISCARD_BUTTON = "discard_button"

# Card positions
DECK_POSITION = (50, 300)
ROOM_POSITIONS = [
    (200, 100), (350, 100), (500, 100), (650, 100)
]
DISCARD_POSITION = (SCREEN_WIDTH - 150, 300)
WEAPON_POSITION = (350, 600)