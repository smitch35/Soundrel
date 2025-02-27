"""
Player component representing the player in the game.
"""
import pygame
from typing import List, Tuple

from src.components.card import Card
from src.components.weapon import WeaponSlot
from src.animations.effects import DamageNumber
from src.constants import GREEN, RED, BLACK

class Player:
    """Player class representing the player character."""
    def __init__(self):
        """Initialize the player."""
        self.max_hp = 20
        self.hp = 20
        self.weapon_slot = WeaponSlot()
        self.rect = pygame.Rect(50, 650, 200, 80)
        self.message = ""
        self.message_time = 0
        self.message_color = BLACK
        self.damage_numbers: List[DamageNumber] = []
        self.healing_numbers: List[DamageNumber] = []
        # Animation properties
        self.hp_display = 20  # For smooth HP bar animation
        self.current_shake = 0  # For screen shake effect
    
    def use_health_potion(self, card: Card) -> None:
        """Use a health potion to restore HP."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + card.value)
        actual_healing = self.hp - old_hp
        self.set_message(f"Restored {actual_healing} HP", GREEN)
        
        # Add healing number animation
        if actual_healing > 0:
            self.add_healing_number(actual_healing, self.rect.x + 100, self.rect.y)
    
    def equip_weapon(self, card: Card) -> None:
        """Equip a weapon."""
        self.weapon_slot.set_weapon(card)
        self.set_message(f"Equipped {card}", (0, 0, 200))  # Blue
    
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
            
            # Add damage number animation
            self.add_damage_number(damage, self.rect.x + 100, self.rect.y)
            
            # Add screen shake for significant damage
            if damage > 5:
                self.current_shake = min(damage, 10)  # Limit shake to max of 10
            
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
            return (255, 215, 0)  # Yellow
        else:
            return RED
    
    def set_message(self, text: str, color: Tuple[int, int, int]) -> None:
        """Set a message to display to the player."""
        self.message = text
        self.message_time = pygame.time.get_ticks()
        self.message_color = color
    
    def add_damage_number(self, value: int, x: int, y: int) -> None:
        """Add a floating damage number."""
        self.damage_numbers.append(DamageNumber(value, x, y, RED))
    
    def add_healing_number(self, value: int, x: int, y: int) -> None:
        """Add a floating healing number."""
        heal_number = DamageNumber(value, x, y, GREEN, is_heal=True)
        self.healing_numbers.append(heal_number)
    
    def update(self) -> None:
        """Update player animations and effects."""
        # Smooth HP bar animation
        hp_diff = self.hp - self.hp_display
        self.hp_display += hp_diff * 0.1  # Animate 10% of the difference per frame
        
        # Update damage numbers
        for damage_num in self.damage_numbers[:]:
            damage_num.update()
            if damage_num.completed:
                self.damage_numbers.remove(damage_num)
        
        # Update healing numbers
        for heal_num in self.healing_numbers[:]:
            heal_num.update()
            if heal_num.completed:
                self.healing_numbers.remove(heal_num)
        
        # Update screen shake
        if self.current_shake > 0:
            self.current_shake *= 0.9  # Reduce shake intensity each frame
            if self.current_shake < 0.1:
                self.current_shake = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player status on the screen."""
        # Draw HP bar background
        hp_rect = pygame.Rect(self.rect.x, self.rect.y, 200, 30)
        pygame.draw.rect(screen, (128, 128, 128), hp_rect, border_radius=5)  # Gray background
        
        # Draw HP bar fill
        hp_pct = self.hp_display / self.max_hp
        hp_width = int(hp_rect.width * hp_pct)
        hp_bar_rect = pygame.Rect(hp_rect.x, hp_rect.y, hp_width, hp_rect.height)
        hp_color = self.get_hp_color()
        pygame.draw.rect(screen, hp_color, hp_bar_rect, border_radius=5)
        
        # Draw HP text
        hp_text = pygame.font.SysFont("Arial", 20).render(f"HP: {self.hp}/{self.max_hp}", True, (0, 0, 0))
        hp_text_rect = hp_text.get_rect(center=hp_rect.center)
        screen.blit(hp_text, hp_text_rect)
        
        # Draw player message
        if self.message and pygame.time.get_ticks() - self.message_time < 3000:
            message_surf = pygame.font.SysFont("Arial", 20).render(self.message, True, self.message_color)
            screen.blit(message_surf, (screen.get_width() // 2 - message_surf.get_width() // 2, 700))
        
        # Draw damage numbers
        for damage_num in self.damage_numbers:
            damage_num.draw(screen)
        
        # Draw healing numbers
        for heal_num in self.healing_numbers:
            heal_num.draw(screen)
        
        # Draw weapon slot
        self.weapon_slot.draw(screen)