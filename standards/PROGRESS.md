# PROGRESS · banksys_sy_zhangrunlu 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by zhangyu)

- **阶段**:`初始化`
- **上一步完成**:已填写 `00-project-context.md`、`01-requirements.md`、`PROGRESS.md`,标准规范已就位。
- **下一步 (TODO 第一条)**:从 `main` 开 feature 分支 `feature/1-project-init`,开始 US-1 工程初始化。
- **阻塞项**:无

---

## 待办清单 (TODO,按优先级)

### 第一批: 工程初始化 + CI/CD 跑通 (US-1)

- [ ] **1.1** 建仓:用 `gh` 创建 GitHub 仓库 `banksys_sy_zhangrunlu`(开源),`main` 放最小引导提交
- [ ] **1.2** 提示人类配置 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`
- [ ] **1.3** 从 `main` 开 feature 分支 `feature/1-project-init`
- [ ] **1.4** 创建项目骨架:目录结构(见 `00-project-context.md` 第 3 节)、`.gitignore`、`requirements.txt`、`requirements-dev.txt`、`Dockerfile`、`.dockerignore`
- [ ] **1.5** 编写 `src/app.py` 最小 Streamlit 入口(首页 hello world + 健康检查)
- [ ] **1.6** 编写 CI workflow(`.github/workflows/ci.yml`):ruff format + ruff check + pytest + docker build
- [ ] **1.7** 编写 CD workflow(`.github/workflows/cd.yml`):SSH → rsync → docker build → docker run → 健康检查
- [ ] **1.8** 编写最小测试 `tests/test_app.py`(验证 Streamlit 可 import、健康检查可通过)
- [ ] **1.9** 本地自检:ruff format --check . && ruff check . && pytest --cov --cov-fail-under=80
- [ ] **1.10** push 分支 + 创建 PR;汇报 CI 状态 → 等待人工 Review 与 Merge

### 第二批: 数据模块 (US-2)

- [ ] **2.1** 实现 `src/data_loader.py`:加载 CSV、缺失值处理、特征分类、编码
- [ ] **2.2** 编写 `tests/test_data_loader.py`(覆盖加载、预处理、编码各路径)
- [ ] **2.3** 本地自检全绿 → PR → 等待合并

### 第三批: 数据分析页面 (US-3)

- [ ] **3.1** 实现 `src/pages/1_📊_数据分析.py`:概览、分布图、散点图、热力图、目标对比
- [ ] **3.2** 编写对应测试
- [ ] **3.3** 本地自检 → PR → 等待合并

### 第四批: 模型训练 + 预测 (US-4 + US-5)

- [ ] **4.1** 实现 `src/model.py`:训练、评估(AUC/准确率)、保存/加载
- [ ] **4.2** 实现 `src/predict.py`:加载模型+编码器 → 推理管道
- [ ] **4.3** 实现 `src/pages/2_🔮_在线预测.py`:交互表单 + 结果显示
- [ ] **4.4** 编写 `tests/test_model.py` 和 `tests/test_predict.py`
- [ ] **4.5** 本地自检(含模型指标门禁:AUC≥0.75, 准确率≥0.80)

### 第五批: Docker 与部署验证 (US-6)

- [ ] **5.1** 完善 `Dockerfile`(含模型训练/加载策略)
- [ ] **5.2** 本地 docker build + docker run 验证(如有 Docker)
- [ ] **5.3** 合并 main 后验证 CD 自动部署 + 健康检查

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 技术栈选 Streamlit 而非 Flask/FastAPI | 项目含数据分析仪表盘+表单,Streamlit 单页框架最适合;无需前后端分离。 |
| 2026-08-02 | 数据集进 Git,模型产物不进 Git | 数据为公开教学数据(CSV,合计约 5MB),入仓方便 CI 和复现;模型二进制文件不入仓,由 Dockerfile 内训练或挂载。 |
| 2026-08-02 | 模型文件由 Docker 构建时训练 | 保证部署产物与代码版本一一对应,避免"模型文件从哪来的"问题。 |
| 2026-08-02 | 端口使用 8888(非 Streamlit 默认 8501) | 实训要求统一端口。 |

---

## 已知坑 (GOTCHAS)

_暂无;开发中遇到故障后将在此记录。_

---

## 里程碑 (DONE)

- [x] **2026-08-02**: 项目上下文 `00-project-context.md` 填写完成
- [x] **2026-08-02**: 需求文档 `01-requirements.md` 填写完成(US-1 ~ US-6 共 6 个用户故事,含验收标准)
- [x] **2026-08-02**: `PROGRESS.md` 初始化完成(第一批 TODO 已列出)
