import pygame
import random
import math
from framwork import GameFramework
import os

class TouhouStage(GameFramework):
    """
    保留原版行为、体验兼容，同时使用新框架的 update()/draw() 分离与非阻塞 end 处理。
    - 逻辑在 update() 中执行（包含输入处理的按键查询、子弹移动、碰撞判定等）。
    - 渲染在 draw() 中完成（不调用 pygame.display.flip()，由框架统一刷新）。
    - end() 不再阻塞；通过 finished 标志显示结算界面，等待按键或超时后调用 super().end()。
    - 尽量保持原有得分、发弹、判定、图像使用等行为一致。
    """

    def __init__(self, width=800, height=600):
        super().__init__("东方永夜抄·样例关", width, height)
        # game parameters (与原版保持相同)
        self.hero_speed = 6
        self.bullet_speed = 12
        self.enemy_bullet_speed = 4
        self.enemy_speed = 2
        self.max_life = 5
        self.inv_frames = 60    # 无敌帧数
        self.shoot_interval = 6 # 自机发射间隔

        # runtime state
        self.bullets = []
        self.enemy_bullets = []
        self.bomb_effects = []
        self.fail = False
        self.pause = False

        self.prestage=True
        self.reimu_talk_img=None
        self.junko_talk_img=None
        self.prev_cnt=0

        # images (loaded in load_images())
        self.reimu_img = None
        self.junko_img = None
        self.background= None
        #sounds
        self.sounds={}

        self.load_images()
        self.load_sound()
        self.reset()

    def load_sound(self):
        pygame.mixer.init()
        self.sounds["biu"]=pygame.mixer.Sound("./EternalNight/biu.wav")
        self.sounds["boss_defeated"]=pygame.mixer.Sound("./EternalNight/boss_defeated.wav")
        self.sounds["bullet_beep"]=pygame.mixer.Sound("./EternalNight/bullet_beep.wav")
        self.sounds["explosure"]=pygame.mixer.Sound("./EternalNight/explosure.wav")
        self.sounds["pick_pic"]=pygame.mixer.Sound("./EternalNight/pick_pic.wav")
        self.sounds["spellcard_start"]=pygame.mixer.Sound("./EternalNight/spellcard_start.wav")

    def load_images(self):
        # 尝试加载资源，若不存在则使用占位图，避免因文件缺失而崩溃
        try:
            #path_reimu = "Reimu.png"
            path_reimu="EternalNight\\Reimu.png"
            if os.path.exists(path_reimu):
                #img = pygame.image.load(path_reimu).convert_alpha()
                img = pygame.image.load(path_reimu)
            else:
                img = pygame.Surface((48,48), pygame.SRCALPHA)
                pygame.draw.circle(img, (200,200,40), (24,24), 22)
            self.reimu_img = pygame.transform.scale(img, (48, 48))
        except Exception:
            self.reimu_img = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(self.reimu_img, (200,200,40), (24,24), 22)

        try:
            path_junko = "EternalNight\\Junko.png"
            if os.path.exists(path_junko):
                #img2 = pygame.image.load(path_junko).convert_alpha()
                img2 = pygame.image.load(path_junko)
            else:
                img2 = pygame.Surface((64,64), pygame.SRCALPHA)
                pygame.draw.rect(img2, (220,80,80), (0,0,64,64))
            self.junko_img = pygame.transform.scale(img2, (64, 64))
        except Exception:
            self.junko_img = pygame.Surface((64,64), pygame.SRCALPHA)
            pygame.draw.rect(self.junko_img, (220,80,80), (0,0,64,64))
        try:
            self.background=pygame.image.load("EternalNight\\Muki.jpg")
        except Exception:
            pass

    def reset(self):
        # 初始化或重置游戏状态（与原 reset 行为等价）
        self.hero_x = self.width // 2
        self.hero_y = self.height - 70
        self.bullets = []
        self.enemy_bullets = []
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
        self.pause = False
        self.start_time = pygame.time.get_ticks()
        self.boss_start_time = None

        # finished overlay state (非阻塞结束)
        self.finished = False
        self.finish_reason = None     # "win" / "lose"
        self.finish_start_ticks = None
        self.finish_auto_seconds = 5  # 自动返回菜单秒数（与原近似）
        self._auto_exit_requested = False

        pygame.mixer.stop()

    def run(self):
        # 每次 run 都重置状态并调用框架的 run()
        self.reset()
        pygame.mixer.Sound("./EternalNight/th15_12.mp3").play()
        super().run()

    # ------------- input: ex 版本可以获得原始 event（推荐使用） -------------
    def on_key_down_ex(self, event):
        # ESC 立即请求返回（按原逻辑，原来是直接 end()）
        if event.key == pygame.K_ESCAPE:
            # 允许在未 finished 的时候把分数结算并显示 overlay，再由确认或超时退出
            if not self.finished:
                # 若游戏尚未结束，则将其当作“中途退出”，计算得分并展示
                if not self.hero_alive:
                    # 如果已经死亡则继续走正常流程
                    pass
                # mark fail if still alive but user quits? 保持原先行为：直接结束并返回
                self._on_lose() if self.fail else None
                # Request finalization: finalize immediately (user intends to quit)
                self._finalize_and_exit()
            else:
                # 如果已经 finished，任何键都立即退出
                self._finalize_and_exit()

    def on_mouse_down_ex(self, event):
        # 如果在结算界面点击，也确认退出
        if self.finished:
            self._finalize_and_exit()

    def enermy_shoot(self):
        # spiral bullets
            for i in range(6):
                angle = (self.framecnt * 2 + i * 60) % 360
                rads = angle * math.pi / 180
                dx = self.enemy_bullet_speed * math.cos(rads)
                dy = self.enemy_bullet_speed * math.sin(rads)
                self.enemy_bullets.append([self.enemy_x+32, self.enemy_y+48, dx, dy])
            # tracking bullet
            cx, cy = self.enemy_x+32, self.enemy_y+48
            tx, ty = self.hero_x+24, self.hero_y+24
            vlen = ((tx-cx)**2 + (ty-cy)**2) ** 0.5
            if vlen == 0:
                vlen = 1
            dx = self.enemy_bullet_speed * (tx-cx)/vlen
            dy = self.enemy_bullet_speed * (ty-cy)/vlen
            self.enemy_bullets.append([cx, cy, dx, dy])

    def enermy_check(self):
        boss_rect = pygame.Rect(self.enemy_x+8, self.enemy_y+8, 48, 48)
        for b in self.bullets[:]:
            if boss_rect.collidepoint(b[0], b[1]):
                self.enemy_hp -= 1
                try:
                    self.bullets.remove(b)
                except ValueError:
                    pass
                self.score += 10

    # ------------- logic update（不绘制） -------------
    def update(self):
        # 帧锁 / 固定帧率由框架统一控制（不要再在 update 中调用 clock.tick）
        if self.pause:
            return
        
        self.prev_cnt+=1
        if self.prev_cnt<5*60:
            return #标题阶段
        elif 5*60<self.prev_cnt<=35*60:
            #放入流星雨
            # 每 20 帧生成一组（可调）
            if self.framecnt % 20 == 0:
            # 选定一个x坐标
                x = random.randint(30, self.width - 30)
                # 生成一束流星：比如5颗纵向，y坐标间隔一致
                for j in range(5):  # 5颗一束
                    y_offset = -j*30    # 间距30像素逐帧入场
                    speed = self.enemy_bullet_speed + random.uniform(-0.5,0.5)
                    self.enemy_bullets.append([x, y_offset, 0, speed])
                # 偶尔生成斜向流星
                if random.random() < 0.20:
                    edge = random.choice(['left', 'right'])
                    y = random.randint(0, int(self.height*0.5))
                    dx = random.uniform(2, 3)
                    if edge == 'left':
                        self.enemy_bullets.append([0, y, dx, random.uniform(3, 4)])
                    else:
                        self.enemy_bullets.append([self.width, y, -dx, random.uniform(3, 4)])
        elif 35*60<self.prev_cnt<=40*60:
            #对话阶段，无弹幕绘制，暂不画敌人
            self.enemy_bullets.clear()
        if self.prev_cnt==60*60:
            pygame.mixer.stop()
            pygame.mixer.Sound("./EternalNight/th15_13.mp3").play()

        # 如果已经 finished（胜利/失败展示中），我们仍然要更新计时器以实现自动返回
        if self.finished:
            # 计算是否超时
            if self.finish_start_ticks is None:
                self.finish_start_ticks = pygame.time.get_ticks()
            else:
                elapsed = (pygame.time.get_ticks() - self.finish_start_ticks) // 1000
                if elapsed >= self.finish_auto_seconds or self._auto_exit_requested:
                    self._finalize_and_exit()
            # 不继续游戏逻辑
            return

        now = pygame.time.get_ticks()
        self.framecnt += 1

        # ---------------- player control ----------------
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
            # boundary
            self.hero_x = max(0, min(self.hero_x, self.width - 48))
            self.hero_y = max(0, min(self.hero_y, self.height - 48))

            # shooting
            if (keys[pygame.K_z] or keys[pygame.K_j]) and self.shoot_cooldown == 0:
                cx = self.hero_x + 24
                cy = self.hero_y + 24
                self.bullets.append([cx, cy-10])
                self.shoot_cooldown = self.shoot_interval
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1

        # ---------------- player bullets movement ----------------
        for b in self.bullets[:]:
            b[1] -= self.bullet_speed
            if b[1] < -20:
                try:
                    self.bullets.remove(b)
                except ValueError:
                    pass

        # ---------------- enemy behavior ----------------
        if self.framecnt % 2 == 0:
            self.enemy_x += self.enemy_move_dir * self.enemy_speed
        if random.random() < 0.05:
            self.enemy_move_dir *= -1
        self.enemy_x = max(0, min(self.enemy_x, self.width - 64))
        self.enemy_y = 100 + int(30 * math.sin(self.framecnt/50))

        # enemy shooting pattern
        if self.prev_cnt>60*60:
            if self.framecnt % 28 == 0 and self.hero_alive:
                self.enermy_shoot()

        # enemy bullets movement
        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if eb[0] < -30 or eb[0] > self.width+30 or eb[1] < -30 or eb[1] > self.height+30:
                try:
                    self.enemy_bullets.remove(eb)
                except ValueError:
                    pass

        # ---------------- collision / graze / life ----------------
        judge_radius = 6
        hx = self.hero_x + 24
        hy = self.hero_y + 36 - 18

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

        if hit:
            self.sounds["biu"].play()

        if hit and self.hero_alive:
            self.life -= 1
            if self.life > 0:
                # respawn with invincibility
                self.hero_x = self.width//2
                self.hero_y = self.height - 60
                self.invincible_timer = self.inv_frames
                self.enemy_bullets.clear()
                self.bullets.clear()
            else:
                # lost
                self.hero_alive = False
                self.fail = True
                # mark finished state instead of blocking end
                self._on_lose()
                return

        # boss collision with player's bullets
        if self.prev_cnt>60*60: #Prev Boss doesn't exist
            self.enermy_check()

        # win condition
        if self.enemy_hp <= 0:
            if self.boss_start_time is None:
                self.boss_start_time = pygame.time.get_ticks()
            self.hero_alive = False
            self.fail = False
            self._on_win()
            return

        # keep score calculation for display moved to get_final_score/draw or when finished
        # no pygame.display.flip() here (framework will handle)

    def boss_hp_bar(self):
        barw = 320
        bx = (self.width - barw) // 2
        pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, barw, 16), 2)
        if self.enemy_hp > 0:
            real_w = int(barw*self.enemy_hp/self.enemy_maxhp)
            pygame.draw.rect(self.screen, (240, 48, 90), (bx, 32, real_w, 16))
        self.text_out("Boss", (bx+barw+10, 30), 22, (255, 90, 130))
        self.text_out(f"{int(100*self.enemy_hp/self.enemy_maxhp)}%", (bx+barw+70, 30), 22, (255,200,200))

    def say(self,name,word):
        if name=="reimu":
            if self.reimu_talk_img==None:
                self.reimu_talk_img=pygame.image.load(".\\EternalNight\\reimu1.png")
            adapt_size=self.reimu_talk_img.get_size()
            adapt_size=tuple(int(x*0.3) for x in adapt_size) 
            self.image_out(self.reimu_talk_img,(self.width*0.25,self.height*0.6),adapt_size,True)
            #self.text_out(word,(self.width*0.3,self.height*0.7),25,(255,75,75))
            self.text_out(word,(self.width*0.1,self.height*0.7),40,(255,75,75))
        if name=="junko":
            if self.junko_talk_img==None:
                self.junko_talk_img=pygame.image.load(".\\EternalNight\\junko1.png")
            adapt_size=self.junko_talk_img.get_size()
            adapt_size=tuple(int(x*0.3) for x in adapt_size) 
            self.image_out(self.junko_talk_img,(self.width*0.75,self.height*0.6),adapt_size,True)
            #self.text_out(word,(self.width*0.3,self.height*0.7),25,(255,165,0))
            self.text_out(word,(self.width*0.1,self.height*0.7),40,(255,165,0))

    # ------------- drawing (rendering only) -------------
    def draw(self):
        

        # background
        #self.screen.fill((10, 0, 40))
        if self.background != None:
            self.screen.blit(self.background,(0,0))
        else:
            self.screen.fill((10,0,40))
        #debug
        self.text_out(f"prev_cnt={self.prev_cnt} \n prev_sec={self.prev_cnt//60}",(0,0),10,(255,255,255))

        if self.prev_cnt<5*60:
            self.text_out("东方永夜抄",(self.width*0.1,self.height*0.4),80,(250,165,0))
            self.text_out("灵梦和纯狐的奇妙Python冒险",(self.width*0.1,self.height*0.6),30,(250,100,100))
            return
        
        #talk
        if 35*60<self.prev_cnt<=40*60:
            self.enemy_bullets.clear()
            #self.text_out()

        # boss
        if self.prev_cnt>=35*60:
            self.screen.blit(self.junko_img, (self.enemy_x, self.enemy_y))

        
        if 35*60<self.prev_cnt<=38*60:
            self.say("reimu","给我干哪来了, 这还是幻想乡吗?")
            return
        elif 38*60<self.prev_cnt<=43*60:
            self.say("junko","如你所见, 我们正在东方永夜抄里")
            self.text_out("只不过是Python版本的",(self.width*0.1,self.height*0.85),40,(255,165,0))
            return
        elif 43*60<self.prev_cnt<=46*60:
            self.say("reimu","纯狐你不是绀珠传里的吗?")
            return
        elif 46*60<self.prev_cnt<=51*60:
            self.say("junko","我在月球上, 永夜抄也在月球上")
            self.text_out("这很正常",(self.width*0.1,self.height*0.85),40,(255,165,0))
            return
        elif 51*60<self.prev_cnt<=56*60:
            self.say("junko","况且作者认为我的弹幕很“纯粹”")
            self.text_out("适合展示",(self.width*0.1,self.height*0.85),40,(255,165,0))
            return
        elif 56*60<self.prev_cnt<=60*60:
            self.say("junko","")
            self.text_out("无需多言,速速动手",(self.width*0.1,self.height*0.85),40,(255,165,0))
            return

        # boss HP bar
        if self.prev_cnt>60*60:
            self.boss_hp_bar()

        # enemy bullets
        if self.prev_cnt>60*60:
            for eb in self.enemy_bullets:
                pygame.draw.circle(self.screen, (255,70,160), (int(eb[0]), int(eb[1])), 8)
        else:
            for eb in self.enemy_bullets:
                pygame.draw.circle(self.screen, (200, 220, 255), (int(eb[0]), int(eb[1])), 6)

        # player bullets
        for b in self.bullets:
            pygame.draw.rect(self.screen, (255,255,200), (b[0]-2, b[1]-8, 5, 12))

        # player sprite and hit point
        if self.hero_alive or self.invincible_timer > 0:
            self.screen.blit(self.reimu_img, (self.hero_x, self.hero_y))
            judge_radius = 6
            hx = self.hero_x + 24
            hy = self.hero_y + 36 - 18
            pygame.draw.circle(self.screen, (40,180,255), (hx, hy), judge_radius)

        # lives icons
        icon = pygame.transform.scale(self.reimu_img, (24,24))
        for i in range(max(0, self.life-1)):
            self.screen.blit(icon, (20+i*28, self.height-40))
        self.text_out(f"x{self.life}", (20+max(0,(self.life-1))*28+28, self.height-34), 24, (180,230,250))

        # score and messages
        self.text_out(f"Score:{self.score}", (20,20), 30, (255,255,90))
        if self.fail:
            # if fail but not finished yet, show Game Over hint (original visual)
            self.text_out("Game Over! 按任意键或ESC返回菜单", (200, 260), 30, (255,80,80))
        elif self.enemy_hp <= 0:
            self.text_out(f"胜利! Boss击破! 按任意键或ESC返回菜单", (160, 220), 30, (100,255,100))

        # If finished, show overlay persistently until confirm or timeout
        if self.finished:
            # compute final score (ensure up-to-date)
            self.get_final_score()
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            self.screen.blit(overlay, (0,0))

            if self.finish_reason == "win":
                title = "You Win!"
            else:
                title = "You Failed!"
            # center messages
            center_x = self.width // 2
            center_y = self.height // 2
            self.text_out(title, (center_x-120, center_y-60), size=48, color=(255,240,180))
            self.text_out("Score: " + str(self.score), (center_x-80, center_y), size=32, color=(220,220,220))

            # countdown hint
            elapsed_seconds = 0
            if self.finish_start_ticks:
                elapsed_seconds = (pygame.time.get_ticks() - self.finish_start_ticks) // 1000
            remain = max(0, self.finish_auto_seconds - elapsed_seconds)
            self.text_out(f"按任意键返回菜单（{remain}s 后自动返回）", (center_x-180, center_y+60), size=20, color=(180,200,220))

            
        if self.pause:
            self.text_out("paused",(int(self.width*0.8),int(self.height*0.9)))

    # ------------- helpers for finish handling -------------
    def get_final_score(self):
        # 同原逻辑：失败时按生存时间与剩余命，通关时按基准和用时
        if not self.hero_alive and self.enemy_hp > 0:  # 死亡
            self.score = int((pygame.time.get_ticks()-self.start_time)/10) + self.life*200
        elif self.enemy_hp <= 0:
            clear_time = (self.boss_start_time-self.start_time)/1000 if self.boss_start_time else 60
            time_bonus = max(2000-int(clear_time*20),0)
            self.score = 10000 + self.life*1000 + time_bonus

    def _on_win(self):
        self.sounds["boss_defeated"].play()
        self.sounds["explosure"].play()
        self.sounds["pick_pic"].play()

        # mark finished state, but don't block — draw() will show overlay
        if self.finished:
            return
        self.finished = True
        self.finish_reason = "win"
        self.finish_start_ticks = pygame.time.get_ticks()
        # ensure score includes boss clear bonus
        self.score = max(0, self.score + 500)

    def _on_lose(self):
        if self.finished:
            return
        self.finished = True
        self.finish_reason = "lose"
        self.finish_start_ticks = pygame.time.get_ticks()
        # compute score now
        self.get_final_score()

    def _finalize_and_exit(self):
        # finalize and stop running — call super().end() which will cause loop() to return self.score
        if self.running:
            pygame.mixer.stop()

            # ensure final score is computed
            self.get_final_score()
            # stop the game loop (non-blocking)
            super().end()

    # maintain compatibility of on_focus handlers if needed
    def on_focus_loss(self):
        pygame.mixer.pause()
        self.pause = True
        # optionally show pause indicator (draw handles this)
    def on_focus_get(self):
        pygame.mixer.unpause()
        self.pause = False

if __name__=="__main__":
    stage=TouhouStage()
    #debug the talk directly
    #stage.prev_cnt=35*60+1
    pygame.font.init()
    stage.run()
    stage.loop()