<div align="center">

# 🌍 智能旅行助手 Trip Planner

**基于 HelloAgents 多智能体框架的 AI 旅行规划系统**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

*输入目的地 → 多智能体协同规划 → 一键生成完整行程*

</div>

---

## ✨ 功能亮点

### 🤖 多智能体协同架构
系统采用 **4 个专业 Agent** 分工协作，各司其职：

| Agent | 职责 | 工具 |
|-------|------|------|
| 🏛️ **景点搜索 Agent** | 根据城市与偏好检索真实景点 POI | 高德地图 MCP |
| 🌤️ **天气查询 Agent** | 获取目的地多日天气预报 | 高德地图 MCP |
| 🏨 **酒店推荐 Agent** | 按住宿偏好搜索匹配酒店 | 高德地图 MCP |
| 📋 **行程规划 Agent** | 整合信息生成完整多日行程 | LLM 推理 |

### 🗺️ 高德地图 MCP 深度集成
通过 MCP（Model Context Protocol）协议接入高德地图 16+ 工具，支持：
- **景点/酒店搜索** — 获取真实 POI 数据、地址与坐标
- **天气查询** — 多日预报含温度、风力、天气状况
- **路线规划** — 步行/驾车/公共交通多模式导航
- **地理编码** — 地址与坐标双向转换

### 🖼️ 多源图片服务
集成 **Unsplash** 与 **Pexels** 双图片 API，为每个景点自动配图：
- `auto` 模式 — 优先可用源，故障自动降级备选
- `unsplash` / `pexels` — 指定单一来源
- 图片 URL 自动持久化至数据库，避免重复调用

### 📤 行程导出
- **长图导出** — 全部天数行程渲染为高清 PNG 截图
- **PDF 导出** — 自动分页生成标准 A4 格式 PDF 文件

### 🎨 玻璃拟态 UI
- 深色玻璃拟态（Glassmorphism）设计语言
- ZCOOL XiaoWei 艺术字体标题动效
- 流畅的入场动画与微交互
- 高德地图 JS API 景点标记与路线展示

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│    Vue 3 + TypeScript + Vite + Ant Design Vue + Pinia        │
│    高德地图 JS API · html2canvas · jsPDF                      │
├──────────────────────────────────────────────────────────────┤
│                      Backend API                              │
│       FastAPI + SSE 实时推送 + SQLAlchemy + Alembic           │
├──────────────────────────────────────────────────────────────┤
│                   Agent 智能体层                               │
│   HelloAgents SimpleAgent × 4 (景点/天气/酒店/规划)            │
├──────────────────────────────────────────────────────────────┤
│                     服务层                                    │
│   AmapService (MCP)  ·  ImageService (Unsplash+Pexels)       │
│   LLMService (DeepSeek / OpenAI / ...)                       │
├──────────────────────────────────────────────────────────────┤
│                    数据层                                     │
│         SQLite (开发)  /  PostgreSQL (Docker 生产)            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
trip-planner/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── agents/
│   │   │   └── trip_planner_agent.py # 多智能体旅行规划核心
│   │   ├── api/
│   │   │   ├── main.py               # FastAPI 应用入口
│   │   │   └── routes/
│   │   │       ├── trip.py           # 行程生成 (SSE 实时推送)
│   │   │       ├── trips.py          # 行程 CRUD
│   │   │       ├── map.py            # 地图/天气/路线 API
│   │   │       └── poi.py            # POI 搜索与图片获取
│   │   ├── services/
│   │   │   ├── amap_service.py       # 高德地图 MCP 服务封装
│   │   │   ├── unsplash_service.py   # 多源图片服务 (Unsplash+Pexels)
│   │   │   └── llm_service.py        # LLM 服务封装
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic 数据模型
│   │   ├── crud/                     # 数据库 CRUD 操作
│   │   ├── db/                       # 数据库连接与 ORM 模型
│   │   └── config.py                 # 应用配置管理
│   ├── .env.example                  # 环境变量模板
│   └── requirements.txt              # Python 依赖
│
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue              # 首页 — 行程表单
│   │   │   ├── Result.vue            # 结果页 — 行程详情/编辑/导出
│   │   │   └── History.vue           # 历史页 — 历史行程档案
│   │   ├── components/
│   │   │   ├── TripMap.vue           # 高德地图景点标记组件
│   │   │   ├── AppNav.vue            # 导航栏
│   │   │   └── GlassIcon.vue         # SVG 图标组件
│   │   ├── stores/                   # Pinia 状态管理
│   │   ├── services/                 # API 请求封装
│   │   ├── styles/                   # 全局样式 (Glassmorphism)
│   │   └── types/                    # TypeScript 类型定义
│   └── package.json
│
├── docker/                           # Docker 构建文件
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── nginx/                            # Nginx 反向代理配置
├── docker-compose.yml                # Docker Compose 编排
└── PRD_智能旅行助手.md                # 产品需求文档
```

---

## 🚀 快速开始

### 前提条件

- **Python** 3.10+
- **Node.js** 18+
- **高德地图 Web 服务 API Key** — [申请地址](https://lbs.amap.com/api/webservice/guide/create-project/get-key)
- **LLM API Key** — 支持 DeepSeek / OpenAI 等兼容 OpenAI 接口的服务
- （可选）**Unsplash Access Key** — [申请地址](https://unsplash.com/developers)
- （可选）**Pexels API Key** — [申请地址](https://www.pexels.com/api/)

### 方式一：本地开发

#### 1. 后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 启动后端服务
python run.py
# 或: uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

打开浏览器访问 **http://localhost:5173** 即可使用。

### 方式二：Docker 部署

```bash
# 确保已配置 backend/.env 中的 API 密钥

# 一键构建并启动所有服务
docker compose up --build -d

# 查看服务状态
docker compose ps
```

访问 **http://localhost:8080** 即可使用。

Docker 编排包含 3 个服务：

| 服务 | 说明 | 端口 |
|------|------|------|
| `postgres` | PostgreSQL 15 数据库 | 内部 5432 |
| `backend` | FastAPI + Gunicorn | 内部 8000 |
| `frontend` | Nginx 静态托管 + 反向代理 | 8080 → 80 |

---

## ⚙️ 环境变量说明

在 `backend/.env` 中配置：

```bash
# ========== 必填 ==========

# LLM 配置
LLM_MODEL_ID=deepseek-v4-flash       # 模型名称
LLM_API_KEY=your_llm_api_key         # API 密钥
LLM_BASE_URL=https://api.deepseek.com  # 服务地址

# 高德地图
AMAP_API_KEY=your_amap_api_key        # Web 服务 API Key

# ========== 可选 ==========

# 图片服务 (配置后自动启用景点配图)
UNSPLASH_ACCESS_KEY=your_key          # Unsplash
PEXELS_API_KEY=your_key               # Pexels

# 服务器
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
```

---

## 📖 使用流程

1. **填写旅行信息** — 在首页选择目的地、日期、天数、交通方式、住宿偏好与旅行风格标签
2. **AI 智能规划** — 系统自动调度 4 个 Agent 分别搜索景点、查询天气、推荐酒店，最终整合生成完整行程
3. **查看行程详情** — 包含每日景点（含配图）、餐饮安排、酒店推荐、预算明细、天气预报
4. **地图可视化** — 高德地图标记所有景点位置，直观呈现行程路线
5. **编辑与保存** — 支持在线编辑行程内容并持久化保存
6. **导出分享** — 一键导出为长图 PNG 或 PDF 文件

---

## 📡 API 文档

启动后端后访问 **http://localhost:8000/docs** 查看 Swagger UI 交互文档。

核心接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/trip/plan` | 生成旅行计划（SSE 实时推送进度） |
| `GET` | `/api/trips/` | 获取历史行程列表 |
| `GET` | `/api/trips/{id}` | 获取行程详情 |
| `PUT` | `/api/trips/{id}` | 更新行程 |
| `DELETE` | `/api/trips/{id}` | 删除行程 |
| `GET` | `/api/poi/search` | 搜索 POI |
| `GET` | `/api/poi/photo` | 获取景点图片（支持 `provider` 参数） |
| `GET` | `/api/map/poi` | 地图 POI 搜索 |
| `GET` | `/api/map/weather` | 天气查询 |
| `POST` | `/api/map/route` | 路线规划 |

---

## 🛠️ 技术栈

### 后端
- **框架**: [HelloAgents](https://github.com/jjyaoao/HelloAgents) + FastAPI
- **智能体**: HelloAgents SimpleAgent × 4
- **MCP 工具**: amap-mcp-server（高德地图 16+ 工具）
- **LLM**: 兼容 OpenAI 接口（DeepSeek / OpenAI / 其他）
- **数据库**: SQLAlchemy + SQLite（开发）/ PostgreSQL（生产）
- **图片服务**: Unsplash + Pexels 双源自动降级

### 前端
- **框架**: Vue 3 + TypeScript + Vite
- **UI 组件库**: Ant Design Vue 4
- **状态管理**: Pinia
- **地图**: 高德地图 JS API
- **导出**: html2canvas + jsPDF
- **设计**: Glassmorphism 玻璃拟态风格

### 部署
- **容器化**: Docker + Docker Compose
- **Web 服务器**: Nginx 反向代理
- **生产数据库**: PostgreSQL 15

---

## 致谢

- [HelloAgents 教程](https://github.com/datawhalechina/Hello-Agents) — Datawhale 智能体教程
- [HelloAgents 框架](https://github.com/jjyaoao/HelloAgents) — 智能体开发框架
- [高德开放平台](https://lbs.amap.com/) — 地图与位置服务
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — 高德地图 MCP 服务器
- [Unsplash](https://unsplash.com/) & [Pexels](https://www.pexels.com/) — 免费高品质图片

---

## 开源协议

本项目基于 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议开源。

---

<div align="center">

**智能旅行助手** — 让旅行计划变得简单而智能 ✈️

</div>
