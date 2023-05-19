import pygame
import sys
import settings as settings
from level import Level
from continue_game import ContinueGame
from overworld import Overworld

class Game:
    """
    High level game class for handling transitioning
    between multiple levels
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level("2", self.screen, self.run_overworld_callback, self.run_continue_game_callback, self.quit_game_callback)
        # self.overworld = Overworld(furthest_unlocked_level="1", run_level_callback=self.run_level_callback)
        self.continue_game = ContinueGame()
        self.mode = "LEVEL"
    
    def run_level_callback(self, level_number: str):
        """
        Switch to running level instead of overworld
        """
        self.level = Level(level_number, self.screen, self.run_overworld_callback, self.run_continue_game_callback, self.quit_game_callback)
        self.mode = "LEVEL"
    
    def run_overworld_callback(self, new_furthest_unlocked_level: str):
        """
        Switch to running overworld instead of level
        """
        self.overworld = Overworld(
            furthest_unlocked_level=new_furthest_unlocked_level, 
            run_level_callback=self.run_level_callback
        )
        self.mode = "OVERWORLD"
    
    def run_continue_game_callback(self):
        """
        Switch to running continue game screen
        """
        self.mode = "CONTINUE"
    
    def quit_game_callback(self):
        """
        Elegantly terminate the program
        """
        pygame.quit()
        sys.exit()
    
    def run(self) -> None:
        """
        Run the game loop
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.screen.fill('black')
            if self.mode == "LEVEL":
                self.level.run()
            elif self.mode == "OVERWORLD":
                self.overworld.run()
            elif self.mode == "CONTINUE":
                self.continue_game.run()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()