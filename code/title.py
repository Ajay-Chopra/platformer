import pygame
import settings

class Title:
    """
    Handles everything related to the title screen
    """
    def __init__(self, run_overworld_callback, run_continue_game_callback, quit_game_callback):
        self.display_surface = pygame.display.get_surface()
        self.run_overworld_callback = run_overworld_callback
        self.run_continue_game_callback = run_continue_game_callback
        self.quit_game_callback = quit_game_callback

        # user input
        self.can_accept_input = True
        self.input_time = None
        self.input_cooldown = 300

        # selection index
        self.menu_options = ["New Game", "Continue", "Quit"]
        self.selection_index = 0

        # get font
        self.title_font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 55)
        self.menu_font = pygame.font.Font("../graphics/ui/ARCADEPI.TTF", 25)
    
    def display_game_title(self):
        """
        Display the game title
        """
        text_surface = self.title_font.render("Pirate Adventure", False, settings.TITLE_COLOR)
        text_surface_rect = text_surface.get_rect()
        text_surface_rect.center = settings.TITLE_CENTER_POS
        self.display_surface.blit(text_surface, text_surface_rect)
    
    def display_menu_box(self):
        """
        Display bounding box for the menu
        """
        menu_rect = pygame.Rect(settings.MENU_BOX_CENTER_POS, (settings.MENU_BOX_WIDTH, settings.MENU_BOX_HEIGHT))
        menu_rect.center = settings.MENU_BOX_CENTER_POS
        pygame.draw.rect(
            self.display_surface,
            settings.TITLE_COLOR,
            menu_rect,
            1
        )
    
    def display_menu_options(self):
        """
        Display menu options in list (New Game, Continue, Quit)
        """
        for i in range(len(self.menu_options)):
            option = self.menu_options[i]
            y_pos = settings.MENU_OPTION_START_HEIGHT + (i * settings.MENU_OPTION_HEIGHT_DELTA)
            color = settings.TITLE_COLOR if i != self.selection_index else 'yellow'
            text_surface = self.menu_font.render(option, False, color)
            text_surface_rect = text_surface.get_rect()
            text_surface_rect.center = (settings.SCREEN_WIDTH / 2, y_pos)
            self.display_surface.blit(text_surface, text_surface_rect)

    def handle_user_input(self):
        """
        Look for user keyboard input and handle accordingly
        """
        if self.can_accept_input:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                if self.selection_index == 0:
                    self.run_overworld_callback("0")
                elif self.selection_index == 1:
                    self.run_continue_game_callback()
                else:
                    self.quit_game_callback()
            elif keys[pygame.K_DOWN]:
                self.can_accept_input = False
                self.input_time = pygame.time.get_ticks()
                if self.selection_index < (len(self.menu_options) - 1):
                    self.selection_index += 1
            elif keys[pygame.K_UP]:
                self.can_accept_input = False
                self.input_time = pygame.time.get_ticks()
                if self.selection_index > 0:
                    self.selection_index -= 1
    
    def handle_input_cooldown(self):
        if not self.can_accept_input:
            current_time = pygame.time.get_ticks()
            if (current_time - self.input_time) > self.input_cooldown:
                self.can_accept_input = True
            

    
    def run(self):
        """
        Display the title page and wait for user input
        """
        self.display_game_title()
        self.handle_user_input()
        self.display_menu_options()
        self.handle_input_cooldown()