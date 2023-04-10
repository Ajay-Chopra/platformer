import pygame
import math
from typing import Tuple
import settings as settings
from tile import AnimatedTile


class Node(AnimatedTile):
    """
    Represents a single node (representing a level)
    of the overworld
    """
    def __init__(self, pos: Tuple[int, int], size: int, path: str, level_name: str):
        super().__init__(pos, size, path)
        self.level_name = level_name
    
    def custom_update(self, is_reachable: bool):
        """
        Custom update function that takes into account
        reachability of node
        """
        if not is_reachable:
            tint_surface = self.image.copy()
            tint_surface.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surface, (0, 0))
        else:
            self.animate()

    def custom_draw(self, display_surface, is_reachable: bool):
        """
        Custom draw function taht takes into account reachability of node
        """
        if not is_reachable:
            tint_surface = self.image.copy()
            tint_surface.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surface, (0, 0))
        display_surface.blit(self.image, self.rect)


class Selector:
    """
    Sprite that hops from node to node
    to indicate level selection
    """
    def __init__(self, current_level: str):
        self.display_surface = pygame.display.get_surface()
        self.current_level = current_level
        self.current_pos = settings.NODE_DATA[self.current_level]["node_pos"]
        self.current_pos = (self.current_pos[0] + settings.NODE_OFFSET, self.current_pos[1] + settings.NODE_OFFSET)

        # Get hat image
        self.image = pygame.image.load("../graphics/overworld/hat.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.current_pos
    
    def move_to_node(self, node_name: str, speed: int, delta_time: float):
        """
        Move to another node given its node name
        """
        node_data = settings.NODE_DATA[node_name]
        node_x = node_data["node_pos"][0] + settings.NODE_OFFSET
        node_y = node_data["node_pos"][1] + settings.NODE_OFFSET

        # Get relative x and y distance
        rel_x = self.rect.centerx - node_x
        rel_y = self.rect.centery - node_y

        # Get distance and angle
        distance = math.sqrt((rel_x ** 2) + (rel_y ** 2))
        angle = math.atan2(- rel_y, - rel_x)

        # Get change in distance
        delta_distance = (distance / (speed * delta_time)) + 5
        if delta_distance > distance:
            delta_distance = distance
        
        delta_x = math.cos(angle) * (delta_distance)
        delta_y = math.sin(angle) * (delta_distance)

        if distance > 0:
            self.rect.centerx += delta_x
            self.rect.centery += delta_y

    def draw(self):
        self.move_to_node(node_name=self.current_level, speed=50, delta_time=0.25)
        self.display_surface.blit(self.image, self.rect)

class Overworld:
    """
    Handles setup and interaction with the 
    overworld where player can progress from
    level to level
    """
    def __init__(self, furthest_unlocked_level: str, run_level_callback):
        self.display_surface = pygame.display.get_surface()
        self.furthest_unlocked_level = furthest_unlocked_level

        if furthest_unlocked_level != "0":
            self.current_level = str(int(furthest_unlocked_level) - 1)
        else:
            self.current_level = self.furthest_unlocked_level
        self.waiting = True
        self.initial_wait = 300
        self.init_time = pygame.time.get_ticks()

        self.num_levels = len(settings.NODE_DATA.keys())
        self.selector = Selector(current_level=self.current_level)

        # Get nodes
        self.node_sprites = self.get_node_sprite_group()

        # Get callback function
        self.run_level_callback = run_level_callback

        # user input variables
        self.can_accept_input = False
        self.input_time = pygame.time.get_ticks()
        self.input_cooldown = 300

        # Get background image
        self.background_image = pygame.image.load("../graphics/overworld/overworld_background.png").convert_alpha()
        self.background_image_rect = self.background_image.get_rect()

    def draw_background_image(self):
        """
        Draw the background image for the overworld
        """
        self.display_surface.blit(self.background_image, self.background_image_rect)
    
    def get_node_sprite_group(self):
        """
        Get a sprite group of animated tiles representing nodes
        """
        node_sprite_group = pygame.sprite.Group()
        for level_name in settings.NODE_DATA:
            node_data = settings.NODE_DATA[level_name]
            node_pos = node_data["node_pos"]
            size = settings.TILE_SIZE
            path = f"../graphics/overworld/{level_name}"
            node = Node(pos=node_pos, size=size, path=path, level_name=level_name)
            node_sprite_group.add(node)
        return node_sprite_group

    def draw_nodes(self):
        """
        Update and draw nodes
        """
        for sprite in self.node_sprites.sprites():
            is_reachable = int(sprite.level_name) <= int(self.furthest_unlocked_level)
            sprite.custom_update(is_reachable=is_reachable)
        self.node_sprites.draw(self.display_surface)
    
    def draw_connections(self):
        """
        Draw lines connecting to nodes that are reachable
        """
        for level_name in settings.NODE_DATA:
            curr_node = settings.NODE_DATA[level_name]
            next_level_name = curr_node["unlock"]
            next_node = settings.NODE_DATA[next_level_name]
            if int(self.furthest_unlocked_level) >= int(next_level_name):
                line_start = curr_node["node_pos"]
                line_start = (line_start[0] + settings.NODE_OFFSET, line_start[1] + settings.NODE_OFFSET)
                line_end = next_node["node_pos"]
                line_end = (line_end[0] + settings.NODE_OFFSET, line_end[1] + settings.NODE_OFFSET)
                pygame.draw.line(self.display_surface, settings.LINE_COLOR, line_start, line_end, width=5)
    
    def handle_user_input(self):
        """
        Look for user key input and handle based
        on the key pressed
        """
        if self.can_accept_input:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.can_accept_input = False
                self.input_time = pygame.time.get_ticks()
                current_level = int(self.current_level)
                if (current_level < self.num_levels - 1) and (current_level <= int(self.furthest_unlocked_level) - 1):
                    self.current_level = str(current_level + 1)
            elif keys[pygame.K_LEFT]:
                self.can_accept_input = False
                self.input_time = pygame.time.get_ticks()
                current_level = int(self.current_level)
                if current_level > 0:
                    self.current_level = str(current_level - 1)
            elif keys[pygame.K_RETURN]:
                self.run_level_callback(level_number=self.current_level)
    
    def handle_input_cooldown(self):
        if not self.can_accept_input:
            current_time = pygame.time.get_ticks()
            if (current_time - self.input_time) > self.input_cooldown:
                self.can_accept_input = True
    
    def handle_initial_wait(self):
        if self.waiting:
            current_time = pygame.time.get_ticks()
            if (current_time - self.init_time) > self.initial_wait:
                self.current_level = self.furthest_unlocked_level
                self.waiting = False

    def run(self):
        """
        Run the overworld loop
        """
        self.draw_background_image()
        self.draw_connections()
        self.draw_nodes()
        self.handle_user_input()
        self.handle_input_cooldown()
        self.handle_initial_wait()
        self.selector.current_level = self.current_level
        self.selector.draw()