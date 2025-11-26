import pygame
import random
from framwork import GameFramework

class Snake(GameFramework):
    def __init__(self, width=800, height=600):
        super().__init__("贪吃蛇", width, height)
        self.block_size = 20
        self.reset()

    def reset(self):
        self.direction = pygame.K_RIGHT
        self.snake = [[6, 10], [5, 10], [4, 10]]  # 初始身体，存储为[格x,格y]
        self.food = self.spawn_food()
        self.score = 0
        self.finnal= 0
        self.last_move_time = 0
        self.interval = 120  # 毫秒间隔

    def spawn_food(self):
        while True:
            fx = random.randint(0, (self.width // self.block_size) - 1)
            fy = random.randint(0, (self.height // self.block_size) - 1)
            if [fx, fy] not in self.snake:
                return [fx, fy]

    def on_key_down(self, key):
        # 不允许直接180°掉头
        opposites = {pygame.K_UP: pygame.K_DOWN, pygame.K_DOWN: pygame.K_UP,
                     pygame.K_LEFT: pygame.K_RIGHT, pygame.K_RIGHT: pygame.K_LEFT}
        if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            if opposites.get(key, None) != self.direction:
                self.direction = key
        elif key == pygame.K_ESCAPE:
            self.end()

    def finnal_screen(self):
        self.finnal=1
        pass

    def update(self):
        if self.finnal>=3*60:
            self.end()
            return
        
        if self.finnal:
            #No more update
            self.finnal+=1
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.interval:
            return
        self.last_move_time = now

        # 移动蛇头
        head = self.snake[0][:]
        if self.direction == pygame.K_UP:
            head[1] -= 1
        elif self.direction == pygame.K_DOWN:
            head[1] += 1
        elif self.direction == pygame.K_LEFT:
            head[0] -= 1
        elif self.direction == pygame.K_RIGHT:
            head[0] += 1

        # 撞墙
        if not (0 <= head[0] < self.width // self.block_size) or not (0 <= head[1] < self.height // self.block_size):
            self.finnal_screen()
            #self.end()
            return

        # 撞身体
        if head in self.snake:
            self.finnal_screen()
            #self.end()
            return

        self.snake = [head] + self.snake
        if head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        # 绘制
        self.screen.fill((30, 30, 30))
        # 画蛇
        for pos in self.snake:
            pygame.draw.rect(self.screen, (0, 255, 0), (pos[0]*self.block_size, pos[1]*self.block_size, self.block_size, self.block_size))
        # 画食物
        pygame.draw.rect(self.screen, (255, 0, 0), (self.food[0]*self.block_size, self.food[1]*self.block_size, self.block_size, self.block_size))
        # 画分数
        self.text_out(f"Score: {self.score}", (10, 10), 30, (255, 255, 0), font="黑体")

        if self.finnal:
            rect=pygame.Surface((800,800))
            rect.set_alpha(100)
            self.screen.blit(rect,(0,0))
            #pygame.draw.rect(self.screen,(0,0,0),(self.width,self.height))
            self.text_out(f"Score:{self.score}",(self.width/2-40,self.height/2-40),36)
            self.text_out(f"{(3-self.finnal//60)} Sec Back to Main Menu",(self.width*0.5-40,self.height*0.8),18)

        #pygame.display.flip()
        return super().draw()


    def run(self):
        self.reset()
        super().run()