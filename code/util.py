import pygame
from typing import List
from os import walk
from csv import reader
import settings as settings

def import_folder(path: str) -> List[pygame.Surface]:
    """
    Import sorted folder of images for animation
    """
    surface_list = []

    for _,_,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surface = pygame.image.load(full_path).convert_alpha()
            # image_surface = pygame.transform.scale(image_surface, (settings.TILE_SIZE, settings.TILE_SIZE))
            surface_list.append(image_surface)
    return surface_list

def import_csv_layout(path: str) -> List[str]:
    """
    Import CSV layout as a 2D list
    """
    map = []
    with open(path) as map_file:
       map_data = reader(map_file, delimiter=',')
       for row in map_data:
        map.append(list(row))
    return map

def import_cut_graphics(path):
	surface = pygame.image.load(path).convert_alpha()
	tile_num_x = int(surface.get_size()[0] / settings.TILE_SIZE)
	tile_num_y = int(surface.get_size()[1] / settings.TILE_SIZE)

	cut_tiles = []
	for row in range(tile_num_y):
		for col in range(tile_num_x):
			x = col * settings.TILE_SIZE
			y = row * settings.TILE_SIZE
			new_surf = pygame.Surface((settings.TILE_SIZE,settings.TILE_SIZE),flags = pygame.SRCALPHA)
			new_surf.blit(surface,(0,0),pygame.Rect(x,y,settings.TILE_SIZE,settings.TILE_SIZE))
			cut_tiles.append(new_surf)

	return cut_tiles