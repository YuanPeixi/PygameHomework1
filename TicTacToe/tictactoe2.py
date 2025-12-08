import pygame
import random
from framwork import GameFramework

class TicTacToeGame(GameFramework):
    def __init__(self):
        super().__init__("井字棋", 300, 300)
        self.board = [[0 for _ in range(3)] for _ in range(3)]
        self.game_over = False
        #self.FONT = pygame.font.Font(None, 60)
        self.last_winner = None

    def reset(self):
        self.board = [[0 for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.last_winner = None

    def draw(self):
        self.screen.fill((255,255,255))
        cell = 100
        # 画线
        pygame.draw.line(self.screen, (0,0,0), (0, cell), (300, cell), 3)
        pygame.draw.line(self.screen, (0,0,0), (0, 2*cell), (300, 2*cell), 3)
        pygame.draw.line(self.screen, (0,0,0), (cell, 0), (cell, 300), 3)
        pygame.draw.line(self.screen, (0,0,0), (2*cell, 0), (2*cell, 300), 3)
        # 画棋子
        for row in range(3):
            for col in range(3):
                x = col * cell + cell//2
                y = row * cell + cell//2
                if self.board[row][col] == 1:
                    pygame.draw.line(self.screen, (255,0,0), (x-30, y-30), (x+30, y+30), 3)
                    pygame.draw.line(self.screen, (255,0,0), (x+30, y-30), (x-30, y+30), 3)
                elif self.board[row][col] == 2:
                    pygame.draw.circle(self.screen, (0,0,255), (x, y), 30, 3)
        # 结束提示
        if self.game_over:
            #1=> Player win, 2=> Computer win, 0=> Tie
            msg = "你获胜啦！" if self.last_winner == 1 else ("电脑获胜！" if self.last_winner == 2 else "平局！")
            #text = self.FONT.render(msg, True, (0,128,0))
            msg_color=(0,128,0) if self.last_winner==1 else (128,0,0)
            self.text_out(msg,(30,120),48,msg_color,"SimSun")
            #self.screen.blit(text, (30, 120))
            self.text_out("按R键重开", (60, 220), 32, (128,0,0))
            if self.last_winner == 1:
                self.score += 100
            elif self.last_winner == 2:
                self.score -= 50

    def update(self):
        pass

    def check_win(self, player):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == player:
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] == player:
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
        return False

    def check_tie(self):
        for row in self.board:
            if 0 in row:
                return False
        return True

    def computer_move(self):
        if not self.game_over:
            empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == 0]
            if empty_cells:
                row, col = random.choice(empty_cells)
                self.board[row][col] = 2
                if self.check_win(2):
                    self.last_winner = 2
                    self.game_over = True
                elif self.check_tie():
                    self.last_winner = 0
                    self.game_over = True

    def on_mouse_down(self, point, button):
        if self.game_over:
            return
        x, y = point
        col = x // 100
        row = y // 100
        if self.board[row][col] == 0:
            self.board[row][col] = 1
            if self.check_win(1):
                self.last_winner = 1
                self.game_over = True
            elif self.check_tie():
                self.last_winner = 0
                self.game_over = True
            else:
                self.computer_move()

    def on_key_down(self, key):
        if self.game_over and key == pygame.K_r:
            self.reset()
        if key == pygame.K_ESCAPE:
            self.end()

# 直接运行
if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()
    game.loop()