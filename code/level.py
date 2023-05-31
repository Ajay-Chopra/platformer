from typing import List, Tuple
import pygame
from sprite import (
    StaticTile, 
    Palm, 
    Crate,
    Crabs,
    Tooth,
    Star,
    Shell, 
    Cannon, 
    Water, 
    SilverCoin, 
    GoldCoin, 
    RedDiamond,
    BlueDiamond,
    GreenDiamond,
    RedPotion,
    BluePotion,
    GreenPotion,
    Skull,
    ParticleEffect
)
from player import Player
from ui import UI, GameOver
from title import Title
import settings as settings
from util import import_csv_layout, import_folder, import_cut_graphics

class Level:
    """
    Represents an individual level of the game
    """
    def __init__(
            self, 
            level_number: str, 
            screen: pygame.Surface,
            restart_level_callback, 
            run_overworld_callback,
            quit_game_callback,
            update_level_failed
        ):
        self.display_surface = screen
        self.level_number = level_number
        self.restart_level_callback = restart_level_callback
        self.run_overworld_callback = run_overworld_callback
        self.quit_game_callback = quit_game_callback
        self.update_level_failed = update_level_failed

        
        # Setup horizontal scrolling
        self.world_x_shift = 0
        self.current_x = 0
        self.player_on_ground = False

        # Setup vertical scrolling
        self.world_y_shift = 0
        self.current_y = 0

        # set up sprite groups
        # self.all_sprites = CameraGroup() # holds all of the sprites
        self.all_sprites = CameraGroup() # holds all of the sprites
        self.collectable_sprites = pygame.sprite.Group() # items that can be collected by the player
        self.damage_sprites = pygame.sprite.Group() # sprites that can inflict damage on the player
        self.shooter_sprites = pygame.sprite.Group() # All shooter trap sprites
        self.collision_sprites = pygame.sprite.Group() # sprites that player can collide with
        self.constraint_sprites = pygame.sprite.Group() # constraint tiles for the enemies
        self.player = pygame.sprite.GroupSingle() # the player
        self.dust_sprite = pygame.sprite.GroupSingle() # the dust sprite created by jumping and landing
        self.goal = pygame.sprite.GroupSingle() # the goal the player must reach to beat level
        self.explosion_sprite = pygame.sprite.GroupSingle() # explosion that plays when player kills enemy
        self.collect_effect_sprites = pygame.sprite.Group() # particle effect that plays when player collects an item
        self.water_sprites = pygame.sprite.Group() # To check if player hits water

        # get csv layouts
        self.csv_layouts = {
            "Sky": [],
            "Constraints": [],
            "Clouds": [],
            "BG_Palms": [],
            "Player": [],
            "Terrain": [],
            "Crates": [],
            "Collectables": [],
            "Enemy": [],
            "Shooters": [],
            "Water": []
        }
        self.get_level_layer_data()
        self.setup_level_sprites()
        self.starting_distance_to_goal = self.goal.sprite.rect.centerx - self.player.sprite.rect.centerx
        self.player_progress = 0

        # Setup vertical scrolling
        self.world_y_shift = self.player.sprite.rect.centery - (settings.SCREEN_HEIGHT / 2)
        self.current_y = 0

        # UI setup
        self.ui = UI()
        self.game_over = GameOver(
            player=self.player.sprite,
            level_number=self.level_number,
            restart_level=self.restart_level_callback,
            run_overworld=self.run_overworld_callback,
            quit_game=self.quit_game_callback
        )
    
    def get_level_layer_data(self) -> None:
        """
        For each layer in the level, import the csv data
        """
        for layer_name in self.csv_layouts.keys():
            self.csv_layouts[layer_name] = import_csv_layout(path=f"../level/{self.level_number}/level_{self.level_number}_{layer_name}.csv")
            if layer_name == "Terrain":
                self.level_width = len(self.csv_layouts[layer_name][0]) * settings.TILE_SIZE
    
    def setup_level_sprites(self) -> None:
        """
        Create the sprites based on the level csv data
        """
        for layer_name in self.csv_layouts.keys():
            layout = self.csv_layouts[layer_name]
            for i, row in enumerate(layout):
                for j, col in enumerate(row):
                    if col != '-1':
                        x = j * settings.TILE_SIZE
                        y = i * settings.TILE_SIZE
                        if layer_name == "Sky":
                            self.create_sky_sprite(pos=(x, y), cell_value=col)
                        elif layer_name == "Clouds":
                            cloud_surfaces = import_folder("../graphics/decoration/clouds")
                            tile_surface = cloud_surfaces[int(col)]
                            StaticTile(
                                pos=(x, y), 
                                size=settings.TILE_SIZE, 
                                groups=[self.all_sprites], 
                                surface=tile_surface
                            )
                        elif layer_name == "Terrain":
                            terrain_surfaces = import_cut_graphics("../graphics/terrain/terrain_tiles.png")
                            tile_surface = terrain_surfaces[int(col)]
                            StaticTile(
                                pos=(x, y), 
                                size=settings.TILE_SIZE, 
                                groups=[self.all_sprites, self.collision_sprites],
                                surface=tile_surface 
                            )
                        elif layer_name == "BG_Palms":
                            Palm(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites],
                                path="../graphics/terrain/palm_bg",
                                offset=64
                            )
                        elif layer_name == "FG_Palms":
                            if col in ["0", "1", "2", "3"]:
                                path = "../graphics/terrain/palm_large"
                                offset = 64
                            elif col in ["4", "5", "6", "7"]:
                                path = "../graphics/terrain/palm_small",
                                offset = 38
                            Palm(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites, self.collision_sprites],
                                path=path,
                                offset=offset
                            )
                        elif layer_name == "Crates":
                            Crate(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites, self.collision_sprites],
                                surface=pygame.image.load("../graphics/terrain/crate.png").convert_alpha()
                            )
                        elif layer_name == "Collectables":
                            if col == "0":
                                BlueDiamond(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["diamonds"]["blue"]["path"]
                                )
                            elif col == "1":
                                BluePotion(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["potions"]["blue"]["path"]
                                )
                            elif col == "2":
                                GoldCoin(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["coins"]["gold"]["path"]
                                )
                            elif col == "3":
                                Skull(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["skull"]["path"]
                                )
                            elif col == "4":
                                GreenPotion(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["potions"]["green"]["path"]
                                )
                            elif col == "5":
                                GreenDiamond(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["diamonds"]["green"]["path"]
                                )
                            elif col == "6":
                                RedDiamond(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["diamonds"]["red"]["path"]
                                )
                            elif col == "7":
                                RedPotion(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["potions"]["red"]["path"]
                                )
                            elif col == "8":
                                SilverCoin(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.collectable_sprites],
                                    path=settings.COLLECTABLE_ITEM_DATA["coins"]["silver"]["path"] 
                                )
                        elif layer_name == "Constraints":
                            StaticTile(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.constraint_sprites],
                                surface=pygame.image.load("../graphics/enemy/setup_tile.png")
                            )
                        elif layer_name == "Enemy":
                            if col == "0":
                                Crabs(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.damage_sprites],
                                    constraint_sprites=self.constraint_sprites
                                )
                            elif col == "1":
                                Tooth(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.damage_sprites],
                                    constraint_sprites=self.constraint_sprites
                                )
                            elif col == "2":
                                Star(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.damage_sprites],
                                    constraint_sprites=self.constraint_sprites
                                )
                        elif layer_name == "Shooters":
                            if col == "0":
                                Cannon(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.damage_sprites, self.shooter_sprites],
                                    direction="left"
                                )
                            elif col == "1":
                                Cannon(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites, self.damage_sprites, self.shooter_sprites],
                                    direction="right"
                                )                        
                        elif layer_name == "Player":
                            if col == "0":
                                sprite = Player(
                                    pos=(x, y),
                                    create_jump_particles=self.create_jump_particles,
                                    toggle_shooter_traps=self.toggle_shooter_traps_active
                                )
                                self.all_sprites.add(sprite)
                                self.player.add(sprite)
                            elif col == "1":
                                sprite = StaticTile(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites],
                                    surface=pygame.image.load("../graphics/character/hat.png").convert_alpha()
                                )
                                self.goal.add(sprite)
                        elif layer_name == "Water":
                            Water(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites, self.water_sprites],
                                path="../graphics/decoration/water"
                            )
                            
    def create_sky_sprite(self, pos: Tuple[int, int], cell_value: str):
        """
        Create the sprites that create the background sky
        """
        if cell_value == "0":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_bottom.png").convert_alpha()
        elif cell_value == "1":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_middle.png").convert_alpha()
        elif cell_value == "2":
            tile_surface = pygame.image.load("../graphics/decoration/sky/sky_top.png").convert_alpha()
        StaticTile(pos=pos, size=settings.TILE_SIZE, groups=[self.all_sprites], surface=tile_surface)
     
    def scroll_x(self) -> None:
        """
        Scroll the platform tiles based on the following logic:
        - if player is in first 1/4 of the screen and moving left, shift right
        - if plyaer is in last 1/4 of screen and moving right, shift left
        - else don't shift
        """
        player = self.player.sprite
        player_x = player.rect.centerx
        print(f"Player_X: {player_x}")
        player_x_direction = player.direction.x

        if player_x < (settings.SCREEN_WIDTH / 4) and player_x_direction < 0:
            self.world_x_shift = 8
            player.speed = 0
        elif player_x > (settings.SCREEN_WIDTH - (settings.SCREEN_WIDTH / 4)) and player_x_direction > 0:
            self.world_x_shift = - 8
            player.speed = 0
        else:
            self.world_x_shift = 0
            player.speed = 8

    def scroll_y(self) -> None:
        """
        """
        player = self.player.sprite
        player_y = player.rect.centery
        print(player_y)
        player_y_direction = player.direction.y

        if player_y < (settings.SCREEN_HEIGHT / 4) and player_y_direction < 0:
            self.world_y_shift = 24
        elif player_y > (settings.SCREEN_HEIGHT - (settings.SCREEN_HEIGHT / 4)) and player_y_direction > 0:
            self.world_y_shift = -24
        else:
            self.world_y_shift = 0
     
    def horizontal_movement_collision(self) -> None:
        """
        Handle horizontal player movement and check for 
        horizontal collision
        """
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: # moving left
                    player.rect.left = sprite.rect.right
                    player.direction.x = 0
                    player.on_left = True
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.direction.x = 0
                    player.on_right = True
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False
    
    def vertical_movement_collision(self) -> None:
        """
        Handle vertical player movement and check for
        vertical collision
        """
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False
    
    def item_collision(self) -> None:
        """
        Handle player's collisions with coin sprites
        """
        player = self.player.sprite
        collected_items = pygame.sprite.spritecollide(player, self.collectable_sprites, dokill=True)
        for item in collected_items:
            item.perform_player_modification(self.player.sprite)
            effect_path = item.effect_path
            self.collect_effect_sprites.add(
                ParticleEffect(
                    pos=item.rect.center,
                    size=settings.TILE_SIZE,
                    groups=[self.all_sprites], 
                    path=effect_path
                )
            )
    
    def player_enemy_collision(self) -> None:
        """
        Handle player's collisions with enemy sprites
        """
        player = self.player.sprite
        for enemy_sprite in self.damage_sprites.sprites():
            if pygame.sprite.collide_rect(player, enemy_sprite):
                # if player rect bottom is higher than enemy top, kill the enemy
                player_bottom = player.rect.bottom
                enemy_top = enemy_sprite.rect.top
                enemy_center = enemy_sprite.rect.centery
                if enemy_top < player_bottom < enemy_center and player.direction.y >= 0:
                    player.direction.y = -15
                    self.explosion_sprite.add(ParticleEffect(
                        pos=enemy_sprite.rect.center,
                        size=settings.TILE_SIZE,
                        groups=[self.all_sprites],
                        path="../graphics/enemy/explosion"
                    ))
                    enemy_sprite.kill()
                else:
                    if self.player.sprite.is_attacking:
                        enemy_sprite.kill()
                    else:
                        if enemy_sprite.rect.left <= player.rect.right:
                            self.player.sprite.get_damage(direction="right")
                        elif enemy_sprite.rect.right >= player.rect.left:
                            self.player.sprite.get_damage(direction="left")
    
    def check_player_off_map(self):
        """
        Check to see if the player has fallen off the map
        """
        player = self.player.sprite
        for water_sprite in self.water_sprites.sprites():
            if pygame.sprite.collide_rect(player, water_sprite):
                self.player.sprite.health = 0
    
    def get_player_on_ground(self):
        """
        Keep track of whether player is on ground or not
        """
        self.player_on_ground = self.player.sprite.on_ground is True

    def create_jump_particles(self, position: Tuple[int, int]) -> None:
        if self.player.sprite.facing_right:
            position -= pygame.math.Vector2(10,5)
        else:
            position += pygame.math.Vector2(10, -5)
        self.dust_sprite.add(ParticleEffect(
            pos=position,
            size=settings.TILE_SIZE,
            groups=[self.all_sprites], 
            path="../graphics/character/dust_particles/jump")
        )
    
    def create_landing_particles(self) -> None:
        """
        Add dust particles when the player lands
        """
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            landing_particle = ParticleEffect(
                pos=self.player.sprite.rect.midbottom - offset,
                size=settings.TILE_SIZE,
                groups=[self.all_sprites],
                path="../graphics/character/dust_particles/land"
            )
            self.dust_sprite.add(landing_particle)
    
    def check_player_death(self) -> None:
        """
        Check to see if player's health is at or below 0
        """
        if self.player.sprite.health <= 0:
            if self.player.sprite.skulls > 0:
                self.player.sprite.skulls -= 1
                self.player.sprite.health = 100
            else:
                self.player.sprite.is_dead = True
                self.get_player_progress()
                self.update_level_failed()
    
    def get_player_progress(self) -> None:
        """
        Check the amount of the map that the player
        covered before dying
        """
        current_distance_to_goal = self.goal.sprite.rect.centerx - self.player.sprite.rect.centerx
        progress = 1 - (current_distance_to_goal / self.starting_distance_to_goal)
        self.player_progress = round(progress, 3) * 100
        print(self.player_progress)
    
    def check_player_reached_goal(self) -> None:
        """
        Check to see if player reached goal
        """
        if self.level_number != "title":
            player = self.player.sprite
            if pygame.sprite.collide_rect(player, self.goal.sprite):
                next_level = int(self.level_number) + 1
                self.run_overworld_callback(str(next_level))
     
    def check_player_status(self) -> None:
        """
        Check if player has reached goal, is off the map
        or is dead
        """
        self.check_player_off_map()
        self.check_player_death()
        self.check_player_reached_goal()
    
    def check_collisions(self) -> None:
        """
        Check for any collisions e.g. player with terrain,
        player with enemy, player with coin, etc.
        """
        # Handle collisions
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.item_collision()
        self.player_enemy_collision()

    def toggle_shooter_traps_active(self, active: bool) -> None:
        """
        Toggle shooter traps between active/inactive
        """
        for shooter_sprite in self.shooter_sprites.sprites():
            shooter_sprite.active = active
    
    def disable_shooter_traps(self) -> None:
        """
        Disable all of the shooter trap sprites
        """
        for shooter_sprite in self.shooter_sprites.sprites():
            shooter_sprite.active = False
    
    def enable_shooter_traps(self) -> None:
        """
        Enable all of the shooter traps again
        """
        for shooter_sprite in self.shooter_sprites.sprites():
            shooter_sprite.active = True

    def run(self, mouse_down: bool) -> None:
        """
        Update all sprites and display them
        """
        self.all_sprites.custom_draw(self.player.sprite)
        self.all_sprites.update(0, 0)
        if not self.player.sprite.is_dead:
            self.dust_sprite.update(0, 0)
            self.dust_sprite.draw(self.display_surface)
            self.create_landing_particles()
            self.check_player_status()
            self.check_collisions()
        else:
            self.game_over.update(mouse_down)
            self.game_over.display(self.player_progress)
            
        self.ui.display(
            player=self.player.sprite
        )


class CameraGroup(pygame.sprite.Group):
    """
    Custom sprite group that contains all sprites and draws them
    according to the player's position
    """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
    
    def custom_draw(self, player: pygame.sprite.Sprite):
        """
        Draw all sprites
        """
        self.offset.x = player.rect.centerx - (settings.SCREEN_WIDTH / 2)
        self.offset.y = player.rect.centery - (settings.SCREEN_HEIGHT / 2)

        for sprite in self:
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)