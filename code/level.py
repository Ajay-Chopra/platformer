from typing import List, Tuple
import pygame
from sprite import StaticTile, Palm, Crate, Coin, Enemy, ShooterTrap, Water
from tile_creator import TileCreator
from player import Player
from particles import ParticleEffect
from projectile import Projectile
from ui import UI
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
            run_overworld_callback,
            run_continue_game_callback, 
            quit_game_callback
        ):
        self.display_surface = screen
        self.level_number = level_number
        self.run_overworld_callback = run_overworld_callback
        
        # Setup horizontal scrolling
        self.world_shift = 0
        self.current_x = 0

        # set up sprite groups
        self.all_sprites = pygame.sprite.Group() # holds all of the sprites
        self.collectable_sprites = pygame.sprite.Group() # items that can be collected by the player
        self.damage_sprites = pygame.sprite.Group() # sprites that can inflict damage on the player
        self.collision_sprites = pygame.sprite.Group() # sprites that player can collide with
        self.constraint_sprites = pygame.sprite.Group() # constraint tiles for the enemies
        self.player = pygame.sprite.GroupSingle() # the player
        self.dust_sprite = pygame.sprite.GroupSingle() # the dust sprite created by jumping and landing
        self.goal = pygame.sprite.GroupSingle() # the goal the player must reach to beat level
        self.explosion_sprite = pygame.sprite.GroupSingle() # explosion that plays when player kills enemy

        # get csv layouts
        self.csv_layouts = {
            "Player": [],
            "Sky": [],
            "Clouds": [],
            "Terrain": [],
            "BG_Palms": [],
            "FG_Palms": [],
            "Crates": [],
            "Coins": [],
            "Enemy": [],
            "Constraints": []
        }
        self.get_level_layer_data()
        self.setup_level_sprites()

        # UI setup
        self.ui = UI()

        # Last but not least the water
        self.water = Water(top=settings.SCREEN_HEIGHT - 20, level_width=self.level_width)
    
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
                        elif layer_name == "Coins":
                            if col == "0":
                                path = "../graphics/coins/gold"
                            elif col == "1":
                                path = "../graphics/coins/silver"
                            Coin(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites, self.collectable_sprites],
                                path=path
                            )
                        elif layer_name == "Constraints":
                            StaticTile(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.constraint_sprites],
                                surface=pygame.image.load("../graphics/enemy/setup_tile.png")
                            )
                        elif layer_name == "Enemy":
                            # Enemy(
                            #     pos=(x, y),
                            #     size=settings.TILE_SIZE,
                            #     groups=[self.all_sprites, self.damage_sprites],
                            #     constraint_sprites=self.constraint_sprites,
                            #     path="../graphics/enemy/crabs",
                            #     animation_speed=0.30,
                            #     min_speed=5,
                            #     max_speed=10
                            # )
                            ShooterTrap(
                                pos=(x, y),
                                size=settings.TILE_SIZE,
                                groups=[self.all_sprites, self.damage_sprites],
                                path="../graphics/enemy/shell"
                            )
                        elif layer_name == "Player":
                            if col == "0":
                                sprite = Player(
                                    pos=(x, y),
                                    create_jump_particles=self.create_jump_particles,
                                    throw_sword=self.handle_sword_throw
                                )
                                self.player.add(sprite)
                            elif col == "1":
                                sprite = StaticTile(
                                    pos=(x, y),
                                    size=settings.TILE_SIZE,
                                    groups=[self.all_sprites],
                                    surface=pygame.image.load("../graphics/character/hat.png").convert_alpha()
                                )
                                self.goal.add(sprite)
                            
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
        player_x_direction = player.direction.x

        if player_x < (settings.SCREEN_WIDTH / 4) and player_x_direction < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > (settings.SCREEN_WIDTH - (settings.SCREEN_WIDTH / 4)) and player_x_direction > 0:
            self.world_shift = - 8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8
     
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
    
    def coin_collision(self) -> None:
        """
        Handle player's collisions with coin sprites
        """
        player = self.player.sprite
        collected_coins = pygame.sprite.spritecollide(player, self.collectable_sprites, dokill=True)
        for coin in collected_coins:
            self.player.sprite.update_coins(coin.type)
    
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
                        position=enemy_sprite.rect.center,
                        type="explosion"
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
    
    def handle_sword_throw(self, sword_velocity: int) -> None:
        """
        Display spinning sword after player
        throws sword
        """
        player = self.player.sprite
        self.projectile_sprites.add(Projectile(
            pos=player.rect.topleft,
            velocity=sword_velocity,
            path="../graphics/projectiles/sword_spinning",
            collidable_sprites=self.terrain_tiles.sprites(),
            killable_sprites=self.enemy_sprites.sprites()
        ))

    def check_player_off_map(self):
        """
        Check to see if the player has fallen off the map
        """
        player = self.player.sprite
        if player.rect.bottom >= settings.SCREEN_HEIGHT:
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
        self.dust_sprite.add(ParticleEffect(position=position, type="jump"))
    
    def create_landing_particles(self) -> None:
        """
        Add dust particles when the player lands
        """
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            landing_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, "land")
            self.dust_sprite.add(landing_particle)
    
    def check_player_death(self) -> None:
        """
        Check to see if player's health is at or below 0
        """
        if self.player.sprite.health <= 0:
            self.player.sprite.run_death_animation()
    
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
        self.coin_collision()
        self.player_enemy_collision()

    def run(self) -> None:
        """
        Update all sprites and display them
        """
        self.all_sprites.update(self.world_shift)
        self.all_sprites.draw(self.display_surface)
        self.player.update()
        self.player.draw(self.display_surface)
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        self.explosion_sprite.update(self.world_shift)
        self.explosion_sprite.draw(self.display_surface)
        self.water.draw(self.display_surface, self.world_shift)
        self.scroll_x()
        self.check_player_status()
        self.check_collisions()
        self.ui.display(
            player_health=self.player.sprite.health,
            gold_coins=self.player.sprite.gold_coins,
            silver_coins=self.player.sprite.silver_coins
        )      