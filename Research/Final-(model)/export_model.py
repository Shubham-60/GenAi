from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

try:
    from imblearn.over_sampling import SMOTE
except Exception:
    SMOTE = None

THRESHOLD = 0.58
FEATURE_ORDER = [
    "HighBP",
    "HighChol",
    "CholCheck",
    "BMI",
    "Smoker",
    "PhysActivity",
    "Fruits",
    "Veggies",
    "HvyAlcoholConsump",
    "AnyHealthcare",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Sex",
    "Age",
    "Education",
    "Income",
]


def train_and_export(dataset_path: Path, output_dir: Path, use_smote: bool = True) -> None:
    dataframe = pd.read_csv(dataset_path)

    target = dataframe["Diabetes_binary"].astype(int)
    features = dataframe.drop(columns=["Diabetes_binary", "Stroke", "HeartDiseaseorAttack"], errors="ignore")
    features = features[FEATURE_ORDER].astype(float)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    train_x = features_scaled
    train_y = target
    if use_smote and SMOTE is not None:
        smote = SMOTE(random_state=42)
        resampled: Any = smote.fit_resample(features_scaled, target)
        train_x, train_y = resampled[0], resampled[1]

    model = LogisticRegression(C=0.01, max_iter=1000, random_state=42)
    model.fit(train_x, train_y)

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "lr_model.pkl"
    scaler_path = output_dir / "scaler.pkl"
    metadata_path = output_dir / "model_metadata.json"

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "threshold": THRESHOLD,
        "feature_order": FEATURE_ORDER,
        "used_smote": bool(use_smote and SMOTE is not None),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved model: {model_path}")
    print(f"Saved scaler: {scaler_path}")
    print(f"Saved metadata: {metadata_path}")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    default_dataset = project_root / "Research" / "data" / "dataset_binary.csv"
    default_output = project_root / "Final" / "models"

    parser = argparse.ArgumentParser(description="Train and export diabetes model artifacts.")
    parser.add_argument("--dataset", type=Path, default=default_dataset)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--no-smote", action="store_true", help="Disable SMOTE balancing.")
    args = parser.parse_args()

    train_and_export(args.dataset, args.output, use_smote=not args.no_smote)
