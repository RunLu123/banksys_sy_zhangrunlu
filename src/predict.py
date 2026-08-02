"""在线预测逻辑模块。"""

from pathlib import Path

import joblib
import pandas as pd

from src.data_loader import CATEGORICAL_COLS, NUMERICAL_COLS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


def load_pipeline():
    """加载已训练的模型与预处理器。

    Returns:
        tuple: (model, preprocessor) 或 (None, None)。
    """
    model_path = MODELS_DIR / "model.pkl"
    preprocessor_path = MODELS_DIR / "preprocessor.pkl"

    if not model_path.exists() or not preprocessor_path.exists():
        return None, None

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    return model, preprocessor


def predict_single(features: dict, model, preprocessor) -> dict:
    """对单条客户特征进行预测。

    Args:
        features: 原始特征字典，键为 CATEGORICAL_COLS + NUMERICAL_COLS。
        model: 已加载的分类模型。
        preprocessor: 已拟合的 ColumnTransformer。

    Returns:
        dict: 含 subscribe (bool) 和 probability (float)。
    """
    # 构建一行 DataFrame，确保列顺序
    all_cols = CATEGORICAL_COLS + NUMERICAL_COLS
    input_df = pd.DataFrame([features])[all_cols]

    # 数值列类型转换
    for col in NUMERICAL_COLS:
        input_df[col] = pd.to_numeric(input_df[col], errors="coerce")

    # 预处理
    X = preprocessor.transform(input_df)

    # 推理
    proba = model.predict_proba(X)[0, 1]
    prediction = bool(proba >= 0.5)

    return {
        "subscribe": prediction,
        "probability": round(float(proba), 4),
    }


def get_feature_choices() -> dict:
    """获取每个分类特征的可选项（从训练数据中提取）。

    Returns:
        dict: {feature_name: [unique_values...]}。
    """
    from src.data_loader import load_train_data

    df = load_train_data()
    choices = {}
    for col in CATEGORICAL_COLS:
        # 排序，去掉 NaN
        vals = sorted(df[col].dropna().unique().tolist(), key=str)
        choices[col] = vals
    return choices


def get_default_features() -> dict:
    """获取预测表单的默认值。

    Returns:
        dict: 分类特征取众数，数值特征取中位数。
    """
    from src.data_loader import load_train_data

    df = load_train_data()
    defaults = {}
    for col in CATEGORICAL_COLS:
        defaults[col] = df[col].mode()[0]
    for col in NUMERICAL_COLS:
        defaults[col] = float(df[col].median())
    return defaults
