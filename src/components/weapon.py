"""
Weapon slot component for managing weapon cards and monsters.
"""
import pygame
from typing import List, Optional, Tuple

from src.components.card import Card
from src.enums import AnimationType
from src.constants import CARD_WIDTH, CARD_HEIGHT, WEAPON_POSITION

class WeaponSlot:
    """Manages the weapon card and associated monsters."""
    def __init__(self):
        """Initialize the weapon slot."""
        self.weapon: Optional[Card] = None
        self.monsters: List[Card] = []
        self.rect = pygame.Rect(WEAPON_POSITION[0], WEAPON_POSITION[1], CARD_WIDTH * 3, CARD_HEIGHT)
    
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
            
            # Add animation for the monster card
            if monster.rect:
                # Calculate final position with offset
                monster_offset = len(self.monsters) * 30
                target_x = self.rect.x + 150 + monster_offset
                target_y = self.rect.y
                
                # Add move animation
                monster.add_animation(
                    AnimationType.CARD_MOVE,
                    300,  # 300ms duration
                    (monster.rect.x, monster.rect.y),
                    (target_x, target_y)
                )
        # No weapon means the monster is defeated but not added to a stack
            
        return True, damage
    
    def set_weapon(self, weapon: Card) -> None:
        """Set a new weapon, clearing any previous weapon and monsters."""
        self.weapon = weapon
        self.monsters = []
        
        # Set weapon position and add animation
        if weapon and weapon.rect:
            # Add move animation to weapon card
            weapon.add_animation(
                AnimationType.CARD_MOVE,
                300,  # 300ms duration
                (weapon.rect.x, weapon.rect.y),
                (self.rect.x, self.rect.y)
            )
            
            # Add pulse animation after move
            weapon.add_animation(
                AnimationType.PULSE,
                500,  # 500ms duration
                1.0,  # Start scale
                1.2  # End scale (not used for pulse)
            )
    
    def discard(self) -> None:
        """Discard this weapon and its monsters."""
        self.weapon = None
        self.monsters = []
    
    def get_protection(self) -> int:
        """Return the protection value of this weapon."""
        return self.weapon.value if self.weapon else 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the weapon slot and cards."""
        # Draw weapon slot background (if no weapon)
        if not self.weapon:
            pygame.draw.rect(screen, (200, 200, 200), self.rect, border_radius=5)
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 1, border_radius=5)
            weapon_text = pygame.font.SysFont("Arial", 16).render("No Weapon", True, (0, 0, 0))
            weapon_text_rect = weapon_text.get_rect(center=self.rect.center)
            screen.blit(weapon_text, weapon_text_rect)
        else:
            # Draw the weapon card
            self.weapon.draw(screen)
            
            # Draw monster cards
            for monster in self.monsters:
                monster.draw(screen)