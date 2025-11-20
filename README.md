# PygameHomework1

本项目为Pygame框架下的综合小游戏与排行榜系统集合。你可以通过启动器选择不同游戏、查看排行榜、体验自定义关卡，并支持分数统计与用户名登记。

## 主要文件说明

### 1. `framework.py` 用法说明

`framework.py` 提供了标准化的游戏开发接口和调度能力，实现了小游戏主循环框架、窗口生命周期、按键/鼠标/焦点分发、计分等标准功能。

**核心类及方法：**

- `GameFramework`：所有自定义游戏都应继承此类，实现 `update()` 和事件处理。
    - `run()`：初始化并打开窗口、准备游戏。
    - `loop()`：主循环，每帧分发输入及刷新界面，退出循环时返回该轮得分（`self.score`）。
    - `on_key_down(key)` / `on_key_up(key)` / `on_mouse_down(pos,btn)` / ... ：可覆写用于自定义输入事件。
    - `text_out(text, pos, size, color, font)`：便捷文本绘制，支持直接渲染中文。
    - `end()`：安全退出本轮，推荐在游戏结束条件调用。

- `MainMenu(GameFramework)`：游戏选择菜单，负责展示所有已注册小游戏名称，响应数字键切换游戏。

- `GameManager`：框架入口与主调度，注册各小游戏，负责主循环与界面切换、窗口初始化。典型用法：
  ```python
  manager = GameManager(800, 600)
  manager.register_game(YourGameClass())
  manager.run()
  manager.loop()  # 返回分数
  ```

### 2. `launcher.py` 文件作用及结构

`launcher.py` 是项目主入口，负责启动游戏框架、加载排行榜系统、管理用户名输入，注册各个小游戏和排行榜界面。

**主要流程：**
1. 创建 `ScoreManager`，初始化排行榜并输入用户名（若未登录）。
2. 创建一个 Pygame 全局窗口 screen 用于用户名的输入。
3. 注册并汇集全部游戏类（如 `snake.py` 中的贪吃蛇、`stage_eternal_night.py` 的弹幕样例等）。
4. 启动调度器，进入主循环。
5. 游戏结束后自动调用 `score_manager.append_score()` 保存本轮分数。

**简化流程示例：**
```python
if __name__=="__main__":
    game_manger = GameManager()
    score_manager = ScoreManager()
    screen = pygame.display.set_mode((600,600))
    while not score_manager.isLogined():
        score_manager.login(screen)
    game = TestGame()
    pygame.display.quit()
    game_manger.register_game(game)
    game_manger.register_game(snake.Snake())
    game_manger.register_game(ScoreBoard.ScoreBoard(score_manager))
    game_manger.register_game(stage_eternal_night.TouhouStage())
    game_manger.run()
    score_manager.append_score("", game_manger.loop())
```
> 你可根据实际需要增减游戏类及排行榜模块。

### 3. `snake.py` 文件解析

`snake.py` 实现了经典贪吃蛇小游戏，继承自 `GameFramework`，示例了如何按照框架接口实现自定义规则和界面。

**主要特性：**
- 支持方向键/WSAD控制蛇移动，自动刷新。
- 吃到食物得分成长，撞到自己或边界死亡。
- 分数以 `self.score` 记录，并在游戏结束时自动返回，用于排行榜系统统计。

**基本结构：**
```python
import pygame
from framwork import GameFramework

class Snake(GameFramework):
    def __init__(self, ...):
        ...
        self.score = 0

    def run(self):
        ...

    def update(self):
        # 蛇的主循环，每帧刷新蛇身、处理输入、判断碰撞和吃食物
        ...

    def on_key_down(self, key):
        # 方向键转向
        ...
```

### 4. 其它说明

- `ScoreManager.py` 提供了用户名输入、分数保存（XML格式）、排行榜界面等功能，保证用户名、得分、时间三元分数统计可靠。
- `ScoreBoard.py` 提供排行榜窗口，继承自 `GameFramework`，可直接注册进游戏列表菜单，实现游戏界面风格一致。
- 支持添加自定义新游戏，只需继承 `GameFramework` 并注册到 `GameManager`。

---

## 如何添加自定义游戏

1. 新建文件继承 `GameFramework`。
2. 实现基本的 `update()`（游戏主逻辑）和输入处理函数。
3. 在 `launcher.py` 通过 `manager.register_game(YourGame())` 注册。

---

## 作者及联系方式

- 仓库维护：[@YuanPeixi](https://github.com/YuanPeixi)
- 使用或拓展中如有问题欢迎提issue交流。

---
## LICENSE 🧾
Any person that is not our homework team member is not allow to use the code here in any form
