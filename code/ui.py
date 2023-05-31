import pygame
import settings as settings
from typing import Tuple, Callable

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

        # blue diamonds
        self.blue_diamond_image = pygame.image.load(settings.COLLECTABLE_ITEM_DATA["diamonds"]["blue"]["ui_path"]).convert_alpha()
        self.blue_diamond_rect = self.blue_diamond_image.get_rect()
        self.blue_diamond_rect.topleft = settings.BLUE_DIAMOND_IMAGE_POS

        # green diamond
        self.green_diamond_image = pygame.image.load(settings.COLLECTABLE_ITEM_DATA["diamonds"]["green"]["ui_path"]).convert_alpha()
        self.green_diamond_rect = self.green_diamond_image.get_rect()
        self.green_diamond_rect.topleft = settings.GREEN_DIAMOND_IMAGE_POS

        # red diamond
        self.red_diamond_image = pygame.image.load(settings.COLLECTABLE_ITEM_DATA["diamonds"]["red"]["ui_path"]).convert_alpha()
        self.red_diamond_rect = self.red_diamond_image.get_rect()
        self.red_diamond_rect.topleft = settings.RED_DIAMOND_IMAGE_POS

        # blue potion
        self.potion_images = {
            "blue": pygame.image.load(settings.COLLECTABLE_ITEM_DATA["potions"]["blue"]["ui_path"]).convert_alpha(),
            "green": pygame.image.load(settings.COLLECTABLE_ITEM_DATA["potions"]["green"]["ui_path"]).convert_alpha()
        }

        # skull image
        self.skull_image = pygame.image.load(settings.COLLECTABLE_ITEM_DATA["skull"]["ui_path"]).convert_alpha()
        self.skull_rect = self.skull_image.get_rect()
        self.skull_rect.topleft = settings.SKULL_IMAGE_POS

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
    
    def display_diamonds(self, blue_diamond_count: int, green_diamond_count: int, red_diamond_count: int):
        """
        Display the player's blue diamond count
        """
        self.display_surface.blit(self.blue_diamond_image, self.blue_diamond_rect)
        self.display_text(f": {blue_diamond_count}", settings.BLUE_DIAMOND_TEXT_POS)
        self.display_surface.blit(self.green_diamond_image, self.green_diamond_rect)
        self.display_text(f": {green_diamond_count}", settings.GREEN_DIAMOND_TEXT_POS)
        self.display_surface.blit(self.red_diamond_image, self.red_diamond_rect)
        self.display_text(f": {red_diamond_count}", settings.RED_DIAMOND_TEXT_POS)
    
    def display_potion_timers(self, potion_timers: dict):
        """
        Display the bars that indicate how much longer
        potions remain effective 
        """
        self.display_potion_timer(potion_timers, "blue")
        self.display_potion_timer(potion_timers, "green")
    
    def display_skull_count(self, skull_count: int):
        """
        Display the number of skulls the player has
        """
        self.display_surface.blit(self.skull_image, self.skull_rect)
        self.display_text(f": {skull_count}", settings.SKULL_TEXT_POS)

    def display_potion_timer(self, potion_timers: dict, color: str):
        """
        Display potion timer based on color
        """
        potion_timer = potion_timers[color]
        if potion_timer.active:
            current_time = pygame.time.get_ticks()
            potion_rect_width = 1 - ((current_time - potion_timer.start_time) / potion_timer.duration)
        else:
            potion_rect_width = 0
        
        potion_bg_rect = pygame.rect.Rect(
            settings.COLLECTABLE_ITEM_DATA["potions"][color]["timer_pos"][0],
            settings.COLLECTABLE_ITEM_DATA["potions"][color]["timer_pos"][1],
            settings.MAX_POTION_RECT_WIDTH,
            settings.POTION_RECT_HEIGHT
        )
        potion_rect = pygame.rect.Rect(
            settings.COLLECTABLE_ITEM_DATA["potions"][color]["timer_pos"][0],
            settings.COLLECTABLE_ITEM_DATA["potions"][color]["timer_pos"][1],
            potion_rect_width * settings.MAX_POTION_RECT_WIDTH,
            settings.POTION_RECT_HEIGHT
        )
        
        potion_image_rect = self.potion_images[color].get_rect()
        potion_image_rect.topleft = settings.COLLECTABLE_ITEM_DATA["potions"][color]["image_pos"]

        self.display_surface.blit(self.potion_images[color], potion_image_rect)
        pygame.draw.rect(self.display_surface, 'black', potion_bg_rect, 3)
        pygame.draw.rect(self.display_surface, color, potion_rect)
        
    def display_text(self, text: str, position: Tuple[int, int]):
        """
        Display text to the screen in a given position
        """
        text_surface = self.font.render(text, False, 'black')
        self.display_surface.blit(text_surface, position)
    
    def display(self, player: pygame.sprite.Sprite):
        """
        Display all player attributes
        """
        self.display_player_health(player.health)
        self.display_player_coins(player.gold_coins, player.silver_coins)
        self.display_diamonds(
            player.diamond_counts["blue"], 
            player.diamond_counts["green"],
            player.diamond_counts["red"]
        )
        self.display_skull_count(player.skulls)
        self.display_potion_timers(potion_timers=player.potion_timers)


class GameOver:
    """
    Displayed if player dies before completing the level
    """
    def __init__(self, 
            player: pygame.sprite.Sprite,
            level_number: str, 
            restart_level: Callable[[str], None],
            run_overworld: Callable[[str], None],
            quit_game: Callable[[], None]
        ):
        self.display_surface = pygame.display.get_surface()
        self.level_number = level_number
        self.restart_level = restart_level
        self.run_overworld = run_overworld
        self.quit_game = quit_game

        self.current_y_diff = 704

        # Game over base image
        self.game_over_image = pygame.image.load(settings.GAME_OVER_BASE_IMAGE_PATH).convert_alpha()
        self.game_over_image_rect = self.game_over_image.get_rect()
        self.game_over_image_rect.center = (settings.GAME_OVER_BASE_IMAGE_POS[0], settings.GAME_OVER_BASE_IMAGE_POS[1] - self.current_y_diff)

        # gold coins
        self.gold_coin_image = pygame.image.load("../graphics/ui/gold_coin.png").convert_alpha()
        self.gold_coin_rect = self.gold_coin_image.get_rect()
        self.gold_coin_rect.topleft = (settings.GAME_OVER_GOLD_COIN_IMAGE_POS[0], settings.GAME_OVER_GOLD_COIN_IMAGE_POS[1] - self.current_y_diff)

        # silver coins
        self.silver_coin_image = pygame.image.load("../graphics/ui/silver_coin.png").convert_alpha()
        self.silver_coin_rect = self.silver_coin_image.get_rect()
        self.silver_coin_rect.topleft = (settings.GAME_OVER_SILVER_COIN_IMAGE_POS[0], settings.GAME_OVER_SILVER_COIN_IMAGE_POS[1] - self.current_y_diff)


        self.player_gold_coins = player.gold_coins
        self.player_silver_coins = player.silver_coins

        self.font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 12)
        self.big_font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 24)

        self.mouse_pos = (0, 0)

        self.button_data = {
            "RESTART": {
                "text": "RESTART",
                "pos": settings.GAME_OVER_RESTART_TEXT_POS,
                "x_range": (442, 546),
                "y_range": (471, 505),
                "func": self.restart_level
            },
            "OVERWORLD": {
                "text": "OVERWORLD",
                "pos": settings.GAME_OVER_OVERWORLD_TEXT_POS,
                "x_range": (442, 545),
                "y_range": (537, 570),
                "func": self.run_overworld
            },
            "QUIT": {
                "text": "QUIT",
                "pos": settings.GAME_OVER_QUIT_GAME_TEXT_POS,
                "x_range": (634, 739),
                "y_range": (504, 538),
                "func": self.quit_game
            }
        }

    
    def display_text(self, font: pygame.font.Font, text: str, position: Tuple[int, int], color: str):
        """
        Display text to the screen in a given position
        """
        text_surface = font.render(text, False, color)
        self.display_surface.blit(text_surface, position)
    
    def display_game_over_banner_text(self):
        self.display_text(
            self.font, 
            "GAME OVER", 
            (settings.GAME_OVER_BANNER_TEXT_POS[0], settings.GAME_OVER_BANNER_TEXT_POS[1] - self.current_y_diff),
            'black'
        )
    
    def display_score_text(self):
        self.display_text(
            self.big_font, 
            "SUMMARY:", 
            (settings.GAME_OVER_RECAP_TEXT_POS[0], settings.GAME_OVER_RECAP_TEXT_POS[1] - self.current_y_diff),
            'black'
        )
    
    def display_coins_and_progress(self, progress):
        self.gold_coin_rect.topleft = (settings.GAME_OVER_GOLD_COIN_IMAGE_POS[0], settings.GAME_OVER_GOLD_COIN_IMAGE_POS[1] - self.current_y_diff)
        self.silver_coin_rect.topleft = (settings.GAME_OVER_SILVER_COIN_IMAGE_POS[0], settings.GAME_OVER_SILVER_COIN_IMAGE_POS[1] - self.current_y_diff)
        self.display_surface.blit(self.gold_coin_image, self.gold_coin_rect)
        self.display_surface.blit(self.silver_coin_image, self.silver_coin_rect)
        self.display_text(
            self.big_font, 
            f": {self.player_gold_coins}", 
            (settings.GAME_OVER_GOLD_COIN_TEXT_POS[0], settings.GAME_OVER_GOLD_COIN_TEXT_POS[1] - self.current_y_diff),
            'black'
        )
        self.display_text(
            self.big_font, 
            f": {self.player_silver_coins}", 
            (settings.GAME_OVER_SILVER_COIN_TEXT_POS[0], settings.GAME_OVER_SILVER_COIN_TEXT_POS[1] - self.current_y_diff),
            'black'
        )
        self.display_text(
            self.big_font, 
            f"Progress: {round(progress, 1)}%", 
            (settings.GAME_OVER_PROGRESS_TEXT_POS[0], settings.GAME_OVER_PROGRESS_TEXT_POS[1] - self.current_y_diff),
            'black'
        )
    
    def get_mouse_in_range(self, mouse_pos: Tuple[int, int], button_data: dict) -> bool:
        """
        Check if mouse is in range of the button
        """
        x_min, x_max = button_data["x_range"]
        y_min, y_max = button_data["y_range"]
        return (
            x_min < mouse_pos[0] 
            and mouse_pos[0] < x_max 
            and y_min < mouse_pos[1] 
            and mouse_pos[1] < y_max
        )
    
    def display_button_text(self, mouse_pos: Tuple[int, int]):
        for button_name in self.button_data:
            x_min, x_max = self.button_data[button_name]["x_range"]
            y_min, y_max = self.button_data[button_name]["y_range"]
            if self.get_mouse_in_range(mouse_pos, self.button_data[button_name]):
                color = 'yellow'
            else:
                color = 'black'

            self.display_text(
                self.font,
                self.button_data[button_name]["text"],
                (self.button_data[button_name]["pos"][0], self.button_data[button_name]["pos"][1] - self.current_y_diff),
                color
            )
    
    def display_game_over_base_image(self):
        """
        Display the base board and buttons that text
        will be wrtiten on
        """
        self.game_over_image_rect.center = (settings.GAME_OVER_BASE_IMAGE_POS[0], settings.GAME_OVER_BASE_IMAGE_POS[1] - self.current_y_diff)
        self.display_surface.blit(self.game_over_image, self.game_over_image_rect)
    
    def handle_mouse_down(self):
        """
        Get player mouse click input
        """
        for button_name in self.button_data:
            if self.get_mouse_in_range(self.mouse_pos, self.button_data[button_name]):
                callback_func = self.button_data[button_name]["func"]
                if button_name == "RESTART" or button_name == "OVERWORLD":
                    callback_func(self.level_number)
                else:
                    callback_func()
       
    def handle_input_cooldown(self):
        """
        Check if user can accept input again
        """
        if not self.can_accept_input:
            current_time = pygame.time.get_ticks()
            if (current_time - self.input_time) > self.input_timeout:
                self.can_accept_input = True
    
    def update(self, mouse_down: bool):
        self.mouse_pos = pygame.mouse.get_pos()
        if mouse_down:
            self.handle_mouse_down()

        if self.current_y_diff > 0:
            self.current_y_diff -= 5
        # if self.game_over_image_rect.centery < settings.GAME_OVER_BASE_IMAGE_POS[1]:
        #     self.game_over_image_rect.centery += 1
    
    def display(self, progress: float):
        self.display_game_over_base_image()
        self.display_game_over_banner_text()
        self.display_score_text()
        self.display_coins_and_progress(progress)
        self.display_button_text(self.mouse_pos)

