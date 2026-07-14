# AI Q&A Chat

基于 FastAPI + Qwen 大模型的 AI 聊天应用，支持多轮对话、流式输出、RAG 知识库检索。

## 功能特性

- 🤖 **AI 对话**：接入 Qwen 大模型，支持多轮对话与 SSE 流式输出
- 📚 **知识库 (RAG)**：上传 PDF/Word 文档，自动解析并向量化，对话时基于语义检索增强回答
- 🗄️ **对话持久化**：对话记录自动保存，支持历史回看
- 📱 **响应式布局**：适配桌面端与移动端，支持侧边栏折叠

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite（本地）/ PostgreSQL（云端）
- **AI 模型**: Qwen (通过 OpenAI 兼容 API)
- **向量嵌入**: Qwen Embedding API
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
QWEN_BASE_URL=https://your-qwen-endpoint.com/compatible-mode/v1
QWEN_MODEL=qwen3-max
DATABASE_URL=sqlite:///./chat.db
```

### 4. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

打开浏览器访问 http://localhost:8000

## 一键部署到 Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/template/python)

### 手动部署步骤

1. 将代码推送到 GitHub 仓库
2. 登录 [Railway](https://railway.app)，点击 **"New Project" → "Deploy from GitHub repo"**
3. 选择你的 GitHub 仓库，Railway 会自动检测 Python 项目并安装 `requirements.txt`
4. 添加 PostgreSQL 数据库：
   - 在项目面板中点击 **"New" → "Database" → "PostgreSQL"**
   - Railway 会自动注入 `DATABASE_URL` 环境变量到你的服务中
5. 在 **Variables** 页签中设置以下环境变量：
   - `QWEN_API_KEY` — 你的 Qwen API Key
   - `QWEN_BASE_URL` — Qwen API 地址
   - `QWEN_MODEL` — 模型名称（如 `qwen3-max`）
   - `DATABASE_URL` — Railway 会自动注入 PostgreSQL 连接串，无需手动设置
6. 设置启动命令：在 **Settings** → **Start Command** 中填写：
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
7. 等待构建完成，Railway 会自动分配一个 `*.up.railway.app` 域名

### 为什么不直接用 SQLite？

Railway 和大多数云平台一样，文件系统是临时的——服务重启或重新部署后，SQLite 数据库文件会被清空。因此本项目自动检测 `DATABASE_URL`：

- 包含 `sqlite` → 本地开发模式，零配置即可运行
- 包含 `postgres` → 云端生产模式，数据持久化存储

你不需要修改任何代码，只需确保生产环境中 `DATABASE_URL` 指向 PostgreSQL 即可。
