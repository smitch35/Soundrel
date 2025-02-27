"""
Gameplay screen for the Solitaire RPG game.
"""
import pygame
import random
from typing import List, Tuple, Optional

from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, LIGHT_GRAY, DARK_GREEN, BROWN,
    FONT_LARGE, FONT_MEDIUM, FONT_XL,
    DECK_POSITION, ROOM_POSITIONS, DISCARD_POSITION
)
from src.components.card import Card
from src.components.player import Player
from src.components.button import Button
from src.animations.effects import ParticleSystem, ScreenShake
from src.enums import GameState, Suit, CardType, AnimationType

class GameplayScreen:
    """Gameplay screen where the main game takes place."""
    def __init__(self):
        """Initialize the gameplay screen."""
        self.player = Player()
        self.deck: List[Card] = []
        self.room_cards: List[Card] = []
        self.discard_pile: List[Card] = []
        self.just_ran = False
        self.selected_card = None
        self.game_over = False
        self.victory = False
        
        # Create gameplay buttons
        self.run_button = Button(50, 580, 100, 40, "Run", GREEN, LIGHT_GRAY, BLACK, "run")
        self.discard_button = Button(350, 550, 120, 40, "Discard Weapon", YELLOW, LIGHT_GRAY, BLACK, "discard")
        self.restart_button = Button(SCREEN_WIDTH - 150, 700, 120, 40, "Restart", BLUE, LIGHT_GRAY, BLACK, "restart")
        self.menu_button = Button(SCREEN_WIDTH - 150, 650, 120, 40, "Main Menu", BLUE, LIGHT_GRAY, BLACK, "main_menu")
        
        # Particle system for effects
        self.particle_system = ParticleSystem()
        
        # Screen shake effect
        self.screen_shake = ScreenShake()
        
        # Initialize the game
        self.initialize_deck()
        self.shuffle_deck()
        self.draw_room()
        
        print("Gameplay initialized!")
    
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
                # Start card at deck position
                card.rect = pygame.Rect(DECK_POSITION[0], DECK_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
                card.position_index = position_index  # Store the position index
                
                # Add animation to move card to its position
                target_pos = ROOM_POSITIONS[position_index]
                card.add_animation(
                    AnimationType.CARD_MOVE,
                    500,  # 500ms duration
                    (card.rect.x, card.rect.y),
                    target_pos
                )
                
                # Add a secondary animation after the move
                card.add_animation(
                    AnimationType.PULSE,
                    300,  # 300ms duration
                    1.0,  # Start scale (not really used for pulse)
                    1.2   # End scale (not really used for pulse)
                )
                
                self.room_cards.append(card)
                
                # Add particles at the target position
                self.particle_system.add_particles(
                    target_pos[0] + CARD_WIDTH // 2,
                    target_pos[1] + CARD_HEIGHT // 2,
                    15,  # Number of particles
                    (100, 100, 255)  # Blue particles
                )
                
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
            self.player.set_message("The room is empty!", (128, 128, 128))
            return
        
        self.player.set_message("Running from the room...", BLUE)
        
        # Animate cards going back to deck
        for card in self.room_cards:
            if card.rect:
                # Animate card moving back to deck
                card.add_animation(
                    AnimationType.CARD_MOVE,
                    300,  # 300ms duration
                    (card.rect.x, card.rect.y),
                    DECK_POSITION
                )
                
                # Add fade out animation
                card.add_animation(
                    AnimationType.FADE,
                    300,  # 300ms duration
                    255,  # Start alpha
                    0  # End alpha
                )
        
        # Add particles for the "running" effect
        self.particle_system.add_particles(
            self.player.rect.x + 100,
            self.player.rect.y,
            30,  # Number of particles
            (150, 150, 150)  # Gray particles for dust
        )
        
        # Wait a bit before reshuffling and drawing new cards
        pygame.time.delay(350)  # Small delay to let animations complete
        
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
            
            # Add heal particles
            self.particle_system.add_particles(
                self.player.rect.x + 100,
                self.player.rect.y,
                20,  # Number of particles
                GREEN,  # Green particles for healing
                speed=3.0
            )
            
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
            
            # Add weapon particles
            self.particle_system.add_particles(
                self.player.weapon_slot.rect.x + CARD_WIDTH // 2,
                self.player.weapon_slot.rect.y + CARD_HEIGHT // 2,
                15,  # Number of particles
                BLUE,  # Blue particles for weapon
                speed=2.5
            )
            
        elif card.card_type == CardType.MONSTER:
            # Only remove the card if the action is successful
            action_successful, player_survived = self.player.fight_monster(card)
            if action_successful:
                # Remove card from room
                self.room_cards.remove(card)
                
                # If no weapon, monster goes directly to discard pile
                if not self.player.weapon_slot.weapon:
                    self.discard_pile.append(card)
                
                # Add monster particles
                self.particle_system.add_particles(
                    card.rect.x + CARD_WIDTH // 2,
                    card.rect.y + CARD_HEIGHT // 2,
                    25,  # Number of particles
                    RED,  # Red particles for combat
                    speed=4.0
                )
                
                # Add screen shake for powerful monsters
                if card.value >= 8:
                    self.screen_shake.start(5.0, 300)  # Intensity, duration
                
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
        if not self.player.weapon_slot.weapon:
            self.player.set_message("No weapon to discard!", YELLOW)
            return
        
        # Add weapon and monsters to discard pile
        weapon = self.player.weapon_slot.weapon
        monsters = self.player.weapon_slot.monsters.copy()
        
        # Animate discard
        if weapon and weapon.rect:
            weapon.add_animation(
                AnimationType.CARD_MOVE,
                300,  # 300ms duration
                (weapon.rect.x, weapon.rect.y),
                DISCARD_POSITION
            )
            
            weapon.add_animation(
                AnimationType.FADE,
                300,  # 300ms duration
                255,  # Start alpha
                0  # End alpha
            )
        
        # Animate monster discards
        for monster in monsters:
            if monster and monster.rect:
                monster.add_animation(
                    AnimationType.CARD_MOVE,
                    300,  # 300ms duration
                    (monster.rect.x, monster.rect.y),
                    DISCARD_POSITION
                )
                
                monster.add_animation(
                    AnimationType.FADE,
                    300,  # 300ms duration
                    255,  # Start alpha
                    0  # End alpha
                )
        
        self.discard_pile.append(weapon)
        self.discard_pile.extend(monsters)
            
        self.player.weapon_slot.discard()
        self.player.set_message("Discarded weapon", BLUE)
        
        # Add discard particles
        self.particle_system.add_particles(
            DISCARD_POSITION[0] + CARD_WIDTH // 2,
            DISCARD_POSITION[1] + CARD_HEIGHT // 2,
            10,  # Number of particles
            (200, 0, 0),  # Red particles for discard
            speed=2.0
        )
        
        # Reset the "just ran" flag when player discards a weapon
        self.just_ran = False
    
    def restart(self) -> None:
        """Restart the game."""
        self.__init__()
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the gameplay state."""
        # Update card animations
        for card in self.room_cards:
            card.update_animations()
        
        if self.player.weapon_slot.weapon:
            self.player.weapon_slot.weapon.update_animations()
            
            for monster in self.player.weapon_slot.monsters:
                monster.update_animations()
        
        # Update player
        self.player.update()
        
        # Update particle system
        self.particle_system.update()
        
        # Update screen shake
        self.screen_shake.update()
        
        # Update button states
        self.run_button.check_hover(mouse_pos)
        self.discard_button.check_hover(mouse_pos)
        self.restart_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)
        
        # Update button enabled states
        self.run_button.enabled = not self.just_ran and bool(self.room_cards)
        self.discard_button.enabled = bool(self.player.weapon_slot.weapon)
    
    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Handle events for the gameplay screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle game over screen
            if self.game_over:
                self.restart()
                return GameState.GAMEPLAY
            
            # Check if a room card was clicked
            for card in self.room_cards:
                if card.rect and card.rect.collidepoint(mouse_pos):
                    self.use_card(self.room_cards.index(card))
                    return GameState.GAMEPLAY
            
            # Check if run button was clicked
            if self.run_button.clicked(mouse_pos):
                self.run_from_room()
                return GameState.GAMEPLAY
            
            # Check if discard button was clicked
            if self.discard_button.clicked(mouse_pos):
                self.discard_weapon()
                return GameState.GAMEPLAY
            
            # Check if restart button was clicked
            if self.restart_button.clicked(mouse_pos):
                self.restart()
                return GameState.GAMEPLAY
            
            # Check if menu button was clicked
            if self.menu_button.clicked(mouse_pos):
                return GameState.MENU
        
        return GameState.GAMEPLAY
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the gameplay screen."""
        try:
            # Apply screen shake
            offset_x, offset_y = self.screen_shake.update()
            
            # Fill the background
            screen.fill(DARK_GREEN)
            
            # Draw table border with offset
            border_rect = pygame.Rect(
                10 + offset_x, 
                10 + offset_y, 
                SCREEN_WIDTH - 20, 
                SCREEN_HEIGHT - 20
            )
            pygame.draw.rect(screen, BROWN, border_rect, 10, border_radius=15)
            
            # Draw deck
            if self.deck:
                deck_rect = pygame.Rect(
                    DECK_POSITION[0] + offset_x, 
                    DECK_POSITION[1] + offset_y, 
                    CARD_WIDTH, 
                    CARD_HEIGHT
                )
                pygame.draw.rect(screen, BLUE, deck_rect, border_radius=5)
                pygame.draw.rect(screen, BLACK, deck_rect, 2, border_radius=5)
                deck_text = FONT_MEDIUM.render(f"Deck: {len(self.deck)}", True, WHITE)
                deck_text_rect = deck_text.get_rect(center=deck_rect.center)
                screen.blit(deck_text, deck_text_rect)
            
            # Draw discard pile on the right side
            discard_rect = pygame.Rect(
                DISCARD_POSITION[0] + offset_x, 
                DISCARD_POSITION[1] + offset_y, 
                CARD_WIDTH, 
                CARD_HEIGHT
            )
            if self.discard_pile:
                pygame.draw.rect(screen, RED, discard_rect, border_radius=5)
                pygame.draw.rect(screen, BLACK, discard_rect, 2, border_radius=5)
                
                # Show the top card of the discard pile
                top_card = self.discard_pile[-1]
                # Make a copy to avoid modifying the original
                top_card_copy = Card(top_card.value, top_card.suit)
                top_card_copy.rect = discard_rect.copy()
                top_card_copy.draw(screen)
            else:
                # Empty discard pile
                pygame.draw.rect(screen, LIGHT_GRAY, discard_rect, border_radius=5)
                pygame.draw.rect(screen, BLACK, discard_rect, 2, border_radius=5)
            
            # Draw discard count
            discard_text = FONT_MEDIUM.render(f"Discard: {len(self.discard_pile)}", True, BLACK)
            discard_text_rect = discard_text.get_rect(center=(discard_rect.centerx, discard_rect.bottom + 25))
            screen.blit(discard_text, discard_text_rect)
            
            # Draw room label
            room_label = FONT_LARGE.render("Room", True, BLACK)
            screen.blit(room_label, (420 + offset_x, 50 + offset_y))
            
            # Draw room cards with offset
            for card in self.room_cards:
                # Temporarily adjust rect for drawing
                original_rect = card.rect.copy() if card.rect else None
                if card.rect:
                    card.rect = pygame.Rect(card.rect.x + offset_x, card.rect.y + offset_y, CARD_WIDTH, CARD_HEIGHT)
                card.draw(screen)
                # Restore original rect
                card.rect = original_rect
            
            # Draw player
            self.player.draw(screen)
            
            # Draw weapon slot label
            weapon_label = FONT_LARGE.render("Weapon Slot", True, BLACK)
            screen.blit(weapon_label, (370 + offset_x, 570 + offset_y))
            
            # Draw "just ran" notification
            if self.just_ran:
                ran_text = FONT_MEDIUM.render("You ran from the last room! Must fight this one!", True, RED)
                screen.blit(ran_text, (50 + offset_x, 550 + offset_y))
            
            # Draw buttons
            self.run_button.draw(screen)
            self.discard_button.draw(screen)
            self.restart_button.draw(screen)
            self.menu_button.draw(screen)
            
            # Draw particles
            self.particle_system.draw(screen)
            
            # Draw game over screen
            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                if self.victory:
                    result_text = FONT_XL.render("VICTORY!", True, GREEN)
                else:
                    result_text = FONT_XL.render("GAME OVER", True, RED)
                
                result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                screen.blit(result_text, result_rect)
                
                restart_text = FONT_LARGE.render("Click anywhere to restart", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(restart_text, restart_rect)
        
        except Exception as e:
            print(f"ERROR drawing gameplay: {e}")