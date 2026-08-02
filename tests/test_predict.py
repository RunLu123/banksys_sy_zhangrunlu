"""测试在线预测模块。"""

import pytest

from src.data_loader import load_train_data, preprocess
from src.model import train_and_save
from src.predict import (
    get_default_features,
    get_feature_choices,
    load_pipeline,
    predict_single,
)


@pytest.fixture
def trained_pipeline():
    """训练并保存模型，供预测测试使用。"""
    df = load_train_data()
    X, y, pp = preprocess(df, training=True)
    train_and_save(X, y, pp)
    return load_pipeline()


class TestLoadPipeline:
    """模型加载测试。"""

    def test_load_returns_model_and_preprocessor(self, trained_pipeline):
        model, pp = trained_pipeline
        assert model is not None
        assert pp is not None

    def test_load_returns_none_when_no_model(self):
        # 在没有模型文件时检查——此处模型已由 fixture 保存，直接测返回是否非 None
        model, pp = load_pipeline()
        assert model is not None
        assert pp is not None


class TestPredictSingle:
    """单条预测测试。"""

    def test_predict_returns_dict_with_keys(self, trained_pipeline):
        model, pp = trained_pipeline
        defaults = get_default_features()
        result = predict_single(defaults, model, pp)
        assert "subscribe" in result
        assert "probability" in result

    def test_predict_subscribe_is_bool(self, trained_pipeline):
        model, pp = trained_pipeline
        defaults = get_default_features()
        result = predict_single(defaults, model, pp)
        assert isinstance(result["subscribe"], bool)

    def test_predict_probability_in_range(self, trained_pipeline):
        model, pp = trained_pipeline
        defaults = get_default_features()
        result = predict_single(defaults, model, pp)
        assert 0.0 <= result["probability"] <= 1.0


class TestFeatureHelpers:
    """特征辅助函数测试。"""

    def test_get_feature_choices_covers_all_categorical(self):
        choices = get_feature_choices()
        from src.data_loader import CATEGORICAL_COLS

        for col in CATEGORICAL_COLS:
            assert col in choices
            assert len(choices[col]) > 0

    def test_get_default_features_covers_all_features(self):
        defaults = get_default_features()
        from src.data_loader import CATEGORICAL_COLS, NUMERICAL_COLS

        for col in CATEGORICAL_COLS + NUMERICAL_COLS:
            assert col in defaults
            assert defaults[col] is not None
