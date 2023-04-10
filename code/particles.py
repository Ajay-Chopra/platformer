import pygame
from typing import Tuple
from util import import_folder

class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, position: Tuple[int, int], type: str):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.15
        if type == "explosion":
            assets_folder = "../graphics/enemy/explosion"
        else:
            assets_folder = f"../graphics/character/dust_particles/{type}"
        self.frames = import_folder(assets_folder)
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
    
    def update(self, x_shift: int) -> None:
        """
        Animate sprites and update x position
        """
        self.animate()
        self.rect.x += x_shift
