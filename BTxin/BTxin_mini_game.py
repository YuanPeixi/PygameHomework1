import pygame as pg
import math
import random
from framwork import GameFramework
# from ScoreManager import ScoreManager

# 备用
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class su(GameFramework):
    def __init__(self, width=800, height=600):
        super().__init__("BTxin", width, height)

        self.path_prefix='.' #Fix for Python:Run Project

        # self.score_tempmanager = ScoreManager()
        # self.is_scoremanager = True
        self.score = 0
        # 音效
        pg.mixer.init()
        self.boss_hit_sound = pg.mixer.Sound(self.path_prefix+"/BTxin/homo2.wav")
        self.player_death_sound = pg.mixer.Sound(self.path_prefix+"/BTxin/homo.wav")
        # 球的初始位置
        self.center = [width // 2, height // 2]
        # 初始方向
        self.direction = list(UP)
        self._normalize_direction()

        self.speed = 0  # 速度
        self.moving = True  # 持续移动
        self.wait = True  # 等待开始
        self.target_pos = None
        self.target_dir = None
        self.target_angle = None

        self.initial_center = [width // 2, height // 2]
        self.initial_direction = list(UP)
        self.initial_boss_health = 100
        self.initial_attack_damage = 10

        self.rotation_step_deg = 4
        self.current_angle = math.atan2(-self.direction[1], self.direction[0])

        self.pic = [self.path_prefix+'/BTxin/homo1.png', self.path_prefix+'/BTxin/homo2.png', self.path_prefix+'/BTxin/homo3.png', self.path_prefix+'/BTxin/homo4.png']
        self.images = [pg.image.load(p).convert_alpha() for p in self.pic]
        self.image_index = 0  # 照片编号
        self.image_timer = 0
        self.image_duration_default = 60
        self.image = self.images[self.image_index]

        self.health = 10
        self.score_temp = 0
        self.font = pg.font.Font(None, 48)

        self.is_dead = False
        self.game_over_font = pg.font.Font(None, 128)
        self.game_over_text = None
        self.info_font = pg.font.Font(None, 24)
        # 倒计时字体与计时器
        self.countdown_font = pg.font.Font(None, 200)
        self.death_countdown_timer = None

        # reset 分数索引
        self.reset_digits = [1, 1, 4, 5, 1, 4]
        self.reset_digit_index = 0
        # 胜利与计时器
        self.has_won = False
        self.win_countdown_timer = None

        # boss
        self.boss = Boss(self.width, self.height)
        self.attackitem = attackitem(self.width, self.height)


    def set_image(self, idx, duration=None):
        if idx < 0 or idx >= len(self.images):
            return
        self.image_index = idx
        self.image = self.images[self.image_index]
        self.image_timer = duration if duration is not None else self.image_duration_default

    # 方向向量恒为1
    def _normalize_direction(self):
        length = math.hypot(self.direction[0], self.direction[1])
        if length != 0:
            self.direction[0] /= length
            self.direction[1] /= length

    # 鼠标点击
    def on_mouse_down(self, point, button):
        if button == pg.BUTTON_LEFT:
            dx = point[0] - self.center[0]
            dy = point[1] - self.center[1]
            self.speed = 9.6

            target_length = math.hypot(dx, dy)
            if target_length == 0:
                return
            target_dir = [dx / target_length, dy / target_length]

            self.target_dir = target_dir
            self.target_angle = math.atan2(-self.target_dir[1], self.target_dir[0])

    def update(self):
        # 计时器
        if self.image_timer > 0:
            self.image_timer -= 1
        else:
            # homo3
            if getattr(self.boss, 'dead', False):
                self.set_image(2, duration=0)
            else:
                # homo1
                self.set_image(0, duration=0)

        if self.target_angle is not None:
            target_angle = self.target_angle

            angle_diff = target_angle - self.current_angle
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            rotation_step = (self.rotation_step_deg * math.pi) / 180.0
            if abs(angle_diff) <= rotation_step:
                self.current_angle = target_angle
                self.target_angle = None
            else:
                self.current_angle += rotation_step if angle_diff > 0 else -rotation_step

            # 更新朝向
            self.direction[0] = math.cos(self.current_angle)
            self.direction[1] = -math.sin(self.current_angle)
            self._normalize_direction()

        if self.moving:
            self.center[0] += self.direction[0] * self.speed
            self.center[1] += self.direction[1] * self.speed

        # 防出界
        self.center[0] = max(10, min(self.center[0], self.width - 10))
        self.center[1] = max(10, min(self.center[1], self.height - 10))

        # 一坨计算距离的
        player_x, player_y = self.center[0], self.center[1]
        player_radius = 10
        boss_x = self.boss.center[0]
        boss_y = self.boss.center[1]
        boss_wid = self.boss.wid
        boss_half_wid = boss_wid / 2
        boss_left = boss_x - boss_half_wid
        boss_right = boss_x + boss_half_wid
        boss_top = boss_y - boss_half_wid
        boss_bottom = boss_y + boss_half_wid
        player_cx, player_cy = player_x, player_y
        closest_x = max(boss_left, min(player_cx, boss_right))
        closest_y = max(boss_top, min(player_cy, boss_bottom))
        distance_x = player_cx - closest_x
        distance_y = player_cy - closest_y
        distance_sq = distance_x ** 2 + distance_y ** 2
        collision_threshold = player_radius ** 2
        if distance_sq <= collision_threshold:
            self.health -= 1
            if self.health < 0:
                self.health = 0
            self.set_image(3, duration=45)

        attackitem_radius = 10
        player_attackitem_x = abs(self.center[0] - self.attackitem.center[0])
        player_attackitem_y = abs(self.center[1] - self.attackitem.center[1])
        if (player_attackitem_x ** 2 + player_attackitem_y ** 2) ** (1 / 2) < attackitem_radius + player_radius:
            if not getattr(self.boss, 'dead', False):
                self.boss.health -= self.attackitem.damage
                if self.boss_hit_sound:
                    self.boss_hit_sound.play()
                self.set_image(1, duration=45)
            del (self.attackitem)
            self.attackitem = attackitem(self.width, self.height)

        # Boss 逻辑
        if getattr(self.boss, 'dead', False):
            # 重生
            if hasattr(self.boss, 'respawn_timer'):
                self.boss.respawn_timer -= 1
                if self.boss.respawn_timer <= 0:
                    self.boss.dead = False
                    self.boss.maxhealth += 100
                    self.health += 10
                    self.boss.health = self.boss.maxhealth
                    # 重生时不再直接增加速度
                    self.set_image(0, duration=30)
        else:
            self.boss.update()
        self.attackitem.update()

        if self.boss.health <= 0 and not getattr(self.boss, 'dead', False):
            # 计时器
            self.boss.dead = True
            self.boss.respawn_timer = 90
            # 每次死亡增加移动速度和体积
            try:
                self.boss.increase_speed()
            except Exception:
                pass
            self.boss.wid += 5
            self.set_image(2, duration=0)
            # Boss 增加分数（0->1->11->114->1145->11451->114514）
            try:
                self.advance_score_sequence()
            except Exception:
                pass

        # 启动胜利倒计时
        if self.score_temp >= 114514 and not self.has_won:
            self.has_won = True
            self.win_countdown_timer = 5 * 60

        self.draw()

        # 角色死亡
        if self.health <= 0:
            if not self.is_dead:
                self.is_dead = True
                # 播放死亡音
                if self.player_death_sound:
                    try:
                        self.player_death_sound.play()
                    except Exception:
                        pass
                # 放大 boss
                self.boss.wid += 600
                # 启动倒计时
                self.death_countdown_timer = 5 * 60

            # 倒计时进行中
            if self.death_countdown_timer is not None:
                self.death_countdown_timer -= 1
                if self.death_countdown_timer <= 0:
                    # 结束游戏
                    self.score = self.score_temp
                    self.reset()
                    self.end()

        # 胜利倒计时
        if self.has_won and self.win_countdown_timer is not None:
            self.win_countdown_timer -= 1
            self.health = 1145114
            if self.win_countdown_timer <= 0:
                try:
                    self.score=self.score_temp
                    self.reset()
                except Exception:
                    pass
                self.end()

        return super().update()

    def draw(self):
        self.screen.fill((30, 30, 30))

        scaled_img = pg.transform.scale(self.images[self.image_index], (self.boss.wid, self.boss.wid))

        if not self.is_dead:
            # 方向线
            dir_end = (self.center[0] + self.direction[0] * 20, self.center[1] + self.direction[1] * 20)
            pg.draw.line(self.screen, (0, 0, 255), self.center, dir_end, 2)  # 蓝色
            # 球体
            pg.draw.circle(self.screen, (255, 255, 255), (int(self.center[0]), int(self.center[1])), 10)
            pg.draw.circle(self.screen, (0, 255, 0), center=(self.attackitem.center[0], self.attackitem.center[1]), radius=10)
            boss_hp_text = self.info_font.render(f"Boss HP: {self.boss.health}/{self.boss.maxhealth}", True, (255, 50, 50))  # 红色
            player_damage_text = self.info_font.render(f"Player ATK: {self.attackitem.damage}", True, (50, 255, 50))  # 绿色
            player_health_text = self.info_font.render(f"player HP: {self.health}", True, (255, 165, 0))
            self.screen.blit(boss_hp_text, (10, 10))
            self.screen.blit(player_damage_text, (10, 35))
            self.screen.blit(player_health_text, (10, 60))
        # boss
        boss_img_rect = scaled_img.get_rect(center=(self.boss.center[0], self.boss.center[1]))
        self.screen.blit(scaled_img, boss_img_rect)
        # 倒计时数字
        if self.death_countdown_timer is not None:
            secs = math.ceil(self.death_countdown_timer / 60.0)
            countdown_surf = self.countdown_font.render(str(secs), True, (255, 0, 0))
            countdown_rect = countdown_surf.get_rect(center=(self.width // 2, self.height // 2 - 80))
            self.screen.blit(countdown_surf, countdown_rect)
        # 胜利显示
        if self.has_won and self.win_countdown_timer is not None:
            win_surf = self.game_over_font.render("YOU WIN", True, (255, 215, 0))
            win_rect = win_surf.get_rect(center=(self.width // 2, self.height // 2 - 160))
            self.screen.blit(win_surf, win_rect)
            win_secs = math.ceil(self.win_countdown_timer / 60.0)
            win_count_surf = self.countdown_font.render(str(win_secs), True, (255, 255, 255))
            win_count_rect = win_count_surf.get_rect(center=(self.width // 2, self.height // 2 - 40))
            self.screen.blit(win_count_surf, win_count_rect)
        elif self.is_dead and self.game_over_text is not None:
            game_over_rect = self.game_over_text.get_rect(center=(self.width // 2, 100))
            self.screen.blit(self.game_over_text, game_over_rect)

        score_text = f"Score: {self.score_temp}"
        score_surface = self.font.render(score_text, True, (255, 255, 255))  # 白色
        score_rect = score_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_surface, score_rect)

    def reset(self):
        # 位置与移动状态
        self.center = self.initial_center.copy()
        self.direction = self.initial_direction.copy()
        self._normalize_direction()
        self.speed = 0
        self.moving = True

        # 角色状态
        self.health = 10
        self.is_dead = False
        self.game_over_text = None
        self.image_index = 0
        self.image_timer = 0

        # 分数与重置序列
        self.score_temp = 0
        self.reset_digits = [1, 1, 4, 5, 1, 4]
        self.reset_digit_index = 0

        # 重置胜利/倒计时状态
        self.death_countdown_timer = None
        self.has_won = False
        self.win_countdown_timer = None

        # Boss 状态重置
        self.boss.health = self.initial_boss_health
        self.boss.maxhealth = 100
        self.boss.dead = False
        self.boss.respawn_timer = 0
        self.boss.center = [random.randint(0, self.width), random.randint(0, self.height)]
        self.boss.wid = 88
        try:
            self.boss.reset_speed()
        except Exception:
            pass

        # 攻击道具重置
        self.attackitem.center = [random.randint(0, self.width), random.randint(0, self.height)]
        self.attackitem.damage = self.initial_attack_damage

        # 停止正在播放的音效（安全调用）
        try:
            if getattr(self, 'player_death_sound', None):
                self.player_death_sound.stop()
        except Exception:
            pass
        try:
            if getattr(self, 'boss_hit_sound', None):
                self.boss_hit_sound.stop()
        except Exception:
            pass

    def advance_score_sequence(self):
        # 隐藏倒计时
        self.death_countdown_timer = None
        try:
            if self.reset_digit_index < len(self.reset_digits):
                digit = self.reset_digits[self.reset_digit_index]
                if self.score_temp == 0:
                    self.score_temp = digit
                else:
                    self.score_temp = int(str(self.score_temp) + str(digit))
                self.reset_digit_index += 1
                # 胜利倒计时
                if self.score_temp >= 114514 and not self.has_won:
                    self.has_won = True
                    self.win_countdown_timer = 5 * 60
        except Exception:
            pass

    # def end(self):
    #     return super().end()

    def on_key_down(self, key):
        # 退出游戏时暂停死亡音
        if key == pg.K_ESCAPE:
            if getattr(self, 'player_death_sound', None):
                try:
                    self.player_death_sound.stop()
                except Exception:
                    pass
            self.end()
        return super().on_key_down(key)
        


class Boss(GameFramework):
    def __init__(self, width, height):
        super().__init__("BTxin", width, height)
        self.dead = True
        self.respawn_timer = 0
        self.maxhealth = 100
        self.health = self.maxhealth
        self.attack = 1
        self.wid = 88
        self.center = [random.randint(0, width), random.randint(0, height)]
        self.velocity = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.change_direction_timer = 0
        self.speed_multiplier = 3.0
        self.base_speed = 3.0

    def update(self):
        # 改变方向
        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            max_speed = self.base_speed * self.speed_multiplier
            self.velocity = [random.uniform(-max_speed, max_speed), random.uniform(-max_speed, max_speed)]
            self.change_direction_timer = 60

        # 平滑移动
        self.center[0] += self.velocity[0]
        self.center[1] += self.velocity[1]

        screen_width = 800
        screen_height = 600
        boss_half_width = self.wid / 2

        # 边缘反弹
        if self.center[0] - boss_half_width <= 0 or self.center[0] + boss_half_width >= screen_width:
            self.velocity[0] = -self.velocity[0]
            self.center[0] = max(boss_half_width, min(self.center[0], screen_width - boss_half_width))

        if self.center[1] - boss_half_width <= 0 or self.center[1] + boss_half_width >= screen_height:
            self.velocity[1] = -self.velocity[1]
            self.center[1] = max(boss_half_width, min(self.center[1], screen_height - boss_half_width))

    def increase_speed(self):
        self.speed_multiplier *= 1.2

    def reset_speed(self):
        self.speed_multiplier = 1.0


class attackitem(GameFramework):
    def __init__(self, width, height):
        super().__init__("BTxin", width, height)
        self.center = [random.randint(0, width), random.randint(0, height)]
        self.damage = 10

    def update(self):
        temp = random.randint(0, 10)
        if temp > 8:
            self.damage = 114514
        elif 5 <= temp <= 8:
            self.damage = random.randint(114, 200)
        else:
            self.damage = random.randint(0, 114)
        try:
            return super().update()
        except Exception:
            return None