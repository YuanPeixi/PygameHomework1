from framwork import *
class MyGame(GameFramework):
    def __init__(self,w,h):
        self.x=0
        self.y=0
        super().__init__("MyGame",w,h)
    def update(self):
        if self.is_key_down('W'):
            y-=5
        pygame.draw.circle(self.screen,(),(x,y))
        return super().update()