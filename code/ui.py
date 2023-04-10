import pygame
import settings as settings
from typing import Tuple

class UI:
    """
    Responsible for all UI features such as player health,
    gold coin and silver coin count
    """
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        # health bar
        self.health_bar_image = pygame.image.load("../graphics/ui/health_bar.png").convert_alpha()
        self.health_bar_rect = self.health_bar_image.get_rect()
        self.health_bar_rect.topleft = settings.HEALTH_BAR_POS

        # gold coins
        self.gold_coin_image = pygame.image.load("../graphics/ui/gold_coin.png").convert_alpha()
        self.gold_coin_rect = self.gold_coin_image.get_rect()
        self.gold_coin_rect.topleft = settings.GOLD_COIN_IMAGE_POS

        # silver coins
        self.silver_coin_image = pygame.image.load("../graphics/ui/silver_coin.png").convert_alpha()
        self.silver_coin_rect = self.silver_coin_image.get_rect()
        self.silver_coin_rect.topleft = settings.SILVER_COIN_IMAGE_POS

        self.font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 12)

    def display_player_health(self, player_health: int):
        """
        Display player health bar
        """
        self.display_surface.blit(self.health_bar_image, self.health_bar_rect)
        health_rect_width = (player_health / 100) * settings.MAX_HEALTH_RECT_WIDTH
        health_rect = pygame.rect.Rect(
            settings.HEALTH_BAR_RECT_POS[0],
            settings.HEALTH_BAR_RECT_POS[1],
            health_rect_width,
            settings.HEALTH_RECT_HEIGHT
        )
        pygame.draw.rect(self.display_surface, 'red', health_rect)
                
    def display_player_coins(self, gold_coins: int, silver_coins: int):
        """
        Display player's gold and silver coin count
        """
        self.display_surface.blit(self.gold_coin_image, self.gold_coin_rect)
        self.display_surface.blit(self.silver_coin_image, self.silver_coin_rect)
        self.display_text(f": {gold_coins}", settings.GOLD_COIN_TEXT_POS)
        self.display_text(f": {silver_coins}", settings.SILVER_COIN_TEXT_POS)
        
    def display_text(self, text: str, position: Tuple[int, int]):
        """
        Display text to the screen in a given position
        """
        text_surface = self.font.render(text, False, 'black')
        self.display_surface.blit(text_surface, position)
    
    def display(self, player_health: int, gold_coins: int, silver_coins: int):
        """
        Display all values
        """
        self.display_player_health(player_health)
        self.display_player_coins(gold_coins, silver_coins)