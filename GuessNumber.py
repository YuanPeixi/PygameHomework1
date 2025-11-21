import random
import pygame
from framwork import GameFramework

class GuessNumber(GameFramework):
    """
    框架化的猜数字（尽可能保留原控制台版的文案与特性）。
    - 区间 [1,200], 最大尝试次数 5（与原版一致）
    - 文案尽量复刻原版的提示（“太小/太大/接近/人身攻击”风格）
    - 支持数字键、小键盘输入、Backspace 删除、Enter 提交、ESC 退出
    - 非阻塞式结束：猜中或耗尽机会后显示结算画面，等待按键或超时返回
    - self.score 在结束时设置，GameManager 可收集并传入 ScoreManager
    """

    def __init__(self, low=1, high=200, max_attempts=5, width=800, height=400):
        super().__init__("猜数字", width, height)
        self.low = low
        self.high = high
        self.max_attempts = max_attempts

        # runtime
        self.target = None
        self.attempts = 0
        self.input_buf = ""
        self.message = ""      # 最近一条提示（与控制台 prompt 对应）
        self.history = []      # (guess:int, msg:str)
        self.finished = False  # 游戏是否结束（显示结算界面）
        self.start_ticks = 0
        self.finish_start_ticks = None
        self.finish_auto_seconds = 6
        self.score = 0

    def run(self):
        """每次进入游戏重置状态并选择新目标。"""
        super().run()
        self.target = random.randint(self.low, self.high)
        self.attempts = 0
        self.input_buf = ""
        # 原始开场文案（尽量复刻）
        self.message = (
            f"欢！迎！来！到！h的猜数字游戏！！！h已经从{self.low}到{self.high}中随机选择了一个整数，"
            f"你最多有{self.max_attempts}次机会来猜这个整数。加油，特种兵！"
        )
        self.history.clear()
        self.finished = False
        self.finish_start_ticks = None
        self.start_ticks = pygame.time.get_ticks()
        self.score = 0

    # --------- 输入处理：同时支持 ex 版本与旧版 ------------
    def on_key_down_ex(self, event):
        # event.unicode 比较可靠（包含字符）
        if event.key == pygame.K_ESCAPE:
            # 退出：若未结束，按 ESC 相当于直接放弃（得分为 0）
            if not self.finished:
                self.score = 0
                # 直接结束（non-blocking）——框架将收集 self.score
                self._finalize_and_exit()
            else:
                # 如果已经处于结算界面，按 ESC 也能确认返回
                self._finalize_and_exit()
            return

        if self.finished:
            # 在结算界面按任意键立即返回
            self._finalize_and_exit()
            return

        # Backspace
        if event.key == pygame.K_BACKSPACE:
            self.input_buf = self.input_buf[:-1]
            return

        # 支持数字字符输入（从 event.unicode）
        ch = getattr(event, "unicode", "")
        if ch and ch.isdigit():
            # 避免过长输入
            if len(self.input_buf) < 6:
                # 防止前导0出现不必要困扰，允许用户输入但不校验这里
                self.input_buf += ch
            return

        # Enter 提交
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self._submit_guess()
            return

        # 其余按键保持兼容：调用老版 on_key_down(key)
        # 以便使用旧框架时也能响应一些键
        try:
            return super().on_key_down(event.key)
        except Exception:
            return

    def on_key_down(self, key):
        # 向后兼容：若框架没有 ex 版本，这里处理数字键和回车
        if key == pygame.K_ESCAPE:
            if not self.finished:
                self.score = 0
                self._finalize_and_exit()
            else:
                self._finalize_and_exit()
            return
        if key == pygame.K_BACKSPACE:
            self.input_buf = self.input_buf[:-1]
            return
        if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self._submit_guess()
            return
        # 数字键 (主键区)
        if pygame.K_0 <= key <= pygame.K_9:
            ch = chr(key - pygame.K_0 + ord('0'))
            if len(self.input_buf) < 6:
                self.input_buf += ch
            return
        # 小键盘数字
        if pygame.K_KP0 <= key <= pygame.K_KP9:
            ch = str(key - pygame.K_KP0)
            if len(self.input_buf) < 6:
                self.input_buf += ch
            return
        return super().on_key_down(key)

    # ----------------- 游戏逻辑 -----------------
    def _submit_guess(self):
        """处理提交的猜测：保留原版语义（范围校验、不计数的非法输入、特有提示）"""
        if self.finished:
            return

        if not self.input_buf:
            self.message = "请输入一个整数再提交。"
            return

        # 解析整数
        try:
            guess = int(self.input_buf)
        except Exception:
            self.message = "请输入一个整数！这次不算数"
            self.input_buf = ""
            return

        # 范围校验（1..200）
        if guess < self.low or guess > self.high:
            self.message = f"请输入一个{self.low}到{self.high}之间的整数！这次不算数"
            self.input_buf = ""
            return

        # 合法猜测，计次数
        remaining_before = self.max_attempts - self.attempts
        self.attempts += 1
        remaining_after = self.max_attempts - self.attempts

        # 判断是否为最后一次且猜错（原控制台在 remaining==1 且猜错时会给出特别的结局）
        if remaining_before == 1 and guess != self.target:
            # 最后一次且失败：直接结束并给出控制台原话风格
            self.message = f"很遗憾，特种兵，你没有猜对。你真是个废物啊，正确答案是{self.target}。这都猜不出来，你是Pig吗？"
            # 保存记录
            self.history.append((guess, self.message))
            # 失败，score 归 0
            self.score = 0
            # 进入非阻塞结算界面
            self._on_lose()
            self.input_buf = ""
            return

        # 正常提示区间（尽可能复刻原版）
        if guess < self.target - 30:
            hint = "你猜的数字太小了！"
        elif guess > self.target - 30 and guess < self.target - 5:
            hint = "你猜的数字有点小！"
        elif guess > self.target - 5 and guess < self.target:
            hint = "你猜的数字有点小，但是很接近了！"
        elif guess > self.target + 30:
            hint = "你猜的数字太大了！"
        elif guess < self.target + 30 and guess > self.target + 5:
            hint = "你猜的数字有点大！"
        elif guess > self.target and guess < self.target + 5:
            hint = "你猜的数字有点大，但是很接近了！"
        elif guess == self.target:
            # 猜中：保留原版台词分支
            if self.attempts == 1:
                hint = "不是哥们你tmd这么能蒙？"
            elif self.attempts > 1 and self.attempts <= 3:
                hint = f"你太厉害了特种兵！你只用了了{self.attempts}次。"
            else:
                hint = f"恭喜你，特种兵，你猜对了！你用了{self.attempts}次机会。"
            # 计算得分（原控制台版没有数值得分，这里提供合理的分值以便排行榜记录）
            elapsed = max(1, (pygame.time.get_ticks() - self.start_ticks) // 1000)
            base = 1000
            score = max(0, base - (self.attempts - 1) * 120 - elapsed * 5)
            self.score = int(score)
            # 记录历史并进入非阻塞结算
            self.history.append((guess, hint))
            self._on_win()
            self.input_buf = ""
            return
        else:
            # 默认提示（冗余保护）
            hint = "继续努力！"

        # 若未结束则保存提示与继续
        self.message = hint
        self.history.append((guess, hint))
        self.input_buf = ""

    # ----------------- finished handling (non-blocking) -----------------
    def _on_win(self):
        if self.finished:
            return
        self.finished = True
        self.finish_reason = "win"
        self.finish_start_ticks = pygame.time.get_ticks()

    def _on_lose(self):
        if self.finished:
            return
        self.finished = True
        self.finish_reason = "lose"
        self.finish_start_ticks = pygame.time.get_ticks()

    def _finalize_and_exit(self):
        """最终结束：确保 self.score 已被设置好，然后调用 super().end() 停止 loop"""
        # 保证计算最终得分（如果是失败且 score 尚未设置，则置 0）
        if not hasattr(self, "score") or self.score is None:
            self.score = 0
        # stop loop (non-blocking)
        super().end()

    # ----------------- update/draw 分离 -----------------
    def update(self):
        # 逻辑更新：若 finished 则计时器走动并在超时后自动退出
        if self.finished:
            if self.finish_start_ticks is None:
                self.finish_start_ticks = pygame.time.get_ticks()
            else:
                elapsed = (pygame.time.get_ticks() - self.finish_start_ticks) // 1000
                if elapsed >= self.finish_auto_seconds:
                    self._finalize_and_exit()
            return
        # 否则正常游戏不需要复杂逻辑帧控制（GameFramework.loop 负责 tick）
        # 所有输入由 on_key_down_ex / on_key_down 处理
        return

    def draw(self):
        # 渲染界面，尽量保留原控制台输出的风格和提示
        self.screen.fill((30, 30, 40))
        title_font = pygame.font.SysFont("SimHei", 36)
        font = pygame.font.SysFont("SimHei", 24)
        small = pygame.font.SysFont("SimHei", 18)

        # 标题与开场文案
        self.text_out("猜数字（框架版）", (30, 20), size=36, color=(255, 220, 120))
        # 显示最初的欢迎/提示信息（保留原文案风格）
        welcome_lines = [
            f"欢！迎！来！到！h的猜数字游戏！！！h已经从{self.low}到{self.high}中随机选择了一个整数，",
            f"你最多有{self.max_attempts}次机会来猜这个整数。加油，特种兵！"
        ]
        for i, ln in enumerate(welcome_lines):
            self.text_out(ln, (30, 70 + i * 26), size=18, color=(200,200,180))

        # 当前提示与输入框
        prompt = f"请输入你猜测的数字： （你还剩下{max(0, self.max_attempts - self.attempts)}次机会！）"
        self.text_out(prompt, (30, 130), size=20, color=(220,220,220))
        input_box = pygame.Rect(30, 160, 300, 44)
        pygame.draw.rect(self.screen, (255,255,255), input_box, 2)
        input_display = self.input_buf if self.input_buf else "_"
        self.text_out(input_display, (input_box.x + 8, input_box.y + 6), size=28, color=(255,255,180))

        # 最近一条消息
        self.text_out(self.message, (30, 220), size=20, color=(200,230,200))

        # 历史记录（最多显示最近 6 条）
        hist_y = 260
        for i, (g, m) in enumerate(self.history[-6:]):
            self.text_out(f"{i+1}. {g} -> {m}", (30, hist_y + i*24), size=18, color=(180,200,240))

        # 若 finished 则显示结算 overlay（保持原控制台结束信息内容）
        if self.finished:
            # 在 overlay 中显示最终消息：和原来控制台的台词保持一致
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))

            center_x = self.width // 2
            center_y = self.height // 2

            if self.finish_reason == "win":
                # 找到历史中最后一个猜对的台词（如果有）
                final_msg = ""
                if self.history:
                    final_msg = self.history[-1][1]
                else:
                    final_msg = "恭喜你，猜对了！"
                self.text_out(final_msg, (center_x-220, center_y-60), size=36, color=(180,255,180))
                self.text_out(f"得分: {self.score}", (center_x-80, center_y), size=28, color=(220,220,200))
            else:
                # 失败
                # 原控制台在最后失败时输出强烈台词，我们保留该台词（如果在提交时已设置 message 则显示）
                final_msg = self.message or f"很遗憾，特种兵，你没有猜对。正确答案是{self.target}。"
                self.text_out(final_msg, (center_x-300, center_y-60), size=28, color=(255,120,120))
                self.text_out(f"得分: {self.score}", (center_x-80, center_y), size=28, color=(220,220,200))

            # 倒计时/提示
            elapsed_seconds = 0
            if self.finish_start_ticks:
                elapsed_seconds = (pygame.time.get_ticks() - self.finish_start_ticks) // 1000
            remain = max(0, self.finish_auto_seconds - elapsed_seconds)
            self.text_out(f"按任意键或 ESC 返回菜单（{remain}s 后自动返回）", (center_x-260, center_y+60), size=18, color=(180,200,220))

    # --------------- 可选：暴露当前分数供外部读取 ---------------
    def get_score(self):
        return self.score