# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、依赖管理、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: Given 空仓库,When 完成初始化,Then 项目目录结构符合 `00-project-context.md` 第 3 节。
- AC2: Given 代码提交 feature 分支并 push,When 创建 PR,Then CI 自动运行 ruff format、ruff check、pytest(覆盖率≥80%)、docker build 四道门禁。
- AC3: Given CI 全绿且人工 Review 通过,When 合并到 main,Then CD 自动触发:SSH 到服务器→docker build→docker run→健康检查通过。
- AC4: Given 部署完成,When 访问 `http://<SSH_HOST>:8888/_stcore/health`,Then 返回 200 OK。
- AC5: Given 项目初始化完成,Then `PROGRESS.md` 已更新当前状态。

技术备注:
- 本地不强制 Docker;docker build 只由 CI 执行。
- 需先配置 GitHub Secrets: `SSH_PRIVATE_KEY`、`SSH_HOST`、`SSH_USER`。

---

### US-2 数据加载与预处理模块 · 状态: Backlog

作为 **数据分析师**,
我想要 系统能正确加载并清洗银行营销数据,
以便 后续分析页面和模型训练都基于干净一致的数据。

验收标准:
- AC1: Given `data/train.csv` 文件存在,When 调用 `load_train_data()`,Then 返回 DataFrame 含 22500 行 22 列(subscribe 列保留)。
- AC2: Given `data/test.csv` 文件存在,When 调用 `load_test_data()`,Then 返回 DataFrame 含 7500 行 21 列(无 subscribe 列)。
- AC3: Given 原始数据含缺失值或异常值,When 执行预处理,Then 缺失值合理填充或标记,异常值被记录日志但不静默丢弃。
- AC4: Given 分类特征(如 job, marital, education 等),When 执行编码,Then 输出数值特征矩阵供模型使用,并保留编码器以便在线预测时复用。

技术备注:
- 分类特征列表: job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome。
- 数值特征列表: age, duration, campaign, pdays, previous, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed。

---

### US-3 数据分析交互页面 · 状态: Backlog

作为 **银行营销人员**,
我想要 在 Web 页面上交互式地探索训练数据,
以便 直观理解客户特征分布、相关性以及与认购行为的关系。

验收标准:
- AC1: Given 启动 Streamlit 应用,When 访问首页/数据分析页,Then 页面展示数据概览(行数、列数、各列类型、缺失值统计)。
- AC2: Given 用户选择某个特征列,When 点击或切换,Then 展示该特征的分布直方图(数值特征)或柱状图(分类特征),并可切换按 subscribe yes/no 分组着色。
- AC3: Given 用户选择两个数值特征,When 查看相关性散点图,Then 图表正确渲染,并可按 subscribe 分组着色。
- AC4: Given 用户选择"相关性热力图",When 点击生成,Then 展示所有数值特征间的相关系数矩阵热力图。
- AC5: Given 用户选择目标变量对比视图,When 切换为 subscribe=yes vs no,Then 并排展示两组在各特征上的分布差异。

---

### US-4 模型离线训练模块 · 状态: Backlog

作为 **数据科学家**,
我想要 基于历史训练数据离线训练一个二分类模型,
以便 为在线预测系统提供准确的认购预测能力。

验收标准:
- AC1: Given train.csv 加载并预处理完毕,When 执行训练脚本/函数,Then 完成训练并输出模型文件到 `models/` 目录。
- AC2: Given 训练完成,When 在留出验证集上评估,Then AUC ≥ 0.75 且准确率 ≥ 0.80。
- AC3: Given 训练完成,When 保存模型,Then 编码器(preprocessor)与模型一并持久化,以便在线预测时完全复现推理管道。
- AC4: Given 训练函数,When 传入随机种子,Then 两次训练结果可复现(相同种子→相同模型指标)。

技术备注:
- 建议模型: 先尝试 LogisticRegression(基线),再尝试 RandomForest 或 XGBoost,取验证集 AUC 最优者。
- 训练/验证集按 80/20 分层划分(stratify=subscribe)。
- 模型文件不进 Git(Dockerfile 内训练或挂载)。

---

### US-5 在线预测系统 · 状态: Backlog

作为 **银行营销人员**,
我想要 在 Web 页面上通过下拉菜单和输入框点选客户特征,
以便 立即获得该客户是否会认购定期存款的预测结果。

验收标准:
- AC1: Given 启动 Streamlit 应用并进入预测页面,When 页面加载,Then 显示完整的客户特征输入表单(分类特征为下拉选择,数值特征为输入框,均预填合理默认值)。
- AC2: Given 用户填好所有特征并点击"预测"按钮,When 系统处理,Then 页面显示预测结果:「预计会认购 ✅」或「预计不会认购 ❌」,并附带预测概率。
- AC3: Given 用户未填完必填字段,When 点击预测,Then 页面给出明确提示"请填写所有字段"而非报错崩溃。
- AC4: Given 模型尚未训练或模型文件缺失,When 进入预测页面,Then 页面给出友好提示"模型尚未就绪,请先完成训练"而非白屏/报错。
- AC5: Given 多次预测不同输入,When 每次点击预测,Then 每次预测结果独立、互不影响,不残留上一次的状态。

技术备注:
- 分类特征下拉选项应从训练数据中提取唯一值,而非硬编码。
- 预测管道: 原始输入 → 编码(复用训练时的编码器) → 模型推理 → 概率 + 类别。

---

### US-6 Docker 容器化与部署 · 状态: Backlog

作为 **运维人员**,
我想要 应用通过 Docker 一键构建和运行,
以便 在任何有 Docker 的服务器上快速部署,且环境一致。

验收标准:
- AC1: Given 项目根目录,When 执行 `docker build -t banksys_sy_zhangrunlu .`,Then 镜像构建成功(含 Streamlit、模型训练产物或训练脚本)。
- AC2: Given 镜像构建成功,When 执行 `docker run -d -p 8888:8888 banksys_sy_zhangrunlu`,Then 容器在端口 8888 提供 Streamlit 服务。
- AC3: Given 容器运行中,When 访问 `http://localhost:8888/_stcore/health`,Then 返回 200。
- AC4: Given 服务器重启,When 容器配置 `--restart unless-stopped`,Then 容器自动恢复运行。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交;PR 尽量小于 400 行。
- **可测试**:核心逻辑(数据加载、预处理、模型训练、预测管道)必须有单元测试,覆盖率 ≥ 80%。
- **可部署**:部署后必须有健康检查;CD 脚本幂等可重跑。
- **可复现**:训练随机种子固定(如 `random_state=42`),依赖版本锁定在 `requirements.txt`。
- **性能**:预测接口单次响应时间 ≤ 2 秒(不含页面渲染)。
- **可用性**:预测表单对手机端不做要求,桌面端表单布局清晰,分组合理。
