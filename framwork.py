import pygame

class GameFramework:
    def __init__(self,name,width,height):
        self.key_status={}
        self.name=name
        self.running=False
        self.width=width
        self.height=height
        self.score=0
        self._fonts={}  # Font cache for performance
        pass
    def run(self):
        self.running=True
        pygame.display.init()
        pygame.display.set_caption(self.name)
        self.screen=pygame.display.set_mode((self.width,self.height))

    def get_name(self):
        return self.name 

    def _get_font(self, font_name, size):
        """Get or create a cached font object."""
        key = (font_name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(font_name, size)
        return self._fonts[key]

    def text_out(self,text,pos=(0,0),size=24,color=(255,255,255),font="SimHei"):
        """Render text to screen using cached fonts. Does not flip display."""
        font_obj = self._get_font(font, size)
        text_surf = font_obj.render(text, True, color)
        self.screen.blit(text_surf, pos)
        
    def image_out(self, image, pos, size=None, center=False, alpha=None):
        """
        统一图片绘制接口
        :param image: pygame.Surface 图片对象
        :param pos: (x, y) 左上角坐标或中心坐标(center=True 时)
        :param size: (宽, 高); 如果指定则自动缩放,否则保持图片原尺寸
        :param center: 如果为True,pos为图片中心;否则为左上角
        :param alpha: 若指定,设置整体不透明度(0-255)
        """
        surf = image
        if size is not None:
            surf = pygame.transform.smoothscale(image, size)
        if alpha is not None and (0 <= alpha <= 255):
            surf = surf.copy()
            surf.set_alpha(alpha)
        if center:
            rect = surf.get_rect(center=pos)
        else:
            rect = surf.get_rect(topleft=pos)
        self.screen.blit(surf, rect)

    def on_mouse_down(self,point,button):
        pass
    def on_mouse_move(self,point):
        pass
    def on_mouse_up(self,point,button):
        pass

    # Extended event handlers with full event object access
    def on_key_down_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_key_down(event.key)
    
    def on_key_up_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_key_up(event.key)
    
    def on_mouse_down_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_mouse_down(event.pos, event.button)
    
    def on_mouse_up_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_mouse_up(event.pos, event.button)
    
    def on_mouse_move_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_mouse_move(event.pos)
    
    def on_focus_get_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_focus_get()
    
    def on_focus_loss_ex(self, event):
        """- Extended focus loss handler with access to full event object.
        - Default implementation calls on_focus_loss for backward compatibility."""
        self.on_focus_loss()

    def on_key_down(self,key):
        self.key_status[key]=True
        
    def on_key_up(self,key):
        self.key_status[key]=False
        
    def is_key_down(self,key):
        return self.key_status.get(key,False)
    
    def update(self):
        """
        - Override this method to implement game logic updates. 
        - No frame control here.(Framework controls it 60FPS) 
        """
        pass
    
    def draw(self):
        """
        - Override this method to implement rendering. Called after update. 
        - Note: The latter it writes the upper layer it draws(Upper layer covers lower)
        """
        pass
        
    def loop(self):
        #Mainly Message Distribution
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running=False
                if event.type==pygame.KEYDOWN:
                    self.on_key_down_ex(event)
                if event.type==pygame.KEYUP:
                    self.on_key_up_ex(event)
                if event.type==pygame.MOUSEBUTTONDOWN:
                    self.on_mouse_down_ex(event)
                if event.type==pygame.MOUSEBUTTONUP:
                    self.on_mouse_up_ex(event)
                if event.type==pygame.MOUSEMOTION:
                    self.on_mouse_move_ex(event)
                if event.type==pygame.ACTIVEEVENT:
                    if event.gain:
                        self.on_focus_get_ex(event)
                    else:
                        self.on_focus_loss_ex(event)
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        pygame.display.quit()
        return self.score
    
    def on_focus_get(self):
        pass
    def on_focus_loss(self):
        pass

    def end(self):
        self.running=False

    

class MainMenu(GameFramework):
    def __init__(self,width=800,height=600):
        super().__init__("MainMenu",width,height)
        self.score=0
        self.games=[]
    def on_key_down(self, key):
        if key==pygame.K_0:
            self.score=0
        elif key==pygame.K_1:
            self.score=1
        elif key==pygame.K_2:
            self.score=2
        elif key==pygame.K_3:
            self.score=3
        elif key==pygame.K_4:
            self.score=4
        elif key==pygame.K_5:
            self.score=5
        elif key==pygame.K_6:
            self.score=6
        elif key==pygame.K_7:
            self.score=7
        elif key==pygame.K_8:
            self.score=8
        elif key==pygame.K_9:
            self.score=9
        elif key==pygame.K_ESCAPE:
            self.score=-1
        else:
            return super().on_key_down(key)#No more action
        self.score+=1 #Exclude Self
        self.end() #Jump to game or exit
        return super().on_key_down(key)

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
    
class GameManager:
    def __init__(self,width=800,height=600):
        pygame.init()
        self.width=800
        self.height=600
        #self.games=[MainMenu()]
        self.games=[]
        self.running=False
        self.score=0
        self.target=0 #The running game

    def __del__(self):
        pygame.quit()    

    def register_game(self,game):
        self.games.append(game)
    
    def end(self):
        self.running=False

    def run(self):
        self.running=True

    def loop(self):
        while self.running:
            #According to current Game deliver Loop
            self.games[0].run()
            self.games[0].set_game_list(self.games)
            self.target=self.games[0].loop()
            if self.target==0:
                self.running=False
            else:
                self.games[self.target].run()
                self.score+=(self.games[self.target].loop())
                self.games[0].score=self.score
        return self.score
                
