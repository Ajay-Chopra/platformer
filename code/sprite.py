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


class Collectable(AnimatedTile):
    """
    Represents any item that the player can collect
    during gameplay in order to enhance their abilities
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
        self.effect_path = ""

    def perform_player_modification(self, player: pygame.sprite.Sprite):
        """
        Perform modification on the player
        """
        pass

class Coin(Collectable):
    """
    Coins add to the player's score
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
        self.effect_path = "../graphics/collectables/coins/effect"

class SilverCoin(Coin):
    """
    Silver are worth less than gold coins
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
    
    def perform_player_modification(self, player: pygame.sprite.Sprite):
        player.update_coins(coin_type="silver")

class GoldCoin(Coin):
    """
    Gold coins count towards player's score but to a larger
    degree than silver coins
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
    
    def perform_player_modification(self, player: pygame.sprite.Sprite):
        player.update_coins(coin_type="gold")


class Diamond(Collectable):
    """
    Diamonds increase the timeout of the potion of the 
    corresponding color
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
        self.effect_path = "../graphics/collectables/diamonds/effect"


class RedDiamond(Diamond):
    """
    Health increases by a larger amount
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)


class BlueDiamond(Diamond):
    """
    Jump increase lasts longer
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)


class GreenDiamond(Diamond):
    """
    Jump increase lasts longer
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
    

class Potion(Collectable):
    """
    Potions enhance player abilities
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
        self.effect_path = "../graphics/collectables/potions/effect"

class RedPotion(Potion):
    """
    The red potion replenishes player health
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)


class BluePotion(Potion):
    """
    The blue potion increases the height of the 
    player's jump
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)


class GreenPotion(Potion):
    """
    The green potion pauses all shooter traps
    for a given amount of time
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)


class Skull(Collectable):
    """
    The skull adds an extra life for the player
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group],
        path: str
    ):
        super().__init__(pos, size, groups, path)
        self.effect_path = "../graphics/collectables/skull/effect"
        
    
    


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

        # These will be overwritten by the child class
        self.shoot_frame = 2
        self.projectile_surface = pygame.image.load("../graphics/projectiles/pearl/pearl.png")
        self.projectile_speed = 20
        self.attack_cooldown_min_time = 4000
        self.attack_cooldown_max_time = 6000
        self.projectile_offset = pygame.math.Vector2(0, 0)

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
        self.attack_cooldown = Timer(randint(self.attack_cooldown_min_time, self.attack_cooldown_max_time))
    
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

        if int(self.frame_index) == self.shoot_frame and 'attack' in self.status and not self.has_shot:
            if 'left' in self.status:
                projectile_direction = pygame.math.Vector2(-1, 0)
                offset = (projectile_direction * 50) + self.projectile_offset
            else:
                projectile_direction = pygame.math.Vector2(1, 0)
                offset = (projectile_direction * 20) + self.projectile_offset
            Projectile(
                pos=self.rect.center + offset,
                size=settings.TILE_SIZE,
                groups=self.groups(),
                direction=projectile_direction,
                speed=self.projectile_speed,
                surface=self.projectile_surface
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


class Shell(ShooterTrap):
    """
    The shell shooter trap that shoots a pearl
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group]
    ):
        super().__int__(pos, size, groups, "../graphics/enemy/shell")
        self.shoot_frame = 2
        self.projectile_surface = pygame.image.load("../graphics/projectiles/pearl/pearl.png")
        self.projectile_speed = 20
        self.attack_cooldown_min_time = 4000
        self.attack_cooldown_max_time = 6000
        self.projectile_offset = pygame.math.Vector2(0, 0)
       

class Cannon(ShooterTrap):
    """
    The cannon shooter trap that shoots a cannnon ball
    """
    def __init__(
        self,
        pos: Tuple[int, int],
        size: int,
        groups: List[pygame.sprite.Group]
    ):
        super().__init__(pos, size, groups, path="../graphics/enemy/cannon")
        self.shoot_frame = 4
        self.projectile_surface = pygame.image.load("../graphics/projectiles/cannon/ball.png")
        self.projectile_speed = 20
        self.attack_cooldown_time = 4000
        self.projectile_offset = pygame.math.Vector2(0, -90)
        


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
