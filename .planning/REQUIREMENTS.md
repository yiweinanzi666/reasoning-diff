# Requirements: Reasoning Diff

定义于 2026-09-20。以下为同事后续实现的验收需求，不是本次初始化已交付的功能。代码验证与科学验证分别记录。

## v1 Requirements
- [ ] **DATA-01**: 可导出并适配官方 iGSM，保留运算语义、DAG 和前提映射；支持 op=5/10/15/21、500 题配置及数值/改名/no-op/来源—数值变体。独立测试夹具不得冒称官方数据。
- [ ] **DATA-02**: 可适配 GSM-Symbolic/GSM-Plus、HotpotQA、MuSiQue、HumanEval，并导入独立标注、构造经核验的扰动；T4 支持策略变化/约束退化标注。缺失图真值显式 unknown。
- [ ] **DATA-03**: 基础题及全部变体共组划分，遵守测试专用限制，记录文件/记录身份和来源。
- [ ] **MEAS-01**: 按事件身份/版本/作用域对齐，保存结构变化、失败和未知；可导出与回填人工复核。
- [ ] **MEAS-02**: 同随机流编辑、配对噪声机会；分开保存任务/有限行为/噪声标签、S/M 原始量/参照/有符号差值；TO/CSP 带完整分母与覆盖率。
- [ ] **MODEL-01**: 支持冻结 Qwen3 与 Qwen2/R1 的 HF 推理，按需采集隐状态和三种边界位置；精确 token 对齐、独立随机流、断点续跑及真实 token/耗时计量。
- [ ] **PROBE-01**: 实现任务/行为双线性低秩头、带未知掩码的加权 BCE、两层边界 MLP、开发集选择与独立完整轨迹/序列校准。
- [ ] **BASE-01**: 实现监督文本、attention/rollout、零样本/少样本/反思/监督 verbalizer 对照；相同标签和划分，按可见前缀区分前瞻与回顾层级。
- [ ] **XFER-01**: 仅在维度兼容时执行冻结直接迁移；不兼容时明确 N/A，无标签配对适配与监督适配分别拟合、留出评估和报告。
- [ ] **CAUSAL-01**: 实现目标首 token 前的交换、选择性消融/INLP、救援与错误来源对照；同批次 C-rand/C-layer 并匹配实际范数。
- [ ] **CAUSAL-02**: 干预前保存来源—数值解耦 donor 和高层响应矩阵，报告目标/非目标/任务正确/无效输出及全部失败。
- [ ] **C3-01**: P1 使用留出预测、链长/op 控制与问题级区间；P2 使用 no-op 配对效果；P3 使用对照后的选择性消融恢复效果。
- [ ] **REPAIR-01**: 附录实现无门控嫁接，Oracle/预测/文本/截断/随机/提示/全重推及检索对照；以原始 token 控制预算，记录逐轮成本及离线失败类型。
- [ ] **OPS-01**: 提供准备/采集/标注/拟合/校准/干预/修复/分析 CLI、清单、配置校验、断点与分片、服务器运行说明；代码任务用隔离执行器评分。
- [ ] **QA-01**: 单元/回归及随机微型 HF CPU 集成测试不依赖真实权重或网络；全模块审查，可复现性、适用条件与未验证项有文档。
- [ ] **DECIDE-01**: Gate 0–2 默认为未预注册，实施 Week-8 分流，C3/迁移优先、C4 附录；不输出未经验证的肯定结论。

## Out of Scope
Real GPU experiments, dataset/weight downloads on this machine, RL, production gates/fallback, publication.

## Traceability
| Requirement | Phase | Status |
|---|---|---|
| DATA-01 | 1 | Pending |
| DATA-02 | 1 | Pending |
| DATA-03 | 1 | Pending |
| MEAS-01 | 1 | Pending |
| MEAS-02 | 1 | Pending |
| MODEL-01 | 2 | Pending |
| PROBE-01 | 3 | Pending |
| BASE-01 | 3 | Pending |
| XFER-01 | 3 | Pending |
| CAUSAL-01 | 4 | Pending |
| CAUSAL-02 | 4 | Pending |
| C3-01 | 5 | Pending |
| REPAIR-01 | 5 | Pending |
| OPS-01 | 6 | Pending |
| QA-01 | 6 | Pending |
| DECIDE-01 | 6 | Pending |

Coverage: 16 requirements, 16 mapped, 0 unmapped. Status only becomes Complete after implemented and verified.
