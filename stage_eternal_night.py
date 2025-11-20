import pygame
import random
import math
from framwork import GameFramework

class TouhouStage(GameFramework):
    def __init__(self, width=800, height=600):
        super().__init__("东方永夜抄·样例关", width, height)
        self.hero_speed = 6
        self.bullet_speed = 12
        self.enemy_bullet_speed = 4
        self.enemy_speed = 2
        self.bullets = []
        self.enemy_bullets = []
        self.bomb_effects = []
        self.max_life = 5
        self.inv_frames = 60    # 无敌帧数，复活短暂无敌
        self.shoot_interval = 6 # 自机发射间隔
        self.fail = False
        self.pause=False
        self.clock = pygame.time.Clock()
        self.load_images()
        self.reset()

    def load_images(self):
        self.reimu_img = pygame.image.load("Reimu.png")
        self.reimu_img = pygame.transform.scale(self.reimu_img, (48, 48))
        self.junko_img = pygame.image.load("Junko.png")
        self.junko_img = pygame.transform.scale(self.junko_img, (64, 64))

    def reset(self):
        self.hero_x = self.width // 2
        self.hero_y = self.height - 70
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemy_x = self.width // 2
        self.enemy_y = 100
        self.enemy_hp = 80
        self.enemy_maxhp = 80
        self.enemy_move_dir = random.choice([-1, 1])
        self.framecnt = 0
        self.score = 0
        self.hero_alive = True
        self.shoot_cooldown = 0
        self.life = self.max_life
        self.invincible_timer = 0
        self.fail = False
        self.start_time = pygame.time.get_ticks()
        self.boss_start_time = None

    def on_key_down(self, key):
        if key == pygame.K_ESCAPE:
            self.end()

    def get_final_score(self):
        # 失败：存活时间+剩余命*200
        # 通关：base10000+剩余命*1000+bonus(用时短)
        if not self.hero_alive and self.enemy_hp > 0:  # 死亡
            self.score = int((pygame.time.get_ticks()-self.start_time)/10) + self.life*200
        elif self.enemy_hp<=0:
            clear_time = (self.boss_start_time-self.start_time)/1000 if self.boss_start_time else 60
            time_bonus = max(2000-int(clear_time*20),0)
            self.score = 10000 + self.life*1000 + time_bonus

    def end(self):
        self.get_final_score()
        if self.fail:
            self.text_out("You Failed!",(300,300),48,(255,50,50))
            self.text_out("Score:"+str(self.score),(300,500))
        else:
            self.text_out("You Win!",(300,300),48,(50,250,50))
            self.text_out("Score:"+str(self.score),(300,500),48,(255,255,90))
        for sec in range(5,-1,-1):
            self.clock.tick(1)
            self.text_out(str(sec)+"sec back to the Main Menu",(300,550),18)
            pygame.display.flip()
        super().end()

    def on_focus_loss(self):
        self.text_out("Pause",(0,550))
        self.pause=True
        super().on_focus_get()

    def on_focus_get(self):
        self.pause=False
        super().on_focus_get()

    def update1(self):
        # 帧锁
        #pygame.time.delay(12)
        self.clock.tick(60)
        if self.pause:
            return
        now = pygame.time.get_ticks()
        # 控制自机
        keys = pygame.key.get_pressed()
        move = [0, 0]
        if self.hero_alive:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move[0] -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move[0] += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move[1] -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move[1] += 1
            if move != [0, 0]:
                norm = (move[0]**2 + move[1]**2)**0.5
                if norm != 0:
                    move[0] /= norm
                    move[1] /= norm
                self.hero_x += int(self.hero_speed * move[0])
                self.hero_y += int(self.hero_speed * move[1])
            # 边界处理 
            self.hero_x = max(0, min(self.hero_x, self.width - 48))
            self.hero_y = max(0, min(self.hero_y, self.height - 48))

            # 发射子弹
            if (keys[pygame.K_z] or keys[pygame.K_j]) and self.shoot_cooldown == 0:
                cx = self.hero_x + 24
                cy = self.hero_y + 24
                self.bullets.append([cx, cy-10])
                self.shoot_cooldown = self.shoot_interval
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1

        # 己弹移动
        for b in self.bullets[:]:
            b[1] -= self.bullet_speed
            if b[1] < -20:
                self.bullets.remove(b)

        # 敌人移动
        self.framecnt += 1
        # 随机左右悬停+缓慢上下小幅波动
        if self.framecnt % 2 == 0:
            self.enemy_x += self.enemy_move_dir * self.enemy_speed
        if random.random() < 0.05:
            self.enemy_move_dir *= -1
        self.enemy_x = max(0, min(self.enemy_x, self.width - 64))
        self.enemy_y = 100 + int(30 * math.sin(self.framecnt/50))

        # 敌人发弹幕
        if self.framecnt % 28 == 0 and self.hero_alive:
            # 螺旋弹
            for i in range(6):
                angle = (self.framecnt * 2 + i * 60) % 360
                rads = angle * math.pi / 180
                dx = self.enemy_bullet_speed * math.cos(rads)
                dy = self.enemy_bullet_speed * math.sin(rads)
                self.enemy_bullets.append([self.enemy_x+32, self.enemy_y+48, dx, dy])
            # 跟踪弹
            cx, cy = self.enemy_x+32, self.enemy_y+48
            tx, ty = self.hero_x+24, self.hero_y+24
            vlen = ((tx-cx)**2 + (ty-cy)**2) ** 0.5
            dx = self.enemy_bullet_speed * (tx-cx)/vlen
            dy = self.enemy_bullet_speed * (ty-cy)/vlen
            self.enemy_bullets.append([cx, cy, dx, dy])

        # 敌弹移动
        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if eb[0] < -30 or eb[0] > self.width+30 or eb[1] < -30 or eb[1] > self.height+30:
                self.enemy_bullets.remove(eb)

        # 判定圈
        graze = False
        judge_radius = 6
        hx = self.hero_x + 24
        hy = self.hero_y + 36 - 18
        # 子弹判定（敌弹 vs 判定圈）
        hit = False
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        else:
            for eb in self.enemy_bullets:
                dx = eb[0] - hx
                dy = eb[1] - hy
                if dx*dx + dy*dy <= judge_radius**2:
                    hit = True
                    break
        if hit and self.hero_alive:
            self.life -= 1
            if self.life > 0:
                self.hero_x = self.width//2
                self.hero_y = self.height - 60
                self.invincible_timer = self.inv_frames
                self.enemy_bullets.clear()
                self.bullets.clear()
            else:
                self.hero_alive = False
                self.fail = True
                self.end()

        # Boss判定
        boss_rect = pygame.Rect(self.enemy_x+8, self.enemy_y+8, 48, 48)
        for b in self.bullets[:]:
            # 判定以Boss中心为主，适当缩小范围
            if boss_rect.collidepoint(b[0], b[1]):
                self.enemy_hp -= 1
                self.bullets.remove(b)
                self.score += 10  # 每Hit加分

        # 胜负判定
        if self.enemy_hp <= 0:
            if self.boss_start_time is None:
                self.boss_start_time = pygame.time.get_ticks()
            self.hero_alive = False
            self.fail = False
            self.end()

        # 画面
        self.screen.fill((10, 0, 40))
        # Boss
        self.screen.blit(self.junko_img, (self.enemy_x, self.enemy_y))
        # Boss血条
        barw = 320
        bx = (self.width - barw) // 2
        pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, barw, 16), 2)
        if self.enemy_hp > 0:
            real_w = int(barw*self.enemy_hp/self.enemy_maxhp)
            pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, real_w, 16))
        self.text_out("Boss", (bx+barw+10, 30), 22, (255, 90, 130))
        # Boss血量百分比
        self.text_out(f"{int(100*self.enemy_hp/self.enemy_maxhp)}%", (bx+barw+70, 30), 22, (255,200,200))

        # 敌弹
        for eb in self.enemy_bullets:
            pygame.draw.circle(self.screen, (255,70,160), (int(eb[0]), int(eb[1])), 8)

        # 自弹
        for b in self.bullets:
            pygame.draw.rect(self.screen, (255,255,200), (b[0]-2, b[1]-8, 5, 12))
        # Reimu
        if self.hero_alive or self.invincible_timer>0:
            self.screen.blit(self.reimu_img, (self.hero_x, self.hero_y))
            # 判定点
            pygame.draw.circle(self.screen, (40,180,255), (hx, hy), judge_radius)
        # 残机显示
        icon = pygame.transform.scale(self.reimu_img, (24,24))
        for i in range(self.life-1):
            self.screen.blit(icon, (20+i*28, self.height-40))
        self.text_out(f"x{self.life}", (20+max(0,(self.life-1))*28+28, self.height-34), 24, (180,230,250))
        # 分数
        self.text_out(f"Score:{self.score}", (20,20), 30, (255,255,90))
        # 提示
        if self.fail:
            self.text_out("Game Over! 按ESC返回菜单", (200, 260), 44, (255,80,80))
        elif self.enemy_hp <=0:
            used_time = (pygame.time.get_ticks() - self.start_time)/1000
            self.text_out(f"胜利! Boss击破! 按ESC返回菜单", (160, 220), 40, (100,255,100))
        pygame.display.flip()

        # 结算分数
        # 失败：存活时间+剩余命*200
        # 通关：base10000+剩余命*1000+bonus(用时短)
        if not self.hero_alive and self.enemy_hp > 0:  # 死亡
            self.score = int((pygame.time.get_ticks()-self.start_time)/10) + self.life*200
        elif self.enemy_hp<=0:
            clear_time = (self.boss_start_time-self.start_time)/1000 if self.boss_start_time else 60
            time_bonus = max(2000-int(clear_time*20),0)
            self.score = 10000 + self.life*1000 + time_bonus

    def update(self):
        # 帧锁
        #pygame.time.delay(12)
        self.clock.tick(60)
        if self.pause:
            return
        now = pygame.time.get_ticks()
        # 控制自机
        keys = pygame.key.get_pressed()
        move = [0, 0]
        if self.hero_alive:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move[0] -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move[0] += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move[1] -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move[1] += 1
            if move != [0, 0]:
                norm = (move[0]**2 + move[1]**2)**0.5
                if norm != 0:
                    move[0] /= norm
                    move[1] /= norm
                self.hero_x += int(self.hero_speed * move[0])
                self.hero_y += int(self.hero_speed * move[1])
            # 边界处理 
            self.hero_x = max(0, min(self.hero_x, self.width - 48))
            self.hero_y = max(0, min(self.hero_y, self.height - 48))

            # 发射子弹
            if (keys[pygame.K_z] or keys[pygame.K_j]) and self.shoot_cooldown == 0:
                cx = self.hero_x + 24
                cy = self.hero_y + 24
                self.bullets.append([cx, cy-10])
                self.shoot_cooldown = self.shoot_interval
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1

        # 己弹移动
        for b in self.bullets[:]:
            b[1] -= self.bullet_speed
            if b[1] < -20:
                self.bullets.remove(b)

        # 敌人移动
        self.framecnt += 1
        # 随机左右悬停+缓慢上下小幅波动
        if self.framecnt % 2 == 0:
            self.enemy_x += self.enemy_move_dir * self.enemy_speed
        if random.random() < 0.05:
            self.enemy_move_dir *= -1
        self.enemy_x = max(0, min(self.enemy_x, self.width - 64))
        self.enemy_y = 100 + int(30 * math.sin(self.framecnt/50))

        # 敌人发弹幕
        if self.framecnt % 28 == 0 and self.hero_alive:
            # 螺旋弹
            for i in range(6):
                angle = (self.framecnt * 2 + i * 60) % 360
                rads = angle * math.pi / 180
                dx = self.enemy_bullet_speed * math.cos(rads)
                dy = self.enemy_bullet_speed * math.sin(rads)
                self.enemy_bullets.append([self.enemy_x+32, self.enemy_y+48, dx, dy])
            # 跟踪弹
            cx, cy = self.enemy_x+32, self.enemy_y+48
            tx, ty = self.hero_x+24, self.hero_y+24
            vlen = ((tx-cx)**2 + (ty-cy)**2) ** 0.5
            dx = self.enemy_bullet_speed * (tx-cx)/vlen
            dy = self.enemy_bullet_speed * (ty-cy)/vlen
            self.enemy_bullets.append([cx, cy, dx, dy])

        # 敌弹移动
        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if eb[0] < -30 or eb[0] > self.width+30 or eb[1] < -30 or eb[1] > self.height+30:
                self.enemy_bullets.remove(eb)

        # 判定圈
        graze = False
        judge_radius = 6
        hx = self.hero_x + 24
        hy = self.hero_y + 36 - 18
        # 子弹判定（敌弹 vs 判定圈）
        hit = False
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        else:
            for eb in self.enemy_bullets:
                dx = eb[0] - hx
                dy = eb[1] - hy
                if dx*dx + dy*dy <= judge_radius**2:
                    hit = True
                    break
        if hit and self.hero_alive:
            self.life -= 1
            if self.life > 0:
                self.hero_x = self.width//2
                self.hero_y = self.height - 60
                self.invincible_timer = self.inv_frames
                self.enemy_bullets.clear()
                self.bullets.clear()
            else:
                self.hero_alive = False
                self.fail = True
                self.end()

        # Boss判定
        boss_rect = pygame.Rect(self.enemy_x+8, self.enemy_y+8, 48, 48)
        for b in self.bullets[:]:
            # 判定以Boss中心为主，适当缩小范围
            if boss_rect.collidepoint(b[0], b[1]):
                self.enemy_hp -= 1
                self.bullets.remove(b)
                self.score += 10  # 每Hit加分

        # 胜负判定
        if self.enemy_hp <= 0:
            if self.boss_start_time is None:
                self.boss_start_time = pygame.time.get_ticks()
            self.hero_alive = False
            self.fail = False
            self.end()

        # 画面
        self.screen.fill((10, 0, 40))
        # Boss
        self.screen.blit(self.junko_img, (self.enemy_x, self.enemy_y))
        # Boss血条
        barw = 320
        bx = (self.width - barw) // 2
        pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, barw, 16), 2)
        if self.enemy_hp > 0:
            real_w = int(barw*self.enemy_hp/self.enemy_maxhp)
            pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, real_w, 16))
        self.text_out("Boss", (bx+barw+10, 30), 22, (255, 90, 130))
        # Boss血量百分比
        self.text_out(f"{int(100*self.enemy_hp/self.enemy_maxhp)}%", (bx+barw+70, 30), 22, (255,200,200))

        # 敌弹
        for eb in self.enemy_bullets:
            pygame.draw.circle(self.screen, (255,70,160), (int(eb[0]), int(eb[1])), 8)

        # 自弹
        for b in self.bullets:
            pygame.draw.rect(self.screen, (255,255,200), (b[0]-2, b[1]-8, 5, 12))
        # Reimu
        if self.hero_alive or self.invincible_timer>0:
            self.screen.blit(self.reimu_img, (self.hero_x, self.hero_y))
            # 判定点
            pygame.draw.circle(self.screen, (40,180,255), (hx, hy), judge_radius)
        # 残机显示
        icon = pygame.transform.scale(self.reimu_img, (24,24))
        for i in range(self.life-1):
            self.screen.blit(icon, (20+i*28, self.height-40))
        self.text_out(f"x{self.life}", (20+max(0,(self.life-1))*28+28, self.height-34), 24, (180,230,250))
        # 分数
        self.text_out(f"Score:{self.score}", (20,20), 30, (255,255,90))
        # 提示
        if self.fail:
            self.text_out("Game Over! 按ESC返回菜单", (200, 260), 44, (255,80,80))
        elif self.enemy_hp <=0:
            used_time = (pygame.time.get_ticks() - self.start_time)/1000
            self.text_out(f"胜利! Boss击破! 按ESC返回菜单", (160, 220), 40, (100,255,100))
        pygame.display.flip()

        # 结算分数
        #迁移至end里
        self.get_final_score()

    def run(self):
        self.reset()
        super().run()