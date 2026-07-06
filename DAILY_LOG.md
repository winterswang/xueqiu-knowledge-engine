
---
## 2026-06-29

## FEATURE
- (none)

## BUGFIX
- (none)

## DISCUSS
- (none)

## DECISION
- (none)

## TODO
- 审计 `2026-06-29-xueqiu-knowledge-engine.md` 等多个计划文件的状态，发现多项异常需跟进：
  - `2026-06-10-dolphin-research-distillation.md`：planning 状态，last_activity 距今 18 天，超过 8h 老化阈值，无截止日期
  - `2026-06-24-tdx-mcp-config.md`：in_progress 状态，last_activity 距今 5 天，且有 blocked task-1
  - `2026-06-26-agent-capability-hardening.md`：planning 状态，距今 3 天，blocked task（等待 TDX MCP）
  - `2026-06-26-deterministic-kpi-extraction.md`：in_progress 状态，距今 3 天，无 blocked 项但已老化
  - `2026-06-27-cron-delivery-governance.md`：planning 状态，距今约 16h，已老化
- 需进一步检查 blocked 项的具体年龄，以判断是否需要升级处理
- 需确认 `2026-06-29-xueqiu-knowledge-engine.md`（JSON 格式）是否包含 last_activity 字段

---

**说明**：本轮对话为计划状态审计/巡检操作（cron 定时检查或手动巡检），未涉及实际功能开发、bug 修复、设计讨论或技术决策。

---
## 2026-06-29

## FEATURE
- (不适用：本次对话为助手对项目计划文件的状态审查与异常评估，未涉及任何功能开发或代码变更)

## BUGFIX
- (不适用：本次对话为计划状态审查，未涉及 bug 定位或修复)

## DISCUSS
- (不适用：本次对话为助手自动巡检多个 plan 文件的状态、优先级、最后活动时间及阻塞项，输出异常清单；非开发方案讨论)

## DECISION
- (不适用：本次对话仅为状态检查，未做出任何架构或技术决策)

## TODO
- 计划 `2026-06-10-dolphin-research-distillation.md` 处于 planning 状态，last_activity 为 2026-06-11（已 18 天），无截止日期，存在老化异常
- 计划 `2026-06-24-tdx-mcp-config.md` 处于 in_progress，task-1 被阻塞，last_activity 为 2026-06-24（已 5 天），存在老化+阻塞异常
- 计划 `2026-06-26-agent-capability-hardening.md` 处于 planning，被 TDX MCP 等待阻塞，last_activity 为 2026-06-26（已 3 天），存在老化+阻塞异常
- 计划 `2026-06-26-deterministic-kpi-extraction.md` 处于 in_progress，无阻塞项，last_activity 为 2026-06-26（已 3 天），存在老化异常
- 计划 `2026-06-27-cron-delivery-governance.md` 处于 planning，last_activity 约 16 小时前，无阻塞项，存在老化异常

---
## 2026-06-30

## FEATURE
- **xueqiu-knowledge-engine Phase 1 完成**：6 个 P0 任务全部完成，包括 746 篇存量文章扫描、`batch_ingest` 实现、50 篇小批量验证（32 success）、质量校准（warnings 83→45）
- **query.py 知识查询引擎上线**：实现四层检索架构——实体直达 → 索引层 → 来源页检索 → 综合层，支持日报生成
- **Phase 2 效果验证达标**：实体识别准确率 87%、概念合理性 80%、信号正确性 90%，三项指标均超门槛，已获准进入 Phase 3（融合阶段）
- **测试日报对比分析完成**：知识引擎版采用"实体为中心"模型，对比旧版"文章为中心"，实现信号可追溯、caveats 结构化

## BUGFIX
- (none)

## DISCUSS
- (不适用：当日对话主要为 cron 管线自动执行 plan 异常扫描（按 4 条规则：P0 逾期/blocked/last_activity>8h/blocked>24h），无新的方案讨论或技术选型对话)

## DECISION
- **TDX MCP 集成方案搁置**：因 TDX MCP 来源信息未到位（已 blocked 6 天），`2026-06-24-tdx-mcp-config.md` task-1 和 `2026-06-26-agent-capability-hardening.md` task-5 持续阻塞 [?]
- **是否归档搁置的 planning 计划**：`2026-06-10-dolphin-research-distillation`（静置 19 天）和 `2026-06-27-cron-delivery-governance`（静置 2.5 天）两个 planning 状态 plan 疑似搁置，待用户决定归档或取消 [?]

## TODO
- **Phase 3 启动准备**（4 个待办任务）：
  1. 改造 crawler 输出（适配实体中心模型）
  2. 退役 `analyzer.py`
  3. 建立 cron 自动化管线
  4. 完善知识引擎文档
- **P1 逾期任务清理**：
  - `2026-06-26-deterministic-kpi-extraction.md` task-6 端到端验证（due 2026-06-28，已逾期 2 天）
  - `2026-06-27-cron-delivery-governance.md` task-4 文档化推送策略（due 2026-06-28，未开始）
  - `2026-06-26-agent-capability-hardening.md` task-6 (P2, due 2026-06-28) 和 task-7 (P2, due 2026-06-30) 未完成
- **TDX MCP 来源信息提供**（用户待办）：tdx-mcp-config 和 agent-capability-hardening 共同阻塞根因，已等 6 天
- **2026-06-30 每日工作总结文档已创建**：飞书链接 https://mcnp7tg4flek.feishu.cn/docx/EBCUdJ36Xo2Sr4xZi4fc8B2dnXc

---
## 2026-06-30

## FEATURE
- (不适用：当日对话主要为 cron 管线定期扫描 plan 异常，无新功能开发；14:01 的日报仅汇总既有成果)
- xueqiu-knowledge-engine Phase 1 完成：746 篇存量文章扫描、batch_ingest 实现、50 篇小批量验证（32 success）、query.py 四层检索引擎（实体直达→索引层→来源页检索→综合层）上线、质量校准（83→45 warnings）
- 测试日报对比分析完成：知识引擎版"实体为中心" vs 旧版"文章为中心"，信号可追溯、caveats 结构化

## BUGFIX
- (none)

## DISCUSS
- (不适用：当日对话全部为 cron 管线自动扫描执行（每隔数小时检查 4 条异常规则：P0 逾期/blocked/last_activity>8h/blocked>24h），无技术方案讨论或设计分歧)

## DECISION
- xueqiu-knowledge-engine Phase 2 效果验证达标：实体识别准确率 87%、概念合理性 80%、信号正确性 90%，三项指标均达门槛，**正式获准进入 Phase 3（融合阶段）**

## TODO
- xueqiu-knowledge-engine Phase 3 待启动 4 个任务：改造 crawler 输出、退役 analyzer.py、建立 cron、完善文档
- TDX MCP 来源信息缺失持续 6 天，阻塞 `2026-06-24-tdx-mcp-config.md` task-1 和 `2026-06-26-agent-capability-hardening.md` task-5（均带 `[!] blocked` 标记），需用户提供 TDX MCP 来源
- `2026-06-10-dolphin-research-distillation.md` 处于 planning 状态静置 19 天未推进，P0 任务（step-0/1/2）均未开始，需决定归档或取消
- `2026-06-26-deterministic-kpi-extraction.md` task-6 端到端验证（P1，due 06-28，标记 `[~]` 未完成）已逾期 2 天
- `2026-06-27-cron-delivery-governance.md` task-4 文档化推送策略（P1，due 06-28）未开始已逾期 2 天
- `2026-06-26-agent-capability-hardening.md` P2 task-6（due 06-28）和 task-7（due 06-30）未完成

---
## 2026-06-30

## FEATURE
- **xueqiu-knowledge-engine Phase 1 完成**：完成 6 个 P0 任务（746 篇存量文章扫描、batch_ingest 实现、50 篇小批量验证 32 success、query.py 四层检索引擎、质量校准从 83 warnings 降至 45）
- **Phase 2 效果验证达标**：实体识别准确率 87%、概念合理性 80%、信号正确性 90%，三项指标均达门槛
- **query.py 知识查询引擎上线**：四层检索（实体直达 → 索引层 → 来源页检索 → 综合层），支持日报生成
- **测试日报对比分析完成**：知识引擎版"实体为中心" vs 旧版"文章为中心"，信号可追溯、caveats 结构化

## BUGFIX
- (none)

## DISCUSS
- (不适用：当日对话主体为 cron 异常扫描管线的多次执行，重复检查 P0 逾期/blocked/老化指标，无实际方案设计或技术选型讨论)

## DECISION
- **xueqiu-knowledge-engine 正式获准进入 Phase 3（融合阶段）**：基于 Phase 2 三项验证指标（实体识别 87%、概念合理性 80%、信号正确性 90%）全部达门槛

## TODO
- **Phase 3 启动 4 项任务**：改造 crawler 输出、退役 analyzer.py、建立 cron 管线、完善文档
- **TDX MCP 来源信息待用户提供**（已阻塞 6 天）：阻塞 `2026-06-24-tdx-mcp-config` task-1 和 `2026-06-26-agent-capability-hardening` task-5
- **P1 逾期任务待处理**：
  - `2026-06-26-deterministic-kpi-extraction` task-6（端到端验证，`[~]` 未完成）、task-7（due 2026-06-28）
  - `2026-06-27-cron-delivery-governance` task-4（文档化推送策略，未开始）
  - `2026-06-26-agent-capability-hardening` task-6/task-7（P2，未完成）
- **搁置计划待决断**：建议归档或取消 `2026-06-10-dolphin-research-distillation`（planning 静置 19 天）和 `2026-06-27-cron-delivery-governance`（planning 静置 2-3 天）
- **xueqiu-knowledge-engine Phase 3 P0 任务待执行**：task-1.3b（pending, est: 8h, 无 due）、task-2.1（due 2026-07-14）

---
## 2026-07-01

## FEATURE
- (不适用：当日对话全部为 cron 触发的 plan 异常扫描，无功能开发)

## BUGFIX
- (不适用：当日对话全部为 cron 触发的 plan 异常扫描，无 bug 修复)

## DISCUSS
- (不适用：当日对话全部为 cron 触发的 plan 异常扫描，无设计讨论或方案分歧)

## DECISION
- (不适用：当日对话全部为 cron 触发的 plan 异常扫描，无技术决策)

## TODO
- (不适用：当日对话全部为 cron 触发的 plan 异常扫描，无新待办任务)

---

**项目状态观测（来自 cron 扫描结果，非开发事件）：**

主项目 `2026-06-29-xueqiu-knowledge-engine`（P0，in_progress）：
- Phase 0/1/2 任务均已 [x] 完成
- task-1.3b 标记为 [~] pending（设计性暂停，等用户决策 Phase 3 批量导入方案）
- 下一 P0 due 日期为 2026-07-14，target_completion 2026-07-18，目前无 P0 逾期

关键阻塞点：**TDX MCP 来源信息**——同时阻塞 `2026-06-24-tdx-mcp-config`（task-1，in_progress）和 `2026-06-26-agent-capability-hardening`（task-5，planning），已阻塞约 7 天，需用户提供来源后解除。

---
## 2026-07-01

## FEATURE
- (不适用：当日对话全部为 cron 管线自动化执行，仅扫描 plan 文件状态并发送异常通知，无任何功能开发或代码变更)

## BUGFIX
- (不适用：当日对话全部为 cron 管线自动化执行，无 bug 定位与修复工作)

## DISCUSS
- (不适用：当日对话全部为 cron 管线自动化执行 plan 状态扫描，无方案讨论、设计分歧或技术选型对话)

## DECISION
- (不适用：当日对话全部为 cron 管线自动化执行，无架构或技术决策)

## TODO
- **2026-06-24-tdx-mcp-config** plan 的 task-1 已阻塞 7 天（等用户提供 TDX MCP 来源信息），需要用户介入解除阻塞
- **2026-06-26-agent-capability-hardening** plan 的 task-5 引用了同一 TDX MCP 阻塞源（已阻塞 5 天），依赖上述来源信息
- **2026-06-10-dolphin-research-distillation** plan 处于 planning 状态 20 天无任何活动，长期停滞需决定是否推进或归档
- **2026-06-27-cron-delivery-governance** plan 老化 4 天，P1 task-4（文档化推送策略）逾期未完成，且 P0 task-2/task-3 被标记为 [~] 跳过未明确收尾
- **2026-06-29-xueqiu-knowledge-engine** plan 老化 26h，P0 task-1.3b（批量导入）处于 [~] 暂停状态，需确认是否进入 Phase 2/3（next due 2026-07-14）

---
## 2026-07-02

## FEATURE
- 创建并推进独立仓库 `/root/code/xueqiu-knowledge-engine/`，完成 Phase 0 骨架：`config/`、`raw/`、`knowledge/`、`src/` 目录，以及最小端到端知识引擎流程。
- 新增 `config/engine.yaml`，用于配置引擎参数；新增 `config/entity_dictionary.yaml`，从 morning-brief watchlist 同步生成初始实体词典，共 130 个实体。
- 新增 `src/extractor.py`，实现 LLM 提取模块，用于从雪球文章中抽取实体、概念、信号等结构化信息。
- 新增 `src/ingest.py`，实现单篇文章摄入管线：读取 `raw/*.md`，调用 `Extractor`，生成 `knowledge/sources/` 来源页，并更新 `knowledge/entities/` 实体页、`knowledge/concepts/` 概念页。
- 新增 `src/validator.py`，实现知识库数据验证层，可检查来源页、实体页、概念页的 YAML frontmatter、必填字段、信号方向等；验证结果达到 0 errors。
- 完成 5 篇测试文章端到端验证：生成来源页、实体页、概念页，并确认 LLM 提取、Markdown 写入、实体/概念更新链路可运行。
- 在 `config/engine.yaml` 增加 `ingest.min_article_length: 2000`，并在 `src/ingest.py` 中实现摄入前长度过滤；测试中 5 篇文章重新运行后，3 篇摄入、2 篇短文跳过。
- 将来源页正文预览长度配置化：在 `config/engine.yaml` 新增 `ingest.max_body_preview_length: 2000`，并调整 `src/ingest.py` 中 `SourcePageWriter` 从配置读取预览长度。
- 新增批量导入能力：实现 `batch_ingest.py`，支持断点续跑、每 50 篇自动 git commit、错误日志记录，并通过 `batch_state.json`、`batch_errors.log`、`batch_ingest.log` 跟踪状态。
- 完成 Phase 1 Task 1.1：扫描 `xueqiu-crawler` 存量数据共 1,302 篇，排除 daily reports 后 1,257 篇，按 `<2000 bytes` 过滤掉 512 篇，最终复制 746 篇文章到 `raw/`。
- 将项目推送到 GitHub：`https://github.com/winterswang/xueqiu-knowledge-engine`，包含 `src/*.py`、`config/*.yaml`、`knowledge/`、`raw/` 等内容。
- 按 SKILL.md 差距修复命名规范：将 119 个概念页重命名为 `概念_[name].md`，49 个实体页重命名为 `实体_[name].md`，并同步更新 `src/ingest.py`、`src/query.py` 的文件命名逻辑。
- 按 SKILL.md 差距补齐标签体系：来源页增加 `_structured_note`、`来源/雪球`，概念页增加 `_concept_page`、`概念`，实体页增加 `_entity_page`、`实体/[name]`，并在 `src/ingest.py` 中自动写入。
- 新增知识库索引与操作记录笔记：`knowledge/_知识库索引.md` 包含概念网络区、来源笔记区、标签云；`knowledge/_操作日志.md` 作为操作记录模板。
- 更新 Task Manager 计划文件 `~/.openclaw/workspace/plans/2026-06-29-xueqiu-knowledge-engine.md`，将项目拆分为 Phase 0 到 Phase 3，并接入 `task-manager-scan` 与 `task-manager-daily-review`。

## BUGFIX
- 修复实体重复问题：在 `src/ingest.py` 的摄入逻辑中按 `name + type` 去重，避免同一实体如“圣邦股份”重复生成。
- 修复实体页重复写入问题：调整 `src/ingest.py` 中实体页更新逻辑，仅更新 frontmatter/时间线相关内容，避免重复追加实体页正文。
- 修复单篇文章 JSON 解析失败会阻断流程的问题：在 `src/extractor.py` / `src/ingest.py` 流程中将解析失败文章记录为质量评分 0，不阻断其他文章摄入。
- 修复 `src/ingest.py` 中 `SourcePageWriter.write()` 硬编码 `article['body'][:2000]` 的问题，改为读取 `config/engine.yaml` 中的 `ingest.max_body_preview_length`。
- 修复 `src/ingest.py` 中 `ConceptPageWriter.update()` 在概念页 frontmatter 损坏或缺失时可能丢失 body 的问题；现在找不到 `---` 边界时会保留原文内容。
- 修复概念标签错误问题 [?]：提交 `2e44ea7 fix: correct concept tags`，用于修正 `knowledge/concepts/` 相关标签。
- 修复 SKILL.md 命名与标签差距：提交 `16886cb fix: SKILL.md gap - naming convention + tags + index notes`，统一实体页、概念页命名和标签写入规则。

## DISCUSS
- 讨论并比较 SQLite 与 Markdown 的关系方案：SQLite 为源、Markdown 为源实时同步、双写、SQLite 只读定期重建；最终倾向 Markdown 为唯一真相源，SQLite 作为只读索引。
- 讨论知识引擎独立验证策略：不直接改造 `xueqiu-crawler`，不立即迁移 `analyzer.py`，先新建独立 `xueqiu-knowledge-engine` 工具，通过批量导入历史文章验证效果，达标后再考虑融合。
- 讨论日报优化方向，并形成文档 `~/.openclaw/workspace/xueqiu-daily-report-optimization.md`：用主题热力图替代“相关股票”，用产业链关联替代“今日操作参考”，新增矛盾信号和知识积累模块。
- 基于最近 7 天 164 篇文章长度分布，讨论短文对知识引擎的噪声影响；结论是 `<2000 bytes` 的快评/标题式文章提取价值低，建议摄入前过滤。
- Code Review 讨论了 `src/ingest.py`、`src/extractor.py`、`src/validator.py` 的中等级问题：来源页正文截断硬编码、概念页 YAML 损坏时 body 丢失、无变化仍 git commit、prompt f-string 双重转义可读性差。
- 诊断批量导入卡住问题：确认 API Key 和 OpenAI client 正常，但 `src/ingest.py` 第一篇长文章 `248257171.md` 的 LLM 调用无响应；讨论备选方案包括小批量验证、增加 timeout/retry、长文章分片处理。

## DECISION
- 决定 Markdown 是知识库唯一真相源，SQLite 仅作为只读索引视图；索引通过 `rebuild_index.py` / `src/indexer.py` 从 `knowledge/` 下 Markdown 定期重建。
- 决定 SQLite 重建触发时机为：每日 ingest 完成后自动重建、手动触发、索引损坏时自动检测并重建；不采用实时同步或双写。
- 决定采用独立验证路线：Phase 0 搭建独立工具，Phase 1 批量导入历史文章，Phase 2 生成测试日报并与现有 `analyzer.py` 对比，Phase 3 才考虑与 `xueqiu-crawler` 融合。
- 决定首轮批量导入范围为最近 3 个月历史文章，经过长度过滤后实际进入 `raw/` 的文章数为 746 篇。
- 决定批量导入默认 batch 大小为 50 篇，并在 `batch_ingest.py` 中实现每 50 篇自动 git commit。
- 决定摄入过滤阈值为 `ingest.min_article_length: 2000`，用于跳过短文、快评和纯标题式内容，降低概念页与实体页噪声。
- 决定实体页和概念页文件命名遵循 SKILL.md：实体页使用 `实体_[name].md`，概念页使用 `概念_[name].md`。
- 决定知识页标签体系：来源页写 `_structured_note` 与 `来源/雪球`，概念页写 `_concept_page` 与 `概念`，实体页写 `_entity_page` 与 `实体/[name]`。

## TODO
- 修复批量导入卡住问题：为 `src/extractor.py` / `src/ingest.py` 的 LLM 调用增加 timeout、重试和失败跳过机制，避免长文章或模型负载导致 `batch_ingest.py` 阻塞。
- 对超长文章实现分片处理：例如对超过 10KB 的文章在 `src/ingest.py` 或 `src/extractor.py` 中分段提取，再合并实体、概念和信号。
- 继续运行 Phase 1 Task 1.3：恢复或重启 `batch_ingest.py`，完成 746 篇历史文章的批量摄入，并监控 `batch_state.json`、`batch_errors.log`、`batch_ingest.log`。
- 执行 Phase 1 Task 1.4：从批量导入结果中抽样 20 篇来源页进行人工质量 review，校准 LLM prompt、实体词典和概念粒度。
- 修复 Code Review 剩余 Medium：在 `src/ingest.py` 的 `git_commit()` 前检查 staged changes，避免无变化时仍尝试提交。
- 修复 Code Review 剩余 Medium：重构 `src/extractor.py` 中 `_build_prompt()` 的 f-string 双重转义，将 prompt 模板提取为常量或改用 `.format()`。
- 修复 Double Check 发现的问题：概念页 body 与 frontmatter 的关联实体不同步，且 119 个概念页存在重复 H1；需调整 `src/ingest.py` 中 `ConceptPageWriter.update()` 的写入逻辑。
- 修复 `src/extractor.py` 中 `ExtractedEntity.verified` 默认值风险：将默认值从 `True` 改为 `False`，避免未来直接构造对象时未验证实体被误标为 verified。
- 统一 `config/entity_dictionary.yaml` 格式：补齐 `status`、`aliases` 等字段，并考虑增加 schema 校验。
- 完善 `README.md`：补充项目说明、安装方法、运行命令、目录结构、Phase 0/Phase 1 使用示例和架构说明。
- 为 `config/engine.yaml` 增加 `llm.max_retries`、`llm.retry_delay`、`log_level` 等配置，并在 `src/extractor.py` 中使用。
- 改进 `src/validator.py` 中 `_name_similarity()` 的概念相似度算法，考虑引入 jieba 分词或词袋方法，降低中文概念相似度误判。
- Phase 2 需要实现或完善 `src/query.py`，基于知识图谱生成测试日报，并与现有 `analyzer.py` 产出的日报进行对比。
- 实现矛盾信号检测能力：识别不同文章中对同一实体/概念的看多、谨慎、看空等分歧点。
- 继续补齐 SKILL.md 剩余差距：数据空间从本地文件到 ima KB 的适配、Layer 0 直达、batch-ingest 主题分组/优先级队列、lint 覆盖 8 类检查、`content-export`、`autoresearch`。

---
## 2026-07-02

## FEATURE
- 创建独立仓库 `/root/code/xueqiu-knowledge-engine/`，完成基础目录结构：`raw/`、`knowledge/`、`src/`、`config/`，并初始化 Git 仓库。
- 新增 `config/engine.yaml` 作为知识引擎配置文件，后续加入 `ingest.min_article_length`、`ingest.max_body_preview_length` 等配置项。
- 新增 `config/entity_dictionary.yaml`，从 morning-brief watchlist 同步生成初始实体词典，共 130 个实体。
- 新增 `src/extractor.py`，实现 LLM 提取模块，用于从雪球文章中提取实体、概念、信号等结构化信息。
- 新增 `src/ingest.py`，实现单篇文章摄入管线：读取 `raw/` 文章，调用 `Extractor`，生成 `knowledge/sources/` 来源页，并更新 `knowledge/entities/` 实体页与 `knowledge/concepts/` 概念页。
- 新增 `src/validator.py`，实现知识库数据验证层，检查来源页、实体页、概念页 YAML frontmatter 与字段合法性；Phase 0 验证结果为 0 errors。
- 完成 Phase 0 端到端验证：最初 5/5 篇文章成功摄入，生成 5 个来源页、16 个实体页、11 个概念页；后续加入长度过滤后，5 篇测试文章中 3 篇摄入、2 篇短文跳过。
- 在 `config/engine.yaml` 中新增文章长度过滤配置 `ingest.min_article_length: 2000`，`src/ingest.py` 摄入前跳过小于 2000 bytes 的短文，降低低价值快评/标题帖对知识库的污染。
- 新增批量导入能力 `batch_ingest.py`，支持断点续跑、每 50 篇自动 Git commit、错误日志记录，并通过 `batch_state.json`、`batch_errors.log`、`batch_ingest.log` 跟踪进度。
- 完成历史文章扫描与复制：从 `xueqiu-crawler` 扫描 1,302 篇文章，排除 daily reports 后剩 1,257 篇，过滤 `<2000 bytes` 短文 512 篇，最终复制 746 篇到 `raw/`。
- 将项目推送到 GitHub：`https://github.com/winterswang/xueqiu-knowledge-engine`，包含 `config/`、`src/`、`knowledge/`、`raw/` 等内容。
- 根据 `SKILL.md` 差距修复，统一知识页命名规范：概念页改为 `knowledge/concepts/概念_[name].md`，实体页改为 `knowledge/entities/实体_[name].md`。
- 根据 `SKILL.md` 差距修复，更新 `src/ingest.py`、`src/query.py` 以适配新的实体页/概念页命名模式。
- 根据 `SKILL.md` 差距修复，完善标签体系：来源页增加 `_structured_note` 与 `来源/雪球`，概念页增加 `_concept_page` 与 `概念`，实体页增加 `_entity_page` 与 `实体/[name]`。
- 新增索引笔记 `knowledge/_知识库索引.md`，包含概念网络区、来源笔记区与标签云。
- 新增操作日志模板 `knowledge/_操作日志.md`，用于记录知识库维护操作。
- 保存日报优化方案文档到 `~/.openclaw/workspace/xueqiu-daily-report-optimization.md`，提出用主题热力图、产业链关联、矛盾信号、知识积累替代原有低密度日报结构。

## BUGFIX
- 修复 `src/ingest.py` 中实体重复问题：摄入结果按 `name + type` 去重，避免如“圣邦股份”重复生成实体记录。
- 修复 `src/ingest.py` 中实体页重复写入问题：实体页更新时只更新 frontmatter/时间线相关内容，避免重复追加整页内容。
- 修复单篇摄入中的 JSON 解析失败处理：LLM 返回解析失败时将质量评分置为 0，并记录失败，不阻断其他文章摄入。
- 修复 Code Review M1：`src/ingest.py` 的 `SourcePageWriter.write()` 不再硬编码 `article['body'][:2000]`，改为从 `config/engine.yaml` 的 `ingest.max_body_preview_length` 读取正文预览长度。
- 修复 Code Review M2：`src/ingest.py` 的 `ConceptPageWriter.update()` 在概念页 frontmatter 缺失或损坏时保留原始 body 内容，避免 YAML 异常导致正文被清空。
- 修复概念标签问题 [?]：提交 `2e44ea7 fix: correct concept tags` 后，远程仓库概念页标签已校正。
- 修复 `SKILL.md` 命名/标签差距：提交 `16886cb fix: SKILL.md gap - naming convention + tags + index notes`，涉及 169 个文件，完成实体页、概念页重命名与标签补齐。

## DISCUSS
- 讨论 SQLite 在知识引擎中的角色，对比 “SQLite 为源”、“Markdown 为源 + 实时同步”、“双写”、“SQLite 只读重建” 四种方案，并倾向选择 SQLite 只读索引、Markdown 作为唯一真相源。
- 讨论知识引擎验证策略，明确先不改造 `xueqiu-crawler`，不迁移 `analyzer.py`，而是新建独立 `xueqiu-knowledge-engine` 工具，先通过历史文章批量导入验证效果。
- 讨论 Phase 0 到 Phase 3 实施路径：Phase 0 独立工具搭建，Phase 1 批量导入历史文章，Phase 2 生成测试日报并评估，Phase 3 再考虑与现有系统融合。
- 分析最近 7 天 164 篇文章长度分布，发现 64.6% 小于 5,000 bytes、25.6% 小于 2,000 bytes，讨论短文对 LLM 成本、概念污染、实体时间线噪声的影响。
- 讨论 ingest 前文章长度过滤阈值，比较无过滤、`>=1000 bytes`、`>=2000 bytes`、`>=5000 bytes` 的保留比例和质量影响，建议采用 `>=2000 bytes`。
- 针对批量导入卡在第一篇文章 `248257171.md` 的问题进行诊断，判断 `batch_ingest.py` 初始化、API Key、OpenAI client 正常，问题集中在 `src/ingest.py` 单篇文章 LLM 调用无响应，并讨论 timeout、重试、长文分片、小批量导入等方案。
- 进行 Code Review，识别 `src/ingest.py`、`src/extractor.py`、`src/validator.py`、`config/entity_dictionary.yaml`、`README.md` 中的 Medium/Minor 问题，并建议 Phase 1 前优先修复 M1-M4。
- 对 `SKILL.md` 差距进行复盘，确认当前仍存在本地文件 vs ima KB 数据空间差异、矛盾检测缺失、Layer 0 直达不足、batch-ingest 优先级不足等架构/能力差距。

## DECISION
- 决定采用 “Markdown 为唯一真相源，SQLite 只读、定期重建” 的索引架构；SQLite 不作为主存储，不做双写事务。
- 决定 SQLite 重建触发时机为：每天 ingest 完成后自动重建、手动触发、索引损坏时自动检测并重建。
- 决定当前阶段不改造 `xueqiu-crawler`，不迁移 `analyzer.py`，而是先独立建设 `/root/code/xueqiu-knowledge-engine/` 并用历史文章验证知识引擎效果。
- 决定 Phase 1 历史文章范围按最近 3 个月约 500-1000 篇执行，实际扫描后导入候选为 746 篇。
- 决定批量导入默认 batch size 为 50 篇，并在 `batch_ingest.py` 中实现每 50 篇自动 Git commit。
- 决定 `config/engine.yaml` 中设置 `ingest.min_article_length: 2000`，默认跳过小于 2000 bytes 的文章。
- 决定 Phase 0 全部完成后，Phase 1 进入批量导入历史文章阶段，任务包括扫描复制、实现 `batch_ingest.py`、运行批量导入、质量 review 与校准。
- 决定按 `SKILL.md` 规范调整知识页命名：概念页使用 `概念_[name].md`，实体页使用 `实体_[name].md`。
- 决定知识页标签规范：来源页使用 `_structured_note`/`来源/雪球`，概念页使用 `_concept_page`/`概念`，实体页使用 `_entity_page`/`实体/[name]`。

## TODO
- 继续 Phase 1 task-1.3：恢复并完成 `batch_ingest.py` 对 746 篇历史文章的批量导入，目前曾出现第一篇 `248257171.md` 在 LLM 调用处卡住的问题。
- 为 `src/extractor.py` 或底层 OpenAI client 调用增加 timeout 配置，例如 60 秒超时，避免单篇文章 LLM 调用无限卡住。
- 为 LLM 调用增加重试策略，在 `config/engine.yaml` 中补充类似 `llm.max_retries`、`llm.retry_delay` 的配置。
- 对超过 10KB 或更长的文章实现分片处理，避免长文导致 `src/ingest.py` 单篇摄入超时。
- 执行 Phase 1 task-1.4：批量导入后随机抽样 20 篇来源页进行人工质量 review，校准 LLM prompt 与实体词典。
- 修复 Code Review M3：`src/ingest.py` 的 `pipeline.git_commit()` 应在提交前检查是否有 staged changes，避免全部跳过时仍尝试 commit。
- 修复 Code Review M4：`src/extractor.py` 的 `_build_prompt()` 中 f-string 双重转义可读性差，建议提取 prompt 模板为常量或改用 `.format()`。
- 完善 `README.md`，补充项目说明、安装方式、使用指南、目录结构与架构说明。
- 统一 `config/entity_dictionary.yaml` 字段格式，确保 `status`、`aliases` 等字段一致，并考虑加入 schema 验证。
- 将 `src/extractor.py` 中 `ExtractedEntity.type` 字段重命名为 `entity_type`，避免与 Python 内置 `type` 冲突。
- 改进 `src/validator.py` 的 `_name_similarity()`，当前字符集合交集算法较粗糙，后续可引入 `jieba` 分词或词袋相似度。
- 修复已确认但尚未完成的问题：`knowledge/concepts/*.md` 概念页 body 与 frontmatter 不同步，并存在重复 H1 标题。
- 修复已确认但尚未完成的问题：`src/extractor.py` 中 `ExtractedEntity.verified` 默认值应从 `True` 改为 `False`，避免未来直接构造实体时误标为已验证。
- 统一时区处理：`src/ingest.py` 与 `src/query.py` 在 UTC 容器环境下可能出现日期错位，应显式使用同一时区。
- 实现 SQLite 索引重建工具，例如 `src/indexer.py` 或 `rebuild_index.py`，从 `knowledge/` Markdown frontmatter 批量重建 SQLite 只读索引。
- 补齐 `SKILL.md` 剩余差距：矛盾检测、Layer 0 优先直达、batch-ingest 主题分组/优先级队列、lint 完整度、content-export、autoresearch。
- 后续 Phase 2 需要实现基于知识图谱查询生成测试日报，并与现有 `analyzer.py` 日报进行对比评估。

---
## 2026-07-02

## FEATURE
- 创建并初始化独立仓库 `/root/code/xueqiu-knowledge-engine/`，包含 `raw/`、`knowledge/`、`src/`、`config/` 等目录，并推送到 GitHub：`https://github.com/winterswang/xueqiu-knowledge-engine`。
- 新增 `config/engine.yaml` 作为引擎配置文件，包含 LLM、ingest 等配置项；新增 `config/entity_dictionary.yaml`，从 morning-brief watchlist 同步生成 130 个初始实体。
- 实现 LLM 抽取模块 `src/extractor.py`，包含 `Extractor._build_prompt()` 等逻辑，用于从雪球文章中抽取实体、概念、信号和质量评分。
- 实现单篇摄入管线 `src/ingest.py`，包括 `SourcePageWriter.write()`、`EntityPageWriter.update()`、`ConceptPageWriter.update()` 等逻辑，可生成来源页、实体页、概念页 Markdown，并更新知识图谱。
- 完成 Phase 0 端到端验证：5 篇测试文章成功跑通摄入流程，生成 `knowledge/sources/`、`knowledge/entities/`、`knowledge/concepts/` 下的知识页；后续加入长度过滤后实际保留 3 篇、跳过 2 篇短文。
- 新增数据验证模块 `src/validator.py`，用于检查来源页、实体页、概念页的 YAML frontmatter、必填字段、信号方向等，验证结果为 0 errors。
- 在 `config/engine.yaml` 中新增 `ingest.min_article_length: 2000`，并在 `src/ingest.py` 摄入流程中启用长度过滤，跳过 `< 2000 bytes` 的短文/快评，降低知识库噪声。
- 实现批量导入脚本 `batch_ingest.py`，支持断点续跑、每 50 篇自动 git commit、错误日志记录，并已扫描复制最近 3 个月存量文章：从 1,257 篇有效文章中过滤短文后复制 746 篇到 `raw/`。
- 完成 Task Manager 计划接管，更新计划文件 `~/.openclaw/workspace/plans/2026-06-29-xueqiu-knowledge-engine.md`，将项目状态从 `planning` 调整为 `in_progress`，并登记 Phase 0/1/2/3 任务。
- 修复 SKILL.md 差距中的命名和标签体系：将概念页统一为 `knowledge/concepts/概念_[name].md`，实体页统一为 `knowledge/entities/实体_[name].md`，并同步更新 `src/ingest.py`、`src/query.py` 的文件命名逻辑。
- 为知识页补充标签体系：来源页增加 `_structured_note`、`来源/雪球`，概念页增加 `_concept_page`、`概念`，实体页增加 `_entity_page`、`实体/[name]`，相关逻辑已写入 `src/ingest.py`。
- 新增知识库索引与操作日志模板：`knowledge/_知识库索引.md`、`knowledge/_操作日志.md`，用于概念网络、来源笔记、标签云和后续操作记录。

## BUGFIX
- 修复 `src/ingest.py` 中实体重复问题：按 `name + type` 对抽取实体去重，避免如“圣邦股份”在同一来源页中重复出现。
- 修复 `src/ingest.py` 中实体页重复写入问题：`EntityPageWriter.update()` 调整为只更新 frontmatter/时间线，避免重复追加相同内容。
- 修复单篇摄入中 LLM JSON 解析失败导致流程中断的问题：`src/extractor.py` / `src/ingest.py` 将解析失败文章标记为质量评分 0，并允许后续文章继续处理。
- 修复 Code Review M1：`src/ingest.py` 中 `SourcePageWriter.write()` 原先硬编码 `article['body'][:2000]`，已改为从 `config/engine.yaml` 的 `ingest.max_body_preview_length` 读取。
- 修复 Code Review M2：`src/ingest.py` 中 `ConceptPageWriter.update()` 在概念页 frontmatter 损坏或缺失时，改为保留原始正文 `body = content`，避免 YAML 异常时丢失概念页正文。
- 修复概念标签问题并推送提交 `2e44ea7 fix: correct concept tags`，使 `knowledge/concepts/` 下概念页标签与新标签体系保持一致。

## DISCUSS
- 讨论并形成日报优化方案，文档保存到 `~/.openclaw/workspace/xueqiu-daily-report-optimization.md`：提出用“主题热力图”替代“相关股票”、用“产业链关联”替代“今日操作参考”，并新增“矛盾信号”和“知识积累”模块。
- 讨论 SQLite 与 Markdown 的关系，比较 `SQLite 为源`、`Markdown 为源 + 实时同步`、`双写`、`SQLite 只读定期重建` 四种方案，倾向于以 Markdown 为唯一真相源，SQLite 作为可重建只读索引。
- 讨论知识引擎的独立验证策略：明确暂不改造 `xueqiu-crawler`，暂不迁移 `analyzer.py`，先新建独立 `xueqiu-knowledge-engine` 工具，通过批量导入历史文章验证效果。
- 基于最近 7 天 164 篇文章长度分布，讨论短文对知识库的污染问题，得出 `< 2000 bytes` 快评/情绪帖价值较低，建议在 `src/ingest.py` 摄入前过滤。
- 针对 `batch_ingest.py` 批量导入卡在第一篇长文 `248257171.md` 的问题，讨论了三种方案：小批量分阶段导入、在 `src/extractor.py` LLM 调用中设置 timeout/retry、对超长文章分片处理。

## DECISION
- 决定采用独立工具路线：`xueqiu-knowledge-engine` 先独立验证，不直接改造 `xueqiu-crawler`，不立即迁移 `analyzer.py`；效果达标后再进入融合阶段。
- 决定以 Markdown 作为知识库唯一真相源，SQLite 仅作为只读索引视图，未来通过类似 `src/indexer.py::rebuild()` 的方式从 `knowledge/` 下 Markdown 定期重建索引。[?]
- 决定 Phase 0 范围为仓库骨架、实体词典、`src/extractor.py`、`src/ingest.py`、`src/validator.py` 和 5 篇文章端到端验证；Phase 0 已完成。
- 决定 Phase 1 批量导入范围为最近 3 个月雪球文章，批次大小按 50 篇处理，并由 `batch_ingest.py` 支持断点续跑和批次提交。
- 决定在 `config/engine.yaml` 中使用 `ingest.min_article_length: 2000` 作为默认长度过滤阈值，批量导入时自动跳过短文。
- 决定知识页命名遵循 SKILL.md 约定：概念页使用 `概念_[name].md`，实体页使用 `实体_[name].md`，并在 `src/ingest.py`、`src/query.py` 中统一执行该规则。

## TODO
- 继续 Phase 1：运行并完成 `batch_ingest.py` 对 `raw/` 中 746 篇历史文章的批量导入，当前因第一篇长文 LLM 调用卡住而暂停。
- 在 `src/extractor.py` 或 LLM client 调用处增加 `timeout`、`max_retries`、`retry_delay` 配置，并在 `config/engine.yaml` 中补充对应配置，避免 `batch_ingest.py` 长时间卡死。
- 为超长文章增加分片处理逻辑，例如在 `src/ingest.py` 或 `src/extractor.py` 中对 `>10KB` 正文拆段抽取，降低单次 LLM 调用超时风险。
- 修复待确认 Medium 问题：`knowledge/concepts/*.md` 概念页 body 与 frontmatter 的关联实体不同步，并存在重复 H1；需调整 `src/ingest.py::ConceptPageWriter.update()` 的 Markdown 重写逻辑。
- 修复待确认 Medium 问题：`src/extractor.py` 中 `ExtractedEntity.verified` 默认值当前为 `True`，应改为 `False`，避免未来手工构造实体时误标为已验证。
- 修复 Minor 问题：`src/ingest.py` 与 `src/query.py` 的时间处理存在 UTC/CST 不一致风险，应统一时区策略。
- 优化 Code Review 剩余问题：`src/ingest.py::git_commit()` 在无 staged changes 时不应尝试提交；`src/extractor.py::_build_prompt()` 中 f-string 双重转义可读性差，建议抽出 prompt 模板常量。
- 补充 `README.md` 的项目说明、安装方式、使用命令、架构说明和数据流示例。
- 统一 `config/entity_dictionary.yaml` schema，补齐 `status`、`aliases` 等字段，并考虑在 `src/validator.py` 中增加词典格式校验。
- 改进 `src/validator.py::_name_similarity()`，当前字符集合相似度对中文概念判断较粗糙，后续可引入 jieba 分词或更可靠的语义相似度算法。
- Phase 1 完成后执行质量 review：随机抽样 20 篇 `knowledge/sources/` 来源页，人工检查实体识别、概念粒度、信号方向和跨文章关联质量。
- 后续补齐 SKILL.md 剩余差距：矛盾检测、Layer 0 直达、batch-ingest 主题分组/优先级队列、lint 覆盖完整度、content-export、autoresearch，以及本地文件与 ima KB 的数据空间差异。

---
## 2026-07-02

## FEATURE
- 创建并初始化独立仓库 `/root/code/xueqiu-knowledge-engine/`，包含 `raw/`、`knowledge/`、`src/`、`config/` 目录，并推送到 GitHub：`https://github.com/winterswang/xueqiu-knowledge-engine`。
- 新增 `config/engine.yaml`，保存知识引擎配置；新增 `config/entity_dictionary.yaml`，从 morning-brief watchlist 同步 130 个初始实体词典。
- 实现 `src/extractor.py`，通过 LLM prompt 提取文章中的实体、概念、信号、质量评分等结构化信息，核心类/函数包括 `ExtractedEntity`、`_build_prompt()`。
- 实现 `src/ingest.py` 单篇摄入管线，支持读取 `raw/*.md` 文章，生成 `knowledge/sources/` 来源页、`knowledge/entities/` 实体页、`knowledge/concepts/` 概念页，并更新实体/概念 frontmatter 与时间线；涉及 `SourcePageWriter.write()`、`EntityPageWriter`、`ConceptPageWriter.update()`、`pipeline.git_commit()`。
- 完成 Phase 0 端到端验证：5 篇测试文章成功跑通摄入流程，生成来源页、实体页和概念页；后续加入长度过滤后实际保留 3 篇有效来源页、10 个实体页、9 个概念页。
- 新增 `src/validator.py` 数据验证层，验证来源页、实体页、概念页的 YAML/frontmatter、必填字段、信号方向等，Phase 0 验证结果为 0 errors。
- 在 `config/engine.yaml` 增加 `ingest.min_article_length: 2000`，并在 `src/ingest.py` 中实现摄入前长度过滤，跳过 `< 2000 bytes` 的短文/快评，降低低价值内容污染。
- 扫描 `xueqiu-crawler` 存量数据完成 Phase 1 Task 1.1：共发现 1,302 篇文章，排除 `daily_reports` 后 1,257 篇，过滤 `< 2000 bytes` 后复制 746 篇到 `raw/`。
- 实现 `batch_ingest.py` 批量摄入脚本，支持断点续跑、每 50 篇自动 git commit、错误日志记录，状态文件包括 `batch_state.json`、`batch_errors.log`、`batch_ingest.log`。
- 完成 SKILL.md 差距修复中的命名与标签体系改造：将概念页重命名为 `knowledge/concepts/概念_[name].md`，实体页重命名为 `knowledge/entities/实体_[name].md`，并同步修改 `src/ingest.py`、`src/query.py` 的路径生成逻辑。
- 为知识库 Markdown 增加标签体系：来源页添加 `_structured_note`、`来源/雪球`；概念页添加 `_concept_page`、`概念`；实体页添加 `_entity_page`、`实体/[name]`。
- 新增索引与操作记录笔记：`knowledge/_知识库索引.md`、`knowledge/_操作日志.md`，包含概念网络区、来源笔记区、标签云与操作记录模板。
- 保存日报优化方案文档到 `~/.openclaw/workspace/xueqiu-daily-report-optimization.md`，提出用主题热力图、产业链关联、矛盾信号、知识积累替代原有低密度日报结构。

## BUGFIX
- 修复 `src/ingest.py` 中实体重复问题：按 `name + type` 去重，避免同一实体如“圣邦股份”重复生成或重复写入实体页。
- 修复实体页重复写入问题：实体页更新时仅更新 frontmatter/时间线，避免重复追加正文内容。
- 修复单篇文章 JSON 解析失败会阻断整体流程的问题：LLM 输出解析失败时将质量评分置为 0 并记录失败，不阻断其他文章摄入。
- 修复 `src/ingest.py` 的 `SourcePageWriter.write()` 中正文预览长度硬编码 `article['body'][:2000]` 的问题：新增 `config/engine.yaml` 配置项 `ingest.max_body_preview_length: 2000`，由配置控制截断长度。
- 修复 `src/ingest.py` 的 `ConceptPageWriter.update()` 在概念页 frontmatter 损坏或缺少 `---` 边界时丢失 body 的问题：找不到 frontmatter 边界时保留原全文内容。
- 修复概念标签错误问题，提交记录为 `2e44ea7 fix: correct concept tags`。[?]
- 推送 M1/M2 修复到 GitHub，提交记录为 `84e8e6d`，验证包括 Python 语法检查、3 篇文章重新摄入、`src/validator.py` 运行 0 errors/0 warnings。

## DISCUSS
- 讨论 SQLite 与 Markdown 的关系，比较了“四种方案”：SQLite 为源、Markdown 为源并实时同步、双写、SQLite 只读定期重建；结论倾向 Markdown 为唯一真相源，SQLite 仅作为可重建索引。
- 讨论知识引擎验证策略：不直接改造 `xueqiu-crawler`，不迁移 `analyzer.py`，先新建独立 `xueqiu-knowledge-engine` 工具，通过批量导入存量文章验证效果，达标后再讨论融合。
- 讨论 Phase 0 到 Phase 3 实施路径：Phase 0 独立工具搭建，Phase 1 批量导入历史文章，Phase 2 生成测试日报并评估效果，Phase 3 再考虑与现有系统融合。
- 分析最近 7 天雪球文章长度分布：164 篇中 64.6% 小于 5,000 bytes，25.6% 小于 2,000 bytes，11% 小于 500 bytes；讨论短文会造成 LLM 成本浪费、概念污染和实体时间线噪声。
- 讨论批量摄入卡住问题：定位为 `ingest.py` 单篇文章 LLM 调用在第一篇 `248257171.md` 卡住，可能与 `minimax-m3` 模型负载、文章过长或网络不稳定有关；提出小批量验证、增加 timeout/retry、长文分片三种方案。
- 进行代码审查并形成评审结论：`src/ingest.py`、`src/extractor.py`、`src/validator.py` 整体结构可用，但存在硬编码、边缘 case、无变化仍提交、prompt 可读性差、README 空壳、缺重试配置等问题。

## DECISION
- 决定采用“Markdown 为唯一真相源，SQLite 只读、定期重建”的索引策略；计划由 `rebuild_index.py` 或 `src/indexer.py` 扫描 `knowledge/` 下 Markdown frontmatter 后重建 SQLite。
- 决定将 SQLite 重建触发时机设为：每日 ingest 完成后自动重建、手动触发、索引损坏时自动检测并重建。
- 决定知识引擎先独立验证，不改造 `xueqiu-crawler`，不处理 `analyzer.py` 迁移，效果达标后再进入融合阶段。
- 决定 Phase 1 批量导入范围为最近 3 个月历史文章，目标约 500-1000 篇；实际扫描后进入 `raw/` 的文章为 746 篇。
- 决定批量导入批次大小采用每批 50 篇，并在 `batch_ingest.py` 中实现每 50 篇自动 git commit。
- 决定摄入前启用文章长度过滤，阈值为 `2000 bytes`，即 `config/engine.yaml` 中 `ingest.min_article_length: 2000`。
- 决定 Phase 0 完成后将仓库推送至 GitHub，作为后续 Phase 1/Phase 2 的基础版本。

## TODO
- 修复已确认的 Medium 问题：概念页 body 与 frontmatter 中 `entities` 不同步，以及概念页重复 H1（如 `# 安全边际` 出现两次），涉及 `src/ingest.py` 的 `ConceptPageWriter.update()`。
- 修复 `src/extractor.py` 中 `ExtractedEntity.verified` 默认值为 `True` 的风险，改为默认 `False`，避免未来直接构造未验证实体时被误标为已验证。
- 为 `src/ingest.py` / LLM 调用增加 timeout 与 retry 配置，例如在 `config/engine.yaml` 增加 `llm.max_retries`、`llm.retry_delay`、timeout 等，解决批量摄入第一篇长文卡住问题。
- 优化 `batch_ingest.py` 批量导入策略：先运行小批量 10 篇短文验证，再逐步扩大批量；对超长文章增加分片处理逻辑。
- 完成 Phase 1 Task 1.3：恢复并跑完 746 篇历史文章的 batch ingest，处理 `batch_state.json`、`batch_errors.log` 中的失败项。
- 完成 Phase 1 Task 1.4：随机抽样 20 篇来源页进行人工质量 review，校准 LLM prompt，补充 `config/entity_dictionary.yaml` 中的实体验证状态。
- 修复代码审查剩余 Medium：`src/ingest.py` 的 `pipeline.git_commit()` 应检查是否有 staged changes 后再提交；`src/extractor.py` 的 `_build_prompt()` 应将复杂 f-string 模板抽离为常量或改用 `.format()`。
- 补齐 `README.md`，增加项目说明、安装步骤、运行命令、目录结构、配置说明、批量导入流程。
- 统一 `config/entity_dictionary.yaml` 格式，补齐 `status`、`aliases` 等字段，并考虑加入 schema 校验。
- 改进 `src/validator.py` 的 `_name_similarity()`，当前字符集合交集算法较粗糙，后续可引入 `jieba` 分词或词袋模型。
- 修复 `src/query.py` 与 `src/ingest.py` 的时区不一致问题：当前在 UTC 容器中 `query.py` 使用 UTC，`ingest.py` 使用 UTC+08:00，可能导致日期错位。
- 实现 Phase 2 Task 2.1：基于知识图谱查询生成测试日报，对比现有 `analyzer.py` 产出的日报。
- 实现 Phase 2 Task 2.2：评估实体识别准确率、概念粒度、信号方向、跨文章关联质量。
- 实现 Phase 2 Task 2.3：根据效果决定进入 Phase 3 融合，或继续调整 prompt、词典、规则并重新 ingest。
- 处理 SKILL.md 剩余差距：本地文件与 ima KB 数据空间差异、矛盾检测未实现、Layer 0 直达不足、batch-ingest 无主题分组/优先级队列、lint 覆盖不完整、`content-export` 未实现、`autoresearch` 未实现。

---
## 2026-07-03

## FEATURE
- 新增 `scripts/sync_raw_to_ima.py` 脚本：将 `raw/` 目录下雪球原始文章同步到 IMA「雪球内容数据」知识库，支持 `--count N`（默认 60）和 `--dry-run` 参数，通过读取 `.ima_sync/uploaded_files.txt` 实现断点续跑（自动跳过已上传），上传成功追加记录
- 运行 `sync_raw_to_ima.py` 批量上传 60 篇雪球原始文章到 IMA 知识库，累计 359 → 419 篇，剩余 327 篇

## BUGFIX
- (none)

## DISCUSS
- 多次 cron 扫描发现 plan `2026-06-29-xueqiu-knowledge-engine` 的 `last_activity`（2026-06-30T19:40）距今已超 8h（实际 ~3 天），触发老化条件；但 Phase 0-2 已完成、Phase 3（融合）明确为「待定」，判定属计划内自然暂停，不需异常通知

## DECISION
- 将原本位于 `/tmp/upload_raw_ima.py` 的一次性临时脚本正式移入项目，保存为 `scripts/sync_raw_to_ima.py`（原脚本无断点续跑、无自动分批）

## TODO
- 继续上传剩余 327 篇雪球原始文章到 IMA 知识库，执行：`cd /root/code/xueqiu-knowledge-engine && python3 scripts/sync_raw_to_ima.py --count 60`
- [?] 在 knowledge-engine 或 xueqiu-crawler 项目下查找 IMA 相关脚本/配置（用户指引方向）

---
## 2026-07-03

## FEATURE
- 正式创建 `scripts/sync_raw_to_ima.py`（原为 `/tmp/upload_raw_ima.py` 临时脚本），用于将 `raw/` 目录下雪球原始文章同步至 IMA "雪球内容数据" 知识库
  - 支持 `--count N` 参数控制单次上传数量（默认 60）
  - 支持 `--dry-run` 预览模式
  - 实现断点续跑：自动读取 `.ima_sync/uploaded_files.txt` 跳过已上传文件
- 批量上传 60 篇原始文章至 IMA 知识库，全部成功，累计已上传 359 → **419/746 篇**

## BUGFIX
- (none)

## DISCUSS
- (none)

## DECISION
- 将临时脚本 `/tmp/upload_raw_ima.py` 正式纳入项目仓库 `scripts/sync_raw_to_ima.py`，避免临时文件丢失
- 复用 `xueqiu-analyzer-skill/src/xueqiu_analyzer/ima_kb_uploader.py` 的 `upload_file` / `list_knowledge_bases` 模块实现上传逻辑

## TODO
- 继续批量上传剩余 **327 篇** 原始文章至 IMA 知识库（执行 `python3 scripts/sync_raw_to_ima.py --count 60`）
- 用户最后追问"在 knowledge-engine 项目中找找"某文件（可能是 crawler 相关脚本），疑似 `xueqiu-crawler` 项目下的爬虫代码需要在 knowledge-engine 中定位确认（具体目标未明确）

---
---
## 2026-07-04

(无实质开发内容)

---
---
## 2026-07-05

(无实质开发内容)
