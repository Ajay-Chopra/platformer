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


class Enemy(AnimatedTile):
    def __init__(self, pos: Tuple[int, int], size: int):
        super().__init__(pos, size, "../graphics/enemy/run")
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


class TileCreator:
    """
    Handles creation of specific tiles
    """
    def __init__(self, pos):
        self.pos = pos
        self.tile_creation_functions = {
            "terrain": self.create_terrain_tile,
            "sky": self.create_sky_tile,
            "clouds": self.create_cloud_tile,
            "bg_palms": self.create_bg_palm_tile,
            "crates": self.create_crate_tile,
            "fg_palms": self.create_fg_palm_tile,
            "coins": self.create_coin_tile,
            "enemies": self.create_enemy_tile,
            "constraints": self.create_constraint_tile
        }
    
    def create_terrain_tile(self, cell_value: str) -> StaticTile:
        terrain_tiles = import_cut_graphics("../graphics/terrain/terrain_tiles.png")
        tile_surface = terrain_tiles[int(cell_value)]
        sprite = StaticTile(self.pos, settings.TILE_SIZE, tile_surface)
        return sprite
    
    def create_sky_tile(self, cell_value: str) -> StaticTile:
        if cell_value == "0":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_bottom.png").convert_alpha()
        elif cell_value == "1":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_middle.png").convert_alpha()
        elif cell_value == "2":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_top.png").convert_alpha()
        sprite = StaticTile(self.pos, settings.TILE_SIZE, tile_surface)
        return sprite
    
    def create_cloud_tile(self, cell_value: str) -> StaticTile:
        clouds = import_folder("../graphics/decoration/clouds")
        tile_surface = clouds[int(cell_value)]
        # cloud_tiles = import_cut_graphics("../graphics/decoration/clouds/1.png")
        # tile_surface = cloud_tiles[int(cell_value)]
        sprite = StaticTile(self.pos, settings.TILE_SIZE, tile_surface)
        return sprite
    
    def create_bg_palm_tile(self, cell_value: str) -> StaticTile:
        path = "../graphics/terrain/palm_bg"
        sprite = Palm(self.pos, settings.TILE_SIZE, path, 64)
        return sprite
    
    def create_crate_tile(self, cell_value: str) -> Crate:
        if cell_value != "-1":
            return Crate(self.pos, settings.TILE_SIZE)
        
    def create_fg_palm_tile(self, cell_value: str) -> Palm:
        if cell_value in ["0", "1", "2", "3"]:
            path = "../graphics/terrain/palm_large"
            sprite = Palm(self.pos, settings.TILE_SIZE, path, 64)
        elif cell_value in ["4", "5", "6", "7"]:
            path = "../graphics/terrain/palm_small"
            sprite = Palm(self.pos, settings.TILE_SIZE, path, 38)
        return sprite
    
    def create_coin_tile(self, cell_value: str) -> Coin:
        if cell_value == "0":
            path = "../graphics/coins/gold"
        elif cell_value == "1":
            path = "../graphics/coins/silver"
        sprite = Coin(self.pos, settings.TILE_SIZE, path)
        return sprite
    
    def create_enemy_tile(self, cell_value: str) -> Enemy:
        if cell_value != "-1":
            return Enemy(self.pos, settings.TILE_SIZE)
    
    def create_constraint_tile(self, cell_value: str) -> Tile:
        if cell_value != "-1":
            return Tile(self.pos, settings.TILE_SIZE)
