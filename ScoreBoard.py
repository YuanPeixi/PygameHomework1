import pygame
from framwork import GameFramework

class ScoreBoard(GameFramework):
    def __init__(self, score_manager, width=800, height=600):
        super().__init__("排行榜", width, height)
        self.score_manager = score_manager
        self.page = 0
        self.page_size = 10

    def on_key_down(self, key):
        total = len(self.score_manager.get_scores())
        maxpage = max(0, (total-1)//self.page_size)
        if key == pygame.K_ESCAPE:
            self.end()
        elif key == pygame.K_DOWN:
            if self.page < maxpage:
                self.page += 1
        elif key == pygame.K_UP:
            if self.page > 0:
                self.page -= 1

    def update(self):
        self.screen.fill((0,0,30))
        font = pygame.font.SysFont("SimHei", 32)
        title = font.render("排行榜 ESC返回 上下翻页", True, (255,255,0))
        self.screen.blit(title, (180, 20))
        scores = self.score_manager.get_scores()
        # 按分数逆序、时间升序排序
        scores = sorted(scores, key=lambda x:(-x['score'], x['date']))
        total = len(scores)
        for idx, entry in enumerate(scores[self.page*self.page_size:(self.page+1)*self.page_size]):
            txt = font.render(
                f"{idx+1+self.page*self.page_size:2d}. {entry['name']} | {entry['date']} | {entry['score']}",
                True, (255,255,255))
            self.screen.blit(txt, (50, 80+idx*40))
        # 页码信息
        page_str = font.render(f"第{self.page+1}页 / 共{max(1,(total-1)//self.page_size+1)}页", True, (180,220,255))
        self.screen.blit(page_str, (550, 560))
        pygame.display.flip()