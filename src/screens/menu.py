"""
Main menu screen for the Solitaire RPG game.
"""
import pygame
from typing import List, Tuple

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK
from src.constants import FONT_TITLE, FONT_LARGE, FONT_SMALL
from src.components.button import Button
from src.enums import GameState

class MenuScreen:
    """Main menu screen for the game."""
    def __init__(self):
        """Initialize the menu screen."""
        self.background_color = (40, 100, 180)  # Medium blue
        
        # Create buttons
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "New Game", (0, 128, 0), (200, 200, 200), BLACK, "new_game"),
            Button(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "Options", (0, 0, 200), (200, 200, 200), BLACK, "options"),
            Button(SCREEN_WIDTH // 2 - 100, 490, 200, 50, "Exit Game", (200, 0, 0), (200, 200, 200), BLACK, "exit")
        ]
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the menu screen."""
        # Update button hover states
        for button in self.buttons:
            button.check_hover(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Handle events for the menu screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.clicked(mouse_pos):
                    if button.action == "new_game":
                        return GameState.GAMEPLAY
                    elif button.action == "options":
                        return GameState.OPTIONS
                    elif button.action == "exit":
                        pygame.quit()
                        exit()
        return GameState.MENU
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu screen."""
        # Draw blue background
        screen.fill(self.background_color)
        
        # Draw placeholder for background art
        pygame.draw.rect(screen, (30, 80, 150), (100, 50, SCREEN_WIDTH - 200, 200))
        
        # Draw game title
        title = FONT_TITLE.render("Solitaire RPG", True, WHITE)
        subtitle = FONT_LARGE.render("Card Dungeon Adventures", True, WHITE)
        
        # Calculate positions
        title_pos = (SCREEN_WIDTH // 2 - title.get_width() // 2, 100)
        subtitle_pos = (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170)
        
        # Draw text
        screen.blit(title, title_pos)
        screen.blit(subtitle, subtitle_pos)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
        # Draw version
        version = FONT_SMALL.render("v1.0", True, WHITE)
        screen.blit(version, (20, SCREEN_HEIGHT - 30))