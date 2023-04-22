from typing import Tuple
import pygame

from util import import_folder

class Projectile(pygame.sprite.Sprite):
    """
    Represents projectile objects such as 
    thrown sword, cannonball, etc.
    """
    def __init__(
            self, 
            pos: Tuple[int, int],
            velocity: int, 
            path: str,
            collidable_sprites: pygame.sprite.Group,
            killable_sprites: pygame.sprite.Group
        ):
        super().__init__()
        self.velocity = velocity
        self.get_projectile_type(path)
        self.get_projectile_frames(path)
        self.get_embedded_frames()
        # self.frames = import_folder(path)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame_index = 0
        self.animation_speed = 0.50
        

        # get sprite groups
        self.collidable_sprites = collidable_sprites # sprites that will cause the projectile to die
        self.killable_sprites = killable_sprites # sprites that will die when the projectile hits it
    
    def get_projectile_type(self, path: str):
        """
        Get the projectile type from the animation path
        """
        self.type = path.split("/")[3]
    
    def get_projectile_frames(self, path: str) -> None:
        """
        Get the frames for the projectile and flip
        if necessary
        """
        projectile_frames = import_folder(path)
        if self.velocity < 0:
            for i in range(len(projectile_frames)):
                projectile_frames[i] = pygame.transform.flip(projectile_frames[i], flip_x=True, flip_y=False)
        self.frames = projectile_frames

    def get_embedded_frames(self) -> None:
        """
        Get the frames for an embedded sword and flip
        if necessary
        """
        embedded_frames = import_folder("../graphics/projectiles/sword_embedded")
        if self.velocity < 0:
            for i in range(len(embedded_frames)):
                embedded_frames[i] = pygame.transform.flip(embedded_frames[i], flip_x=True, flip_y=False)
        self.embedded_frames = embedded_frames

    def animate(self) -> None:
        """
        Update to the next frame
        """
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            if self.velocity == 0:
                self.animation_speed = 0
                self.frame_index = len(self.frames) - 1
            else:
                self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def check_for_collision(self) -> None:
        """
        Check for collision with collidable sprites
        """
        for sprite in self.collidable_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.type == "sword_spinning":
                    if self.velocity > 0:
                        sword_right = self.rect.right
                        terrain_left = sprite.rect.left
                        if sword_right > terrain_left + 5:
                            self.frames = self.embedded_frames
                            self.velocity = 0
                    else:
                        sword_left = self.rect.left
                        terrain_right = sprite.rect.right
                        if sword_left < (terrain_right - 5):
                            self.frames = self.embedded_frames
                            self.velocity = 0
    
    def update(self, x_shift: int) -> None:
        """
        Update the x coordinate based on player
        movement
        """
        self.check_for_collision()
        self.rect.x += x_shift
        self.rect.x += self.velocity
        self.animate()