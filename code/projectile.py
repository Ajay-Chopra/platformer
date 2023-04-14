from typing import Tuple
import pygame

from util import import_folder

class Projectile(pygame.sprite.Sprite):
    """
    Represents projectile objects such as 
    thrown sword, cannonball, etc.
    """
    def __init__(self, pos: Tuple[int, int], path: str):
        super().__init__()
        self.frames = import_folder(path)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame_index = 0
        self.animation_speed = 0.50
        self.velocity = 10
    
    def animate(self) -> None:
        """
        Update to the next frame
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def update(self, x_shift: int) -> None:
        """
        Update the x coordinate based on player
        movement
        """
        self.rect.x += x_shift
        self.rect.x += self.velocity
        self.animate()