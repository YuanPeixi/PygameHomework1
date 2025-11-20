import pygame
from framwork import GameFramework

class ScoreBoard(GameFramework):
    def __init__(self, score_manager, width=800, height=600):
        super().__init__("排行榜", width, height)
        self.score_manager = score_manager
        self.page = 0
        self.page_size = 10

    def on_key_down(self, key):
        if key == pygame.K_ESCAPE:
            self.end()
        elif key == pygame.K_DOWN:
            self.page += 1
        elif key == pygame.K_UP:
            self.page = max(self.page-1, 0)

    def update(self):
        self.screen.fill((0,0,30))
        font = pygame.font.SysFont("SimHei", 32)
        title = font.render("排行榜 ESC返回 上下翻页", True, (255,255,0))
        self.screen.blit(title, (230, 20))
        scores = sorted(self.score_manager.get_scores(), key=lambda x:(x['game'], -x['score'], x['date']))
        for idx, entry in enumerate(scores[self.page*self.page_size:(self.page+1)*self.page_size]):
            txt = font.render(
                f"{idx+1+self.page*self.page_size:2d}. {entry['game']} | {entry['name']} | {entry['date']} | {entry['score']}",
                True, (255,255,255))
            self.screen.blit(txt, (50, 80+idx*40))
        pygame.display.flip()