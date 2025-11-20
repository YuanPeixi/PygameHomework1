import xml.etree.ElementTree as ET
import datetime
import os
import pygame
import string

SCORE_XML = "rank.xml"

class ScoreManager:
    def __init__(self, filename=SCORE_XML):
        self.filename = filename
        self.scores = []
        self.username = None
        self.load()

    def load(self):
        self.scores.clear()
        if not os.path.exists(self.filename):
            # 文件不存在，后续写入会自动创建
            return
        try:
            tree = ET.parse(self.filename)
            root = tree.getroot()
            for node in root.findall("score"):
                name = node.find("name").text
                date = node.find("date").text
                score_text = node.find("point").text
                try:
                    score = int(score_text)
                except:
                    score = 0
                self.scores.append({'name': name, 'date': date, 'score': score})
        except Exception as e:
            print(f"加载排行榜时出错: {e}")
            self.scores = []

    def append_score(self, name, score):
        # 强制分数为整数和安全用户名
        if not name:
            name = self.username if self.username else "?"
        try:
            score = int(score)
        except:
            score = 0
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.scores.append({'name': name, 'date': date, 'score': score})
        # 只排序有数字分数的项，且KeyError安全
        safe_scores = [s for s in self.scores if isinstance(s.get('score', None), int)]
        self.scores = sorted(safe_scores, key=lambda x: (-x['score'], x['date']))
        # 写到XML，不包含任何'game'字段
        root = ET.Element("scores")
        for entry in self.scores:
            node = ET.SubElement(root, "score")
            ET.SubElement(node, "name").text = entry['name']
            ET.SubElement(node, "date").text = entry['date']
            ET.SubElement(node, "point").text = str(entry['score'])
        tree = ET.ElementTree(root)
        tree.write(self.filename, encoding="utf-8", xml_declaration=True)

    def get_scores(self):
        return self.scores

    def isLogined(self):
        return bool(self.username)

    def login(self, screen=None, width=800, height=600):
        if self.isLogined():
            return self.username
        font = pygame.font.SysFont("SimHei", 22)
        username = ""
        done = False
        clock = pygame.time.Clock()
        hint = font.render("请输入用户名, 按回车结束：", True, (255, 255, 0))
        input_charset = string.ascii_letters + string.digits + "_-."
        while not done:
            screen.fill((30,30,30))
            screen.blit(hint, (width//2-220, height//2-60))
            text = font.render(username, True, (255,255,255))
            screen.blit(text, (width//2-150, height//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    username = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if username:
                            done = True
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        username = None
                        done = True
                    else:
                        ch = event.unicode
                        if ch and ch in input_charset and len(username) < 16:
                            username += ch
            clock.tick(30)
        self.username = username
        return username

    def get_username(self):
        return self.username

    def show_rank_board(self, screen, width=800, height=600):
        font = pygame.font.SysFont("SimHei", 24)
        title_font = pygame.font.SysFont("SimHei", 44)
        page = 0
        page_size = 10
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw_rank_board(screen, width, height, page, page_size, font, title_font)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_DOWN:
                        page = min(page+1, (len(self.scores)-1)//page_size)
                    elif event.key == pygame.K_UP:
                        page = max(page-1, 0)
            clock.tick(30)

    def draw_rank_board(self, screen, width, height, page, page_size, font, title_font):
        scores = self.scores
        screen.fill((0,0,30))
        title = title_font.render("排行榜 (ESC返回 上下翻页)", True, (255,255,100))
        screen.blit(title, (width//2-200, 20))
        for idx in range(page*page_size, min((page+1)*page_size, len(scores))):
            entry = scores[idx]
            txt = font.render(
                f"{idx+1:2d} {entry['name']}  {entry['date']}  {entry['score']}",
                True, (255,255,255))
            screen.blit(txt, (70, 90 + (idx%page_size)*40))
        pygame.display.flip()