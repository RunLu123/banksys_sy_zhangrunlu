"""离线训练脚本 —— 由 Dockerfile 在构建时调用。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_train_data, preprocess
from src.model import train_and_save


def main():
    print("Loading training data...")
    df = load_train_data()
    X, y, preprocessor = preprocess(df, training=True)

    print("Training model...")
    result = train_and_save(X, y, preprocessor, "models/")

    print(f"Model trained: {result['model_name']}")
    print(f"  AUC: {result['auc']}")
    print(f"  Accuracy: {result['accuracy']}")
    print(f"  CV AUC (mean ± std): {result['cv_auc_mean']} ± {result['cv_auc_std']}")
    print("Model training completed.")


if __name__ == "__main__":
    main()
