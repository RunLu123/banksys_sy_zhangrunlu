"""在线预测页面 —— 点选输入客户特征，预测认购结果。"""

import streamlit as st

from src.predict import (
    get_default_features,
    get_feature_choices,
    load_pipeline,
    predict_single,
)

st.set_page_config(
    page_title="在线预测",
    page_icon="🔮",
    layout="wide",
)

st.title("🔮 在线预测")


# ── 加载模型 ──
@st.cache_resource
def get_pipeline():
    return load_pipeline()


model, preprocessor = get_pipeline()

if model is None or preprocessor is None:
    st.warning("⚠️ 模型尚未就绪，请先完成模型训练。")
    st.stop()


# ── 加载特征选项与默认值 ──
@st.cache_data
def get_choices():
    return get_feature_choices()


@st.cache_data
def get_defaults():
    return get_default_features()


choices = get_choices()
defaults = get_defaults()

# ── 输入表单 ──
st.markdown("### 客户特征输入")
st.markdown("请根据客户信息填写以下特征，点击 **开始预测** 获取认购预测结果。")

with st.form("prediction_form"):
    # 分类特征：下拉选择
    st.markdown("#### 个人信息")
    col1, col2, col3 = st.columns(3)
    job = col1.selectbox("职业 (job)", choices["job"], index=choices["job"].index(defaults["job"]))
    marital = col2.selectbox(
        "婚姻状态 (marital)",
        choices["marital"],
        index=choices["marital"].index(defaults["marital"]),
    )
    education = col3.selectbox(
        "教育程度 (education)",
        choices["education"],
        index=choices["education"].index(defaults["education"]),
    )
    age = col1.number_input("年龄 (age)", min_value=17, max_value=100, value=int(defaults["age"]))

    st.markdown("#### 资产与信贷")
    col1, col2, col3 = st.columns(3)
    default = col1.selectbox(
        "是否有违约 (default)",
        choices["default"],
        index=choices["default"].index(defaults["default"]),
    )
    housing = col2.selectbox(
        "是否有房贷 (housing)",
        choices["housing"],
        index=choices["housing"].index(defaults["housing"]),
    )
    loan = col3.selectbox(
        "是否有个人贷款 (loan)",
        choices["loan"],
        index=choices["loan"].index(defaults["loan"]),
    )

    st.markdown("#### 联系方式与时机")
    col1, col2, col3 = st.columns(3)
    contact = col1.selectbox(
        "联系方式 (contact)",
        choices["contact"],
        index=choices["contact"].index(defaults["contact"]),
    )
    month = col2.selectbox(
        "联系月份 (month)",
        choices["month"],
        index=choices["month"].index(defaults["month"]),
    )
    day_of_week = col3.selectbox(
        "联系星期 (day_of_week)",
        choices["day_of_week"],
        index=choices["day_of_week"].index(defaults["day_of_week"]),
    )

    st.markdown("#### 营销活动信息")
    col1, col2, col3 = st.columns(3)
    duration = col1.number_input(
        "通话时长/秒 (duration)", min_value=0, value=int(defaults["duration"])
    )
    campaign = col2.number_input(
        "本次活动联系次数 (campaign)", min_value=1, value=int(defaults["campaign"])
    )
    pdays = col3.number_input("距上次活动天数 (pdays)", min_value=0, value=int(defaults["pdays"]))
    previous = col1.number_input(
        "之前活动联系次数 (previous)", min_value=0, value=int(defaults["previous"])
    )
    poutcome = col2.selectbox(
        "上次活动结果 (poutcome)",
        choices["poutcome"],
        index=choices["poutcome"].index(defaults["poutcome"]),
    )

    st.markdown("#### 经济指标")
    col1, col2, col3 = st.columns(3)
    emp_var_rate = col1.number_input(
        "就业变化率 (emp_var_rate)",
        value=float(defaults["emp_var_rate"]),
        step=0.1,
        format="%.1f",
    )
    cons_price_index = col2.number_input(
        "消费价格指数 (cons_price_index)",
        value=float(defaults["cons_price_index"]),
        step=0.01,
        format="%.2f",
    )
    cons_conf_index = col3.number_input(
        "消费者信心指数 (cons_conf_index)",
        value=float(defaults["cons_conf_index"]),
        step=0.01,
        format="%.2f",
    )
    lending_rate3m = col1.number_input(
        "3月期贷款利率 (lending_rate3m)",
        value=float(defaults["lending_rate3m"]),
        step=0.01,
        format="%.2f",
    )
    nr_employed = col2.number_input(
        "就业人数 (nr_employed)",
        value=float(defaults["nr_employed"]),
        step=0.01,
        format="%.2f",
    )

    submitted = st.form_submit_button("🔮 开始预测", type="primary", use_container_width=True)

# ── 预测结果 ──
if submitted:
    features = {
        "job": job,
        "marital": marital,
        "education": education,
        "age": age,
        "default": default,
        "housing": housing,
        "loan": loan,
        "contact": contact,
        "month": month,
        "day_of_week": day_of_week,
        "duration": duration,
        "campaign": campaign,
        "pdays": pdays,
        "previous": previous,
        "poutcome": poutcome,
        "emp_var_rate": emp_var_rate,
        "cons_price_index": cons_price_index,
        "cons_conf_index": cons_conf_index,
        "lending_rate3m": lending_rate3m,
        "nr_employed": nr_employed,
    }

    result = predict_single(features, model, preprocessor)

    st.markdown("---")
    if result["subscribe"]:
        st.success("### ✅ 预计会认购")
    else:
        st.error("### ❌ 预计不会认购")

    col1, col2 = st.columns(2)
    col1.metric("认购概率", f"{result['probability']:.2%}")
    col2.metric("预测阈值", "50%")
    st.progress(result["probability"])
