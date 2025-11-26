import pygame
import os

from framwork import GameFramework

class MainMenu3(GameFramework):
    """
    支持列表视图与海报（格子）视图切换的美化主菜单。
    - 左上角显示视图模式切换按钮（点击/悬浮高亮）
    - 海报视图每个游戏读取cover图片（支持自动编号: covers/01.jpg, 02.jpg ...）
    - 鼠标悬浮时，封面产生自下而上的白色动画，并显示游戏名
    - 鼠标点击游戏即可启动
    """
    def __init__(self, width=900, height=600, covers_dir="./MainMenu/covers"):
        super().__init__("MainMenu", width, height)
        self.games = []  # [(name, game实例)]
        self.selected_idx = 0  # 键盘选中
        self.hover_idx = -1    # 鼠标悬浮
        self.on_grid_view = True # True:海报/格子模式, False:列表模式
        self.covers_dir = covers_dir
        self.cover_images = []
        self.grid_rects = [] # 存储海报的rect及其idx,便于鼠标检测&动画
        self.switch_btn_rects = {}
        # 动画进度 - 每个格子一个动画值
        self.grid_ani_progress = []
        # 用于判断鼠标事件
        self.last_mouse_pos = (0, 0)

        self._load_covers()
        self.last_switch_tick = 0

        self.background=None


    def run(self):
        super().run()
        try:
            self.background=pygame.image.load("./MainMenu/Background.jpg")
        except:
            pass
        

    def _load_covers(self):
        # 假定图片名为 01.jpg, 02.jpg ...，不足时用灰色方块
        self.cover_images = []
        for i in range(40): # 最多40个封面
            fn = f"{self.covers_dir}/{i+1:02d}.jpg"
            if os.path.exists(fn):
                im = pygame.image.load(fn).convert()
                im = pygame.transform.smoothscale(im, (180, 240))
            else:
                im = pygame.Surface((180,240))
                im.fill((200, 200, 200))
                pygame.draw.rect(im, (120,120,120), im.get_rect(), 4)
            self.cover_images.append(im)
        self.grid_ani_progress = [0.0 for _ in range(40)]

    def set_game_list(self, games):
        self.games = [(g.get_name(), g) for g in games if g.get_name() != "MainMenu"]
        self._load_covers()
        # 更新动画长度（games变了也要同步）
        self.grid_ani_progress = [0.0 for _ in range(max(40, len(self.games)))]

    def draw(self):
        if self.background == None:
            self.screen.fill((10, 15, 50))
        else:
            self.screen.blit(self.background,(0,0))
        # 1. 左上角视图切换按钮
        list_btn = pygame.Rect(20, 20, 56, 36)
        grid_btn = pygame.Rect(90, 20, 56, 36)
        mx, my = pygame.mouse.get_pos()
        self.switch_btn_rects = {"list":list_btn, "grid":grid_btn}

        font = pygame.font.SysFont("SimHei", 25)
        ficon = pygame.font.SysFont("Verdana", 27, bold=True)
        # list_btn
        col = (240,240,180) if (list_btn.collidepoint(mx,my) or not self.on_grid_view) else (120,120,100)
        pygame.draw.rect(self.screen, col, list_btn, border_radius=7)
        self.text_out("≡", (list_btn.x+14, list_btn.y+3), 28, (60,60,60), font="Verdana")
        self.text_out("列表", (list_btn.x+12, list_btn.y+5), 17, (60,60,60))

        col2 = (240,240,180) if (grid_btn.collidepoint(mx,my) or self.on_grid_view) else (120,120,100)
        pygame.draw.rect(self.screen, col2, grid_btn, border_radius=7)
        self.text_out("☷", (grid_btn.x+14, grid_btn.y+3), 28, (60,60,60), font="Verdana")
        self.text_out("海报", (grid_btn.x+12, grid_btn.y+5), 17, (60,60,60))

        # 2. 两种视图绘制
        if self.on_grid_view:
            self._draw_grid_menu(mx, my)
        else:
            self._draw_list_menu(mx, my)

        # 右下角 说明
        if self.background==None:
            self.text_out("←/→切换视图 鼠标选择游戏 Enter/点击游戏图标进入    Esc退出", (self.width-740, self.height-36), 22, (180,200,220))
        else:
            self.text_out("←/→切换视图 鼠标选择游戏 Enter/点击游戏图标进入    Esc退出", (self.width-740, self.height-36), 22, (255,255,255))

    def _draw_grid_menu(self, mx, my):
        # 海报格子 3 列，排版
        cols = 4
        cell_w, cell_h = 195, 285
        margin_x, margin_y = 50, 96
        grid_x0, grid_y0 = 50, 90
        # 所有格子的 rect 区域和映射
        self.grid_rects = []
        for idx, (gamename, _) in enumerate(self.games):
            row = idx // cols
            col = idx % cols
            x = grid_x0 + col * cell_w + margin_x
            y = grid_y0 + row * cell_h + margin_y

            rect = pygame.Rect(x, y, 180, 240)
            self.grid_rects.append(rect)
            # 封面
            img = self.cover_images[idx] if idx < len(self.cover_images) else self.cover_images[0]
            # 悬浮检测
            hover = rect.collidepoint(mx, my)
            if hover:
                self.hover_idx = idx
            # 动画处理
            speed = 0.13
            # 动画递进/回退
            if hover:
                self.grid_ani_progress[idx] = min(self.grid_ani_progress[idx] + speed, 1.0)
            else:
                self.grid_ani_progress[idx] = max(self.grid_ani_progress[idx] - speed*1.25, 0.0)

            # 绘制封面
            self.screen.blit(img, (x, y))
            # 悬浮时动态白色遮罩和游戏名
            ani = self.grid_ani_progress[idx]
            if ani > 0.01:
                ani_height = int(ani * 85)
                cover = pygame.Surface((180, ani_height), pygame.SRCALPHA)
                cover.fill((255,255,255, min(200, int(230*ani))))
                self.screen.blit(cover, (x, y+240-ani_height))
                if ani>0.7:
                    self.text_out(gamename, (x+32, y+240-ani_height+12), 22, (24,28,60))

    def _draw_list_menu(self, mx, my):
        starty = 110
        rowh = 54
        self.hover_idx = -1
        iconw, iconh = 56, 56
        for idx, (gamename, _) in enumerate(self.games):
            y = starty+idx*rowh
            hover = (30 <= mx <= 680 and y<= my <= y+rowh)
            # 鼠标悬浮高亮
            bgcol = (240,255,255) if hover else (24,24,60)
            textcolor=(24,24,60) if hover else (240,255, 255)
            pygame.draw.rect(self.screen, bgcol, (26,y,680,rowh-8), border_radius=8)
            if hover:
                self.hover_idx = idx
            # 序号
            self.text_out(f"{idx+1:02d}", (34, y+6), 28, (130,130,130))
            # 封面缩略图
            img = self.cover_images[idx] if idx < len(self.cover_images) else self.cover_images[0]
            thumb = pygame.transform.smoothscale(img, (iconw, iconh))
            self.screen.blit(thumb, (80, y+1))
            # 游戏名
            self.text_out(gamename, (170, y+15), 26, textcolor)
            # 右侧小箭头
            self.text_out("▶", (687, y+13), 28, (120,130,180))

    def on_mouse_down_ex(self, event):
        mx, my = event.pos
        # 点击左上角视图切换
        for k, rect in self.switch_btn_rects.items():
            if rect.collidepoint(mx, my):
                self.on_grid_view = (k == "grid") # grid/list
                return
        # 点击游戏（海报模式或列表模式）
        idx = self._point_to_gameidx(mx, my)
        if idx is not None:
            self.selected_idx = idx
            self.end() # 框架会根据 self.score+1 跳转游戏

    def _point_to_gameidx(self, mx, my):
        # 判断当前鼠标点落在哪个游戏格子/行
        if self.on_grid_view:
            for i, rect in enumerate(self.grid_rects):
                if rect.collidepoint(mx, my):
                    return i
        else:
            starty = 110
            rowh = 54
            for idx in range(len(self.games)):
                y = starty+idx*rowh
                if 30 <= mx <= 680 and y<= my <= y+rowh:
                    return idx
        return None

    def on_key_down(self, key):
        # 支持ESC退出
        if key == pygame.K_ESCAPE:
            self.selected_idx=-1
            self.end()
        if key == pygame.K_LEFT or key==pygame.K_a:
            self.on_grid_view = False
        if key == pygame.K_RIGHT or key==pygame.K_d:
            self.on_grid_view = True
        if key == pygame.K_DOWN:
            self.selected_idx = min(self.selected_idx+1, len(self.games)-1)
        if key == pygame.K_UP:
            self.selected_idx = max(self.selected_idx-1, 0)
        if key == pygame.K_RETURN or key==pygame.K_KP_ENTER:
            self.end()
        super().on_key_down(key)

    def end(self):
        # 跳转到self.selected_idx所代表的游戏（score+1）
        self.score = self.selected_idx+1
        super().end()