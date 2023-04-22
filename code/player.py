import pygame
from typing import Tuple, Callable
import settings
from util import import_folder
from math import sin

class Player(pygame.sprite.Sprite):
    """
    Represents player sprite
    """
    def __init__(
            self, 
            pos: Tuple[int, int], 
            create_jump_particles: Callable[[Tuple[int, int]], None],
            throw_sword: Callable[[], None]
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

        # Coins and health
        self.silver_coins = 0
        self.gold_coins = 0
        self.health = 100

        # Attack status
        self.is_attacking = False
        self.attack_time = None
        self.current_air_attack = None
        self.can_begin_new_attack = True
        self.attack_cooldown_time = 400

        # Sword and sword throwing
        self.has_sword = True
        self.throw_sword = throw_sword
    
    def import_character_assets(self) -> None:
        """
        Import all animation/graphics assets
        needed for the player
        """
        assets_path = '../graphics/character/'
        self.animations = {
            'idle': [],
            'idle_s': [],
            'run': [],
            'run_s': [],
            'jump': [],
            'jump_s': [],
            'fall': [],
            'fall_s': [],
            'attack_1': [],
            'attack_2': [],
            'attack_3': [],
            'air_attack_1': [],
            'air_attack_2': [],
            'throw_sword': []
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
            if self.is_attacking:
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
        
        # set rectangle
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright = self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft = self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop = self.rect.midtop)
        
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

            if self.has_sword:
                if keys[pygame.K_d]:
                    self.is_attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.status = 'attack_1'
                    self.current_air_attack = 'air_attack_1'
                elif keys[pygame.K_s]:
                    self.is_attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.status = 'attack_2'
                    self.current_air_attack = 'air_attack_2'
                elif keys[pygame.K_a]:
                    self.is_attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.status = 'attack_3'
                    self.current_air_attack = None
                elif keys[pygame.K_SPACE]:
                    self.is_attacking = True
                    self.attack_time = pygame.time.get_ticks()
                    self.status = 'throw_sword'
                    self.current_air_attack = 'throw_sword'
                    sword_velocity = settings.SWORD_VELOCITY if self.facing_right else (-1 * settings.SWORD_VELOCITY)
                    self.throw_sword(sword_velocity)
                                
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

    def get_damage(self) -> None:
        """
        Inflict damage on the player
        """
        if self.can_be_damaged:
            self.health -= 25
            self.can_be_damaged = False
            self.damaged_time = pygame.time.get_ticks()
    
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

    def update(self) -> None:
        """
        Receive user input and update variables
        """
        self.get_input()
        self.get_status()
        self.animate()
        self.animate_dust()
        # Sself.attack_cooldown()
        self.check_damage_timeout()