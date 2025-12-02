from framwork import *
import ScoreBoard
from ScoreManager import *
import GuessNumber.GuessNumber as GuessNumber
import Snake.snake as snake
import EternalNight.stage_eternal_night2 as stage_eternal_night
from BTxin.BTxin_mini_game import su
from MainMenu.MainMenu3 import *

class TestGame(GameFramework):
    def __init__(self,width=800,height=600):
        super().__init__("TestGame",width,height)
    def update(self):
        self.text_out("This is Test Game",(250,400),36,(255,0,0))
        return super().update()
    def on_key_down(self, key):
        if key==pygame.K_ESCAPE:
            self.end()
        return super().on_key_down(key)
    def end(self):
        self.score=1000
        super().end()

import MainMenu
#中文输入法导致游戏输入异常
if __name__=="__main__":
    game_manger=GameManager()
    score_manager=ScoreManager()
    screen=pygame.display.set_mode((600,600))
    while not score_manager.isLogined():
        score_manager.login(screen)
    game_manger.register_game(MainMenu3())
    game=TestGame()
    BTxin_mini_game=su()
    pygame.display.quit()
    #game_manger.games[0]=MainMenu()
    game_manger.register_game(ScoreBoard.ScoreBoard(score_manager))

    game_manger.register_game(snake.Snake())
    game_manger.register_game(stage_eternal_night.TouhouStage())
    game_manger.register_game(GuessNumber.GuessNumber())
    game_manger.register_game(BTxin_mini_game)
    game_manger.run()
    
    score_manager.append_score("",game_manger.loop())