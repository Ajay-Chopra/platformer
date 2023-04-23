from typing import List, Tuple
import pygame
from tile import StaticTile, Water, TileCreator
from player import Player
from particles import ParticleEffect
from projectile import Projectile
from ui import UI
from title import Title
import settings as settings
from util import import_csv_layout

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
        
        # player setup and stats
        if self.level_number != "title":
            player_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Player.csv")
            self.player = pygame.sprite.GroupSingle()
            self.goal = pygame.sprite.GroupSingle()
            self.player_setup(layout=player_layout)
        else:
            self.title = Title(
                run_overworld_callback=self.run_overworld_callback,
                run_continue_game_callback=run_continue_game_callback,
                quit_game_callback=quit_game_callback
            )

        # UI setup
        self.ui = UI()

        # sky
        sky_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Sky.csv")
        self.sky_tiles = self.create_tile_group(layout=sky_layout, type="sky")

        # clouds
        cloud_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Clouds.csv")
        self.cloud_tiles = self.create_tile_group(layout=cloud_layout, type="clouds")

        # terrain
        terrain_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Terrain.csv")
        self.terrain_tiles = self.create_tile_group(layout=terrain_layout, type="terrain")
        level_width = len(terrain_layout[0]) * settings.TILE_SIZE

        # bg palms
        bg_palms_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_BG_Palms.csv")
        self.bg_palm_tiles = self.create_tile_group(layout=bg_palms_layout, type="bg_palms")

        # fg palms
        fg_palms_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_FG_Palms.csv")
        self.fg_palm_tiles = self.create_tile_group(layout=fg_palms_layout, type="fg_palms")

        # crates
        crates_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Crates.csv")
        self.crate_tiles = self.create_tile_group(layout=crates_layout, type="crates")

        # coins
        coins_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Coins.csv")
        self.coins_tiles = self.create_tile_group(layout=coins_layout, type="coins")

        # enemies
        enemies_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Enemy.csv")
        self.enemy_sprites = self.create_tile_group(layout=enemies_layout, type="enemies")

        # constraints
        constraints_layout = import_csv_layout(path=f"../level/{level_number}/level_{level_number}_Constraints.csv")
        self.constraint_tiles = self.create_tile_group(layout=constraints_layout, type="constraints")

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosions
        self.explosion_sprite = pygame.sprite.GroupSingle()

        # water
        self.water = Water(top=settings.SCREEN_HEIGHT - 20, level_width=level_width)

        # Get collidable sprites
        self.collidable_sprites = self.terrain_tiles.sprites() + self.crate_tiles.sprites() + self.fg_palm_tiles.sprites()

        # Create the group we'll need for projectile sprites
        self.projectile_sprites = pygame.sprite.Group()
    
    def player_setup(self, layout: List[str]) -> None:
        """
        Place player start and end positions
        """
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                x = j * settings.TILE_SIZE
                y = i * settings.TILE_SIZE
                if cell == '0':
                    sprite = Player(
                        pos=(x, y), 
                        create_jump_particles=self.create_jump_particles,
                        throw_sword=self.handle_sword_throw
                    )
                    self.player.add(sprite)
                elif cell == '1':
                    hat_surface = pygame.image.load("../graphics/character/hat.png")
                    sprite = StaticTile(pos=(x, y), size=settings.TILE_SIZE, surface=hat_surface)
                    self.goal.add(sprite)
    
    def create_tile_group(self, layout: List[str], type: str) -> pygame.sprite.Group:
        sprite_group = pygame.sprite.Group()
        
        for i, row in enumerate(layout):
            for j, col in enumerate(row):
                if col != '-1':
                    x = j * settings.TILE_SIZE
                    y = i * settings.TILE_SIZE
                    tile_creator = TileCreator(pos=(x, y))
                    sprite = tile_creator.tile_creation_functions[type](cell_value=col)
                    sprite_group.add(sprite)
        return sprite_group
    
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
    
    def enemy_collision(self) -> None:
        """
        Handle enemy collisions with the constraints tiles
        """
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_tiles, dokill=False):
                enemy.reverse()
                    
    
    def horizontal_movement_collision(self) -> None:
        """
        Handle horizontal player movement and check for 
        horizontal collision
        """
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.collidable_sprites:
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

        for sprite in self.collidable_sprites:
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
        collected_coins = pygame.sprite.spritecollide(player, self.coins_tiles, dokill=True)
        for coin in collected_coins:
            self.player.sprite.update_coins(coin.type)
    
    def player_enemy_collision(self) -> None:
        """
        Handle player's collisions with enemy sprites
        """
        player = self.player.sprite
        for enemy_sprite in self.enemy_sprites.sprites():
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
            # self.player.sprite.take_hit(direction="left")
            # self.run_overworld_callback(self.level_number)
    
    def check_player_reached_goal(self) -> None:
        """
        Check to see if player reached goal
        """
        if self.level_number != "title":
            player = self.player.sprite
            if pygame.sprite.collide_rect(player, self.goal.sprite):
                next_level = int(self.level_number) + 1
                self.run_overworld_callback(str(next_level))
    
    def draw_non_player_sprites(self) -> None:
        """
        Draw all sprites that are not the player
        """
        self.sky_tiles.update(self.world_shift)
        self.sky_tiles.draw(self.display_surface)

        self.cloud_tiles.update(self.world_shift)
        self.cloud_tiles.draw(self.display_surface)

        self.bg_palm_tiles.update(self.world_shift)
        self.bg_palm_tiles.draw(self.display_surface)

        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        self.explosion_sprite.update(self.world_shift)
        self.explosion_sprite.draw(self.display_surface)

        self.projectile_sprites.update(self.world_shift)
        self.projectile_sprites.draw(self.display_surface)

        self.terrain_tiles.update(self.world_shift)
        self.terrain_tiles.draw(self.display_surface)

        self.crate_tiles.update(self.world_shift)
        self.crate_tiles.draw(self.display_surface)

        self.fg_palm_tiles.update(self.world_shift)
        self.fg_palm_tiles.draw(self.display_surface)

        self.coins_tiles.update(self.world_shift)
        self.coins_tiles.draw(self.display_surface)

        self.enemy_sprites.update(self.world_shift)
        self.enemy_sprites.draw(self.display_surface)

        self.constraint_tiles.update(self.world_shift)
        self.water.draw(self.display_surface, self.world_shift)
    
    def draw_player_related_sprites(self) -> None:
        """
        Draw player sprite and any sprite related to the player
        i.e. the goal sprite
        """
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        self.player.update()
        self.create_landing_particles()
        self.player.draw(self.display_surface)
    
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
        # self.enemy_collision()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.coin_collision()
        self.player_enemy_collision()

    def run(self) -> None:
        """
        Update all sprites and display them
        """
        self.draw_non_player_sprites()
        self.enemy_collision()
        if self.level_number != "title":
            self.scroll_x()
            self.draw_player_related_sprites()
            self.check_player_status()
            self.check_collisions()
            self.ui.display(
                player_health=self.player.sprite.health,
                gold_coins=self.player.sprite.gold_coins,
                silver_coins=self.player.sprite.silver_coins
            )
        else:
            self.title.run()        