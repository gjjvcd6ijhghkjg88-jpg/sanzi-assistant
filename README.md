# sanzi-assistant

<!-- 作用：项目总入口文档，说明三资管理智能问答助手的定位、结构、启动方式和协作规则。 -->

三资管理助手是一个面向村级经办人员的 LLM 问答系统，目标是把政策法规、工作手册、业务规范和平台操作说明转成更简明、更场景化、同时适配 PC 与移动端的问答体验。

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI + Python
- 问答能力：本地知识库检索优先，支持接入 OpenAI 兼容 LLM
- 协作方式：`main` 保护分支 + 功能分支 + Pull Request 合并

## 项目结构

```text
sanzi-assistant/
  backend/                 # FastAPI 后端服务
    app/
      api/routes/          # API 路由
      core/                # 配置与基础能力
      services/            # 问答、知识库、LLM 服务
    data/                  # 示例知识库数据
    tests/                 # 后端测试
  frontend/                # React 前端应用
    src/
      api/                 # 前端 API Client
      components/          # 页面组件
      hooks/               # 业务 Hook
      styles/              # 全局样式
  docs/                    # 架构、分支、任务拆分文档
```

## 快速启动

### 1. 后端

```powershell
cd D:\sanzi-assistant\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 2. 前端

```powershell
cd D:\sanzi-assistant\frontend
npm install
npm run dev
```

前端默认访问：

```text
http://127.0.0.1:5173
```

## LLM 配置

默认不配置 API Key 也可以运行，系统会使用本地知识库生成可演示的回答。

如需接入真实模型，在 `backend/.env` 中配置：

```env
OPENAI_API_KEY=你的_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

## 分支分工

- 成员 A：`feat/project-init`，项目管理、整体架构、main 分支管理
- 成员 B：`feat/pc-ui`，PC 端智能问答界面
- 成员 C：`feat/mobile-ui`，移动端适配
- 成员 D：`feat/knowledge-graph`，知识库整合与图谱构建

详细规范见 [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md)。

