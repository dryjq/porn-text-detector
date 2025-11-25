# 基于文本的色情网站识别教学系统

本项目提供一个可在本地运行的 Flask Web 系统，用于演示如何通过文本信息对网站内容进行色情/正常分类。系统内置 fastText、TextCNN、RoBERTa-small、ALBERT 四类模型封装，默认使用关键词规则作为占位，方便课堂实验与演示。

## 环境准备

1. 创建并激活虚拟环境（可选）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\\Scripts\\activate
   ```
2. 安装依赖（如不需要真实模型，可跳过大体量库的安装）：
   ```bash
   pip install -r requirements.txt
   ```

## 启动方式

```bash
python app.py
```

启动后访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)，使用默认账号登录：

- 用户名：`admin`
- 密码：`123456`

## 目录结构

```
├─ app.py                # Flask 入口
├─ config.py             # 配置文件
├─ models/               # 模型封装，占位实现
├─ services/             # 网页嗅探与分类服务
├─ templates/            # 前端页面
└─ static/               # 静态资源（CSS/JS/图片）
```

## 模型文件说明

- 默认使用关键词规则以保证开箱即用。
- 如果有训练好的模型，可将文件放入 `model_files/` 目录并调整 `config.py` 中的路径：
  - `FASTTEXT_MODEL_PATH`
  - `TEXTCNN_MODEL_PATH`
  - `ROBERTA_MODEL_PATH`
  - `ALBERT_MODEL_PATH`

## 训练提示

- `models/fasttext_model.py` 中提供 `train_fasttext` 示例；
- 其他模型可结合 PyTorch / transformers 的标准训练流程，完成后将权重路径配置到 `config.py`；
- 系统通过 `services/storage.py` 使用 SQLite 记录检测日志，可在 `detector_logs.db` 中查看历史记录。

## 常见问题

- 若无法联网下载大模型，可保持默认占位实现，系统仍可完成演示流程。
- 导出 CSV 按钮将下载最近一次批量/在线检测的结果，历史导出请使用“检测日志”页签的“导出全部”。
