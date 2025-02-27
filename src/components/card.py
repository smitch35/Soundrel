"""
Card component representing a playing card in the game.
"""
import pygame
import math
from dataclasses import dataclass, field
from typing import List, Any, Tuple, Optional

from src.enums import Suit, CardType, AnimationType
from src.constants import CARD_WIDTH, CARD_HEIGHT, RED, FONT_LARGE, FONT_SMALL, FONT_XL

@dataclass
class Animation:
    """Animation data for animating card properties."""
    type: AnimationType
    start_time: int
    duration: int
    start_value: Any
    end_value: Any
    target: Any = None
    progress: float = 0.0
    completed: bool = False
    
    def update(self, current_time: int) -> None:
        """Update animation progress."""
        elapsed = current_time - self.start_time
        self.progress = min(1.0, elapsed / self.duration)
        
        if self.progress >= 1.0:
            self.completed = True

@dataclass
class Card:
    """Card class representing a playing card."""
    value: int
    suit: Suit
    rect: pygame.Rect = None
    selected: bool = False
    position_index: int = -1  # To track position in the room
    animating: bool = False
    animations: List[Animation] = field(default_factory=list)
    rotation: float = 0
    scale: float = 1.0
    alpha: int = 255
    
    @property
    def card_type(self) -> CardType:
        """Determine the card type based on its suit."""
        if self.suit == Suit.HEARTS:
            return CardType.HEALTH
        elif self.suit == Suit.DIAMONDS:
            return CardType.WEAPON
        else:  # CLUBS or SPADES
            return CardType.MONSTER
    
    def __str__(self) -> str:
        """String representation of the card."""
        return f"{self.value} of {self.suit.value}"
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get the color of the card based on its suit."""
        if self.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            return RED
        else:
            return (0, 0, 0)  # Black
    
    def add_animation(self, anim_type: AnimationType, duration: int, start_value: Any, end_value: Any, target: Any = None) -> None:
        """Add a new animation to this card."""
        animation = Animation(
            type=anim_type,
            start_time=pygame.time.get_ticks(),
            duration=duration,
            start_value=start_value,
            end_value=end_value,
            target=target
        )
        self.animations.append(animation)
        self.animating = True
    
    def update_animations(self) -> None:
        """Update all animations for this card."""
        if not self.animations:
            self.animating = False
            return
            
        current_time = pygame.time.get_ticks()
        completed_animations = []
        
        for anim in self.animations:
            anim.update(current_time)
            
            # Apply animation effects
            if anim.type == AnimationType.CARD_MOVE:
                # Linear interpolation between positions
                start_x, start_y = anim.start_value
                end_x, end_y = anim.end_value
                current_x = start_x + (end_x - start_x) * anim.progress
                current_y = start_y + (end_y - start_y) * anim.progress
                self.rect = pygame.Rect(current_x, current_y, CARD_WIDTH, CARD_HEIGHT)
            
            elif anim.type == AnimationType.PULSE:
                # Pulse scale (grow and shrink)
                pulse_amount = 0.2  # 20% size increase at peak
                # Use sine wave for smooth pulsing
                pulse_progress = math.sin(anim.progress * math.pi)
                self.scale = 1.0 + (pulse_amount * pulse_progress)
            
            elif anim.type == AnimationType.FADE:
                # Fade transparency
                start_alpha, end_alpha = anim.start_value, anim.end_value
                self.alpha = int(start_alpha + (end_alpha - start_alpha) * anim.progress)
            
            elif anim.type == AnimationType.SHAKE:
                # Shake effect (random offset that reduces over time)
                import random
                shake_amount = 10 * (1 - anim.progress)  # Reduce shake as animation progresses
                if self.rect:
                    offset_x = random.uniform(-shake_amount, shake_amount)
                    offset_y = random.uniform(-shake_amount, shake_amount)
                    self.rect = pygame.Rect(
                        self.rect.x + offset_x, 
                        self.rect.y + offset_y, 
                        CARD_WIDTH, 
                        CARD_HEIGHT
                    )
            
            # Check if animation is completed
            if anim.completed:
                completed_animations.append(anim)
        
        # Remove completed animations
        for anim in completed_animations:
            self.animations.remove(anim)
            
        # Update animation flag
        self.animating = len(self.animations) > 0

    def draw(self, screen: pygame.Surface, selected: bool = False) -> None:
        """Draw the card on the screen."""
        if not self.rect:
            return
            
        try:
            # Create a transparent surface for the card
            card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            
            # Draw card background 
            border = 2 if selected or self.selected else 1
            pygame.draw.rect(card_surface, (255, 255, 255, self.alpha), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
            pygame.draw.rect(card_surface, (0, 0, 0, self.alpha), (0, 0, CARD_WIDTH, CARD_HEIGHT), border, border_radius=5)
            
            # Get card color
            color = self.get_color()
            color_with_alpha = (*color, self.alpha)
            
            # Card value text
            value_text = str(self.value)
            if self.value == 11:
                value_text = "J"
            elif self.value == 12:
                value_text = "Q"
            elif self.value == 13:
                value_text = "K"
            elif self.value == 14:
                value_text = "A"
                
            value_surf = FONT_LARGE.render(value_text, True, color)
            card_surface.blit(value_surf, (5, 5))
            
            # Card suit symbol
            suit_symbol = ""
            if self.suit == Suit.HEARTS:
                suit_symbol = "♥"
            elif self.suit == Suit.DIAMONDS:
                suit_symbol = "♦"
            elif self.suit == Suit.CLUBS:
                suit_symbol = "♣"
            elif self.suit == Suit.SPADES:
                suit_symbol = "♠"
                
            suit_surf = FONT_LARGE.render(suit_symbol, True, color)
            card_surface.blit(suit_surf, (5, 30))
            
            # Draw card type identifier
            type_text = ""
            type_color = (0, 0, 0)  # Black
            
            if self.suit == Suit.HEARTS:
                type_text = "HEALTH"
                type_color = (0, 128, 0)  # Green
            elif self.suit == Suit.DIAMONDS:
                type_text = "WEAPON"
                type_color = (0, 0, 200)  # Blue
            elif self.suit == Suit.CLUBS or self.suit == Suit.SPADES:
                type_text = "MONSTER"
                type_color = (200, 0, 0)  # Red
                
            type_color_with_alpha = (*type_color, self.alpha)
            type_surf = FONT_SMALL.render(type_text, True, type_color)
            card_surface.blit(type_surf, (10, CARD_HEIGHT - 25))
            
            # Draw center symbol
            center_symbol = suit_symbol
            center_surf = FONT_XL.render(center_symbol, True, color)
            center_rect = center_surf.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
            card_surface.blit(center_surf, center_rect)
            
            # Apply scaling if necessary
            if self.scale != 1.0:
                scaled_width = int(CARD_WIDTH * self.scale)
                scaled_height = int(CARD_HEIGHT * self.scale)
                scaled_surface = pygame.transform.scale(card_surface, (scaled_width, scaled_height))
                
                # Draw the scaled surface centered on the original position
                offset_x = (scaled_width - CARD_WIDTH) // 2
                offset_y = (scaled_height - CARD_HEIGHT) // 2
                screen.blit(scaled_surface, (self.rect.x - offset_x, self.rect.y - offset_y))
            else:
                # Draw the normal surface
                screen.blit(card_surface, self.rect)
                
        except Exception as e:
            print(f"ERROR drawing card: {e}")