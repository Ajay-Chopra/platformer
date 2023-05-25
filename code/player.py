import pygame
from typing import Tuple, Callable, List
from timer import Timer
from util import import_folder
from math import sin
import settings

class Player(pygame.sprite.Sprite):
    """
    Represents player sprite
    """
    def __init__(
            self, 
            pos: Tuple[int, int],
            create_jump_particles: Callable[[Tuple[int, int]], None],
            toggle_shooter_traps: Callable[[bool], None]
        ):
        super().__init__()

        # movement and jumping
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -16

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_right = False
        self.on_left = False

        # get character assets
        self.import_character_assets()

        # animations
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle_s'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        # dust animations
        self.display_surface = pygame.display.get_surface()
        self.create_jump_particles = create_jump_particles
        self.import_run_dust_animation()
        self.dust_frame_index = 0
        self.dust_image = self.dust_frames[self.dust_frame_index]
        self.dust_animation_speed = 0.15

        # Damage
        self.damaged_time = None
        self.can_be_damaged = True
        self.damage_timeout = 300

        # Coins
        self.silver_coins = 0
        self.gold_coins = 0

        # Health
        self.health = 100
        self.health_increase_amount = settings.COLLECTABLE_ITEM_DATA["diamonds"]["red"]["increase_amount"]

        # potions
        self.potion_timeouts = {
            "blue": settings.COLLECTABLE_ITEM_DATA["potions"]["blue"]["base_time_amount"],
            "green": settings.COLLECTABLE_ITEM_DATA["potions"]["green"]["base_time_amount"]
        }
        self.potion_timers = {
            "blue": Timer(self.potion_timeouts["blue"]),
            "green": Timer(self.potion_timeouts["green"])
        }
        self.toggle_shooter_traps = toggle_shooter_traps

        # diamonds
        self.diamond_counts = {
            "blue": 0,
            "green": 0,
            "red": 0
        }

        # skulls
        self.skulls = 0

        # Attack status
        self.is_attacking = False
        self.attack_time = None
        self.current_air_attack = None
        self.can_begin_new_attack = True
        self.attack_cooldown_time = 400

        # Sword and sword throwing
        self.has_sword = True

        # death animation
        self.is_dead = False
        self.hit_y_speed = -5
        self.hit_x_speed = 10
        self.last_hit_direction = None
    
    def import_character_assets(self) -> None:
        """
        Import all animation/graphics assets
        needed for the player
        """
        assets_path = '../graphics/character/'
        self.animations = {
            'idle_s': [],
            'run_s': [],
            'jump_s': [],
            'fall_s': [],
            'dead_hit': []
        }
        for animation in self.animations.keys():
            full_path = assets_path + animation
            self.animations[animation] = import_folder(full_path)
    
    def import_run_dust_animation(self) -> None:
        """
        Import dust animation used for when character
        is running
        """
        self.dust_frames = import_folder("../graphics/character/dust_particles/run")
    
    def animate(self):
        """
        Animate the player based on status
        """
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.is_dead:
                self.frame_index = len(animation) - 1
            elif self.is_attacking:
                if self.status == 'throw_sword':
                    self.has_sword = False
                self.is_attacking = False
                self.get_status()
                self.frame_index = 0
            else:
                self.frame_index = 0
        
        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, flip_x=True, flip_y=False)
            self.image = flipped_image
        
        # flicker the player if he was damaged
        if not self.can_be_damaged:
            alpha = self.get_wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
    
    def animate_dust(self) -> None:
        """
        Run the dust animation if the player is running
        """
        if self.status == 'run' and self.on_ground:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_frames):
                self.dust_frame_index = 0
            self.dust_image = self.dust_frames[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(self.dust_image, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(self.dust_image, flip_x=True, flip_y=False)
                self.display_surface.blit(flipped_dust_particle, pos)
        
    def get_status(self) -> None:
        """
        Get the status of the player for animation
        """
        if not self.is_dead:
            if self.direction.y < 0:
                if self.current_air_attack is not None:
                    self.status = self.current_air_attack
                else:
                    if self.has_sword:
                        self.status = 'jump_s'
                    else:
                        self.status = 'jump'
            elif self.direction.y > 1:
                if self.current_air_attack is not None:
                    self.status = self.current_air_attack
                else:
                    if self.has_sword:
                        self.status = 'fall_s'
                    else:
                        self.status = 'fall'
            else:
                self.current_air_attack = None
                if self.direction.x != 0:
                    if self.has_sword:
                        self.status = 'run_s'
                    else:
                        self.status = 'run'
                else:
                    if not self.is_attacking:
                        if self.has_sword:
                            self.status = 'idle_s'
                        else:
                            self.status = 'idle'
        else:
            self.status = 'dead_hit'
    
    def get_input(self) -> None:
        """
        Receive user key input
        """
        if not self.is_attacking:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing_right = True
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_right = False
            else:
                self.direction.x = 0
            
            if keys[pygame.K_UP] and self.on_ground:
                self.jump()
                self.create_jump_particles(position = self.rect.midbottom)
                                
    def attack_cooldown(self) -> None:
        """
        Wait for attack to cooldown
        """
        if not self.can_begin_new_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown_time:
                self.can_begin_new_attack = True

    def jump(self) -> None:
        """
        Have the player jump by increasing their
        jump speed toward the top of the screen
        """
        self.direction.y = self.jump_speed
    
    def run_death_animation(self) -> None:
        """
        If the player receives a death blow, update the status
        and alter their x and y position
        """
        if not self.is_dead:
            self.is_dead = True
            self.frame_index = 0
            self.direction.y = self.hit_y_speed
            if self.last_hit_direction == "right":
                self.direction.x = -1 * self.hit_x_speed
            else:
                self.direction.x = self.hit_x_speed
    
    def apply_gravity(self) -> None:
        """
        Apply gravitational force so the player
        doesn't just fly off the screen
        """
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
    
    def get_wave_value(self) -> int:
        """
        Get a periodic wave value for flickering
        player after he experiences damage
        """
        sin_value = sin(pygame.time.get_ticks())
        return 255 if sin_value >= 0 else 0

    def get_damage(self, direction: str) -> None:
        """
        Inflict damage on the player
        """
        if self.can_be_damaged:
            self.health -= 25
            self.can_be_damaged = False
            self.damaged_time = pygame.time.get_ticks()
            self.last_hit_direction = direction
    
    def check_damage_timeout(self) -> None:
        """
        Check to see if damage timeout has elapsed
        """
        if not self.can_be_damaged:
            current_time = pygame.time.get_ticks()
            if (current_time - self.damaged_time) >= self.damage_timeout:
                self.can_be_damaged = True
    
    def update_coins(self, coin_type: str):
        """
        Update player's coin count
        """
        if coin_type == "gold":
            self.gold_coins += 1
        else:
            self.silver_coins += 1
    
    def handle_blue_potion(self):
        """
        Update the player's jump height
        """
        self.jump_speed -= settings.COLLECTABLE_ITEM_DATA["potions"]["blue"]["increase_amount"]
        self.potion_timers["blue"].activate()
        self.diamond_counts["blue"] = 0
    
    def handle_green_potion(self):
        """
        Disable all shooter traps
        """
        self.toggle_shooter_traps(active=False)
        self.potion_timers["green"].activate()
        self.diamond_counts["green"] = 0
    
    def handle_red_potion(self):
        """
        Increase player health
        """
        self.health_increase_amount += self.diamond_counts["red"] * settings.COLLECTABLE_ITEM_DATA["diamonds"]["red"]["increase_amount"]
        self.diamond_counts["red"] = 0
        if self.health < 100:
            self.health += settings.COLLECTABLE_ITEM_DATA["potions"]["red"]["base_increase_amount"]
            self.health = min(100, self.health)
    
    def handle_diamond(self, color: str) -> None:
        """
        Handle diamond depending on color
        """
        self.diamond_counts[color] += 1
        if color == "blue" or color == "green":
            self.potion_timeouts[color] += self.diamond_counts[color] * settings.COLLECTABLE_ITEM_DATA["diamonds"][color]["increase_amount"]
            potion_timer = self.potion_timers[color]
            if potion_timer.active:
                time_remaining = potion_timer.duration - potion_timer.time_running
                potion_timer.deactivate()
                potion_timer = Timer(time_remaining + self.potion_timeouts[color])
                potion_timer.activate()
                self.diamond_counts[color] = 0
            else:
                potion_timer = Timer(self.potion_timeouts[color])
            self.potion_timers[color] = potion_timer
    
    def handle_skull(self) -> None:
        self.skulls += 1
        
    def check_potion_timer_expirations(self):
        """
        Check to see if the potion timers have expired
        """
        if not self.potion_timers["blue"].active:
            self.jump_speed = -16
            self.potion_timeouts["blue"] = settings.COLLECTABLE_ITEM_DATA["potions"]["blue"]["base_time_amount"]
        if not self.potion_timers["green"].active:
            self.toggle_shooter_traps(active=True)
            self.potion_timeouts["green"] = settings.COLLECTABLE_ITEM_DATA["potions"]["green"]["base_time_amount"]
    
    def update_potion_timers(self):
        """
        Update the potion timers
        """
        self.potion_timers["blue"].update()
        self.potion_timers["green"].update()

    def update(self, x_shift=0, y_shift=0) -> None:
        """
        Receive user input and update variables
        """
        self.get_input()
        self.get_status()
        self.animate()
        self.animate_dust()
        self.check_damage_timeout()
        self.check_potion_timer_expirations()
        self.update_potion_timers()