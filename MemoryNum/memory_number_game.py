import pygame
import random
import time
from framwork import GameFramework

class MemoryNumberGame(GameFramework):
    def __init__(self, width=600, height=400):
        super().__init__("记忆数字", width, height)
        pygame.font.init()
        self.font_big = pygame.font.SysFont("simhei", 80)
        self.font_mid = pygame.font.SysFont("simhei", 50)
        self.font_small = pygame.font.SysFont("simhei", 36)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 80, 80)
        self.GREEN = (80, 200, 120)
        self.BLUE = (100, 150, 255)
        self.state = "start"
        self.user_input = ""
        self.numbers = []
        self.show_start_time = 0
        self.input_start_time = 0
        self.score = 0

    def generate_numbers(self):
        return [random.randint(0, 9) for _ in range(5)]

    def draw_text_center(self, text, font, color, y_offset=0):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2 + y_offset))
        self.screen.blit(text_surf, text_rect)

    def run(self):
        super().run()
        # 初始化状态
        self.state = "start"
        self.user_input = ""
        self.numbers = []
        self.show_start_time = 0
        self.input_start_time = 0
        self.score = 0

    def update(self):
        self.screen.fill(self.WHITE)
        # ==================== 开始界面 ====================
        if self.state == "start":
            self.draw_text_center("5秒记忆数字挑战", self.font_mid, self.BLACK, -60)
            self.draw_text_center("按回车键开始游戏", self.font_small, self.BLUE, 0)
            self.draw_text_center("游戏中按 ESC 退出", self.font_small, (100,100,100), 60)

        # ==================== 显示数字阶段（2秒） ====================
        elif self.state == "show_numbers":
            self.draw_text_center("请记住以下数字！", self.font_mid, self.BLACK, -80)
            num_str = "  ".join(map(str, self.numbers))
            self.draw_text_center(num_str, self.font_big, self.RED, 20)
            self.draw_text_center("2秒后开始输入...", self.font_small, self.BLACK, 100)
            if time.time() - self.show_start_time > 2.0:
                self.state = "input"
                self.user_input = ""
                self.input_start_time = time.time()

        # ==================== 输入阶段（5秒） ====================
        elif self.state == "input":
            remaining = max(0, 5.0 - (time.time() - self.input_start_time))
            self.draw_text_center("请快速输入你记住的5个数字", self.font_mid, self.BLACK, -80)
            display_input = self.user_input + "_" * (5 - len(self.user_input))
            self.draw_text_center(display_input, self.font_big, self.BLUE, 0)
            self.draw_text_center(f"剩余时间: {remaining:.1f}s", self.font_mid, self.RED, 80)
            if remaining <= 0:
                self.state = "result"
                self.user_input = self.user_input.ljust(5, " ")[:5]

        # ==================== 结果判定 ====================
        elif self.state == "result":
            correct = "".join(map(str, self.numbers))
            if self.user_input.strip() == correct:
                self.draw_text_center("完全正确！太厉害了！", self.font_mid, self.GREEN, -60)
                self.score = 100
            else:
                self.draw_text_center("挑战失败", self.font_mid, self.RED, -80)
                self.draw_text_center(f"正确答案：{correct}", self.font_big, self.BLACK, 0)
                self.draw_text_center(f"你的答案：{self.user_input}", self.font_mid, (100,100,100), 60)
                self.score = 0
            self.draw_text_center("按回车键再来一局", self.font_small, self.BLUE, 140)
        return super().update()
    def on_key_down(self, key):
        # ESC退出
        if key == pygame.K_ESCAPE:
            self.end()
        # 开始界面按回车
        if self.state == "start" and key == pygame.K_RETURN:
            self.state = "show_numbers"
            self.numbers = self.generate_numbers()
            self.show_start_time = time.time()
        # 输入数字
        if self.state == "input":
            if pygame.K_0 <= key <= pygame.K_9 and len(self.user_input) < 5:
                self.user_input += chr(key)
            if key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            if key == pygame.K_RETURN and len(self.user_input) == 5:
                self.state = "result"
        # 结果界面按回车重开
        if self.state == "result" and key == pygame.K_RETURN:
            self.state = "show_numbers"
            self.numbers = self.generate_numbers()
            self.show_start_time = time.time()
        super().on_key_down(key)

    def end(self):
        super().end()

# 用法（示例，在 launcher.py 里注册即可）
if __name__ == "__main__":
    game = MemoryNumberGame()
    game.run()
    game.loop()
    print(f"游戏结束！你的得分是: {game.score}")