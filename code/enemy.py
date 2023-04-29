import pygame
from tile import AnimatedTile
from timer import Timer
from typing import Tuple
from random import randint
from util import import_folder
import settings

class Enemy(AnimatedTile):
    def __init__(self, pos: Tuple[int, int], size: int, path: str):
        super().__init__(pos, size, path)
        self.rect.y += size - self.image.get_size()[1]
        self.speed = randint(3, 5)
    
    def move(self) -> None:
        self.rect.x += self.speed
    
    def reverse_image(self) -> None:
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def reverse(self) -> None:
        self.speed *= -1
    
    def update(self, x_shift: int) -> None:
        self.rect.x += x_shift
        self.move()
        self.animate()
        self.reverse_image()

class Tooth(Enemy):
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__(pos, size, "../graphics/enemy/tooth/run")

class Star(Enemy):
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__(pos, size, "../graphics/enemy/star")
        self.animation_speed = 0.30
        self.speed = randint(10, 15)

class Crabs(Enemy):
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__(pos, size, "../graphics/enemy/crabs")

class Shell(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__()
        self.animation_frames = {
            'left_idle': [],
            'right_idle': [],
            'left_attack': [],
            'right_attack': []
        }
        self.get_assets()
        self.frame_index = 0
        self.status = 'left_attack'
        self.image = self.animation_frames[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.bottom = self.rect.top + settings.TILE_SIZE
        self.speed = 0
        self.animation_speed = 0.15

        # shooting
        self.has_shot = False
        self.attack_cooldown = Timer(2000)

    def get_assets(self):
        """
        Import the animation frames for the shell
        """
        for animation in self.animation_frames.keys():
            full_path = f"../graphics/enemy/shell/{animation}"
            self.animation_frames[animation] = import_folder(full_path)
    
    def animate(self):
        """
        Animate the shell basdd on its current status
        """
        current_animation = self.animation_frames[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.has_shot:
                self.attack_cooldown.activate()
                self.has_shot = False
        self.image = current_animation[int(self.frame_index)]


    def reverse(self) -> None:
        pass

    def get_status(self):
        if not self.attack_cooldown.active:
            self.status = 'left_attack'
        else:
            self.status = 'left_idle'

    def update(self, x_shift: int) -> None:
        """
        Shift the x coordinate based on player movement
        """
        self.rect.x += x_shift
        self.get_status()
        self.animate()
        self.attack_cooldown.update()

class Pearl(pygame.sprite.Sprite):
    """
    Represents the pearl that is shot from the shell
    """
    def __init__(self):
        super().__init__()
        self.image = pygame
        self.pos = pygame.math.Vector2(self.rect.topleft)