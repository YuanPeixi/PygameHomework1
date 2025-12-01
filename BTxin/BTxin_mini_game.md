# BTxin — 游戏与代码说明

此文档为 BTxin 小游戏的精简说明，面向开发者与代码维护者。包含运行方法、核心架构、主要文件/变量说明及常见开发提示。

---

## 快速运行

- 依赖：Python + Pygame
- 运行：在仓库根目录下运行游戏启动器：

```powershell
python -u "./PygameHomework1/launcher.py"
```

如果出现缺少模块错误，请先 `pip install pygame`。

---

## 概览（玩法要点）

- 玩家控制一个白色小球（蓝色为小球正方向、小球始终向正方向前进、左键点击设置方向）。
- 目标是通过多次击败 Boss，按序推进分数至 `114514`（分数序列：0 → 1 → 11 → 114 → 1145 → 11451 → 114514）。
- 玩家生命值降为 0 或达成目标都会进入倒计时，倒计时结束后调用框架的 `end()`。

---

## 代码架构要点（重要文件）

- `PygameHomework1/BTxin/BTxin_mini_game.py` — 主游戏实现（类 `su`）
    - `update()`：游戏逻辑与状态机
    - `draw()`：渲染
    - `reset()`：重置游戏状态（注意：会重置 `score_temp` 与 `reset_digit_index`）
    - `advance_score_sequence()`：按序推进 `score_temp`（在 Boss 死亡时调用）
    - 关键字段：`score_temp`, `reset_digits`, `reset_digit_index`, `death_countdown_timer`, `win_countdown_timer`

- `PygameHomework1/framwork.py` — 简单的游戏框架
    - 提供 `run()`, `loop()`, `on_key_down/on_key_up` 等事件钩子
    - `end()` 将停止当前游戏（把 `running=False`），并由 `GameManager` 聚合结果

- `PygameHomework1/launcher.py` — 启动与菜单管理（负责创建 `GameManager` 并调度游戏）

---

## 关键实现细节（供修改/排障参考）

- 分数推进：
    - 由 `reset_digits = [1,1,4,5,1,4]` 和 `reset_digit_index` 控制，函数 `advance_score_sequence()` 将把下一位连接到 `score_temp`。
    - 每次 Boss 被击败时会调用 `advance_score_sequence()`（在 `su.update()` 中触发）。

- 结束与得分回传：
    - 在死亡或胜利的倒计时结束处，代码应先 `self.score = self.score_temp`，然后调用 `self.end()`（框架的 `end()` 会使外部 loop 返回 `self.score`）。
    - 注意：不要在 `end()` 之前调用会重置分数的 `reset()`，否则返回值会被清零。

- Boss 行为：
    - 随机速度向量，定期更改方向，触边反弹。
    - 每次死亡会调用 `increase_speed()`（乘以 1.2）并增大 `wid`，且 `respawn_timer` 控制重生延迟。

- 音效与资源：
    - 重要文件在 `PygameHomework1/BTxin/`：`homo1.png` … `homo4.png`，`homo2.wav`（boss 受击），`homo.wav`（玩家死亡）。
    - 音效播放使用 `pygame.mixer.Sound.play()`，播放/停止都应包在 try/except 以防无声卡错误。

---

## 常见开发/调试流程

- 启动与观察：运行 `launcher.py` 并从菜单进入 BTxin 游戏；按 `R` 可用于某些开发版本做快速 reset（视实现而定）。
- 查看分数问题：确认 `self.score_temp` 是否被正确推进（在 Boss 死亡分支是否调用 `advance_score_sequence()`），并在结束处将 `self.score = self.score_temp` 后再调用 `end()`。
- 声音问题：若窗口关闭音效未停止，请实现 `on_quit()` 或在 `framwork.loop()` 接到 `QUIT` 时调用 `on_quit()`，并在 `su.on_quit()` 停止音效。

---

## 代码风格与约定（项目特定）

- 用 `score_temp` 保存内部分数推进，最后在结束时写回 `score` 以便 `GameManager` 收集。
- 计时器均以帧为单位（60 FPS），例如 5 秒 = `5 * 60` 帧。
- Boss 的速度使用 `base_speed * speed_multiplier` 模式；`increase_speed()` 使用乘法增长以避免线性增长过快。

---

## 对 AI 助手 / 贡献者的建议

- 变更分数或结束流程时，始终检查三个点：
    1. 分数推进点（`advance_score_sequence()` 被正确调用）
    2. 在 `end()` 之前不要重置会清除 `score` 的变量
    3. 结束时确保停止所有正在播放的音效（可在 `on_quit()` 处理）

- 如果要调整 Boss 难度，优先改 `Boss.increase_speed()` 或 `Boss.base_speed`，不要直接大幅增加 `wid` 或瞬时速度。
