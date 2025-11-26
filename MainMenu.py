from framwork import *

class MainMenu2(GameFramework):
    def __init__(self,width=800,height=600):
        super().__init__("MainMenu",width,height)
        self.score=0
        self.games=[]

    def set_game_list(self,games):
        self.games=games

    def run(self):
        super().run()
        self.screen.fill((0,0,50))

    def add_score(self,score):
        self.score+=score
    
    def get_score(self):
        return self.score

    def update(self):
        #In Update draw out game list and score
        if len(self.games) == 0:
            self.text_out("There's No Game Here",(250,400),36,(255,0,0))
        else:
            height=50
            cnt=0
            for game in self.games:
                if game.get_name()=="MainMenu":
                    continue
                self.text_out(str(cnt)+'.'+game.get_name(),(250,height))
                height+=50
                cnt+=1
            height+=50
            self.text_out("Press Number Key to Run Games",(250,height))
            self.text_out("Score:"+str(self.score),(0,0))
        return super().update()