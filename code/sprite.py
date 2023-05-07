import pygame
from typing import Tuple, List
from random import randint
from util import import_folder
import settings
from timer import Timer

class Generic(pygame.sprite.Sprite):
    """
    The parent sprite class that all other sprites
    will inherit from 
    """
    def __init__(
        self, 
        pos: Tuple[int, int], 
        size: int, 
        groups: List[pygame.sprite.Group]
    ):
        super().__init__(groups)
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=pos)
    
    def update(self, x_shift: int) -> None:
        """
        All tiles must have their x coordinate shifted
        based on player movement
        """
        self.rect.x += x_shift
    

class StaticTile(Generic):
    """
    Represents a immovable tile
    """
    def __init__(
        self, 
        pos: Tuple[int , int], 
        size: int, 
        groups: List[pygame.sprite.Group],
        surface: pygame.Surface
    ):
        super().__init__(pos, size, groups)
        self.image = surface


class Crate(StaticTile):
    """
    Separate class needed for the crates because
    they're special and the image needs adjusting
    """
    def __init__(
            self,
            pos: Tuple[int, int],
            size: int,
            groups: List[pygame.sprite.Group],
            surface: pygame.Surface
    ):
        super().__init__(pos, size, groups, surface)
        x, y = pos
        offset_y = size + y
        self.rect = self.image.get_rect(bottomleft = (x, offset_y))


class AnimatedTile(Generic):
    """
    For simple animated sprites and level tiles
    """
    def __init__(
        self, 
        pos: Tuple[int, int], 
        size: int, 
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups)
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
    """
    For FG and BG Palms
    """
    def __init__(
        self, 
        pos: Tuple[int, int], 
        size: int,
        groups: List[pygame.sprite.Group], 
        path: str, 
        offset: int
    ):
        super().__init__(pos, size, groups, path)
        x, y = pos
        offset_y = y - offset
        self.rect.topleft = (x, offset_y)


class Coin(AnimatedTile):
    """
    Used for coins that player can collect
    (may extend to other kinds of gems as well)
    """
    def __init__(
        self, 
        pos: Tuple[int, int], 
        size: int, 
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
        x, y = pos
        center_x = x + int(size / 2)
        center_y = y + int(size / 2)
        self.rect = self.image.get_rect(center = (center_x,center_y))
        if "gold" in path:
            self.type = "gold"
        else:
            self.type = "silver"


class Enemy(AnimatedTile):
    """
    Generic enemy class
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        constraint_sprites: pygame.sprite.Group,
        path: str,
        animation_speed: float,
        min_speed: int,
        max_speed
    ):
        super().__init__(pos, size, groups, path)
        self.constraint_sprites = constraint_sprites
        self.animation_speed = animation_speed
        self.speed = randint(min_speed, max_speed)
        self.rect.y += size - self.image.get_size()[1]
    
    def move(self) -> None:
        self.rect.x += self.speed
    
    def check_for_collision(self) -> None:
        """
        Check to see if enemy has collided with a
        constraint sprite
        """
        if pygame.sprite.spritecollide(self, self.constraint_sprites, dokill=False):
            self.reverse()
    
    def reverse_image(self) -> None:
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def reverse(self) -> None:
        self.speed *= -1
    
    def update(self, x_shift: int) -> None:
        self.rect.x += x_shift
        self.move()
        self.check_for_collision()
        self.animate()
        self.reverse_image()


class ShooterTrap(Generic):
    """
    For any enemy that shoots projectiles
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups)
        self.animation_frames = {
            'left_idle': [],
            'right_idle': [],
            'left_attack': [],
            'right_attack': []
        }
        self.get_assets(path)
        self.frame_index = 0
        self.status = 'left_attack'
        self.image = self.animation_frames[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.bottom = self.rect.top + settings.TILE_SIZE
        self.speed = 0
        self.animation_speed = 0.15

        # shooting
        self.has_shot = False
        self.attack_cooldown = Timer(4000)
    
    def get_assets(self, path: str):
        """
        Import the animation frames for the shell
        """
        for animation in self.animation_frames.keys():
            full_path = f"{path}/{animation}"
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

        if int(self.frame_index) == 2 and 'attack' in self.status and not self.has_shot:
            if 'left' in self.status:
                projectile_direction = pygame.math.Vector2(-1, 0)
                offset = (projectile_direction * 50) + pygame.math.Vector2(0, 0)
            else:
                projectile_direction = pygame.math.Vector2(1, 0)
                offset = (projectile_direction * 20) + pygame.math.Vector2(0, 0)
            Projectile(
                pos=self.rect.center + offset,
                size=settings.TILE_SIZE,
                groups=self.groups(),
                direction=projectile_direction,
                speed=20,
                surface=pygame.image.load("../graphics/projectiles/pearl/pearl.png")
            )
            self.has_shot = True

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


class Projectile(Generic):
    """
    Any projectile that is shot from a shooter trap
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        direction: pygame.math.Vector2,
        speed: int,
        surface: pygame.Surface
    ):
        super().__init__(pos, size, groups)

        # movement
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = direction
        self.speed = speed
        self.image = surface

        # self destruct
        self.timer = Timer(6000)
        self.timer.activate()
    
    def update(self, x_shift: int):
        self.pos.x += self.direction.x * self.speed
        self.rect.x = round(self.pos.x)

        self.timer.update()
        if not self.timer.active:
            self.kill()


class Water:
    def __init__(self,top,level_width):
        water_start = -settings.SCREEN_WIDTH
        water_tile_width = 192
        tile_x_amount = int((level_width + settings.SCREEN_WIDTH * 2) / water_tile_width)
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile((x, y), 192, [], "../graphics/decoration/water")
            self.water_sprites.add(sprite)
            
    def draw(self,surface,shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)
