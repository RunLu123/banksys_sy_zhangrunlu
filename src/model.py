"""模型训练与持久化模块。"""

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
RANDOM_STATE = 42


def train_and_save(X, y, preprocessor, output_dir: str | None = None) -> dict:
    """训练二分类模型，评估后保存模型与预处理器。

    Args:
        X: 特征矩阵（已预处理）。
        y: 目标标签 (0/1)。
        preprocessor: 拟合好的 ColumnTransformer。
        output_dir: 模型保存目录，默认为 models/。

    Returns:
        dict: 含 model_name, auc, accuracy, model_path, preprocessor_path。
    """
    output_dir = Path(output_dir) if output_dir else MODELS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # 按 80/20 分层划分
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 尝试两个模型，选 AUC 更优的
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1
        ),
    }

    best_model = None
    best_auc = -1.0
    best_name = ""

    for name, model in candidates.items():
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_prob)
        if auc > best_auc:
            best_auc = auc
            best_model = model
            best_name = name

    # 评估
    y_pred = best_model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    auc = roc_auc_score(y_val, best_model.predict_proba(X_val)[:, 1])

    # 交叉验证
    cv_scores = cross_val_score(
        best_model,
        X,
        y,
        cv=StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE),
        scoring="roc_auc",
    )

    # 持久化
    model_path = output_dir / "model.pkl"
    preprocessor_path = output_dir / "preprocessor.pkl"
    joblib.dump(best_model, model_path)
    joblib.dump(preprocessor, preprocessor_path)

    return {
        "model_name": best_name,
        "auc": round(float(auc), 4),
        "accuracy": round(float(acc), 4),
        "cv_auc_mean": round(float(cv_scores.mean()), 4),
        "cv_auc_std": round(float(cv_scores.std()), 4),
        "model_path": str(model_path),
        "preprocessor_path": str(preprocessor_path),
    }
