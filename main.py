"""
Main game class that manages the game state and screens.
"""
import pygame
import sys
from typing import Dict, Any

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.enums import GameState
from src.screens.intro import IntroScreen
from src.screens.menu import MenuScreen
from src.screens.options import OptionsScreen
from src.screens.gameplay import GameplayScreen

class Game:
    """Main game class that controls the game flow."""
    def __init__(self):
        """Initialize the game."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Solitaire RPG")
        self.clock = pygame.time.Clock()
        
        # Current game state
        self.state = GameState.INTRO
        
        # Initialize screens
        self.screens = {
            GameState.INTRO: IntroScreen(),
            GameState.MENU: MenuScreen(),
            GameState.OPTIONS: OptionsScreen(),
            GameState.GAMEPLAY: GameplayScreen()
        }
        
        # Debug message on init
        print("Game initialized!")
    
    def handle_events(self) -> bool:
        """Handle all pygame events. Returns False if the game should exit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle events for the current screen
            new_state = self.screens[self.state].handle_event(event)
            if new_state != self.state:
                print(f"Changing state from {self.state} to {new_state}")
                self.state = new_state
                
                # If transitioning to gameplay, make sure it's initialized
                if new_state == GameState.GAMEPLAY:
                    self.screens[GameState.GAMEPLAY] = GameplayScreen()
        
        return True
    
    def update(self) -> None:
        """Update the current game state."""
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Update the current screen
        if self.state == GameState.INTRO:
            new_state = self.screens[self.state].update()
            if new_state != self.state:
                self.state = new_state
        elif self.state == GameState.MENU:
            self.screens[self.state].update(mouse_pos)
        elif self.state == GameState.OPTIONS:
            self.screens[self.state].update(mouse_pos)
        elif self.state == GameState.GAMEPLAY:
            self.screens[self.state].update(mouse_pos)
    
    def draw(self) -> None:
        """Draw the current game state."""
        # Draw the current screen
        self.screens[self.state].draw(self.screen)
        
        # Update the display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw the game
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)