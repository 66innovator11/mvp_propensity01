import argparse
import os
import pickle
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer


def load_model_and_preprocessor(model_path: str, preprocessor_path: str):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(preprocessor_path, "rb") as f:
        preprocessor = pickle.load(f)
    return model, preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    # For sklearn >= 1.0
    if hasattr(preprocessor, "get_feature_names_out"):
        return list(preprocessor.get_feature_names_out())
    # Fallback: manually construct names
    numeric_features = preprocessor.named_transformers_["num"].get_feature_names_out()
    categorical_transformer = preprocessor.named_transformers_["cat"]
    ohe = categorical_transformer.named_steps["onehot"]
    cat_features = ohe.get_feature_names_out(categorical_transformer._feature_names_in)
    return list(numeric_features) + list(cat_features)


def extract_coefficients(model, feature_names: List[str]) -> pd.DataFrame:
    if hasattr(model, "coef_"):
        # Logistic regression
        coefs = model.coef_.flatten()
        importance = np.abs(coefs)
        direction = np.sign(coefs)
    elif hasattr(model, "feature_importances_"):
        # Tree-based models
        importance = model.feature_importances_
        direction = np.ones_like(importance)
    else:
        raise ValueError("Model does not expose coefficients or feature importances.")
    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance,
        "direction": direction
    })
    df["abs_importance"] = df["importance"].abs()
    df = df.sort_values("abs_importance", ascending=False).reset_index(drop=True)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--propensity-dir", default=os.path.join(os.path.dirname(__file__), "propensity_outputs"), help="Folder with propensity outputs")
    parser.add_argument("--outputs-dir", default=os.path.join(os.path.dirname(__file__), "insights_outputs"), help="Folder to write model insights")
    args = parser.parse_args()

    os.makedirs(args.outputs_dir, exist_ok=True)

    # We'll assume models were saved with pickle in train_propensity_models.py (modify if needed)
    # For now, we'll simulate by loading a placeholder if present
    model_insights = {}
    for target in ["whole_life_cluster0", "term_life_cluster1"]:
        model_path = os.path.join(args.propensity_dir, f"model_{target}.pkl")
        preprocessor_path = os.path.join(args.propensity_dir, f"preprocessor_{target}.pkl")
        if os.path.exists(model_path) and os.path.exists(preprocessor_path):
            model, preprocessor = load_model_and_preprocessor(model_path, preprocessor_path)
            feature_names = get_feature_names(preprocessor)
            coef_df = extract_coefficients(model, feature_names)
            # Save
            coef_path = os.path.join(args.outputs_dir, f"feature_importance_{target}.csv")
            coef_df.to_csv(coef_path, index=False)
            model_insights[target] = coef_df
            print(f"Saved feature importance for {target} to {coef_path}")
        else:
            print(f"Model/preprocessor not found for {target}; skipping.")

    # Save a summary
    if model_insights:
        summary_rows = []
        for target, df in model_insights.items():
            top_features = df.head(5)[["feature", "abs_importance"]].to_dict(orient="records")
            summary_rows.append({"target": target, "top_features": top_features})
        summary_path = os.path.join(args.outputs_dir, "model_summary.json")
        pd.DataFrame(summary_rows).to_json(summary_path, orient="records", indent=2)
        print(f"Model summary saved to {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
