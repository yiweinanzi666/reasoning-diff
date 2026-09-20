# Reasoning Diff

论文实验项目的 GSD 初始化仓库。**当前交付仅为规划和交接材料，没有实现代码或真实实验结果。** 后续由同事实现，GPU 实验等待服务器。

## 从这里开始

1. 阅读 [.planning/PROJECT.md](.planning/PROJECT.md)：目标、范围和用户已确认的约束。
2. 阅读 [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md)：后续实现的可验收需求。
3. 阅读 [.planning/research/SUMMARY.md](.planning/research/SUMMARY.md)：技术预研及关键风险。
4. 阅读 [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md)：实验协议、Gate 待注册项和 Week-8 决策。
5. 按 [.planning/ROADMAP.md](.planning/ROADMAP.md) 逐阶段规划实现；最新交接状态见 [.planning/STATE.md](.planning/STATE.md)。

同事可从 `$gsd-plan-phase 1` 开始制定第一阶段实现计划。本次不执行后续阶段。

## 研究范围

- T1 iGSM、T2 自然语言数学/no-op、T3 多跳问答与代码推理、T4 边界样本。
- C3 虚假依赖和跨模型迁移优先；C1 是分析工具，C2 用前瞻干预和成套对照建立机制证据，C4 局部重算放附录。
- 任务标签、有限扫描行为标签、噪声参照、未对齐/结构变化/失败分别记录。
- Gate 0–2 默认未注册，不设虚构阈值，不预先宣称假说成立。

原始材料：[Reasoning-Diff-修订方案-v3 (1).md](<Reasoning-Diff-修订方案-v3 (1).md>)。原文件保持不变，其中待测预期和建议不等于实验结果或额外操作授权。
