import pygame
import random
from framwork import GameFramework

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 10列 * 30px
PLAY_HEIGHT = 600  # 20行 * 30px
BLOCK_SIZE = 30
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), 
                (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0], pos[1])
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def clear_rows(grid, locked):
    increment = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            increment += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + increment)
                locked[new_key] = locked.pop(key)
    return increment

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, 
                                 (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
    surface.blit(label, (sx + 10, sy - 30))

def draw_score(score, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 200
    surface.blit(label, (sx + 10, sy))

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), 30))
    draw_score(score, surface)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], 
                             (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
    pygame.draw.rect(surface, (255, 255, 255), 
                     (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + i*BLOCK_SIZE), 
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i*BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y), 
                             (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))
    
class TetrisGame(GameFramework):
    def __init__(self):
        super().__init__('Tetris', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.locked_positions = {}
        self.grid = create_grid(self.locked_positions)
        self.change_piece = False
        self.current_piece = get_shape()
        self.next_piece = get_shape()
        self.fall_time = 0
        self.fall_speed = 0.75
        self.level_time = 0
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()

    def reset(self):
        self.locked_positions = {}
        self.grid = create_grid(self.locked_positions)
        self.change_piece = False
        self.current_piece = get_shape()
        self.next_piece = get_shape()
        self.fall_time = 0
        self.fall_speed = 0.75
        self.level_time = 0
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return
        self.grid = create_grid(self.locked_positions)
        self.fall_time += self.clock.get_rawtime()
        self.level_time += self.clock.get_rawtime()
        self.clock.tick()
        if self.level_time/1000 > 5:
            self.level_time = 0
            if self.fall_speed > 0.1:
                self.fall_speed -= 0.05
        if self.fall_time/1000 >= self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                self.change_piece = True
        shape_pos = convert_shape_format(self.current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                self.grid[y][x] = self.current_piece.color
        if self.change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = get_shape()
            self.change_piece = False
            self.score += clear_rows(self.grid, self.locked_positions) * 10
        if check_lost(self.locked_positions):
            self.game_over = True

    def draw(self):
        draw_window(self.screen, self.grid, self.score)
        draw_next_shape(self.next_piece, self.screen)
        if self.game_over:
            font = pygame.font.SysFont('comicsans', 80)
            label = font.render('YOU LOST!', 1, (255, 255, 255))
            self.screen.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), 
                                     TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))

    def on_key_down(self, key):
        if self.game_over:
            if key == pygame.K_r:
                self.reset()
            elif key == pygame.K_ESCAPE:
                self.end()
            return
        if key == pygame.K_LEFT:
            self.current_piece.x -= 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x += 1
        elif key == pygame.K_RIGHT:
            self.current_piece.x += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x -= 1
        elif key == pygame.K_DOWN:
            self.current_piece.y += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.y -= 1
        elif key == pygame.K_UP:
            self.current_piece.rotation += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.rotation -= 1
        elif key == pygame.K_SPACE:
            while valid_space(self.current_piece, self.grid):
                self.current_piece.y += 1
            self.current_piece.y -= 1
        elif key == pygame.K_ESCAPE:
            self.end()

if __name__ == '__main__':
    game = TetrisGame()
    game.run()
    game.loop()
