import pygame
import random

# 初始化pygame
pygame.init()

# 设置窗口大小
windows_width = 800
windows_height = 600

# 创建游戏窗口
screen = pygame.display.set_mode((windows_width, windows_height))
pygame.display.set_caption("Python 贪吃蛇小游戏")

# 设置颜色
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
dark_blue = (0, 0, 139)
blue = (0, 0, 255)

# 设置游戏参数
cell_size = 20
map_width = windows_width // cell_size
map_height = windows_height // cell_size
snake_speed = 10

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def terminate():
    pygame.quit()
    exit()

def get_random_location():
    return {'x': random.randint(0, map_width - 1), 
            'y': random.randint(0, map_height - 1)}

def show_start_info(screen):
    font = pygame.font.Font(None, 40)
    tip = font.render('按任意键开始游戏', True, (65, 105, 225))
    screen.blit(tip, (windows_width // 2 - 150, windows_height // 2))
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                else:
                    return

def show_gameover_info(screen):
    font = pygame.font.Font(None, 40)
    tip = font.render('游戏结束! 按任意键重新开始', True, (65, 105, 225))
    screen.blit(tip, (windows_width // 2 - 200, windows_height // 2))
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                else:
                    return

def draw_snake(screen, snake_coords):
    for coord in snake_coords:
        x = coord['x'] * cell_size
        y = coord['y'] * cell_size
        # 绘制蛇身
        snake_segment = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(screen, dark_blue, snake_segment)
        # 绘制蛇身内部
        inner_segment = pygame.Rect(x + 4, y + 4, cell_size - 8, cell_size - 8)
        pygame.draw.rect(screen, blue, inner_segment)

def draw_food(screen, food):
    x = food['x'] * cell_size
    y = food['y'] * cell_size
    food_rect = pygame.Rect(x, y, cell_size, cell_size)
    pygame.draw.rect(screen, red, food_rect)

def draw_score(screen, score):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'得分: {score}', True, green)
    screen.blit(score_text, (windows_width - 150, 10))

def move_snake(direction, snake_coords):
    # 根据方向计算新的头部位置
    if direction == UP:
        new_head = {'x': snake_coords[0]['x'], 'y': snake_coords[0]['y'] - 1}
    elif direction == DOWN:
        new_head = {'x': snake_coords[0]['x'], 'y': snake_coords[0]['y'] + 1}
    elif direction == LEFT:
        new_head = {'x': snake_coords[0]['x'] - 1, 'y': snake_coords[0]['y']}
    elif direction == RIGHT:
        new_head = {'x': snake_coords[0]['x'] + 1, 'y': snake_coords[0]['y']}
    
    # 将新头部添加到蛇身
    snake_coords.insert(0, new_head)

def snake_is_alive(snake_coords):
    # 检查是否撞墙
    if (snake_coords[0]['x'] == -1 or snake_coords[0]['x'] == map_width or 
        snake_coords[0]['y'] == -1 or snake_coords[0]['y'] == map_height):
        return False
    
    # 检查是否撞到自己
    for snake_body in snake_coords[1:]:
        if snake_body['x'] == snake_coords[0]['x'] and snake_body['y'] == snake_coords[0]['y']:
            return False
    
    return True

def snake_is_eat_food(snake_coords, food):
    # 检查是否吃到食物
    if snake_coords[0]['x'] == food['x'] and snake_coords[0]['y'] == food['y']:
        # 生成新食物
        food['x'] = random.randint(0, map_width - 1)
        food['y'] = random.randint(0, map_height - 1)
        return True
    else:
        # 没吃到食物，删除尾部
        del snake_coords[-1]
        return False

def running_game(screen, snake_speed_clock):
    # 初始化蛇的位置
    startx = random.randint(3, map_width - 8)
    starty = random.randint(3, map_height - 8)
    snake_coords = [{'x': startx, 'y': starty},
                    {'x': startx - 1, 'y': starty},
                    {'x': startx - 2, 'y': starty}]
    
    # 初始方向向右
    direction = RIGHT
    
    # 生成食物
    food = get_random_location()
    
    # 游戏主循环
    while True:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_ESCAPE:
                    terminate()
        
        # 移动蛇
        move_snake(direction, snake_coords)
        
        # 检查蛇是否存活
        if not snake_is_alive(snake_coords):
            break
        
        # 检查是否吃到食物
        snake_is_eat_food(snake_coords, food)
        
        # 绘制游戏界面
        screen.fill(white)
        draw_snake(screen, snake_coords)
        draw_food(screen, food)
        draw_score(screen, len(snake_coords) - 3)
        pygame.display.update()
        
        # 控制游戏速度
        snake_speed_clock.tick(snake_speed)

def main():
    # 创建时钟对象控制游戏速度
    snake_speed_clock = pygame.time.Clock()
    
    # 显示开始信息
    show_start_info(screen)
    
    # 游戏主循环
    while True:
        running_game(screen, snake_speed_clock)
        show_gameover_info(screen)

# 运行游戏
if __name__ == '__main__':
    main()

from framwork import *
class SnakeGame(GameFramework):
    def __init__(self):
        super().__init__("SnakeGame",800,800)
        
        global windows_width, windows_height,screen
        self.screen=screen
        self.width=windows_width
        self.height=windows_height

        self.clock = pygame.time.Clock()
        self.running=False
        
