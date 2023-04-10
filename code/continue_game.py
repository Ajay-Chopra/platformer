import pygame
import settings

class ContinueGame:
    """
    Screen that allows the player to choose a previously 
    saved game to continue playing
    """
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 25)
    
    def run(self):
        self.display_surface.fill('black')
        text_surface = self.font.render("Whoops! Looks like this feature isn't implemented yet", False, 'white')
        text_surface_rect = text_surface.get_rect()
        text_surface_rect.center = settings.TITLE_CENTER_POS
        self.display_surface.blit(text_surface, text_surface_rect)

    