"""
Button component representing interactive UI buttons.
"""
import pygame
from typing import Tuple

from src.constants import FONT_MEDIUM, BLACK

class Button:
    """Interactive button class for UI."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int], action: str):
        """Initialize a button with position, size, colors, and action."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.hovered = False
        self.enabled = True
        # Animation properties
        self.scale = 1.0
        self.pulse_direction = 1
        self.pulse_speed = 0.01
        self.pulse_max = 1.05
        self.pulse_min = 0.95
        self.pressed = False
        self.press_time = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen."""
        color = self.hover_color if self.hovered else self.color
        if not self.enabled:
            color = (128, 128, 128)  # Gray for disabled buttons
        
        # Calculate scaled rectangle
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        centered_x = self.rect.centerx - scaled_width // 2
        centered_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(centered_x, centered_y, scaled_width, scaled_height)
        
        # Draw button with scaling
        pygame.draw.rect(screen, color, scaled_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, scaled_rect, 2, border_radius=5)
        
        # Brighten text color when pressed
        current_text_color = self.text_color
        if self.pressed:
            # Make text brighter
            r, g, b = self.text_color
            current_text_color = (min(255, r + 50), min(255, g + 50), min(255, b + 50))
        
        text_surf = FONT_MEDIUM.render(self.text, True, current_text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)
        
        # Update button animation
        self.update_animation()
    
    def update_animation(self) -> None:
        """Update button animations."""
        # Check if button was recently pressed
        if self.pressed:
            current_time = pygame.time.get_ticks()
            if current_time - self.press_time > 150:  # 150ms press animation
                self.pressed = False
        
        # If hovered, animate pulse effect
        if self.hovered and self.enabled:
            self.scale += self.pulse_direction * self.pulse_speed
            if self.scale >= self.pulse_max:
                self.pulse_direction = -1
            elif self.scale <= self.pulse_min:
                self.pulse_direction = 1
        else:
            # Return to normal scale
            self.scale = 1.0
    
    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Check if mouse is hovering over the button."""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button was clicked."""
        was_clicked = self.enabled and self.rect.collidepoint(pos)
        if was_clicked:
            self.pressed = True
            self.press_time = pygame.time.get_ticks()
            self.scale = 0.9  # Shrink when clicked
        return was_clicked