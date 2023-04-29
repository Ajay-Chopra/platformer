import pygame
from typing import Tuple
from util import import_folder, import_cut_graphics
import settings as settings
from random import randint


class Tile(pygame.sprite.Sprite):
    """
    Represents a single platform tile
    """
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft = pos)
    
    def update(self, x_shift: int) -> None:
        """
        All tiles must have their x coordinate shifted
        based on player movement
        """
        self.rect.x += x_shift


class StaticTile(Tile):
    """
    Represents a static (i.e. non animated) tile
    """
    def __init__(self, pos: Tuple[int, int], size: int, surface):
        super().__init__(pos, size)
        self.image = surface


class Crate(StaticTile):
    """
    Represents a crate that player can hop on
    """
    def __init__(self, pos: Tuple[int, int], size: int):
        image = pygame.image.load("../graphics/terrain/crate.png").convert_alpha()
        super().__init__(pos, size, image)
        x, y = pos
        offset_y = size + y
        self.rect = self.image.get_rect(bottomleft = (x, offset_y))


class AnimatedTile(Tile):
    """
    Represents a tile that has several image frames
    instead of a static image
    """
    def __init__(self, pos: Tuple[int, int], size: int, path: str):
        super().__init__(pos, size)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 0.15
    
    def animate(self) -> None:
        """
        Update the current image
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def update(self, x_shift: int) -> None:
        """
        Update the tile by shifting it and
        also running the animation
        """
        self.rect.x += x_shift
        self.animate()


class Palm(AnimatedTile):
    def __init__(self, pos: Tuple[int, int], size: int, path: str, offset: int):
        super().__init__(pos, size, path)
        x, y = pos
        offset_y = y - offset
        self.rect.topleft = (x, offset_y)


class Coin(AnimatedTile):
    def __init__(self, pos: Tuple[int, int], size: int, path: str):
        super().__init__(pos, size, path)
        x, y = pos
        center_x = x + int(size / 2)
        center_y = y + int(size / 2)
        self.rect = self.image.get_rect(center = (center_x,center_y))
        if "gold" in path:
            self.type = "gold"
        else:
            self.type = "silver"


class Water:
    def __init__(self,top,level_width):
        water_start = -settings.SCREEN_WIDTH
        water_tile_width = 192
        tile_x_amount = int((level_width + settings.SCREEN_WIDTH * 2) / water_tile_width)
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile((x, y), 192, "../graphics/decoration/water")
            self.water_sprites.add(sprite)
            
    def draw(self,surface,shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)