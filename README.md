# porn-text-detector

本项目提供基于文本内容的涉黄检测能力，包含实验管理与在线检测两个部分。下文重点说明检测队列、统计报表以及实验管理的使用方法。

## 运行与依赖

1. 安装依赖：`pip install -r requirements.txt`。
2. 启动服务：`python app.py`，默认监听 `http://localhost:5000`。
3. 环境变量：
   - `APP_DB_PATH`：自定义 SQLite 路径，默认 `app.db`。
   - `SEED_DOMAINS`：逗号分隔的种子域名列表，用于每日循环扫描。
   - `SEED_SCAN_INTERVAL`：种子域名扫描间隔（秒），默认 86400，可在本地调试时缩短。

## 检测队列与进度

- 在首页填写 URL 列表与选择模型，点击“加入队列”即可提交批量检测任务。
- 后台线程会持续拉取队列，将状态从 `pending` → `in_progress` → `completed`；前端每 2 秒轮询进度接口并更新进度条。
- 进度接口 `/api/progress` 返回总数、已完成数、命中率（色情命中数/已完成数），便于前端渲染。
- 最近检测结果表格显示 `url`、`model`、`score` 与状态标签，可用于快速确认检测效果。
- 队列详情 `/api/queue` 提供优先级、尝试次数与状态；`/api/retry_failed` 可重试失败任务，`/api/purge_completed` 可清理历史记录。
- 事件流 `/api/events` 记录入队、完成、失败等操作，便于回溯。

## 种子域名与定时扫描

- 在“种子域名”区域配置域名（逗号分隔），后端会定时生成形如 `https://{domain}/content/{timestamp}` 的 URL 并自动入队。
- 通过 `/api/seeds` 获取当前配置，向该接口发送 POST 即可更新种子域名列表。
- 扫描周期由 `SEED_SCAN_INTERVAL` 控制，默认每日一次。循环逻辑在后台线程中完成，无需额外调度器依赖。

## 统计报表

- 访问 `/stats` 查看图表：
  - 按天检测数量与命中数量（折线图）。
  - 模型调用次数（柱状图）。
  - 域名热度与耗时分布（柱状/饼图）。
- 命中率汇总以百分比展示，所有统计均来自 `urls` 表 `completed` 状态的数据。
- 统计数据接口 `/api/stats` 支持前端或第三方 BI 拉取。

## 事件日志

- 事件流表 `events` 记录队列关键节点：`event` 字段包含 `enqueued/completed/failed`，`payload` 为 JSON 字符串。
- 可以通过 `sqlite3 app.db 'SELECT * FROM events ORDER BY id DESC LIMIT 20'` 直接查询，或在 `/reports` 页面查看最近 200 条事件。

## 实验管理

### SQLite 表概览

项目默认使用 `experiments.db` 记录实验相关数据，核心表如下：

- **datasets**：记录数据集来源与拆分方式。主要字段包括 `id`、`name`（数据集名称）、`path`（本地或远端路径）、`split`（训练/验证比例）、`created_at`。
- **experiments**：每次训练的元信息。主要字段包括 `id`、`name`（实验名称）、`status`（pending/running/succeeded/failed）、`started_at`、`finished_at`、`log_path`（日志文件位置）、`metrics_path`（训练指标输出文件）。
- **hyperparameters**：存放每个实验的超参数设置。主要字段包括 `experiment_id`（外键）、`param_name`、`param_value`，支持多条记录描述同一实验的不同参数。
- **runs**：跟踪训练过程中每个 epoch 或 checkpoint。主要字段包括 `experiment_id`、`epoch`、`loss`、`accuracy`、`checkpoint_path`、`created_at`。

### 在前端启动训练

1. 确保后端与前端服务已启动（通常通过 `npm run dev` 或 `docker compose up`）。
2. 打开前端页面，进入“实验管理”或“训练”模块。
3. 点击“新建实验”，填写实验名称并选择数据集。
4. 在超参数区域输入训练配置（见下节示例），确认后点击“开始训练”。前端会向后端提交任务并在 `experiments` 表生成一条新记录。

### 超参数示例

在新建实验时，可参考以下常用配置：

- 学习率：`1e-4`
- 批大小：`32`
- 最大序列长度：`256`
- 训练轮数：`5`
- 优化器：`adamw`
- 预训练模型：`bert-base-chinese`

这些参数会保存在 `hyperparameters` 表中，可在前端界面或直接查询数据库查看。

### 查看日志与实验记录

- **实时日志**：训练进行时，前端的“日志”面板会通过轮询或 WebSocket 展示 `log_path` 指向的日志文件内容，便于观察 loss/accuracy 走势。
- **训练指标**：训练结束后，`metrics_path` 中的 JSON/CSV 会被解析并展示在“指标”图表中，同时 `runs` 表记录的每个 epoch 结果可用于折线图。
- **历史实验列表**：前端的“实验记录”页面会读取 `experiments` 表，显示实验名称、状态、耗时和指标摘要；点击某一条可展开查看关联的超参数（来自 `hyperparameters` 表）和详细日志。
- **直接查询数据库**：若需要离线排查，可使用 `sqlite3 experiments.db` 并执行 `SELECT * FROM experiments;` 等命令查看原始记录。

以上流程便于统一管理训练实验、追踪超参数与日志，适用于迭代模型时的对比分析。
