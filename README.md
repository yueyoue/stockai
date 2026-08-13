# 📈 StockAI - 智能股票资讯研报分析平台

> 私有化部署的 A 股智能投研工具。全天候自动采集研报、资讯、公告，支持多用户隔离，针对自选股自动生成 AI 决策仪表盘，分时段推送标准化决策内容。

**⚠️ 免责声明：所有 AI 解读仅客观拆解信息，不构成任何投资建议。股市有风险，投资需谨慎。**

---

## ✨ 功能特性

### 📊 个股 AI 决策仪表盘

| 模块 | 功能 |
|------|------|
| 头部标识区 | 综合评分 0-100、操作信号（买入/观望/卖出）、核心结论 |
| 技术面分析 | MA5/10/20 均线、乖离率、量能、MACD、RSI、支撑压力位 |
| 仓位建议 | 持仓者/空仓者分别操作指引 |
| 交易狙击方案 | 理想买入区间、二次加仓、止损价、目标位 |
| 操作检查清单 | ✅/⚠️/❌ 自动校验全部前置条件 |
| 🏷️ 板块概念 | 所属行业板块、概念题材 |
| 👥 同行业对标 | 同板块关联个股，点击跳转分析 |
| 💰 北向资金 | 近 3 日净买入/卖出金额 |
| 🐉 龙虎榜 | 上榜记录、机构买卖方向、成交占比 |
| 📰 舆情情报 | 利好催化清单、风险警报清单、最新动态汇总 |
| 📄 关联研报 | 近期券商研报摘要 |
| 🤖 AI 完整报告 | Markdown 格式深度分析，一键复制 |

### 📈 大盘复盘仪表盘

| 模块 | 功能 |
|------|------|
| 主要指数 | 上证/深证/创业板/沪深 300 实时点位、涨跌幅 |
| 市场统计 | 涨跌家数、涨停/跌停数量 |
| 自选股看板 | 全部自选股评分/信号/涨跌汇总，点击进入个股分析 |

### 🔍 智能搜索添加自选股

- 支持**股票代码**搜索（如 `600519`）
- 支持**股票名称**搜索（如 `茅台`）
- 支持**拼音首字母**搜索（如 `GZMT`）
- 下拉列表实时匹配，点击直接添加

### 📰 数据采集与资讯

- 全网卖方研报采集（东方财富研报频道）
- 行情资讯、上市公司公告采集
- **多引擎全网搜索**：博查 / Tavily / Brave / SearXNG
- 文章全文自动抓取（bs4 解析）
- 增量采集，定时轮询

### 📄 研报/资讯详情页

- 研报详情：AI 解读全文展示
- 资讯详情：正文内容 + AI 影响解读
- 点击即可查看全文，移动端全屏适配

### 👥 多用户系统

- 注册/登录、密码修改
- 管理员可控制注册开关、禁用/启用用户
- 数据完全隔离，用户仅可见自己的数据
- **图形化管理后台**（4个标签页）

### ⚙️ 图形化系统设置

| 标签页 | 功能 |
|--------|------|
| 🤖 AI 模型 | API Key / Base URL / 模型名称配置，一键测试连接 |
| 🔍 搜索引擎 | 博查/Tavily/Brave/SearXNG 配置，每个附带详细说明 |
| 🕷️ 爬虫 | 采集间隔配置 |
| 👥 用户管理 | 用户列表、禁用/启用、重置密码 |

### 🔔 分时段自动推送（开发中）

- 08:30 开盘前决策看板
- 09:30-11:30 / 13:00-15:00 盘中增量推送
- 11:40 午盘简评
- 15:30 盘后总结

### 📱 自适应 Web 前端

- PC/手机浏览器均可访问
- Vue3 + Element Plus 现代 UI
- 响应式布局，移动端侧边栏抽屉
- 刘海屏安全区域支持

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy + APScheduler |
| 前端 | Vue3 + Element Plus + Tailwind CSS + Vite |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 行情数据 | 腾讯财经 API + 东方财富 datacenter |
| 全网搜索 | 博查 / Tavily / Brave / SearXNG |
| AI 模型 | DeepSeek / 通义千问 / Claude / OpenAI |
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

> ⚠️ **首次登录后请立即修改密码！进入「系统管理」配置 AI 模型和搜索引擎。**

---

## ⚙️ 配置说明

### 图形化配置（推荐）

登录后进入「系统管理」页面，分 4 个标签页配置：

#### 🤖 AI 模型配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| API Key | AI 模型密钥 | `sk-xxx` |
| Base URL | API 请求地址 | `https://api.deepseek.com` |
| 模型名称 | 使用的模型 | `deepseek-chat` |

支持的 AI 服务商：

| 服务商 | Base URL | 推荐模型 |
|--------|----------|----------|
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat`（推荐） |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| OpenAI | `https://api.openai.com` | `gpt-4o-mini` |
| Claude | `https://api.anthropic.com` | `claude-3-5-sonnet` |

#### 🔍 搜索引擎配置

用于全网资讯搜索，获取更丰富的新闻、研报、公告信息。

| 引擎 | 用途 | 免费额度 | 官网 |
|------|------|----------|------|
| **博查** | 国内中文搜索，A股新闻/公告/研报 | 100次/天 | [bocha.cn](https://bocha.cn) |
| **Tavily** | AI优化搜索，全球财经新闻 | 1000次/月 | [tavily.com](https://tavily.com) |
| **Brave** | 隐私搜索引擎，英文财经 | 2000次/月 | [brave.com/search/api](https://brave.com/search/api/) |
| **SearXNG** | 自建元搜索引擎，完全免费 | 无限制 | [docs.searxng.org](https://docs.searxng.org/) |

搜索引擎按优先级自动切换：博查 → Tavily → Brave → SearXNG。

### 环境变量配置

也可通过 `.env` 文件配置（图形化配置优先级更高）：

```bash
# JWT 密钥（务必修改！）
SECRET_KEY=your-s…here

# AI 模型
LLM_API_KEY=***
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

---

## 📂 项目结构

```
stockai/
├── api/                              # FastAPI 后端
│   ├── app/
│   │   ├── core/                     # 配置、数据库、安全（JWT）
│   │   ├── models/                   # SQLAlchemy 数据模型
│   │   ├── schemas/                  # Pydantic 数据验证
│   │   ├── routes/                   # API 路由
│   │   │   ├── auth.py               # 认证（注册/登录/用户管理）
│   │   │   ├── watchlist.py          # 自选股（搜索/添加/删除）
│   │   │   ├── reports.py            # 研报（列表/详情/下载）
│   │   │   ├── news.py               # 资讯（列表/详情/全文抓取）
│   │   │   ├── push.py               # 推送配置/记录
│   │   │   ├── dashboard.py          # 数据看板（个股/大盘/自选）
│   │   │   └── settings.py           # 系统设置（AI/搜索引擎/爬虫）
│   │   └── services/                 # 业务逻辑
│   │       ├── data_provider.py      # 行情数据（腾讯+东方财富）
│   │       ├── stock_analyzer.py     # 技术分析引擎
│   │       ├── stock_search.py       # 股票搜索（腾讯+新浪）
│   │       ├── search_service.py     # 全网搜索（博查/Tavily/Brave/SearXNG）
│   │       ├── llm_service.py        # 多 LLM 后端调用
│   │       └── push_service.py       # 推送服务
│   └── Dockerfile
├── crawler/                          # 数据采集服务
│   ├── sources/
│   │   ├── eastmoney.py              # 东方财富研报采集
│   │   └── news_crawler.py           # 资讯采集
│   ├── main.py                       # 采集调度
│   └── Dockerfile
├── web/                              # Vue3 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue             # 登录/注册
│   │   │   ├── Layout.vue            # 响应式布局框架
│   │   │   ├── MarketDashboard.vue   # 大盘复盘 + 自选股看板
│   │   │   ├── StockDetail.vue       # 个股 AI 决策仪表盘
│   │   │   ├── Reports.vue           # 研报中心（含详情弹窗）
│   │   │   ├── News.vue              # 市场资讯（含详情弹窗）
│   │   │   ├── Watchlist.vue         # 自选股管理（搜索添加）
│   │   │   ├── PushSettings.vue      # 推送设置
│   │   │   └── Admin.vue             # 管理后台（4标签页）
│   │   ├── router/                   # 路由
│   │   ├── stores/                   # Pinia 状态管理
│   │   └── composables/              # API 封装
│   └── Dockerfile
├── .github/workflows/                # GitHub Actions CI/CD
├── docker-compose.yml                # 预编译镜像部署
├── docker-compose.build.yml          # 本地构建部署
└── README.md
```

---

## 📡 数据源说明

| 数据 | 来源 | 备注 |
|------|------|------|
| 实时行情 | 腾讯财经 `qt.gtimg.cn` | A 股全量实时报价 |
| K 线数据 | 腾讯财经 `web.ifzq.gtimg.cn` | 日 K 线，前复权 |
| 大盘指数 | 腾讯财经 | 上证/深证/创业板/沪深 300 |
| 股票搜索 | 腾讯 + 新浪 | 代码/名称/拼音搜索 |
| 板块概念 | 东方财富 datacenter | 行业板块、概念题材 |
| 北向资金 | 东方财富 datacenter | 沪深港通资金流向 |
| 龙虎榜 | 东方财富 datacenter | 机构买卖、上榜记录 |
| 研报采集 | 东方财富研报频道 | 券商研报、行业报告 |
| 资讯采集 | 东方财富资讯频道 | 财经新闻、公司公告 |
| 全网搜索 | 博查/Tavily/Brave/SearXNG | 需配置 API Key |

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

# 2. 删除数据卷（⚠️ 此操作将删除所有数据！）
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

## 🗺️ 开发路线

### ✅ 一期（已完成）

- [x] 多用户系统（注册/登录/角色/数据隔离）
- [x] 自选股管理（搜索/添加/删除）
- [x] 实时行情数据（腾讯 API）
- [x] 技术分析引擎（MA/MACD/RSI/量能/支撑压力）
- [x] 个股 AI 决策仪表盘（12 个模块）
- [x] 大盘复盘仪表盘
- [x] 板块概念 / 同行业个股
- [x] 北向资金 / 龙虎榜数据
- [x] 舆情情报板块（利好/风险/动态）
- [x] 研报 / 资讯采集与详情展示
- [x] 多引擎全网搜索（博查/Tavily/Brave/SearXNG）
- [x] 多 LLM 后端支持
- [x] 图形化系统设置（AI/搜索引擎/爬虫/用户）
- [x] 移动端自适应布局
- [x] Docker Compose 部署
- [x] GitHub Actions CI/CD

### 🔜 二期（规划中）

- [ ] 分时段自动推送（开盘前/盘中/午盘/盘后）
- [ ] 研报 PDF 下载与解析
- [ ] 策略问股（Agent 多轮对话）
- [ ] 回测功能
- [ ] Flutter 移动端 APP
- [ ] 深色主题

---

## 📄 License

MIT License

---

## 🙏 致谢

- [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) - 参考项目
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Vue3](https://vuejs.org/) - 前端框架
- [Element Plus](https://element-plus.org/) - UI 组件库
- [腾讯财经](https://stockapp.finance.qq.com/) - 行情数据 API
- [东方财富](https://www.eastmoney.com/) - 板块/资金/龙虎榜数据
