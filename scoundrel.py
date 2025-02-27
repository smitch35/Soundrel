import pygame
import sys
import random
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

# Initialize pygame
pygame.init()

# Game states
class GameState(Enum):
    INTRO = "intro"
    MENU = "menu"
    OPTIONS = "options"
    GAMEPLAY = "gameplay"

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 20
FPS = 60

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

# Font
font_small = pygame.font.SysFont("Arial", 16)
font_medium = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 24)
font_xl = pygame.font.SysFont("Arial", 32)
font_title = pygame.font.SysFont("Arial", 64)

# Zones on the board
class Zone:
    DECK = "deck"
    ROOM = "room"
    WEAPON = "weapon"
    DISCARD = "discard"
    PLAYER = "player"
    RUN_BUTTON = "run_button"
    DISCARD_BUTTON = "discard_button"

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class CardType(Enum):
    HEALTH = "Health Potion"
    WEAPON = "Weapon"
    MONSTER = "Monster"

@dataclass
class Card:
    value: int
    suit: Suit
    rect: pygame.Rect = None
    selected: bool = False
    position_index: int = -1  # To track position in the room
    
    @property
    def card_type(self) -> CardType:
        if self.suit == Suit.HEARTS:
            return CardType.HEALTH
        elif self.suit == Suit.DIAMONDS:
            return CardType.WEAPON
        else:  # CLUBS or SPADES
            return CardType.MONSTER
    
    def __str__(self) -> str:
        return f"{self.value} of {self.suit.value}"
    
    def get_color(self) -> Tuple[int, int, int]:
        if self.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            return RED
        else:
            return BLACK

class WeaponSlot:
    def __init__(self):
        self.weapon: Optional[Card] = None
        self.monsters: List[Card] = []
        self.rect = pygame.Rect(350, 600, CARD_WIDTH * 3, CARD_HEIGHT)
    
    def can_add_monster(self, monster: Card) -> bool:
        """Check if a monster can be added to this slot."""
        # If no weapon, monsters don't need to stack - they just get defeated directly
        if not self.weapon:
            return True
            
        # When weapon is equipped, check the monster stacking rule
        if self.monsters:
            last_monster = self.monsters[-1]
            # Can only add monster if it's equal to or lower than the last monster
            if monster.value > last_monster.value:
                return False
                
        return True
    
    def add_monster(self, monster: Card) -> Tuple[bool, int]:
        """
        Try to add a monster to this slot.
        Returns a tuple of (success, damage_taken)
        """
        if not self.can_add_monster(monster):
            return False, 0
        
        damage = monster.value
        if self.weapon:
            damage = max(0, monster.value - self.weapon.value)
            # Only add monster to stack if there's a weapon
            self.monsters.append(monster)
            
            # Update monster position
            monster_offset = len(self.monsters) * 30
            monster.rect = pygame.Rect(
                self.rect.x + 150 + monster_offset, 
                self.rect.y, 
                CARD_WIDTH, 
                CARD_HEIGHT
            )
        # No weapon means the monster is defeated but not added to a stack
            
        return True, damage
    
    def set_weapon(self, weapon: Card) -> None:
        """Set a new weapon, clearing any previous weapon and monsters."""
        self.weapon = weapon
        self.monsters = []
        
        # Set weapon position
        if weapon:
            weapon.rect = pygame.Rect(
                self.rect.x, 
                self.rect.y, 
                CARD_WIDTH, 
                CARD_HEIGHT
            )
    
    def discard(self) -> None:
        """Discard this weapon and its monsters."""
        self.weapon = None
        self.monsters = []
    
    def get_protection(self) -> int:
        """Return the protection value of this weapon."""
        return self.weapon.value if self.weapon else 0

class Player:
    def __init__(self):
        self.max_hp = 20
        self.hp = 20
        self.weapon_slot = WeaponSlot()
        self.rect = pygame.Rect(50, 650, 200, 80)
        self.message = ""
        self.message_time = 0
        self.message_color = BLACK
    
    def use_health_potion(self, card: Card) -> None:
        """Use a health potion to restore HP."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + card.value)
        actual_healing = self.hp - old_hp
        self.set_message(f"Restored {actual_healing} HP", GREEN)
    
    def equip_weapon(self, card: Card) -> None:
        """Equip a weapon."""
        self.weapon_slot.set_weapon(card)
        self.set_message(f"Equipped {card}", BLUE)
    
    def fight_monster(self, monster: Card) -> Tuple[bool, bool]:
        """
        Fight a monster using weapon or bare hands. 
        Returns (action_successful, player_survived)
        """
        # Check if monster can be added (this is only a restriction when using weapons)
        if not self.weapon_slot.can_add_monster(monster):
            self.set_message("Cannot fight this monster. Monsters must be in decreasing order.", RED)
            return False, True
        
        # Add monster and calculate damage
        success, damage = self.weapon_slot.add_monster(monster)
        
        if damage > 0:
            self.hp -= damage
            if self.weapon_slot.weapon:
                protection = self.weapon_slot.weapon.value
                self.set_message(f"Weapon ({protection}) vs Monster ({monster.value}): Took {damage} damage!", RED)
            else:
                self.set_message(f"No weapon! Defeated monster but took full {damage} damage!", RED)
            
            if self.hp <= 0:
                self.hp = 0
                self.set_message("You died!", RED)
                return True, False
        else:
            self.set_message("Your weapon fully protected you!", GREEN)
        
        return True, True
    
    def get_hp_color(self) -> Tuple[int, int, int]:
        """Return color based on current health."""
        if self.hp > 13:
            return GREEN
        elif self.hp >= 9:
            return YELLOW
        else:
            return RED
    
    def set_message(self, text: str, color: Tuple[int, int, int]) -> None:
        """Set a message to display to the player."""
        self.message = text
        self.message_time = pygame.time.get_ticks()
        self.message_color = color

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int], action: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.hovered = False
        self.enabled = True
    
    def draw(self, screen: pygame.Surface) -> None:
        color = self.hover_color if self.hovered else self.color
        if not self.enabled:
            color = GRAY
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surf = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Check if mouse is hovering over the button."""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button was clicked."""
        return self.enabled and self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Solitaire RPG")
        self.clock = pygame.time.Clock()
        
        # Set initial game state to intro
        self.state = GameState.INTRO
        self.intro_start_time = pygame.time.get_ticks()
        self.intro_duration = 3000  # 3 seconds for intro video placeholder
        
        # Menu buttons
        self.menu_buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "New Game", GREEN, LIGHT_GRAY, BLACK, "new_game"),
            Button(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "Options", BLUE, LIGHT_GRAY, BLACK, "options"),
            Button(SCREEN_WIDTH // 2 - 100, 490, 200, 50, "Exit Game", RED, LIGHT_GRAY, BLACK, "exit")
        ]
        
        # Options buttons
        self.options_buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 490, 200, 50, "Back to Menu", YELLOW, LIGHT_GRAY, BLACK, "back_to_menu")
        ]
        
        # Initialize gameplay variables (but don't start gameplay yet)
        self.player = None
        self.deck = []
        self.room_cards = []
        self.discard_pile = []
        self.just_ran = False
        self.selected_card = None
        self.game_over = False
        self.victory = False
        self.run_button = None
        self.discard_button = None
        self.restart_button = None
        self.menu_button = None
        
        # Debug message on init
        print("Game initialized!")
    
    def initialize_gameplay(self):
        """Initialize gameplay elements."""
        print("Starting gameplay initialization...")
        try:
            self.player = Player()
            self.deck = []
            self.room_cards = []
            self.discard_pile = []  # New discard pile
            self.just_ran = False
            self.selected_card = None
            self.game_over = False
            self.victory = False
            
            # Create gameplay buttons
            self.run_button = Button(50, 580, 100, 40, "Run", GREEN, LIGHT_GRAY, BLACK, "run")
            self.discard_button = Button(350, 550, 120, 40, "Discard Weapon", YELLOW, LIGHT_GRAY, BLACK, "discard")
            self.restart_button = Button(SCREEN_WIDTH - 150, 700, 120, 40, "Restart", BLUE, LIGHT_GRAY, BLACK, "restart")
            self.menu_button = Button(SCREEN_WIDTH - 150, 650, 120, 40, "Main Menu", BLUE, LIGHT_GRAY, BLACK, "main_menu")
            
            # Initialize game
            self.initialize_deck()
            self.shuffle_deck()
            self.draw_room()
            
            print("Gameplay initialization complete!")
        except Exception as e:
            print(f"ERROR during gameplay initialization: {e}")
            # Reset to menu if there's an error
            self.state = GameState.MENU
        
    def initialize_deck(self) -> None:
        """Create the custom deck without red face cards."""
        for suit in Suit:
            if suit in [Suit.HEARTS, Suit.DIAMONDS]:
                # Red suits: only 2-10
                values = range(2, 11)
            else:
                # Black suits: 2-10, J, Q, K, A (represented as 11, 12, 13, 14)
                values = list(range(2, 11)) + [11, 12, 13, 14]
            
            for value in values:
                card = Card(value, suit)
                self.deck.append(card)
                
        # Debug: print deck contents
        print(f"Deck created with {len(self.deck)} cards")
        suit_counts = {}
        for card in self.deck:
            suit_name = card.suit.value
            if suit_name not in suit_counts:
                suit_counts[suit_name] = 0
            suit_counts[suit_name] += 1
        
        print("Cards per suit:")
        for suit, count in suit_counts.items():
            print(f"  {suit}: {count} cards")
    
    def shuffle_deck(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.deck)
    
    def draw_card(self) -> Optional[Card]:
        """Draw a card from the deck."""
        if not self.deck:
            print("The deck is empty!")
            return None
        return self.deck.pop(0)
    
    def draw_room(self) -> None:
        """Draw cards to fill the room (up to 4 cards)."""
        room_positions = [
            (200, 100), (350, 100), (500, 100), (650, 100)
        ]
        
        # Print current state before drawing
        print(f"Current room size before drawing: {len(self.room_cards)}")
        
        # Only draw cards if we have 1 or fewer cards in the room
        if len(self.room_cards) > 1:
            print("Skipping card draw - room still has enough cards")
            return
        
        # Keep track of which positions need filling
        empty_positions = []
        for i in range(4):
            # Check if this position is empty
            position_empty = True
            for card in self.room_cards:
                if card.position_index == i:
                    position_empty = False
                    break
            
            if position_empty:
                empty_positions.append(i)
        
        # Draw new cards for empty positions
        for position_index in empty_positions:
            if not self.deck:
                break
                
            card = self.draw_card()
            if card:
                pos = room_positions[position_index]
                card.rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
                card.position_index = position_index  # Store the position index
                self.room_cards.append(card)
                
        # Debug information
        print(f"Room cards after draw: {len(self.room_cards)}")
        for card in self.room_cards:
            print(f"Card at position {card.position_index}: {card} - Type: {card.card_type.value}")
    
    def run_from_room(self) -> None:
        """Run from the current room, placing cards at the bottom of the deck."""
        if self.just_ran:
            self.player.set_message("Cannot run from rooms consecutively!", RED)
            return
            
        if not self.room_cards:
            self.player.set_message("The room is empty!", GRAY)
            return
        
        self.player.set_message("Running from the room...", BLUE)
        # Shuffle the room cards and add them to the bottom of the deck
        random.shuffle(self.room_cards)
        self.deck.extend(self.room_cards)
        self.room_cards = []
        
        # Draw a new room
        self.draw_room()
        
        # Set the flag that player just ran
        self.just_ran = True
    
    def use_card(self, card_index: int) -> bool:
        """Use a card from the room. Returns True if the game should continue."""
        if not (0 <= card_index < len(self.room_cards)):
            self.player.set_message("Invalid card selection!", RED)
            return True
        
        card = self.room_cards[card_index]
        
        # Debug info
        print(f"Using card: {card} - Type: {card.card_type.value}")
        print(f"Suit: {card.suit.value}, Value: {card.value}, Position: {card.position_index}")
        
        # Save position_index for later reference
        position_index = card.position_index
        
        # Handle the card based on its type
        if card.card_type == CardType.HEALTH:
            # Remove card from room first
            self.room_cards.remove(card)
            self.player.use_health_potion(card)
            self.discard_pile.append(card)  # Add to discard pile
        elif card.card_type == CardType.WEAPON:
            # If player already has a weapon, discard it first
            if self.player.weapon_slot.weapon:
                old_weapon = self.player.weapon_slot.weapon
                old_monsters = self.player.weapon_slot.monsters.copy()
                self.discard_pile.append(old_weapon)
                self.discard_pile.extend(old_monsters)
            
            # Remove card from room
            self.room_cards.remove(card)
            self.player.equip_weapon(card)
        elif card.card_type == CardType.MONSTER:
            # Only remove the card if the action is successful
            action_successful, player_survived = self.player.fight_monster(card)
            if action_successful:
                # Remove card from room
                self.room_cards.remove(card)
                
                # If no weapon, monster goes directly to discard pile
                if not self.player.weapon_slot.weapon:
                    self.discard_pile.append(card)
                    
                if not player_survived:
                    self.game_over = True
                    return False  # Player died
            # If action was not successful, card stays in room
        
        # Refill the room only if there's 1 or fewer cards left
        if len(self.room_cards) <= 1:
            self.draw_room()
        
        # Reset the "just ran" flag when player uses a card
        self.just_ran = False
        
        # Check victory condition
        if not self.deck and not self.room_cards:
            self.victory = True
            self.game_over = True
        
        return True
    
    def discard_weapon(self) -> None:
        """Discard the current weapon and its monsters."""
        if not self.player or not self.player.weapon_slot.weapon:
            if self.player:
                self.player.set_message("No weapon to discard!", YELLOW)
            return
        
        # Add weapon and monsters to discard pile
        weapon = self.player.weapon_slot.weapon
        monsters = self.player.weapon_slot.monsters.copy()
        self.discard_pile.append(weapon)
        self.discard_pile.extend(monsters)
            
        self.player.weapon_slot.discard()
        self.player.set_message("Discarded weapon", BLUE)
        
        # Reset the "just ran" flag when player discards a weapon
        self.just_ran = False
    
    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click events."""
        try:
            # Handle clicks based on current game state
            if self.state == GameState.INTRO:
                # Skip intro on click
                self.state = GameState.MENU
                return
                
            elif self.state == GameState.MENU:
                # Handle menu button clicks
                for button in self.menu_buttons:
                    if button.clicked(pos):
                        if button.action == "new_game":
                            print("New Game clicked!")
                            try:
                                # Initialize gameplay fresh
                                self.initialize_gameplay()
                                # Switch to gameplay state
                                self.state = GameState.GAMEPLAY
                                print("Switched to gameplay state")
                            except Exception as e:
                                print(f"ERROR starting new game: {e}")
                        elif button.action == "options":
                            self.state = GameState.OPTIONS
                        elif button.action == "exit":
                            pygame.quit()
                            sys.exit()
                return
                
            elif self.state == GameState.OPTIONS:
                # Handle options button clicks
                for button in self.options_buttons:
                    if button.clicked(pos):
                        if button.action == "back_to_menu":
                            self.state = GameState.MENU
                return
                
            elif self.state == GameState.GAMEPLAY:
                # Verify we have the necessary gameplay objects
                if self.player is None or self.run_button is None:
                    print("ERROR: Gameplay not properly initialized")
                    self.state = GameState.MENU
                    return
                    
                # Handle in-game clicks
                if self.game_over:
                    # Restart game if it's over
                    self.initialize_gameplay()
                    return
                    
                # Check if a room card was clicked
                for card in self.room_cards:
                    if card.rect and card.rect.collidepoint(pos):
                        # Find the index of the card in the room_cards list
                        card_index = self.room_cards.index(card)
                        self.use_card(card_index)
                        return
                
                # Check if run button was clicked
                if self.run_button.clicked(pos):
                    self.run_from_room()
                    return
                    
                # Check if discard button was clicked
                if self.discard_button.clicked(pos):
                    self.discard_weapon()
                    return
                    
                # Check if restart button was clicked
                if self.restart_button.clicked(pos):
                    self.initialize_gameplay()
                    return
                    
                # Check if menu button was clicked
                if self.menu_button.clicked(pos):
                    self.state = GameState.MENU
                    return
        except Exception as e:
            print(f"ERROR in handle_click: {e}")
            # If an error occurs, go back to menu as a safety measure
            self.state = GameState.MENU
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        """Update hover state of interactive elements."""
        try:
            if self.state == GameState.MENU:
                # Update menu button hover states
                for button in self.menu_buttons:
                    button.check_hover(pos)
                    
            elif self.state == GameState.OPTIONS:
                # Update options button hover states
                for button in self.options_buttons:
                    button.check_hover(pos)
                    
            elif self.state == GameState.GAMEPLAY:
                # Make sure gameplay components exist
                if self.run_button is None or self.discard_button is None or self.restart_button is None:
                    return
                    
                # Update gameplay button hover states
                self.run_button.check_hover(pos)
                self.discard_button.check_hover(pos)
                self.restart_button.check_hover(pos)
                self.menu_button.check_hover(pos)
                
                # Update button enabled states
                if self.player:
                    self.run_button.enabled = not self.just_ran and bool(self.room_cards)
                    self.discard_button.enabled = bool(self.player.weapon_slot.weapon)
        except Exception as e:
            print(f"ERROR in update_hover: {e}")
    
    def draw_card_graphics(self, screen: pygame.Surface, card: Card, selected: bool = False) -> None:
        """Draw a card with full graphics."""
        if not card or not card.rect:
            return
            
        try:
            # Debug: confirm card type
            card_type = card.card_type
                
            # Draw card background
            border = 2 if selected else 1
            pygame.draw.rect(screen, WHITE, card.rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, card.rect, border, border_radius=5)
            
            # Draw card value and suit
            color = card.get_color()
            
            # Card value text
            value_text = str(card.value)
            if card.value == 11:
                value_text = "J"
            elif card.value == 12:
                value_text = "Q"
            elif card.value == 13:
                value_text = "K"
            elif card.value == 14:
                value_text = "A"
                
            value_surf = font_large.render(value_text, True, color)
            screen.blit(value_surf, (card.rect.x + 5, card.rect.y + 5))
            
            # Card suit symbol
            suit_symbol = ""
            if card.suit == Suit.HEARTS:
                suit_symbol = "♥"
            elif card.suit == Suit.DIAMONDS:
                suit_symbol = "♦"
            elif card.suit == Suit.CLUBS:
                suit_symbol = "♣"
            elif card.suit == Suit.SPADES:
                suit_symbol = "♠"
                
            suit_surf = font_large.render(suit_symbol, True, color)
            screen.blit(suit_surf, (card.rect.x + 5, card.rect.y + 30))
            
            # Draw card type identifier - more explicit check
            type_text = ""
            type_color = BLACK
            if card.suit == Suit.HEARTS:
                type_text = "HEALTH"
                type_color = GREEN
            elif card.suit == Suit.DIAMONDS:
                type_text = "WEAPON"
                type_color = BLUE
            elif card.suit == Suit.CLUBS or card.suit == Suit.SPADES:
                type_text = "MONSTER"
                type_color = RED
                
            type_surf = font_small.render(type_text, True, type_color)
            screen.blit(type_surf, (card.rect.x + 10, card.rect.y + CARD_HEIGHT - 25))
            
            # Draw center symbol
            center_symbol = suit_symbol
            center_surf = font_xl.render(center_symbol, True, color)
            center_rect = center_surf.get_rect(center=(card.rect.centerx, card.rect.centery))
            screen.blit(center_surf, center_rect)
        except Exception as e:
            print(f"ERROR drawing card: {e}")
    
    def draw_intro(self) -> None:
        """Draw intro video placeholder."""
        # Fill with black background for video
        self.screen.fill(BLACK)
        
        # Draw a placeholder for the video
        title = font_title.render("Solitaire RPG", True, WHITE)
        subtitle = font_medium.render("Intro Video Placeholder", True, WHITE)
        skip = font_medium.render("Click anywhere to skip...", True, GRAY)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(skip, (SCREEN_WIDTH // 2 - skip.get_width() // 2, SCREEN_HEIGHT * 3 // 4))
        
        # Auto-advance after intro_duration
        current_time = pygame.time.get_ticks()
        if current_time - self.intro_start_time > self.intro_duration:
            self.state = GameState.MENU
            
    def draw_menu(self) -> None:
        """Draw the main menu."""
        # Draw blue background (placeholder for background asset)
        self.screen.fill((40, 100, 180))  # Medium blue
        
        # Draw placeholder for background art
        pygame.draw.rect(self.screen, (30, 80, 150), (100, 50, SCREEN_WIDTH - 200, 200))
        
        # Draw game title
        title = font_title.render("Solitaire RPG", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        subtitle = font_large.render("Card Dungeon Adventures", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
            
        # Draw version
        version = font_small.render("v1.0", True, WHITE)
        self.screen.blit(version, (20, SCREEN_HEIGHT - 30))
            
    def draw_options(self) -> None:
        """Draw the options screen."""
        # Draw dark blue background
        self.screen.fill((20, 60, 120))
        
        # Draw title
        title = font_title.render("Options", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw placeholder options
        option_texts = ["Sound: ON", "Music: ON", "Difficulty: Normal"]
        for i, text in enumerate(option_texts):
            option = font_medium.render(text, True, WHITE)
            self.screen.blit(option, (SCREEN_WIDTH // 2 - option.get_width() // 2, 200 + i * 60))
        
        # Draw note that options aren't functional yet
        note = font_small.render("Note: Options are not functional in this version", True, YELLOW)
        self.screen.blit(note, (SCREEN_WIDTH // 2 - note.get_width() // 2, 400))
        
        # Draw buttons
        for button in self.options_buttons:
            button.draw(self.screen)
            
    def draw_gameplay(self) -> None:
        """Draw the gameplay screen."""
        try:
            # Check if gameplay is initialized
            if self.player is None:
                # Initialize gameplay if not already done
                self.initialize_gameplay()
                # Check if initialization was successful
                if self.player is None:
                    print("ERROR: Failed to initialize gameplay!")
                    self.state = GameState.MENU
                    return
            
            # Fill the background
            self.screen.fill(DARK_GREEN)
            
            # Draw table border
            pygame.draw.rect(self.screen, BROWN, (10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20), 10, border_radius=15)
            
            # Draw deck
            if self.deck:
                deck_rect = pygame.Rect(50, 300, CARD_WIDTH, CARD_HEIGHT)
                pygame.draw.rect(self.screen, BLUE, deck_rect, border_radius=5)
                pygame.draw.rect(self.screen, BLACK, deck_rect, 2, border_radius=5)
                deck_text = font_medium.render(f"Deck: {len(self.deck)}", True, WHITE)
                deck_text_rect = deck_text.get_rect(center=deck_rect.center)
                self.screen.blit(deck_text, deck_text_rect)
            
            # Draw discard pile on the right side
            discard_rect = pygame.Rect(SCREEN_WIDTH - 150, 300, CARD_WIDTH, CARD_HEIGHT)
            if self.discard_pile:
                pygame.draw.rect(self.screen, RED, discard_rect, border_radius=5)
                pygame.draw.rect(self.screen, BLACK, discard_rect, 2, border_radius=5)
                
                # Show the top card of the discard pile
                top_card = self.discard_pile[-1]
                # Create a temporary rect for drawing the top card
                temp_rect = top_card.rect
                top_card.rect = discard_rect.copy()
                self.draw_card_graphics(self.screen, top_card)
                # Restore the original rect
                top_card.rect = temp_rect
            else:
                # Empty discard pile
                pygame.draw.rect(self.screen, LIGHT_GRAY, discard_rect, border_radius=5)
                pygame.draw.rect(self.screen, BLACK, discard_rect, 2, border_radius=5)
            
            # Draw discard count
            discard_text = font_medium.render(f"Discard: {len(self.discard_pile)}", True, BLACK)
            discard_text_rect = discard_text.get_rect(center=(discard_rect.centerx, discard_rect.bottom + 25))
            self.screen.blit(discard_text, discard_text_rect)
            
            # Draw room cards
            for card in self.room_cards:
                self.draw_card_graphics(self.screen, card)
            
            # Draw room label
            room_label = font_large.render("Room", True, BLACK)
            self.screen.blit(room_label, (420, 50))
            
            # Draw weapon and monsters
            if self.player.weapon_slot.weapon:
                self.draw_card_graphics(self.screen, self.player.weapon_slot.weapon)
                
                # Draw monsters
                for i, monster in enumerate(self.player.weapon_slot.monsters):
                    self.draw_card_graphics(self.screen, monster)
            else:
                # Draw empty weapon slot
                empty_weapon_rect = pygame.Rect(self.player.weapon_slot.rect.x, self.player.weapon_slot.rect.y, 
                                               CARD_WIDTH, CARD_HEIGHT)
                pygame.draw.rect(self.screen, LIGHT_GRAY, empty_weapon_rect, border_radius=5)
                pygame.draw.rect(self.screen, BLACK, empty_weapon_rect, 1, border_radius=5)
                weapon_text = font_small.render("No Weapon", True, BLACK)
                weapon_text_rect = weapon_text.get_rect(center=empty_weapon_rect.center)
                self.screen.blit(weapon_text, weapon_text_rect)
            
            # Draw weapon slot label
            weapon_label = font_large.render("Weapon Slot", True, BLACK)
            self.screen.blit(weapon_label, (370, 570))
            
            # Draw player HP
            hp_rect = pygame.Rect(50, 650, 200, 30)
            pygame.draw.rect(self.screen, GRAY, hp_rect, border_radius=5)
            
            # HP bar
            hp_pct = self.player.hp / self.player.max_hp
            hp_width = int(hp_rect.width * hp_pct)
            hp_bar_rect = pygame.Rect(hp_rect.x, hp_rect.y, hp_width, hp_rect.height)
            hp_color = self.player.get_hp_color()
            pygame.draw.rect(self.screen, hp_color, hp_bar_rect, border_radius=5)
            
            # HP text
            hp_text = font_medium.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, BLACK)
            hp_text_rect = hp_text.get_rect(center=hp_rect.center)
            self.screen.blit(hp_text, hp_text_rect)
            
            # Draw player message
            if self.player.message and pygame.time.get_ticks() - self.player.message_time < 3000:
                message_surf = font_medium.render(self.player.message, True, self.player.message_color)
                self.screen.blit(message_surf, (SCREEN_WIDTH // 2 - message_surf.get_width() // 2, 700))
            
            # Draw buttons
            self.run_button.draw(self.screen)
            self.discard_button.draw(self.screen)
            self.restart_button.draw(self.screen)
            self.menu_button.draw(self.screen)
            
            # Draw "just ran" notification
            if self.just_ran:
                ran_text = font_medium.render("You ran from the last room! Must fight this one!", True, RED)
                self.screen.blit(ran_text, (50, 550))
            
            # Draw game over screen
            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                if self.victory:
                    result_text = font_xl.render("VICTORY!", True, GREEN)
                else:
                    result_text = font_xl.render("GAME OVER", True, RED)
                
                result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(result_text, result_rect)
                
                restart_text = font_large.render("Click anywhere to restart", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                self.screen.blit(restart_text, restart_rect)
        except Exception as e:
            print(f"ERROR drawing gameplay: {e}")
            # If an error occurs during drawing, go back to menu
            self.state = GameState.MENU
    
    def draw(self) -> None:
        """Draw the game state."""
        try:
            # Fill the background based on current state
            if self.state == GameState.INTRO:
                self.draw_intro()
            elif self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.OPTIONS:
                self.draw_options()
            elif self.state == GameState.GAMEPLAY:
                self.draw_gameplay()
                
            # Update display
            pygame.display.flip()
        except Exception as e:
            print(f"ERROR in draw: {e}")
            # If an error occurs during drawing, go back to menu
            self.state = GameState.MENU
            
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            try:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            self.handle_click(event.pos)
                    elif event.type == pygame.MOUSEMOTION:
                        self.update_hover(event.pos)
                
                # Draw the game
                self.draw()
                
                # Cap the frame rate
                self.clock.tick(FPS)
            except Exception as e:
                print(f"ERROR in main loop: {e}")
                # If a critical error occurs, just continue the loop
                # This keeps the game running even if there's an error
                
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()