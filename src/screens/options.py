"""
Options screen for the Solitaire RPG game.
"""
import pygame
from typing import List, Tuple

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, YELLOW
from src.constants import FONT_TITLE, FONT_MEDIUM, FONT_SMALL
from src.components.button import Button
from src.enums import GameState

class OptionsScreen:
    """Options screen for the game."""
    def __init__(self):
        """Initialize the options screen."""
        self.background_color = (20, 60, 120)  # Dark blue
        
        # Create buttons
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 490, 200, 50, "Back to Menu", (255, 215, 0), (200, 200, 200), BLACK, "back_to_menu")
        ]
        
        # Option values (not functional in this version)
        self.sound_enabled = True
        self.music_enabled = True
        self.difficulty = "Normal"
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the options screen."""
        # Update button hover states
        for button in self.buttons:
            button.check_hover(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Handle events for the options screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.clicked(mouse_pos):
                    if button.action == "back_to_menu":
                        return GameState.MENU
        return GameState.OPTIONS
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the options screen."""
        # Draw dark blue background
        screen.fill(self.background_color)
        
        # Draw title
        title = FONT_TITLE.render("Options", True, WHITE)
        title_pos = (SCREEN_WIDTH // 2 - title.get_width() // 2, 100)
        screen.blit(title, title_pos)
        
        # Draw placeholder options
        option_texts = [
            f"Sound: {'ON' if self.sound_enabled else 'OFF'}",
            f"Music: {'ON' if self.music_enabled else 'OFF'}",
            f"Difficulty: {self.difficulty}"
        ]
        
        for i, text in enumerate(option_texts):
            option = FONT_MEDIUM.render(text, True, WHITE)
            pos = (SCREEN_WIDTH // 2 - option.get_width() // 2, 200 + i * 60)
            screen.blit(option, pos)
        
        # Draw note that options aren't functional yet
        note = FONT_SMALL.render("Note: Options are not functional in this version", True, YELLOW)
        note_pos = (SCREEN_WIDTH // 2 - note.get_width() // 2, 400)
        screen.blit(note, note_pos)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)