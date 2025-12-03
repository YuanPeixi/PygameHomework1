import pygame
from framwork import GameFramework
import time
import random

MAZE_MAP = [
    "###########",
    "#S   #   E#",
    "# # # # # #",
    "# #     # #",
    "###########"
]

CELL_SIZE = 40
MARGIN = 40
MAZE_ROWS = len(MAZE_MAP)
MAZE_COLS = len(MAZE_MAP[0])

COLOR_WALL = (120, 120, 120)
COLOR_PATH = (255, 255, 255)
COLOR_START = (0, 200, 0)
COLOR_END = (200, 0, 0)
COLOR_PLAYER = (38, 130, 255)
COLOR_BG = (0, 0, 50)
COLOR_TEXT = (255, 255, 255)

def find_xy(symbol):
    for r, line in enumerate(MAZE_MAP):
        for c, x in enumerate(line):
            if x == symbol:
                return r, c
    return None

def gen_random_map():
    '''
    Generate a random maze map
    - Borders are walls
    - Inside cells are walls with 30% probability
    - Put into MAZE_MAP global variable
    '''
    random.seed(time.time())
    global MAZE_MAP
    MAZE_MAP = []
    for r in range(MAZE_ROWS):
        line = ""
        for c in range(MAZE_COLS):
            if r == 0 or r == MAZE_ROWS-1 or c == 0 or c == MAZE_COLS-1:
                line += "#"
            else:
                line += ' ' if random.random() < 0.7 else '#'
        MAZE_MAP.append(line)


def dfs(pos,target,visited):
    if visited[pos[0]][pos[1]]:
        return False
    visited[pos[0]][pos[1]]=True
    if pos==target:
        return True
    if pos[0]>0 and MAZE_MAP[pos[0]-1][pos[1]]!='#':
        tmp=pos.copy()
        tmp[0]-=1
        if dfs(tmp,target,visited):
            return True
    if pos[1]>0 and MAZE_MAP[pos[0]][pos[1]-1]!='#':
        tmp=pos.copy()
        tmp[1]-=1
        if dfs(tmp,target,visited):
            return True
    if pos[0]<MAZE_ROWS-1 and MAZE_MAP[pos[0]+1][pos[1]]!='#':
        tmp=pos.copy()
        tmp[0]+=1
        if dfs(tmp,target,visited):
            return True
    if pos[1]<MAZE_COLS-1 and MAZE_MAP[pos[0]][pos[1]+1]!='#':
        tmp=pos.copy()
        tmp[1]+=1
        if dfs(tmp,target,visited):
            return True
    return False


def check_map_solvable():
    '''
    - return a solvable (start,end) pair
    - if not solvable,return None
    '''
    for x0 in range(MAZE_ROWS):
        for y0 in range(MAZE_COLS):
            if MAZE_MAP[x0][y0]!=' ':
                continue
            for x1 in range(MAZE_ROWS-1,-1,-1):
                for y1 in range(MAZE_COLS-1,-1,-1):
                    if MAZE_MAP[x1][y1]!=' ' or (x0==x1 and y0==y1):
                        continue
                    start=(x0,y0)
                    end=(x1,y1)
                    visited = [[False]*MAZE_COLS for _ in range(MAZE_ROWS)]
                    if dfs(list(start),list(end),visited):
                        return start,end
    return None


class MazeGame(GameFramework):
    def __init__(self, width=MAZE_COLS * CELL_SIZE + MARGIN*2, height=MAZE_ROWS * CELL_SIZE + MARGIN*2):
        super().__init__("走迷宫", width, height)
        self.start_pos = find_xy('S')
        self.end_pos = find_xy('E')
        self.player_pos = list(self.start_pos)
        self.game_start_time = None
        self.game_end_time = None
        self.finished = False
        self.score = 0

    def run(self):
        super().run()
        self.player_pos = list(self.start_pos)
        self.game_start_time = time.time()
        self.game_end_time = None
        self.finished = False
        gen_random_map()
        while True:
            solvable_pair = check_map_solvable()
            if solvable_pair!=None:
                self.start_pos, self.end_pos = solvable_pair
                break
            gen_random_map()
        self.start_pos = list(self.start_pos)
        #self.start_pos = tuple(x+1 for x in self.start_pos)
        self.end_pos = tuple(self.end_pos)
        MAZE_MAP[self.start_pos[0]] = MAZE_MAP[self.start_pos[0]][:self.start_pos[1]] + 'S' + MAZE_MAP[self.start_pos[0]][self.start_pos[1]+1:]
        MAZE_MAP[self.end_pos[0]] = MAZE_MAP[self.end_pos[0]][:self.end_pos[1]] + 'E' + MAZE_MAP[self.end_pos[0]][self.end_pos[1]+1:]
        self.player_pos = list(self.start_pos)


    def is_valid(self, r, c):
        return (0 <= r < MAZE_ROWS and 0 <= c < MAZE_COLS and MAZE_MAP[r][c] != '#')

    def update(self):
        if self.finished:
            return

        r, c = self.player_pos
        # 键盘检测（wasd和方向键）
        moved = False
        if self.is_key_down(pygame.K_w) or self.is_key_down(pygame.K_UP):
            nr, nc = r-1, c
            moved = True
        elif self.is_key_down(pygame.K_s) or self.is_key_down(pygame.K_DOWN):
            nr, nc = r+1, c
            moved = True
        elif self.is_key_down(pygame.K_a) or self.is_key_down(pygame.K_LEFT):
            nr, nc = r, c-1
            moved = True
        elif self.is_key_down(pygame.K_d) or self.is_key_down(pygame.K_RIGHT):
            nr, nc = r, c+1
            moved = True
        else:
            nr, nc = r, c  # no move

        if moved and self.is_valid(nr, nc):
            self.player_pos = [nr, nc]

        if tuple(self.player_pos) == self.end_pos:
            self.finished = True
            self.game_end_time = time.time()
            self.score = max(0, int(100 - (self.game_end_time - self.game_start_time)*10))  # 比如按用时转换分数
            self.end()  # 框架要求

    def draw(self):
        self.screen.fill(COLOR_BG)
        # 画迷宫
        for r, line in enumerate(MAZE_MAP):
            for c, x in enumerate(line):
                rect = pygame.Rect(MARGIN + c * CELL_SIZE, MARGIN + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if x == '#':
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                elif x == 'S':
                    pygame.draw.rect(self.screen, COLOR_START, rect)
                elif x == 'E':
                    pygame.draw.rect(self.screen, COLOR_END, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
        # 画玩家
        pr, pc = self.player_pos
        rect = pygame.Rect(MARGIN + pc * CELL_SIZE, MARGIN + pr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, COLOR_PLAYER, rect)

        # 信息显示
        if self.game_start_time:
            now = time.time()
            t = now - self.game_start_time if not self.finished else self.game_end_time - self.game_start_time
            self.text_out(f'用时: {t:.2f}秒', (self.width*0.01, 10), color=COLOR_TEXT)
            self.text_out(f'得分: {self.score}', (self.width*0.32, 10),  color=COLOR_TEXT)
            self.text_out('请用方向键或WSAD控制', (self.width*0.5,10),  color=COLOR_TEXT)
            if self.finished:
                self.text_out('通关成功！', (180, self.height-50), 32, COLOR_END)

    def on_key_down(self, key):  # 避免长按多步，建议采用按下移动
        if self.finished:
            return
        r, c = self.player_pos
        if key==pygame.K_ESCAPE:
            self.end()
        if key == pygame.K_w or key == pygame.K_UP:
            nr, nc = r-1, c
        elif key == pygame.K_s or key == pygame.K_DOWN:
            nr, nc = r+1, c
        elif key == pygame.K_a or key == pygame.K_LEFT:
            nr, nc = r, c-1
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            nr, nc = r, c+1
        else:
            nr, nc = r, c
        if self.is_valid(nr, nc):
            self.player_pos = [nr, nc]
        if tuple(self.player_pos) == self.end_pos:
            self.finished = True
            self.game_end_time = time.time()
            self.score = max(0, int(100 - (self.game_end_time - self.game_start_time)*10))
            self.end()  # 游戏结束

    def end(self):
        super().end()  # 通知管理器游戏结束


# 连通性检查测试
def test_connectivity():
    print("当前地图:")
    for line in MAZE_MAP:
        print(line)
    result = check_map_solvable()
    if result:
        start, end = result
        print(f"找到可达路径: 起点 {start}, 终点 {end}")
    else:
        print("没有找到可达路径！")

# 用法（示例，在 launcher.py 里注册即可）
if __name__ == "__main__":
    game = MazeGame()
    game.run()  
    test_connectivity()
    print("本轮得分:", game.loop())