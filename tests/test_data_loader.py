"""测试数据加载与预处理模块。"""

import numpy as np
import pandas as pd

from src.data_loader import (
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
    TARGET_COL,
    load_test_data,
    load_train_data,
    preprocess,
)


class TestLoadTrainData:
    """训练数据加载测试。"""

    def test_load_returns_dataframe(self):
        df = load_train_data()
        assert isinstance(df, pd.DataFrame)

    def test_load_has_correct_shape(self):
        df = load_train_data()
        assert df.shape[0] == 22500
        assert df.shape[1] == 22  # id + 20 features + subscribe

    def test_load_contains_expected_columns(self):
        df = load_train_data()
        for col in CATEGORICAL_COLS + NUMERICAL_COLS + [TARGET_COL, "id"]:
            assert col in df.columns

    def test_subscribe_has_two_classes(self):
        df = load_train_data()
        assert set(df[TARGET_COL].unique()) <= {"yes", "no"}


class TestLoadTestData:
    """测试数据加载测试。"""

    def test_load_returns_dataframe(self):
        df = load_test_data()
        assert isinstance(df, pd.DataFrame)

    def test_load_has_correct_shape(self):
        df = load_test_data()
        assert df.shape[0] == 7500
        assert df.shape[1] == 21  # id + 20 features, no subscribe

    def test_load_has_no_subscribe_column(self):
        df = load_test_data()
        assert TARGET_COL not in df.columns


class TestPreprocess:
    """预处理测试。"""

    def test_training_mode_returns_three_values(self):
        df = load_train_data()
        X, y, preprocessor = preprocess(df, training=True)
        assert X is not None
        assert y is not None
        assert preprocessor is not None

    def test_training_mode_output_shape(self):
        df = load_train_data()
        X, y, _ = preprocess(df, training=True)
        assert X.shape[0] == 22500
        assert len(y) == 22500

    def test_y_is_binary(self):
        df = load_train_data()
        _, y, _ = preprocess(df, training=True)
        assert set(np.unique(y)) <= {0, 1}

    def test_inference_mode_returns_processed_X(self):
        df = load_train_data()
        _X, _y, _preprocessor = preprocess(df, training=True)
        # 用已经 fit 的 preprocessor 做 inference
        X2, y2, _ = preprocess(df.head(10), training=False)
        assert X2.shape[0] == 10
        assert y2 is None

    def test_preprocess_handles_missing_values(self):
        df = load_train_data()
        # 人为制造缺失
        df_copy = df.copy()
        df_copy.loc[0, "age"] = np.nan
        df_copy.loc[0, "job"] = np.nan
        X, y, _ = preprocess(df_copy, training=True)
        # 不应有 NaN 输出
        assert not np.any(np.isnan(X))
        assert len(y) == len(df_copy)

    def test_preprocess_output_is_numeric(self):
        df = load_train_data()
        X, _, _ = preprocess(df, training=True)
        assert np.issubdtype(X.dtype, np.floating)
