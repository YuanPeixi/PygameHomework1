# PygameHomework1 — 新框架说明（针对重构后的 framwork.py）

此 README 适用于已重构、向后兼容但行为优化过的框架版本。它说明了新的 GameFramework 行为、事件扩展（ex）钩子、绘制/更新分离、统一文本输出（text_out 使用 SimHei）及迁移/兼容性检查清单和示例。

---

## 目录
- 概览
- 主要改动与设计理念
- 核心 API 与用法示例
- 子类迁移指南（兼容旧代码）
- 常见问题与故障排查
- 开发 / 测试 / 运行
- 兼容性检查清单（逐项）
- 贡献与分支/备份建议

---

## 概览
该项目提供一个轻量但工程化的 Pygame 框架，用于托管多个小游戏并统一管理得分排行榜。重构目标是：
- 把“逻辑更新”与“绘制”分离（update / draw），避免子类在 update 中阻塞或直接 flip 导致的问题；
- 丰富事件处理：新增 `*_ex` 版本（如 on_key_down_ex(event)）以接收原始 pygame Event（包含 event.unicode 等），同时保留原有 on_key_down(key) 等向后兼容接口；
- 优化文本绘制：统一 `text_out`，默认使用 SimHei（如不可用回退），并使用字体缓存减少开销；
- 保证向后兼容，提供迁移说明和检查清单，减少整合成本；
- 防止在 end() 中进行阻塞操作，使用非阻塞的“finished overlay”显示胜负并由用户按键或超时确认退出（避免 Win10+Py3.11 卡死问题）。

---

## 主要改动与设计理念

1. update() / draw() 分离
   - update(): 负责游戏逻辑（按键状态查询、物理、碰撞、状态变更等）。不应做耗时等待或调用 pygame.display.flip()。
   - draw(): 负责所有渲染（绘图、文字、UI）。不再调用 pygame.display.flip()。框架的 loop() 在每一帧统一调用 update() -> draw() -> pygame.display.flip()。

2. 事件处理增强（ex 版本）
   - 新增 on_key_down_ex(event), on_key_up_ex(event), on_mouse_down_ex(event), on_mouse_move_ex(event) 等。它们接收 pygame.Event 对象，包含 event.unicode、event.mod、event.pos 等。
   - 向后兼容：如果子类只实现 on_key_down(key)，框架仍会调用它（ex 默认实现可调用原生 on_key_down），因此旧代码继续生效。
   - 推荐使用 ex 版本以获取完整的输入信息（例如字符输入 event.unicode，或鼠标原始事件）。

3. text_out 优化
   - text_out(text, pos=(0,0), size=24, color=(255,255,255), font="SimHei")
     - 默认字体为 `SimHei`（防止中文乱码）。若系统无 SimHei，会自动回退到默认字体。
     - 内部维护字体缓存，避免每帧重新创建字体对象。
     - text_out 不负责翻转屏幕（不调用 pygame.display.flip()）。

4. end() 与非阻塞结算
   - 子类的 end() 不应做阻塞等待、sleep 或新的事件循环。
   - 建议用 `finished` 标志与 draw() 中的 overlay 方式显示胜利/失败信息，再由用户按键或超时调用真正的 `super().end()`（或框架提供的 _finalize_and_exit()）来结束本轮。
   - 这样可以避免在不同系统/解释器上出现窗口无响应问题。

---

## 核心 API 与用法示例

- 主要类（位于 framwork.py）：
  - class GameFramework:
    - run(): 初始化显示（打开窗口、设置标题等）。
    - loop(): 统一事件分发 -> update() -> draw() -> pygame.display.flip() -> tick()
    - update(): 子类重写，做逻辑更新
    - draw(): 子类重写，做渲染
    - text_out(text, pos=(0,0), size=24, color=(255,255,255), font="SimHei")
    - on_key_down(key) / on_key_down_ex(event)（ex 版本接收完整 event）
    - on_mouse_down(pos, button) / on_mouse_down_ex(event)
    - end(): 结束当前 game 的运行（通常由子类在确认后调用 super().end()）

- 注册并运行（launcher.py 示例）：
```python
from framwork import GameManager
import GuessNumber
import snake
import ScoreBoard

if __name__ == "__main__":
    manager = GameManager(800, 600)
    manager.register_game(GuessNumber.GuessNumber())
    manager.register_game(snake.Snake())
    # 注册排行榜界面（需要 ScoreManager 实例）
    # manager.register_game(ScoreBoard.ScoreBoard(score_manager))
    manager.run()
    manager.loop()
```

---

## 将已有子类迁移到新框架（推荐步骤）

1. 把所有绘制代码（以前可能在 update() 中）迁移到 draw()：
   - update() 保持只负责逻辑：物体位置、碰撞检测、输入 state 的更新（键状态、按键触发等）。
   - draw() 完成所有 blit、draw.rect、text_out 等渲染。

2. 移除子类里直接调用的 pygame.display.flip()/pygame.display.update():
   - 框架在 loop() 末尾统一调用 flip，子类无需/不应再次调用。

3. 如果子类需要字符输入（event.unicode），请实现 on_key_down_ex(self, event)：
   - ex 版本接收完整 event，可直接使用 event.unicode、event.mod、event.key 等。
   - ex 的默认实现会继续调用原先的 on_key_down(key)（如果需要兼容）。

4. 避免在 end() 中使用阻塞代码：
   - 若需要显示结算 UI，设置一个 finished 标志，并在 draw() 中绘制 overlay（倒计时、提示）。
   - 由用户按键或超时触发实际结束：调用 super().end() 停止循环且返回 self.score。

5. 文本显示改为 text_out：
   - 用法与以前类似，但无需 flip。
   - text_out 默认字体为 SimHei，如环境中没有该字体，考虑在系统中安装或修改为合适 ttf。

---

## 示例：把控制台 GuessNumber 框架化（使用本框架最佳实践）
- 已有示例文件 `GuessNumber.py`（在仓库中）展示如何保留原文案并用 text_out 渲染、用 on_key_down_ex 处理 event.unicode。

主要要点：
- 用 event.unicode 或 on_key_down_ex 获取字符输入；
- 把结算信息作为 overlay（finished 标志）显示；
- 结束时把得分写入 ScoreManager（由 GameManager.loop 返回后保存）。

---

## 常见问题与故障排查

- Q: 我按 ESC 退出后界面卡住 / 无响应
  - A: 确保你的子类没有在 end() 中做阻塞等待（time.sleep、循环等待事件等）。使用 finished 标志与非阻塞的 _finalize_and_exit()。

- Q: 中文显示乱码或找不到 SimHei
  - A: 框架尝试使用 `SimHei` 系统字体作为默认。若系统没有安装 SimHei，请安装相应字体或修改 text_out 调用时指定自己的 ttf 字体，或在 framwork.py 中改为一个可用字体名（如 "Microsoft YaHei" / 指定字体文件）。

- Q: 我需要 event.unicode（字符）但 on_key_down 里没提供
  - A: 使用 on_key_down_ex(event)，它会接收 pygame.KEYDOWN 的完整 event 对象。

- Q: 子类在 update 中绘制内容后看不到东西
  - A: 框架会在每帧统一 flip；确保没有多余的 flip 干扰，以及绘制在 draw() 中会更可靠。

---

## 兼容性检查清单（合并/重构前请一项项检查）
1. 是否在任何子类的 update() 中直接调用了 pygame.display.flip()/update()？若有，移除。
2. 是否在 end() 中做了阻塞等待或 time.sleep？若有，改为非阻塞方式（finished 标志 + overlay）。
3. 是否依赖 event.unicode / event.pos / event.mod？若是，改用 on_*_ex(event)。
4. text_out 使用是否需要更改字体名（环境无 SimHei 时）？
5. ScoreManager / ScoreBoard 是否有直接调用 flip 或在 update 中阻塞？若有，调整为 draw() 渲染并移除 flip。
6. GameManager.loop 依赖返回值的地方（launcher.append_score("", game_manager.loop())）应确认 game 返回 self.score。
7. 若某模块直接在 loop 外消费 pygame.event.get()（清空事件队列），请改回使用框架事件钩子（on_*_ex 或 on_*）。
8. 确保每个子类的 run() 调用 super().run() 来初始化窗口与状态（若需要）。

---

## 开发 / 测试 / 运行

1. 安装依赖
```bash
pip install pygame
```

2. 运行 launcher（示例）
```bash
python launcher.py
```
- 先输入用户名（ScoreManager.login），再在主菜单中选择游戏。
- 游戏结束后，GameManager.loop() 将返回本轮 self.score，交由 ScoreManager.append_score 保存为排行榜。

3. 单元测试与本地调试
- 在合并到 main 前，请在临时分支（staging）上合并并运行 launcher，重点在 Windows 10 + Python 3.11 执行胜负场景测试（避免卡死）。
- 如果要回退，请先创建备份分支或 tag（参考仓库维护策略）。

---

## 贡献与分支/备份建议
- 建议协作者通过 Fork -> Pull Request 流程提交新游戏或修改；
- 在你合并大型重构前，请创建备份分支或 tag（例如 `backup/main-YYYYMMDD-HHMM`）；
- 若要允许合作者直接 push，请仅授予信任用户“协作者”权限，并谨慎设置 branch protection。
