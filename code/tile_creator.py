import pygame
import settings
from util import import_cut_graphics, import_folder
from tile import StaticTile, Palm, Crate, Coin, Tile
from enemy import Enemy, Tooth, Star, Crabs, Shell

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
            return Shell(self.pos, settings.TILE_SIZE)
    
    def create_constraint_tile(self, cell_value: str) -> Tile:
        if cell_value != "-1":
            return Tile(self.pos, settings.TILE_SIZE)