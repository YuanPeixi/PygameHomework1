import pygame
import sys
import random

pygame.init()

SCREEN_SIZE = 300
CELL_SIZE = 100
LINE_COLOR = (0, 0, 0)
X_COLOR = (255, 0, 0)
O_COLOR = (0, 0, 255)
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 60)

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("单人井字棋（人机对战）")

board = [[0 for _ in range(3)] for _ in range(3)]
game_over = False

def draw_board():
    screen.fill(WHITE)
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE), (SCREEN_SIZE, CELL_SIZE), 3)
    pygame.draw.line(screen, LINE_COLOR, (0, 2*CELL_SIZE), (SCREEN_SIZE, 2*CELL_SIZE), 3)
    pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE, 0), (CELL_SIZE, SCREEN_SIZE), 3)
    pygame.draw.line(screen, LINE_COLOR, (2*CELL_SIZE, 0), (2*CELL_SIZE, SCREEN_SIZE), 3)

def draw_pieces():
    for row in range(3):
        for col in range(3):
            x = col * CELL_SIZE + CELL_SIZE//2
            y = row * CELL_SIZE + CELL_SIZE//2
            if board[row][col] == 1:
                pygame.draw.line(screen, X_COLOR, (x-30, y-30), (x+30, y+30), 3)
                pygame.draw.line(screen, X_COLOR, (x+30, y-30), (x-30, y+30), 3)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, O_COLOR, (x, y), 30, 3)

def check_win(player):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] == player:
            return True
        if board[0][i] == board[1][i] == board[2][i] == player:
            return True
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

def check_tie():
    for row in board:
        if 0 in row:
            return False
    return True

def computer_move():
    if not game_over:
        empty_cells = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == 0:
                    empty_cells.append((row, col))
        if empty_cells:
            row, col = random.choice(empty_cells)
            board[row][col] = 2
            if check_win(2):
                print("电脑获胜！")
                return True
            elif check_tie():
                print("平局！")
                return True
    return False

running = True
while running:
    draw_board()
    draw_pieces()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = pygame.mouse.get_pos()
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if board[row][col] == 0:
                board[row][col] = 1
                if check_win(1):
                    print("你获胜啦！")
                    game_over = True
                elif check_tie():
                    print("平局！")
                    game_over = True
                else:
                    game_over = computer_move()
    pygame.display.flip()