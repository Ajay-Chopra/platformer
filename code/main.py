import pygame
import sys
import settings as settings
from level import Level
from continue_game import ContinueGame
from overworld import Overworld


AWS_SECRET_KEY = "ASIAY34FZKBOKMUTVV7"


class Game:
    """
    High level game class for handling transitioning
    between multiple levels
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level(
            "test", 
            self.screen, 
            self.run_level_callback, 
            self.run_overworld_callback, 
            self.quit_game_callback,
            self.update_level_failed
        )
        self.overworld = Overworld(furthest_unlocked_level="2", run_level_callback=self.run_level_callback)
        self.continue_game = ContinueGame()
        self.mode = "LEVEL"
        self.level_failed = False
    
    def run_level_callback(self, level_number: str):
        """
        Switch to running level instead of overworld
        """
        self.level = Level(
            level_number, 
            self.screen, 
            self.run_level_callback, 
            self.run_overworld_callback, 
            self.quit_game_callback,
            self.update_level_failed
        )
        self.mode = "LEVEL"
        self.level_failed = False
    
    def run_overworld_callback(self, new_furthest_unlocked_level: str):
        """
        Switch to running overworld instead of level
        """
        self.overworld = Overworld(
            furthest_unlocked_level=new_furthest_unlocked_level, 
            run_level_callback=self.run_level_callback
        )
        self.mode = "OVERWORLD"
    
    def quit_game_callback(self):
        """
        Elegantly terminate the program
        """
        pygame.quit()
        sys.exit()
    
    def update_level_failed(self):
        """
        Called when player dies before completing level
        """
        self.level_failed = True
    
    def run(self) -> None:
        """
        Run the game loop
        """
        while True:
            mouse_down = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and self.mode == "LEVEL" and self.level_failed:
                    mouse_down = True
            
            self.screen.fill('black')
            if self.mode == "LEVEL":
                self.level.run(mouse_down)
            elif self.mode == "OVERWORLD":
                self.overworld.run()
            elif self.mode == "CONTINUE":
                self.continue_game.run()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()