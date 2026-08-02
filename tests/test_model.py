"""测试模型训练模块。"""

import joblib
import pytest

from src.data_loader import load_train_data, preprocess
from src.model import train_and_save


@pytest.fixture
def training_data():
    """准备训练数据。"""
    df = load_train_data()
    X, y, preprocessor = preprocess(df, training=True)
    return X, y, preprocessor


class TestTrainAndSave:
    """模型训练与保存测试。"""

    def test_train_returns_metrics_dict(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        assert "model_name" in result
        assert "auc" in result
        assert "accuracy" in result
        assert "cv_auc_mean" in result

    def test_auc_meets_threshold(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        assert result["auc"] >= 0.75, f"AUC {result['auc']} < 0.75"

    def test_accuracy_meets_threshold(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        assert result["accuracy"] >= 0.80, f"Accuracy {result['accuracy']} < 0.80"

    def test_model_file_saved(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        import os

        assert os.path.exists(result["model_path"])
        assert os.path.exists(result["preprocessor_path"])

    def test_saved_model_can_be_loaded(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        model = joblib.load(result["model_path"])
        pp = joblib.load(result["preprocessor_path"])
        assert model is not None
        assert pp is not None

    def test_loaded_model_can_predict(self, training_data):
        X, y, preprocessor = training_data
        result = train_and_save(X, y, preprocessor)
        model = joblib.load(result["model_path"])
        proba = model.predict_proba(X[:5])
        assert proba.shape == (5, 2)

    def test_training_is_reproducible(self, training_data):
        """相同种子应产生相同指标。"""
        X, y, preprocessor = training_data

        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            r1 = train_and_save(X, y, preprocessor, output_dir=tmpdir)
            # 清除旧文件
            for f in os.listdir(tmpdir):
                os.remove(os.path.join(tmpdir, f))
            r2 = train_and_save(X, y, preprocessor, output_dir=tmpdir)
            assert r1["auc"] == r2["auc"]
            assert r1["accuracy"] == r2["accuracy"]
