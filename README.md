# 📈 StockAI - 智能股票资讯研报分析平台

> 私有化部署的 Web 股票资讯工具，全天候自动采集卖方券商研报、市场行情资讯、上市公司公告。支持多用户隔离管理，针对用户自选股自动生成 AI 解读，并分时段推送标准化决策内容。

**⚠️ 免责声明：所有 AI 解读仅客观拆解信息，不构成任何投资建议。**

---

## ✨ 功能特性

- 📊 全网卖方研报采集，支持分类筛选、标题检索
- 📰 重点行情资讯、上市公司公告采集
- 👥 多用户系统，管理员可控制注册开关
- ⭐ 用户自选股模块，个股关联研报、公告、资讯
- 🤖 AI 解读：研报分析、资讯影响评估（利好/中性/利空）
- 🔔 分时段自动推送：开盘前、盘中、午盘、盘后
- 📱 自适应 Web 前端，PC/手机浏览器均可访问
- 🔐 JWT 鉴权，数据多用户隔离

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy |
| 前端 | Vue3 + Element Plus + Tailwind CSS |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 部署 | Docker Compose |
| CI/CD | GitHub Actions → GitHub Container Registry |

---

## 🚀 快速安装

### 前置要求

- Linux 服务器（推荐 Ubuntu 20.04+）
- [Docker](https://docs.docker.com/engine/install/) 已安装
- [Docker Compose](https://docs.docker.com/compose/install/) 已安装

### 方式一：使用预编译镜像（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/yueyoue/stockai.git
cd stockai

# 2. 创建数据目录
mkdir -p data/{db,redis,reports}

# 3. 启动服务
docker compose up -d

# 4. 查看运行状态
docker compose ps
```

### 方式二：本地编译构建

```bash
# 1. 克隆项目
git clone https://github.com/yueyoue/stockai.git
cd stockai

# 2. 创建数据目录
mkdir -p data/{db,redis,reports}

# 3. 本地构建并启动
docker compose -f docker-compose.build.yml up -d --build

# 4. 查看运行状态
docker compose -f docker-compose.build.yml ps
```

### 访问系统

| 服务 | 地址 |
|------|------|
| 🌐 前端界面 | `http://你的服务器IP:6688` |
| 📖 API 文档 | `http://你的服务器IP:8000/docs` |

### 默认管理员账号

| 字段 | 值 |
|------|------|
| 用户名 | `admin` |
| 密码 | `admin123` |

> ⚠️ **首次登录后请立即修改密码！**

---

## ⚙️ 配置说明

### 环境变量

在项目根目录创建 `.env` 文件：

```bash
# JWT 密钥（务必修改！）
SECRET_KEY=your-secret-key-here

# AI 模型配置（可选，用于 AI 解读功能）
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

### 支持的 AI 模型

- DeepSeek（推荐，国内访问快）
- 通义千问
- Claude
- OpenAI
- 其他兼容 OpenAI 格式的模型

---

## 📂 项目结构

```
stockai/
├── api/                          # FastAPI 后端
│   ├── app/
│   │   ├── core/                 # 配置、数据库、安全
│   │   ├── models/               # 数据模型
│   │   ├── schemas/              # 数据验证
│   │   ├── routes/               # API 路由
│   │   └── services/             # 业务逻辑
│   └── Dockerfile
├── crawler/                      # 数据采集服务
│   ├── sources/                  # 数据源采集器
│   └── Dockerfile
├── web/                          # Vue3 前端
│   ├── src/
│   └── Dockerfile
├── .github/workflows/            # GitHub Actions CI/CD
├── docker-compose.yml            # 预编译镜像部署
├── docker-compose.build.yml      # 本地构建部署
└── README.md
```

---

## 🔧 运维管理

### 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f stock-api      # API 日志
docker compose logs -f stock-crawler  # 爬虫日志
docker compose logs -f stock-web      # 前端日志

# 重启服务
docker compose restart

# 停止所有服务
docker compose down

# 停止并删除所有数据（⚠️ 慎用！）
docker compose down -v
```

### 更新升级

```bash
# 拉取最新代码
git pull

# 拉取最新镜像并重启
docker compose pull
docker compose up -d
```

### 数据备份

```bash
# 备份 PostgreSQL 数据库
docker exec stock-db pg_dump -U stockai stockai > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup_20260101.sql | docker exec -i stock-db psql -U stockai stockai
```

---

## 🗑️ 完整删除

如需完全卸载 StockAI，执行以下命令：

```bash
# 1. 停止并删除容器、网络
docker compose down

# 2. 删除数据卷（⚠️ 此操作将删除所有数据，包括数据库、缓存、研报文件！）
docker compose down -v

# 3. 删除镜像
docker rmi ghcr.io/yueyoue/stockai-api:latest
docker rmi ghcr.io/yueyoue/stockai-crawler:latest
docker rmi ghcr.io/yueyoue/stockai-web:latest

# 4. 删除项目文件夹
cd .. && rm -rf stockai

# 5. （可选）清理 Docker 未使用的资源
docker system prune -a
```

> ⚠️ **警告：删除数据卷后，所有用户数据、研报、资讯将无法恢复！请提前备份重要数据。**

---

## 📋 推送渠道配置

| 渠道 | 配置方式 |
|------|----------|
| 飞书 | 创建自定义机器人，获取 Webhook Key |
| 企业微信 | 创建群机器人，获取 Webhook Key |
| Telegram | 通过 @BotFather 创建 Bot，格式：`BotToken:ChatID` |
| 邮箱 | 需配置 SMTP 服务（开发中） |

---

## 📄 License

MIT License

---

## 🙏 致谢

- [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) - 参考项目
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Vue3](https://vuejs.org/) - 前端框架
- [Element Plus](https://element-plus.org/) - UI 组件库
