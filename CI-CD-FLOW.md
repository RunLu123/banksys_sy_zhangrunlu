# CI/CD 全流程开发指南

> 基于 `banksys_sy_zhangrunlu` 项目实战总结 · 2026-08-02

---

## 一、全景架构：三方流转

```text
┌──────────────┐      git push       ┌──────────────────┐      SSH + rsync      ┌──────────────┐
│   本机       │ ──────────────────▶  │     GitHub       │ ──────────────────▶   │   远程服务器  │
│  (Windows)   │ ◀──────────────────  │  (Actions CI/CD) │ ◀──────────────────   │  (京东云)     │
│              │      git pull        │                  │      curl health     │              │
│ 写代码+测试   │                     │  PR → CI 检查     │                     │  docker 部署  │
│ ruff + pytest│                     │  Merge → CD 部署  │                     │  对外提供服务  │
└──────────────┘                     └──────────────────┘                     └──────────────┘
```

三个角色各司其职：

| 角色 | 做什么 | 不做什么 |
|---|---|---|
| **本机** | 写代码、写测试、本地自检、push 分支 | 不直接改 main、不做部署 |
| **GitHub** | 托管代码、CI 自动检查、CD 自动部署 | 不存储密钥明文 |
| **远程服务器** | 运行 Docker 容器、对外提供服务 | 不参与开发决策 |

---

## 二、六步开发闭环

### 第 ① 步：建仓 + 配 Secrets

```text
本机: gh repo create → 仓库就绪
      ↓
      git push main（只放最小引导：README + .gitignore + standards/）
      ↓
GitHub: 仓库创建完毕
      ↓
你: 去 Settings → Secrets and variables → Actions → Repository secrets
      添加 SSH_PRIVATE_KEY / SSH_HOST / SSH_USER
```

> **关键**：Secrets 配置必须在 CD 第一次运行之前完成，否则部署必然失败。

---

### 第 ② 步：开 feature 分支

```bash
# 本机
git switch main
git pull
git switch -c feature/1-project-init    # 从 main 分叉
```

> **铁律**：日常开发绝不直接 push main。一需求一分支一 PR。

---

### 第 ③ 步：本地模块化开发

```text
本机模块开发循环：
  写代码 → 写测试 → 更新 PROGRESS.md → 汇报进度
```

本项目实际模块划分：

| 模块 | 文件 | 职责 |
|---|---|---|
| 数据层 | `src/data_loader.py` | 加载 CSV、缺失值处理、OneHot 编码、标准化 |
| 模型层 | `src/model.py` | 训练（LR vs RF 择优）、AUC/准确率评估、持久化 |
| 推理层 | `src/predict.py` | 加载模型+预处理器 → 单条推理管道 |
| 页面层 | `src/app.py` + `src/pages/` | Streamlit 多页面（数据分析 + 在线预测） |
| CI/CD | `.github/workflows/ci.yml` + `cd.yml` | 自动化检查与部署 |
| 容器 | `Dockerfile` | Python 3.11-slim → 训练模型 → 启动 Streamlit |

---

### 第 ④ 步：本地 CI 自检（AI 执行）

```bash
# 本机执行——三道门禁
ruff format --check .    # 格式检查
ruff check .             # 静态检查
pytest --cov=src         # 单元测试 + 覆盖率（≥ 80%）
```

> **本地不强制 Docker**，镜像构建交给 CI 云端 runner。

---

### 第 ⑤ 步：Push → PR → CI 复检

```text
本机:  git push origin feature/xxx
        gh pr create --base main --head feature/xxx

GitHub: PR 事件触发 CI
        → ruff format ✅
        → ruff check ✅
        → pytest + coverage ✅
        → docker build ✅
        → 全绿后 PR 可合并
```

**这一步 AI 停下，等你 Review 和 Merge。**

---

### 第 ⑥ 步：人工审核 → 合并 → CD 自动部署

```text
你:    Review 代码 → 点 Merge pull request

GitHub: main 收到 push → 触发 CD workflow
        → SSH 连接服务器（用 SSH_PRIVATE_KEY 认证）
        → rsync 同步代码到 /opt/banksys_sy_zhangrunlu/
        → docker build（换清华源加速 apt/pip、训练模型）
        → docker rm -f 旧容器（幂等）
        → docker run -d --restart unless-stopped -p 8888:8888
        → curl /_stcore/health → 200 OK ✅
```

---

## 三、git 流转全图

```text
                    GitHub
  本机              ┌─────────────────────────────┐         远程服务器
                    │                             │
  main ──push──▶   │  main (受保护，永远可部署)      │
                    │    │                        │
                    │    │ PR merge (人操作)        │
                    │    ▼                        │
  feature/xxx       │  main ←── feature/xxx       │
  │ 写代码           │    │                        │
  │ 写测试           │    │ push 触发 CD            │
  │ ruff+pytest     │    ▼                        │
  │                 │  CD workflow                │
  │                 │  ├─ SSH + rsync ──────────▶ │ /opt/banksys_sy_zhangrunlu/
  │                 │  ├─ SSH docker build ─────▶ │ docker build
  │                 │  └─ SSH docker run ───────▶ │ docker run -p 8888
  │                 │                             │
  └──push──▶        │  PR 触发 CI                  │
                    │  ├─ ruff                    │
                    │  ├─ pytest                  │
                    │  └─ docker build            │
                    │                             │
                    │  Secrets (加密存储):          │
                    │  SSH_PRIVATE_KEY ──────────▶ 用于 SSH 认证
                    │  SSH_HOST ─────────────────▶  117.72.172.21
                    │  SSH_USER ─────────────────▶  root
                    └─────────────────────────────┘
```

**流转规则**：

| 方向 | 触发方式 | 内容 |
|---|---|---|
| 本机 → GitHub | `git push` | 源代码（不含密钥、模型产物） |
| GitHub → 服务器 | SSH + rsync（CD workflow 自动） | 源代码同步 |
| 服务器内部 | `docker build` + `docker run` | 构建镜像、启动容器 |
| 外界 → 服务器 | HTTP/HTTPS | 访问 `http://117.72.172.21:8888` |

---

## 四、SSH 密钥配置（最容易卡住的一步）

### 原理

```
GitHub Actions Runner                   你的服务器
┌──────────────────┐                   ┌──────────────────┐
│ SSH_PRIVATE_KEY  │ ──── 认证 ────▶   │ authorized_keys  │
│ (GitHub Secret)  │                   │ (含对应公钥)      │
└──────────────────┘                   └──────────────────┘
```

GitHub Actions 的 runner 是**无交互终端**的，只能通过密钥认证，不能用密码。如果密钥对不匹配，CD 第一步就死。

### 正确配置流程

**在服务器上**：

```bash
# 1. 生成专用于 GitHub Actions 的密钥对
ssh-keygen -t ed25519 -f ~/.ssh/github_cd -N "" -C "github-cd"

# 2. 公钥加入授权列表
cat ~/.ssh/github_cd.pub >> ~/.ssh/authorized_keys

# 3. 打印私钥——全选复制
cat ~/.ssh/github_cd
```

**在 GitHub 上**：

去 `Settings → Secrets and variables → Actions → Repository secrets`，将私钥全文粘贴到 `SSH_PRIVATE_KEY`。

**在本机验证**：

```bash
# 用同样的私钥测试免密登录
ssh -i <私钥文件> root@117.72.172.21
# 应该直接登录，不弹密码提示
```

---

## 五、实际踩坑与解决

| # | 现象 | 根因 | 解决 |
|---|---|---|---|
| 1 | `docker build` 报 `unknown instruction: import` | Dockerfile 多行 `RUN python -c "..."` 被 BuildKit 误解析 | 抽成独立脚本 `RUN python src/train.py` |
| 2 | `pip install` 报 `index url "" seems invalid` | `ARG PIP_INDEX_URL` 在 `FROM` 前声明，构建阶段不可见 | 移到 `FROM` 之后重新声明 |
| 3 | CD 13 秒就 `Permission denied` | GitHub Secret 私钥与服务器 `authorized_keys` 不匹配 | 服务器重新生成密钥对，更新 Secret |
| 4 | `apt-get update` 下载 9 分钟（17.9 kB/s） | 京东云从 `deb.debian.org` 拉包极慢 | Dockerfile 加 `sed` 切清华 apt 源 |
| 5 | 构建超时被杀 (`Run Command Timeout`) | SSH action 默认 `command_timeout` 仅 10 分钟 | CD workflow 加 `command_timeout: 30m` |
| 6 | `pip install` 从清华 PyPI 源 SSL 错误 | Windows 下 SSL 证书问题 | 换默认 PyPI 源 |
| 7 | `git push` HTTPS 超时 | 网络代理不覆盖 git | 切 SSH remote (`git@github.com:...`) |

---

## 六、关键文件速查

| 文件 | 作用 | 在哪运行 |
|---|---|---|
| `.github/workflows/ci.yml` | PR 触发：ruff + pytest + docker build | GitHub Actions |
| `.github/workflows/cd.yml` | main push 触发：SSH → rsync → docker run → health | GitHub Actions |
| `Dockerfile` | 定义镜像：apt 源 → pip 依赖 → 训练模型 → 启动服务 | 服务器 |
| `pyproject.toml` | pytest + coverage 配置 | 本机 / CI |
| `ruff.toml` | 代码风格规则 | 本机 / CI |
| `requirements.txt` | 生产运行依赖 | Docker 构建 |
| `requirements-dev.txt` | 开发检查依赖（ruff/pytest） | 本机 / CI |
| `src/train.py` | 离线训练脚本（Dockerfile 调用） | Docker 构建 |

---

## 七、一句话总结

> **本机写代码测试 → git push 到 GitHub → PR 触发 CI 全绿 → 人点 Merge → CD 自动 SSH 到服务器 → docker build & run → 对外提供 Web 服务。**
>
> 密钥进 GitHub Secrets，代码进 Git，模型在 Docker 构建时训练。
> CI 红灯不合并，合并是人类动作，部署是自动的。
