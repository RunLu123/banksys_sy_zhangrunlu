"""数据分析交互页面 —— 探索银行营销训练数据。"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.data_loader import (
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
    TARGET_COL,
    load_train_data,
)

st.set_page_config(
    page_title="数据分析",
    page_icon="📊",
    layout="wide",
)

st.title("📊 数据分析")


# ── 加载数据（缓存） ──
@st.cache_data
def get_data():
    return load_train_data()


df = get_data()

# ── 侧边栏 ──
st.sidebar.header("分析选项")
analysis_type = st.sidebar.selectbox(
    "选择分析类型",
    ["数据概览", "特征分布", "相关性分析", "目标变量对比"],
)

# ═══════════════════════════════════════════════════════════
# 1. 数据概览
# ═══════════════════════════════════════════════════════════
if analysis_type == "数据概览":
    st.header("数据概览")

    col1, col2, col3 = st.columns(3)
    col1.metric("总行数", f"{len(df):,}")
    col2.metric("总列数", len(df.columns))
    col3.metric("认购率", f"{df[TARGET_COL].eq('yes').mean():.1%}")

    st.subheader("前 10 行数据")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("各列信息")
    info = pd.DataFrame(
        {
            "类型": df.dtypes,
            "缺失数": df.isnull().sum(),
            "缺失率": (df.isnull().sum() / len(df) * 100).round(2).astype(str) + "%",
            "唯一值数": df.nunique(),
        }
    )
    st.dataframe(info, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 2. 特征分布
# ═══════════════════════════════════════════════════════════
elif analysis_type == "特征分布":
    st.header("特征分布")

    all_features = NUMERICAL_COLS + CATEGORICAL_COLS
    feature = st.selectbox("选择特征", all_features)

    split_by_target = st.checkbox("按认购结果分组着色", value=True)

    if feature in NUMERICAL_COLS:
        if split_by_target:
            fig = px.histogram(
                df,
                x=feature,
                color=TARGET_COL,
                barmode="overlay",
                opacity=0.7,
                marginal="box",
                color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
            )
        else:
            fig = px.histogram(df, x=feature, marginal="box")
        fig.update_layout(bargap=0.1)
    else:
        # 分类特征
        counts = df.groupby([feature, TARGET_COL], observed=False).size().reset_index(name="count")
        if split_by_target:
            fig = px.bar(
                counts,
                x=feature,
                y="count",
                color=TARGET_COL,
                barmode="group",
                color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
            )
        else:
            fig = px.bar(
                counts.groupby(feature, observed=False)["count"].sum().reset_index(),
                x=feature,
                y="count",
            )

    fig.update_layout(height=500, title=f"{feature} 分布")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 3. 相关性分析
# ═══════════════════════════════════════════════════════════
elif analysis_type == "相关性分析":
    st.header("相关性分析")

    view = st.radio("视图", ["热力图", "散点图"], horizontal=True)

    if view == "热力图":
        corr = df[NUMERICAL_COLS].corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
        )
        fig.update_layout(height=600, title="数值特征相关性热力图")
        st.plotly_chart(fig, use_container_width=True)
    else:
        col1, col2 = st.columns(2)
        x_feat = col1.selectbox("X 轴", NUMERICAL_COLS, index=0)
        y_feat = col2.selectbox("Y 轴", NUMERICAL_COLS, index=min(1, len(NUMERICAL_COLS) - 1))
        color_by = st.checkbox("按认购结果着色", value=True)

        if color_by:
            fig = px.scatter(
                df,
                x=x_feat,
                y=y_feat,
                color=TARGET_COL,
                opacity=0.6,
                color_discrete_map={"yes": "#2E86AB", "no": "#A23B72"},
            )
        else:
            fig = px.scatter(df, x=x_feat, y=y_feat, opacity=0.6)
        fig.update_layout(height=500, title=f"{x_feat} vs {y_feat}")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 4. 目标变量对比
# ═══════════════════════════════════════════════════════════
elif analysis_type == "目标变量对比":
    st.header("目标变量对比：认购 vs 未认购")

    yes_df = df[df[TARGET_COL] == "yes"]
    no_df = df[df[TARGET_COL] == "no"]

    st.subheader("数值特征均值对比")
    compare_data = []
    for col in NUMERICAL_COLS:
        compare_data.append(
            {
                "特征": col,
                "认购 (yes)": round(yes_df[col].mean(), 2),
                "未认购 (no)": round(no_df[col].mean(), 2),
            }
        )
    compare_df = pd.DataFrame(compare_data)
    st.dataframe(compare_df, use_container_width=True)

    # 并排箱线图
    st.subheader("数值特征分布对比")
    selected_num = st.multiselect(
        "选择数值特征（最多 4 个）",
        NUMERICAL_COLS,
        default=NUMERICAL_COLS[:4],
        max_selections=4,
    )
    if selected_num:
        rows = (len(selected_num) + 1) // 2
        fig = make_subplots(rows=rows, cols=2, subplot_titles=selected_num)
        for i, col in enumerate(selected_num):
            r = i // 2 + 1
            c = i % 2 + 1
            fig.add_trace(
                go.Box(
                    y=yes_df[col],
                    name="yes",
                    marker_color="#2E86AB",
                    showlegend=(i == 0),
                ),
                row=r,
                col=c,
            )
            fig.add_trace(
                go.Box(y=no_df[col], name="no", marker_color="#A23B72", showlegend=(i == 0)),
                row=r,
                col=c,
            )
        fig.update_layout(height=300 * rows, title="")
        st.plotly_chart(fig, use_container_width=True)

    # 分类特征对比
    st.subheader("分类特征分布对比")
    selected_cat = st.selectbox("选择分类特征", CATEGORICAL_COLS)
    cat_counts = (
        df.groupby([selected_cat, TARGET_COL], observed=False).size().reset_index(name="count")
    )
    pivot = cat_counts.pivot(index=selected_cat, columns=TARGET_COL, values="count").fillna(0)
    pivot["yes_pct"] = (pivot["yes"] / (pivot["yes"] + pivot["no"]) * 100).round(1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(name="yes", x=pivot.index, y=pivot["yes"], marker_color="#2E86AB"))
    fig.add_trace(go.Bar(name="no", x=pivot.index, y=pivot["no"], marker_color="#A23B72"))
    fig.add_trace(
        go.Scatter(
            name="yes%",
            x=pivot.index,
            y=pivot["yes_pct"],
            mode="lines+markers",
            marker_color="#D00000",
            line={"width": 3},
        ),
        secondary_y=True,
    )
    fig.update_layout(height=450, barmode="stack", title=f"{selected_cat} 分布与认购率")
    fig.update_yaxes(title_text="人数", secondary_y=False)
    fig.update_yaxes(title_text="认购率 (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
