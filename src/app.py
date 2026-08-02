"""Streamlit 应用入口 —— 银行营销数据分析与在线预测系统。"""

import streamlit as st

# 页面配置（必须在任何 st.* 调用之前）
st.set_page_config(
    page_title="银行营销认购预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 首页内容 ──
st.title("🏦 银行营销认购预测系统")
st.markdown("---")

st.markdown("""
### 欢迎使用银行营销数据分析与在线预测系统

本系统基于银行营销历史数据，提供两大功能：

| 功能 | 说明 |
|---|---|
| 📊 **数据分析** | 交互式探索训练数据，查看特征分布、相关性、按认购结果对比 |
| 🔮 **在线预测** | 输入客户特征，即时预测是否会认购定期存款 |

### 快速导航

使用左侧边栏切换页面，或点击下方按钮：
""")

col1, col2 = st.columns(2)
with col1:
    if st.button("📊 进入数据分析", use_container_width=True):
        st.switch_page("pages/1_📊_数据分析.py")
with col2:
    if st.button("🔮 进入在线预测", use_container_width=True):
        st.switch_page("pages/2_🔮_在线预测.py")

st.markdown("---")
st.caption("banksys_sy_zhangrunlu · Python 3.11 · Streamlit · scikit-learn")
