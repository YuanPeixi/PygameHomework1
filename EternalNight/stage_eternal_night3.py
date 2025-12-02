import pygame
import random
import math
from framwork import *
import os

'''
新结构设计
STG:
- Entity(递交Update (Update中用is_key_down更新),递交Draw(提供DC))
(Move Speed,JudgeCircleSize,FallbackShape,HP)
    - Player
    - Enermy (Just Move Ups and Downs)

PreStage (流星雨)
FinalStage (纯粹的弹幕地狱)
(需要支持:直线子弹即可中间、左右、和限位(圆形放置))
对话 (直接暂停游戏)

子弹设定

流程:
    - 初始化实例
    - 循环更新
    - 轮流绘制:
        Background,Bullet
        Character
        HUB
    
'''

class Entity:
    def __init__(self,HP,speed,image,shape,judge):
        self.HP = HP
        self.speed = speed
        self.image = image
        self.shape = shape
        self.judge = judge

class Bullet:
    def __init__(self,color,pos,dir,size):
        self.color=color
        self.pos=pos
        self.dir=dir
        self.size=size


class TouhouStage(GameFramework):
    def __init__(self,width=800,height=600):
        #0 running 1 paused 2 talking 3 final_win 4 final_loss
        super().__init__("东方永夜抄 -手写完整版",width,height)
        #Game Status
        self.status=0
        self.slow=False
        #Entity Data
        self.player_speed=500
        self.player_pos=[self.width*0.5,self.height*0.85]
        self.enermy_pos=[self.width*0.5,self.height*0.15]
        self.load_image()
        #Bullet
        self.bullets=[]
    
    def load_image(self):
        self.background=pygame.image.load(".\\EternalNight\\Muki.jpg")
        self.reimu=pygame.image.load(".\\EternalNight\\Reimu.png")
        self.junko=pygame.image.load(".\\EternalNight\\Junko.png")

    def run(self):
        #super ahead to init window
        if not pygame.font.get_init():
            pygame.font.init()
        #if not pygame.mixer.init():
        pygame.mixer.init()
        super().run()

    def end(self):
        pygame.mixer.stop()
        super().end()

    def on_focus_get(self):
        if self.status==1: #paused
            self.status=0
            pygame.mixer.unpause()
        return super().on_focus_get()
    
    def on_focus_loss(self):
        self.status=1 #paused
        pygame.mixer.pause()
        return super().on_focus_loss()

    def on_key_down(self, key):
        if key==pygame.K_ESCAPE:
            self.end()
        if key==pygame.K_LSHIFT:
            self.slow=True
        return super().on_key_down(key)

    def on_key_up(self, key):
        if key==pygame.K_LSHIFT:
            self.slow=False
        return super().on_key_up(key)

    def collided(self,pos1,size1,pos2,size2):
        assert(size1>0)
        assert(size2>0)
        dist=math.sqrt(math.pow(pos1[0]-pos2[0],2)+math.pow(pos1[1]-pos2[1],2))
        return dist<=(size1+size2)

    def update(self):
        if self.status == 1:
            return #pause

        #bullet calculation
        for bullet in self.bullets:
            #move those out
            if bullet.pos[0]<=0 or bullet.pos[1]<=0 or bullet.pos[0]>=self.width or bullet.pos[1]>=self.height:
                self.bullets.remove(bullet)
            #Striaght Down => dir=0 (inv clock is pos)
            bullet.pos[1]+=bullet.speed*math.cos(bullet.dir)
            bullet.pos[1]+=bullet.speed*math.sin(bullet.dir)
        #collison
        for bullet in self.bullets:
            if self.collided(bullet.pos,bullet.size,self.get_collis_circle()[0],self.get_collis_circle()[1]):
                
                pass
        #character update
        speed_modified=False
        if self.slow:
            self.player_speed/=2
            speed_modified=True
        if self.is_key_down(pygame.K_UP):
            self.player_pos[1]-=self.player_speed/60
        if self.is_key_down(pygame.K_DOWN):
            self.player_pos[1]+=self.player_speed/60
        if self.is_key_down(pygame.K_LEFT):
            self.player_pos[0]-=self.player_speed/60
        if self.is_key_down(pygame.K_RIGHT):
            self.player_pos[0]+=self.player_speed/60
        if speed_modified:
            self.player_speed*=2
        super().update()

    def get_collis_circle(self):
        return ((self.player_pos[0],self.player_pos[1]+5),5)

    def draw(self):

        #backround
        self.screen.blit(self.background,(0,0))
        #character
        adapt_size=tuple(x*0.12 for x in (self.reimu.get_size()))
        self.image_out(self.reimu,(self.player_pos[0],self.player_pos[1]),(adapt_size),True)
        adapt_size=tuple(x*0.1 for x in (self.junko.get_size()))
        self.image_out(self.junko,(self.enermy_pos[0],self.enermy_pos[1]),(adapt_size),True)
        if self.slow:
            pygame.draw.circle(self.screen,(10,10,240),self.get_collis_circle()[0],self.get_collis_circle()[1])
        #bullet
        for bullet in self.bullets:
            pygame.draw.circle(self.screen,bullet.color,bullet.pos,bullet.size)
        #HUB
        
        if self.status==1:
            self.text_out("paused",(20,self.height*0.95))
        return super().draw()
    

if __name__=="__main__":
    stage=TouhouStage()
    stage.run()
    stage.loop()