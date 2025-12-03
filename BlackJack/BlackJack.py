import pygame
import random
from framwork import *


class Blackjack(GameFramework):
    def __init__(self):
        super().__init__("Blackjack", 800, 800)
        self.card_list = []  # 牌堆
        self.player_hand = []  # 玩家手牌
        self.current_card_index = 0  # 当前发牌位置
        self.game_state = "deal"  # deal: 发牌阶段, playing: 游戏中, over: 游戏结束
        self.message = "按空格键开始发牌"
        self.score = 0
        self.init_cards()

    def init_cards(self):
        """初始化牌堆"""
        self.card_list = []
        # 创建一副牌：1-13各4张
        for value in range(1, 14):
            for _ in range(4):
                self.card_list.append(value)
        random.shuffle(self.card_list)  # 洗牌
        self.player_hand = []
        self.current_card_index = 0
        self.game_state = "deal"

    def deal_initial_cards(self):
        """发初始两张牌"""
        if len(self.player_hand) < 2 and self.current_card_index < len(self.card_list):
            card = self.card_list[self.current_card_index]
            self.player_hand.append(card)
            self.current_card_index += 1

        if len(self.player_hand) == 2:
            self.game_state = "playing"
            self.message = "按H加牌，按S停牌"

    def hit(self):
        """玩家要牌"""
        if self.game_state != "playing":
            return

        if self.current_card_index < len(self.card_list):
            card = self.card_list[self.current_card_index]
            self.player_hand.append(card)
            self.current_card_index += 1

            total = sum(self.player_hand)

            if total > 21:
                self.game_state = "over"
                self.score = 0
                self.message = f"爆牌了！总点数{total}。按R重新开始"
            elif total == 21:
                self.game_state = "over"
                self.score = 100 + len(self.player_hand) * 10  # 奖励分数
                self.message = f"21点！太厉害了！得分：{self.score}。按R重新开始"
            else:
                self.message = f"当前点数：{total}。按H加牌，按S停牌"

    def stand(self):
        """玩家停牌"""
        if self.game_state != "playing":
            return

        total = sum(self.player_hand)
        self.game_state = "over"

        # 计算分数：越接近21分越高
        if total <= 21:
            self.score = total * 5 + (21 - total) * 2  # 基础分数
            if len(self.player_hand) <= 3:
                self.score += 20  # 少牌奖励
            self.message = f"停牌！总点数{total}，得分：{self.score}。按R重新开始"
        else:
            self.score = 0
            self.message = f"爆牌了！总点数{total}。按R重新开始"

    def update(self):
        """游戏逻辑更新"""
        pass  # 主要逻辑在事件处理中

    def on_key_down(self, key):
        """处理按键"""
        if key == pygame.K_SPACE and self.game_state == "deal":
            self.deal_initial_cards()
        elif key == pygame.K_h and self.game_state == "playing":  # H键要牌
            self.hit()
        elif key == pygame.K_s and self.game_state == "playing":  # S键停牌
            self.stand()
        elif key == pygame.K_r:  # R键重新开始
            self.init_cards()
            self.message = "按空格键开始发牌(你至少需要发两张牌)"
        elif key == pygame.K_ESCAPE:  # ESC键退出游戏
            self.end()

    def draw_card(self, card_value, position, is_face_up=True):
        """绘制一张牌"""
        x, y = position
        width, height = 80, 120

        # 绘制牌背景
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 3)

        if is_face_up:
            # 牌面显示
            colors = {
                1: ("A", (255, 0, 0)),
                11: ("J", (0, 0, 0)),
                12: ("Q", (0, 0, 0)),
                13: ("K", (0, 0, 0))
            }

            if card_value in colors:
                text, color = colors[card_value]
            else:
                text = str(card_value)
                color = (0, 0, 0)

            # 绘制牌值
            font = pygame.font.SysFont("SimHei", 24)
            text_surf = font.render(text, True, color)
            self.screen.blit(text_surf, (x + 10, y + 10))

            # 绘制花色图案
            if card_value in [1, 11, 12, 13]:
                # 特殊牌绘制简单图案
                pygame.draw.circle(self.screen, (200, 50, 50),
                                   (x + width // 2, y + height // 2), 15)
        else:
            # 背面
            pygame.draw.rect(self.screen, (50, 100, 200), (x + 5, y + 5, width - 10, height - 10))
            pygame.draw.rect(self.screen, (30, 70, 150), (x + 10, y + 10, width - 20, height - 20))

    def draw(self):
        """绘制游戏界面"""
        # 清屏
        self.screen.fill((50, 100, 50))

        # 绘制标题
        self.text_out("21点 Blackjack", (250, 20), 48, (255, 255, 200), "SimHei")

        # 绘制玩家手牌
        self.text_out("你的手牌:", (50, 100), 36, (255, 255, 255), "SimHei")

        for i, card in enumerate(self.player_hand):
            x = 50 + i * 100
            y = 150
            self.draw_card(card, (x, y))

        # 绘制牌堆（剩余的牌）
        self.text_out(f"剩余牌堆: {len(self.card_list) - self.current_card_index}张",
                      (50, 300), 28, (255, 255, 200), "SimHei")

        # 绘制牌堆背面
        for i in range(min(10, len(self.card_list) - self.current_card_index)):
            x = 50 + i * 3
            y = 350 + i * 2
            self.draw_card(0, (x, y), is_face_up=False)

        # 绘制当前点数
        if self.player_hand:
            total = sum(self.player_hand)
            color = (255, 255, 255) if total <= 21 else (255, 50, 50)
            self.text_out(f"当前点数: {total}", (500, 150), 36, color, "SimHei")

        # 绘制分数
        self.text_out(f"得分: {self.score}", (500, 200), 36, (255, 255, 100), "SimHei")

        # 绘制游戏说明
        self.text_out(self.message, (50, 450), 32, (200, 255, 200), "SimHei")

        # 绘制控制提示
        controls = [
            "游戏控制:",
            "空格键 - 开始发牌/重新发牌",
            "H键 - 要牌 (Hit)",
            "S键 - 停牌 (Stand)",
            "R键 - 重新开始",
            "ESC键 - 返回主菜单"
        ]

        for i, text in enumerate(controls):
            self.text_out(text, (50, 500 + i * 30), 24, (200, 200, 255), "SimHei")

    def end(self):
        """结束游戏"""
        super().end()


# 测试代码
if __name__ == "__main__":
    game = Blackjack()
    game.run()
    score = game.loop()
    print(f"最终得分: {score}")