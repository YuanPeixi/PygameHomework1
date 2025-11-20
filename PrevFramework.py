import pygame


'''
One Game collection only have one App Instance
One App Instance can have numerous GameFrame Instance
Each Single Game is child of GameFrame

Main Wnd Delivery

'''

class GameManger:
    def __init__(self,width=800,height=600):
        pygame.init()
        self.game_list=[]
        self.game_list.append()
        self.running_game=0
        self.main_window=pygame.display.set_mode((height,width))
    def draw_menu(self):
        pass
    def start_game(self):
        pass
    def register_game(self,game):
        self.game_list.append(game)
    def game_loop(self):
        while running:
            #The whole game is running
            #Show MainWnd and Enter Its 
            pass

            

class GameFrame:
    def __init__(self):
        self.running=True
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def pause(self):
        pass
    def hub(self):
        pass
    def on_key_down(self,key):
        pass
    def on_key_up(self,key):
        pass
    def on_mouse_move(self,):
        pass
    def on_mouse_down(self):
        pass
    def loop(self):
        while running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running=False
                if event.type==pygame.KEYDOWN:
                    self.on_key_down(self,event.key)
                if event.type==pygame.MOUSEBUTTONDOWN:
                    self.on_mouse_down(self,event.pos,event.button)

class MainMenu(GameFrame):
    def __init__(self):
        super().__init__()
    def on_key_down(self):
        
        return super().on_key_down()


def main():
    app=GameApp()
    

if __name__ == "__main__":
    main()