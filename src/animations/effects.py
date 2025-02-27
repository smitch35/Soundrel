"""
Animation effects for gameplay.
"""
import pygame
import math
import random
from typing import List, Dict, Tuple, Any

from src.constants import FONT_LARGE

class DamageNumber:
    """Floating damage number animation."""
    def __init__(self, value: int, x: int, y: int, color: Tuple[int, int, int], is_heal: bool = False):
        """Initialize a damage number animation."""
        self.value = value
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.is_heal = is_heal
        self.start_time = pygame.time.get_ticks()
        self.duration = 1500  # 1.5 seconds
        self.alpha = 255
        self.completed = False
    
    def update(self) -> None:
        """Update the damage number animation."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        # Move upward and fade out
        self.y = self.start_y - (50 * progress)  # Move up 50 pixels
        self.alpha = 255 * (1 - progress)  # Fade out
        
        if progress >= 1.0:
            self.completed = True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the damage number."""
        if self.completed:
            return
            
        font = FONT_LARGE
        
        # Create text with alpha
        prefix = "+" if self.is_heal else "-"
        text = font.render(f"{prefix}{self.value}", True, self.color)
        text_alpha = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_alpha.fill((255, 255, 255, self.alpha))
        text.blit(text_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw text
        screen.blit(text, (self.x, self.y))

class Particle:
    """Individual particle for particle effects."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 velocity: Tuple[float, float], size: int, life: int):
        """Initialize a particle."""
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.size = size
        self.life = life
        self.max_life = life
        self.alpha = 255
    
    def update(self) -> None:
        """Update particle position and properties."""
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Apply gravity
        self.vy += 0.05
        
        # Reduce lifetime
        self.life -= 1
        
        # Update alpha for fade-out
        self.alpha = int(255 * (self.life / self.max_life))
    
    def is_alive(self) -> bool:
        """Check if the particle is still alive."""
        return self.life > 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle on the screen."""
        # Apply alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Calculate size based on remaining life
        current_size = max(1, int(self.size * (self.life / self.max_life)))
        
        # Draw the particle
        pygame.draw.circle(screen, color_with_alpha, (int(self.x), int(self.y)), current_size)

class ParticleSystem:
    """Manages multiple particles for effects."""
    def __init__(self):
        """Initialize the particle system."""
        self.particles: List[Particle] = []
    
    def add_particles(self, x: int, y: int, count: int, color: Tuple[int, int, int], 
                     speed: float = 2.0, size_range: Tuple[int, int] = (2, 6), 
                     life_range: Tuple[int, int] = (20, 60)) -> None:
        """Add multiple particles at the specified position."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed_val = random.uniform(0.5, speed)
            vx = math.cos(angle) * speed_val
            vy = math.sin(angle) * speed_val
            
            size = random.randint(*size_range)
            life = random.randint(*life_range)
            
            particle = Particle(x, y, color, (vx, vy), size, life)
            self.particles.append(particle)
    
    def update(self) -> None:
        """Update all particles."""
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)

class ScreenShake:
    """Screen shake effect."""
    def __init__(self):
        """Initialize the screen shake effect."""
        self.intensity = 0
        self.duration = 0
        self.start_time = 0
        self.active = False
    
    def start(self, intensity: float, duration: int) -> None:
        """Start a screen shake effect."""
        self.intensity = intensity
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.active = True
    
    def update(self) -> Tuple[int, int]:
        """Update the screen shake and return the current offset."""
        if not self.active:
            return (0, 0)
        
        # Calculate progress
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.active = False
            return (0, 0)
        
        # Calculate remaining intensity
        progress = elapsed / self.duration
        current_intensity = self.intensity * (1 - progress)
        
        # Generate random offset
        offset_x = random.uniform(-current_intensity, current_intensity)
        offset_y = random.uniform(-current_intensity, current_intensity)
        
        return (int(offset_x), int(offset_y))