import pygame
from typing import Tuple
from util import import_folder

class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, position: Tuple[int, int], path: str):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = import_folder(path)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = position)
    
    def animate(self) -> None:
        """
        Loop through animation once
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
    
    def update(self, x_shift: int, y_shift: int) -> None:
        """
        Animate sprites and update x position
        """
        self.animate()
        self.rect.x += x_shift
