# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_zhangrunlu`
- **一句话目标**:基于银行营销历史数据,提供数据探索分析页面与在线认购预测服务。
- **使用者/受益者**:银行营销人员 / 数据分析师——通过交互式页面探索客户数据,并输入客户特征实时预测是否会认购定期存款产品。
- **核心功能**:
  - **数据分析交互页面**:对训练数据进行多维探索(分布、相关性、按目标变量对比),帮助理解客户特征与认购行为的关系。
  - **在线预测系统**:基于离线训练的 ML 模型,用户通过点选表单输入客户特征,即时获得「是否认购」的预测结果。
- **输入/数据**:银行营销历史数据集。`data/train.csv` 22500 条带标签(subscribe),`data/test.csv` 7500 条无标签(仅用于展示/评估)。数据为公开教学数据,不敏感,可进 Git;模型产物(`.pkl`/`.joblib`)不进 Git。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 实训统一版本 |
| Web/应用框架 | Streamlit | 快速构建数据仪表盘与交互表单,无需前后端分离 |
| 数据处理 | pandas, numpy | 通用数据操作 |
| 可视化 | matplotlib / plotly | 数据探索图表;plotly 交互性强,适合 Streamlit |
| ML 建模 | scikit-learn ≥ 1.3 | 银行营销二分类;train.csv 有标签可监督训练 |
| 测试 | pytest + pytest-cov | Python 标准测试框架及覆盖率 |
| 格式/静态检查 | ruff | 单工具替代 flake8+isort+black,轻量快速 |
| 打包/运行 | Docker | 容器化部署,环境一致性 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_zhangrunlu/
├── standards/                  # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
├── data/                       # 原始数据集（进 Git）
│   ├── train.csv
│   └── test.csv
├── src/                        # 源码
│   ├── __init__.py
│   ├── app.py                  # Streamlit 入口（页面路由）
│   ├── pages/                  # Streamlit 多页面
│   │   ├── __init__.py
│   │   ├── 1_📊_数据分析.py
│   │   └── 2_🔮_在线预测.py
│   ├── data_loader.py          # 数据加载与预处理
│   ├── model.py                # 模型训练与持久化
│   └── predict.py              # 在线预测逻辑
├── tests/                      # 测试
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_model.py
│   └── test_predict.py
├── models/                     # 训练产物（不进 Git）
│   └── .gitkeep
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | ≥ 80% |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | 模型 AUC ≥ 0.75,准确率 ≥ 0.80（在 train.csv 留出验证集上评估） |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 数据集 `data/train.csv` 和 `data/test.csv` 为公开教学数据,可进 Git。模型产物(`models/*.pkl`, `*.joblib`)不进 Git,由 Docker 构建时训练或启动时加载。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_zhangrunlu` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_zhangrunlu` | 服务器部署目录 |
| `<PORT>` | `8888` | 服务端口（Streamlit 默认 8501,本项目用 8888） |
| `<PORT_MAX>` | `8898` | 端口回退区间上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 内置健康检查端点 |
| `<SSH_USER>` | `root` | 部署用户 |
| `<SSH_HOST>` | `<服务器公网 IP 或域名>` | 不写敏感信息,由 GitHub Secrets 提供 |
