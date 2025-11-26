from framwork import *

class MainMenu2(GameFramework):
    def __init__(self,width=800,height=600):
        super().__init__("MainMenu",width,height)
        self.score=0
        self._fonts[("STFANGSO",24)]=pygame.font.Font("MainMenu\\STFANGSO.ttf",24)
        self._fonts[("STFANGSO",36)]=pygame.font.Font("MainMenu\\STFANGSO.ttf",36)
        self.font_name="STFANGSO"
        self.games=[]

    def set_game_list(self,games):
        self.games=games

    def on_key_down(self, key):
        if key==pygame.K_ESCAPE:
            self.end()
        return super().on_key_down(key)

    def run(self):
        super().run()
        background = pygame.image.load("MainMenu\\background.jpg")
        self.screen.blit(background,(0,0))

    def add_score(self,score):
        self.score+=score

    def get_score(self):
        return self.score
    
    def on_mouse_move(self, point):
        return super().on_mouse_move(point)
    
    def on_mouse_down(self, point, button):
        return super().on_mouse_down(point, button)

    def update(self):
        #In Update draw out game list and score
        #计算游戏Cover的位置并
        pass

    def draw(self):

        return super().draw()