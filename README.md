# AI Q&A Chat

基于 FastAPI + Qwen 大模型的 AI 聊天应用，支持多轮对话、流式输出。

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite（本地）/ PostgreSQL（云端）
- **AI 模型**: Qwen (通过 OpenAI 兼容 API)
- **前端**: 原生 HTML/CSS/JS，SSE 流式响应

## 本地运行

### 1. 克隆项目

```bash
git clone <你的仓库地址>
cd projectdemo
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 Qwen API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
QWEN_API_KEY=你的API_Key
QWEN_BASE_URL=你的Qwen接口地址
QWEN_MODEL=qwen3-max
DATABASE_URL=sqlite:///./chat.db
```

### 4. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

打开浏览器访问 http://localhost:8000

## 一键部署到 Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

### 手动部署步骤

1. 将代码推送到 GitHub 仓库
2. 登录 [Render](https://render.com)，点击 "New +" → "Blueprint"
3. 选择你的 GitHub 仓库，Render 会按 `render.yaml` 自动创建服务
4. 在 Web Service 的环境变量中设置：
   - `QWEN_API_KEY` — 你的 Qwen API Key
   - `QWEN_BASE_URL` — Qwen API 地址
   - `QWEN_MODEL` — 模型名称
   - `DATABASE_URL` — Render 会自动生成 PostgreSQL 连接串，无需手动设置
5. 等待部署完成，访问 Render 分配的 `.onrender.com` 域名

### 为什么不直接用 SQLite？

Render 的文件系统是临时的，重启后会清空数据。因此本项目自动检测 `DATABASE_URL`：
- 包含 `sqlite` → 本地开发模式
- 包含 `postgres` → 云端生产模式
