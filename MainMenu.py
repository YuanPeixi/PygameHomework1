from framwork import *

class MainMenu2(GameFramework):
    def __init__(self,width=800,height=600):
        super().__init__("MainMenu",width,height)
        self.score=0
        self._fonts[("STFANGSO",24)]=pygame.font.Font("STFANGSO.ttf",24)
        self._fonts[("STFANGSO",36)]=pygame.font.Font("STFANGSO.ttf",36)
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
        background = pygame.image.load("background.jpg")
        self.screen.blit(background,(0,0))

    def add_score(self,score):
        self.score+=score
    
    def get_score(self):
        return self.score

    def update(self):
        #In Update draw out game list and score
        if len(self.games) == 0:
            self.text_out("There's No Game Here",(250,400),36,(255,0,0),font=self.font_name)
        else:
            height=50
            cnt=0
            for game in self.games:
                if game.get_name()=="MainMenu":
                    continue
                self.text_out(str(cnt)+'.'+game.get_name(),(250,height),font=self.font_name)
                height+=50
                cnt+=1
            height+=50
            self.text_out("Press Number Key to Run Games",(250,height),font=self.font_name)
            self.text_out("Score:"+str(self.score),(0,0),font=self.font_name)
        return super().update()