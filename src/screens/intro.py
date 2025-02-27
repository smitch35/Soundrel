"""
Intro screen for the Solitaire RPG game.
"""
import pygame
from typing import Tuple

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GRAY
from src.constants import FONT_TITLE, FONT_MEDIUM
from src.enums import GameState

class IntroScreen:
    """Intro screen for the game."""
    def __init__(self):
        """Initialize the intro screen."""
        self.start_time = pygame.time.get_ticks()
        self.duration = 3000  # 3 seconds
    
    def update(self) -> GameState:
        """Update the intro screen and check if it should transition."""
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            return GameState.MENU
        return GameState.INTRO
    
    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Handle events for the intro screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return GameState.MENU
        return GameState.INTRO
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the intro screen."""
        # Fill with black background for video
        screen.fill(BLACK)
        
        # Draw a placeholder for the video
        title = FONT_TITLE.render("Solitaire RPG", True, WHITE)
        subtitle = FONT_MEDIUM.render("Intro Video Placeholder", True, WHITE)
        skip = FONT_MEDIUM.render("Click anywhere to skip...", True, GRAY)
        
        # Calculate positions
        title_pos = (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3)
        subtitle_pos = (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2)
        skip_pos = (SCREEN_WIDTH // 2 - skip.get_width() // 2, SCREEN_HEIGHT * 3 // 4)
        
        # Draw text
        screen.blit(title, title_pos)
        screen.blit(subtitle, subtitle_pos)
        screen.blit(skip, skip_pos)