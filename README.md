# banksys_sy_zhangrunlu

银行营销数据分析与在线认购预测系统。

## 功能

- **数据分析交互页面**: 对银行营销数据进行多维探索,包括特征分布、相关性热力图、按认购结果分组对比。
- **在线预测系统**: 基于离线训练的 ML 模型,用户通过点选表单输入客户特征,即时预测是否会认购定期存款。

## 技术栈

Python 3.11 · Streamlit · scikit-learn · pandas · plotly · Docker · GitHub Actions

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run src/app.py --server.port 8888
```

## 项目结构

```
├── standards/      # AI 项目记忆与工程规范
├── data/           # 训练/测试数据集
├── src/            # 源码
├── tests/          # 测试
├── models/         # 训练产物(不进 Git)
└── .github/        # CI/CD workflows
```
