"""数据加载与预处理模块。"""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 项目根目录（src/ 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# 特征分类
CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]
NUMERICAL_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
TARGET_COL = "subscribe"
ID_COL = "id"


def load_train_data() -> pd.DataFrame:
    """加载训练数据集（含 subscribe 标签）。

    Returns:
        pd.DataFrame: 训练数据，22500 行 × 22 列。
    """
    path = DATA_DIR / "train.csv"
    if not path.exists():
        raise FileNotFoundError(f"训练数据文件不存在: {path}")
    return pd.read_csv(path)


def load_test_data() -> pd.DataFrame:
    """加载测试数据集（无 subscribe 标签）。

    Returns:
        pd.DataFrame: 测试数据，7500 行 × 21 列。
    """
    path = DATA_DIR / "test.csv"
    if not path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {path}")
    return pd.read_csv(path)


def preprocess(df: pd.DataFrame, *, training: bool = False) -> tuple:
    """数据预处理：缺失值填充、分类编码、数值标准化。

    Args:
        df: 原始 DataFrame。
        training: True 时需包含 subscribe 列，并返回 y 和 fitted preprocessor。

    Returns:
        training=True:  (X, y, preprocessor)
        training=False: (X, None, preprocessor)   # preprocessor 已 fitted
    """
    df = df.copy()

    # 构建特征矩阵
    X = df[CATEGORICAL_COLS + NUMERICAL_COLS]

    # 分类管道：众数填充 + One-Hot 编码
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    # 数值管道：中位数填充 + 标准化
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("cat", cat_pipe, CATEGORICAL_COLS),
            ("num", num_pipe, NUMERICAL_COLS),
        ]
    )

    X_processed = preprocessor.fit_transform(X)

    if training and TARGET_COL in df.columns:
        y = (df[TARGET_COL] == "yes").astype(int).values
        return X_processed, y, preprocessor

    return X_processed, None, preprocessor
