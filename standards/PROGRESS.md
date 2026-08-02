# PROGRESS · banksys_sy_zhangrunlu 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by zhangyu)

- **阶段**:`PR 待审核`（对应六步流程第⑤步）
- **上一步完成**:US-1 ~ US-5 全部代码+测试已完成,PR #1 已发起,CI 运行中。
- **下一步 (TODO 第一条)**:**人工 Review + Merge PR #1**,合并后触发 CD 自动部署。
- **阻塞项**:等待人工审核 PR；CD 尚未验证（需合并 main 后触发）。

---

## 待办清单 (TODO,按优先级)

### 第一批: 工程初始化 + CI/CD 跑通 (US-1)

- [x] **1.1** 建仓:用 `gh` 创建 GitHub 仓库 `banksys_sy_zhangrunlu`(开源),`main` 放最小引导提交
- [x] **1.2** 提示人类配置 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`
- [x] **1.3** 从 `main` 开 feature 分支 `feature/1-project-init`
- [x] **1.4** 创建项目骨架:目录结构、`.gitignore`、`requirements.txt`、`requirements-dev.txt`、`Dockerfile`、`.dockerignore`、`ruff.toml`、`pyproject.toml`
- [x] **1.5** 编写 `src/app.py` Streamlit 入口(多页面首页)
- [x] **1.6** 编写 CI workflow(`.github/workflows/ci.yml`):ruff + pytest(≥80%) + docker build
- [x] **1.7** 编写 CD workflow(`.github/workflows/cd.yml`):SSH → rsync → docker build → docker run → 健康检查
- [x] **1.8** 编写核心模块测试(27 个,覆盖 data_loader/model/predict)
- [x] **1.9** 本地自检通过:ruff format ✅、ruff check ✅、pytest --cov=src 27 passed, 97.2% ✅
- [x] **1.10** push 分支 + 创建 PR #1；CI 运行中 → ✋ 等待人工 Review 与 Merge

### 第二批: 数据模块 (US-2)

- [x] **2.1** 实现 `src/data_loader.py`:加载 CSV、缺失值处理、特征分类(10 cat + 10 num)、编码
- [x] **2.2** 编写 `tests/test_data_loader.py`(13 个用例,覆盖加载、预处理、编码、缺失值)
- [x] **2.3** 本地自检全绿 ✅（合并进本轮 PR）

### 第三批: 数据分析页面 (US-3)

- [x] **3.1** 实现 `src/pages/1_📊_数据分析.py`:概览、分布图、散点图、热力图、目标变量对比
- [x] **3.2** Streamlit 页面为 UI 代码,已排除出覆盖率统计(pyproject.toml omit 配置)
- [x] **3.3** 本地自检全绿 ✅（合并进本轮 PR）

### 第四批: 模型训练 + 预测 (US-4 + US-5)

- [x] **4.1** 实现 `src/model.py`:Logistic/RF 对比择优、80/20 分层划分、交叉验证、AUC/准确率
- [x] **4.2** 实现 `src/predict.py`:加载模型+编码器 → 单条推理管道
- [x] **4.3** 实现 `src/pages/2_🔮_在线预测.py`:分组表单(个人信息/资产/联系方式/营销/经济指标) + 预测结果
- [x] **4.4** 编写 `tests/test_model.py` 和 `tests/test_predict.py`(14 个用例)
- [x] **4.5** 模型指标门禁通过:AUC ≥ 0.75, 准确率 ≥ 0.80 ✅（合并进本轮 PR）

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
| 2026-08-02 | ruff.toml 忽略 N999(模块名含中文/emoji) | Streamlit 多页面命名规范要求 `<number>_<emoji>_<name>.py`。 |
| 2026-08-02 | Streamlit 页面文件排除出覆盖率统计 | UI 代码依赖 Streamlit runtime,在单元测试中难以覆盖;核心逻辑(data_loader/model/predict)覆盖率 97.2%。 |
| 2026-08-02 | 模型选择策略:对比 LR 与 RF 后取 AUC 优者 | 简单高效,无需额外超参调优;实测 RF 胜出。 |

---

## 已知坑 (GOTCHAS)

_暂无;开发中遇到故障后将在此记录。_

---

## 里程碑 (DONE)

- [x] **2026-08-02**: 项目上下文 `00-project-context.md` 填写完成
- [x] **2026-08-02**: 需求文档 `01-requirements.md` 填写完成(US-1 ~ US-6 共 6 个用户故事,含验收标准)
- [x] **2026-08-02**: `PROGRESS.md` 初始化完成(第一批 TODO 已列出)
- [x] **2026-08-02**: US-1~US-5 全部代码+测试完成；PR #1 已创建，CI 运行中
