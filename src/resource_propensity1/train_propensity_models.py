import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


@dataclass(frozen=True)
class PropensityResult:
    model: Pipeline
    feature_names_in: list
    auc: float
    precision_at_10: float
    propensity_scores: pd.DataFrame


def _sanitize_filename(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def _income_band_to_numeric(value: str) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip()
    s = s.replace(",", "")
    s = s.replace("–", "-")
    if s.startswith("<"):
        m = re.search(r"(\d+)", s)
        if not m:
            return np.nan
        upper = float(m.group(1)) * 1000.0
        return upper / 2.0
    if s.startswith(">"):
        m = re.search(r"(\d+)", s)
        if not m:
            return np.nan
        lower = float(m.group(1)) * 1000.0
        return lower * 1.15
    m = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if not m:
        return np.nan
    low = float(m.group(1)) * 1000.0
    high = float(m.group(2)) * 1000.0
    return (low + high) / 2.0


def _postcode_to_area(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"
    s = str(value).strip().upper()
    m = re.match(r"^([A-Z]+)", s)
    if not m:
        return "unknown"
    return m.group(1)


def _read_inputs(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    customer_path = os.path.join(data_dir, "customer_profile.csv")
    policy_path = os.path.join(data_dir, "insurance_products.csv")
    txn_path = os.path.join(data_dir, "transactions.csv")
    events_path = os.path.join(data_dir, "customer_events.csv")

    customers = pd.read_csv(customer_path)
    policies = pd.read_csv(policy_path, parse_dates=["PolicyStartDate", "PolicyLapseDate"], keep_default_na=True)
    txns = pd.read_csv(txn_path, parse_dates=["TransactionDate"], keep_default_na=True)

    events = None
    if os.path.exists(events_path):
        events = pd.read_csv(events_path)

    return customers, policies, txns, events


def _build_policy_features(policies: pd.DataFrame) -> pd.DataFrame:
    df = policies.copy()

    for c in ["CoverageAmount", "PremiumAmount", "PolicyTermYears"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    max_date = df["PolicyStartDate"].max()
    if pd.isna(max_date):
        max_date = pd.Timestamp(datetime.utcnow().date())

    df["is_active_policy"] = (df["Status"].astype(str).str.lower() == "active").astype(int)
    df["is_lapsed_policy"] = (df["Status"].astype(str).str.lower() == "lapsed").astype(int)
    df["policy_age_days"] = (max_date - df["PolicyStartDate"]).dt.days

    base_agg = df.groupby("CustomerID").agg(
        policy_count=("PolicyID", "count"),
        policy_active_count=("is_active_policy", "sum"),
        policy_lapsed_count=("is_lapsed_policy", "sum"),
        coverage_sum=("CoverageAmount", "sum"),
        coverage_mean=("CoverageAmount", "mean"),
        coverage_max=("CoverageAmount", "max"),
        premium_sum=("PremiumAmount", "sum"),
        premium_mean=("PremiumAmount", "mean"),
        premium_max=("PremiumAmount", "max"),
        term_mean=("PolicyTermYears", "mean"),
        policy_age_days_min=("policy_age_days", "min"),
        policy_age_days_max=("policy_age_days", "max"),
    )

    product_counts = (
        df.pivot_table(index="CustomerID", columns="Product", values="PolicyID", aggfunc="count", fill_value=0)
        .add_prefix("policy_product_count_")
        .astype(float)
    )

    beneficiary_counts = (
        df.pivot_table(index="CustomerID", columns="BeneficiaryRelation", values="PolicyID", aggfunc="count", fill_value=0)
        .add_prefix("policy_beneficiary_relation_count_")
        .astype(float)
    )

    out = base_agg.join(product_counts, how="left").join(beneficiary_counts, how="left")
    out = out.reset_index()
    return out


def _build_txn_features(txns: pd.DataFrame) -> pd.DataFrame:
    df = txns.copy()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    df["is_credit"] = (df["TransactionType"].astype(str).str.lower() == "credit").astype(int)
    df["is_debit"] = (df["TransactionType"].astype(str).str.lower() == "debit").astype(int)

    df["credit_amount"] = np.where(df["is_credit"] == 1, df["Amount"], 0.0)
    df["debit_amount"] = np.where(df["is_debit"] == 1, df["Amount"], 0.0)

    df["txn_month"] = df["TransactionDate"].dt.to_period("M").astype(str)

    base = df.groupby("CustomerID").agg(
        txn_count=("TransactionID", "count"),
        txn_credit_count=("is_credit", "sum"),
        txn_debit_count=("is_debit", "sum"),
        credit_sum=("credit_amount", "sum"),
        debit_sum=("debit_amount", "sum"),
        amount_mean=("Amount", "mean"),
        amount_std=("Amount", "std"),
        txn_first_date=("TransactionDate", "min"),
        txn_last_date=("TransactionDate", "max"),
        active_months=("txn_month", "nunique"),
    )

    base["net_flow"] = base["credit_sum"].fillna(0.0) - base["debit_sum"].fillna(0.0)
    base["debit_share"] = base["debit_sum"] / (base["credit_sum"] + base["debit_sum"]).replace(0, np.nan)
    base["credit_share"] = base["credit_sum"] / (base["credit_sum"] + base["debit_sum"]).replace(0, np.nan)
    base["avg_credit_per_month"] = base["credit_sum"] / base["active_months"].replace(0, np.nan)
    base["avg_debit_per_month"] = base["debit_sum"] / base["active_months"].replace(0, np.nan)
    base["avg_txn_per_month"] = base["txn_count"] / base["active_months"].replace(0, np.nan)

    max_date = df["TransactionDate"].max()
    if pd.isna(max_date):
        max_date = pd.Timestamp(datetime.utcnow().date())
    base["days_since_last_txn"] = (max_date - base["txn_last_date"]).dt.days
    base["txn_span_days"] = (base["txn_last_date"] - base["txn_first_date"]).dt.days

    base = base.drop(columns=["txn_first_date", "txn_last_date"]).reset_index()

    category_counts = (
        df.pivot_table(index="CustomerID", columns="Category", values="TransactionID", aggfunc="count", fill_value=0)
        .add_prefix("txn_category_count_")
        .astype(float)
        .reset_index()
    )

    payment_counts = (
        df.pivot_table(index="CustomerID", columns="PaymentMethod", values="TransactionID", aggfunc="count", fill_value=0)
        .add_prefix("txn_payment_count_")
        .astype(float)
        .reset_index()
    )

    out = base.merge(category_counts, on="CustomerID", how="left").merge(payment_counts, on="CustomerID", how="left")
    return out


def _build_event_features(events: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if events is None or events.empty:
        return None
    df = events.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    counts = (
        df.pivot_table(index="CustomerID", columns="Event", values="Year", aggfunc="count", fill_value=0)
        .add_prefix("event_count_")
        .astype(float)
        .reset_index()
    )

    last_year = df.groupby("CustomerID")["Year"].max().rename("event_last_year").reset_index()
    out = counts.merge(last_year, on="CustomerID", how="left")
    return out


def _assemble_customer_table(customers: pd.DataFrame, policies: pd.DataFrame, txns: pd.DataFrame, events: Optional[pd.DataFrame]) -> pd.DataFrame:
    cust = customers.copy()
    cust["IncomeBandNumeric"] = cust["IncomeBand"].apply(_income_band_to_numeric)
    if "Postcode" in cust.columns:
        cust["PostcodeArea"] = cust["Postcode"].apply(_postcode_to_area)
        cust = cust.drop(columns=["Postcode"])

    policy_features = _build_policy_features(policies)
    txn_features = _build_txn_features(txns)
    event_features = _build_event_features(events)

    out = cust.merge(policy_features, on="CustomerID", how="left").merge(txn_features, on="CustomerID", how="left")
    if event_features is not None:
        out = out.merge(event_features, on="CustomerID", how="left")

    return out


def _load_assignments_and_profiles(outputs_dir: str) -> Dict[str, pd.DataFrame]:
    return {
        "agnostic_assign": pd.read_csv(os.path.join(outputs_dir, "product_agnostic_assignments.csv")),
        "agnostic_profile": pd.read_csv(os.path.join(outputs_dir, "product_agnostic_cluster_profile.csv")),
        "whole_life_assign": pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_whole_life.csv")),
        "whole_life_profile": pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_whole_life.csv")),
        "term_life_assign": pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_term_life.csv")),
        "term_life_profile": pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_term_life.csv")),
    }


def _build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )
    return preprocessor


def _train_and_evaluate(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, model_type: str, random_state: int) -> PropensityResult:
    preprocessor = _build_preprocessor(X_train)

    if model_type == "logistic":
        model = LogisticRegression(max_iter=1000, random_state=random_state, n_jobs=-1)
    elif model_type == "rf":
        model = RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1, class_weight="balanced")
    elif model_type == "xgboost":
        model = XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            eval_metric="logloss",
            n_jobs=-1,
        )
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    pipe = Pipeline(steps=[("prep", preprocessor), ("clf", model)])
    pipe.fit(X_train, y_train)

    # Get feature names after preprocessing
    if hasattr(preprocessor, "get_feature_names_out"):
        feature_names = list(preprocessor.get_feature_names_out())
    else:
        # Fallback for older sklearn versions
        ohe = preprocessor.named_transformers_["cat"].named_steps["onehot"]
        cat_features = ohe.get_feature_names_out([c for c in X_train.columns if c not in preprocessor.named_transformers_["num"]])
        num_features = preprocessor.named_transformers_["num"].get_feature_names_out()
        feature_names = list(num_features) + list(cat_features)

    y_proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)

    # Precision at top 10%
    top_n = max(1, int(0.1 * len(y_test)))
    top_idx = np.argsort(-y_proba)[:top_n]
    precision_at_10 = y_test.iloc[top_idx].mean()

    propensity_df = pd.DataFrame({"CustomerID": X_test.index, "propensity": y_proba})

    return PropensityResult(model=pipe, feature_names_in=feature_names, auc=auc, precision_at_10=precision_at_10, propensity_scores=propensity_df)


def _prepare_labels_for_target(customer_table: pd.DataFrame, assignments: pd.DataFrame, target_cluster_id: int) -> pd.Series:
    merged = customer_table.merge(assignments, on="CustomerID", how="left")
    # Label 1 if in target cluster, 0 otherwise (including NaN)
    y = (merged["cluster"] == target_cluster_id).astype(int)
    y.index = merged["CustomerID"]
    return y


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__)), help="Folder with input CSVs")
    parser.add_argument("--outputs-dir", default=os.path.join(os.path.dirname(__file__), "outputs"), help="Folder with clustering results")
    parser.add_argument("--propensity-dir", default=os.path.join(os.path.dirname(__file__), "propensity_outputs"), help="Folder to write propensity results")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.propensity_dir, exist_ok=True)

    # Load data and assignments
    customers, policies, txns, events = _read_inputs(args.data_dir)
    customer_table = _assemble_customer_table(customers, policies, txns, events)
    assign_dict = _load_assignments_and_profiles(args.outputs_dir)

    # Identify customers without Whole Life or Term Life
    whole_life_customers = set(policies[policies["Product"] == "Whole Life"]["CustomerID"])
    term_life_customers = set(policies[policies["Product"] == "Term Life"]["CustomerID"])

    # Prepare features (same as clustering)
    feature_cols = [c for c in customer_table.columns if c != "CustomerID"]
    X = customer_table.set_index("CustomerID")[feature_cols]

    # Target 1: Whole Life Cluster 0 (mainstream)
    y_whole = _prepare_labels_for_target(customer_table, assign_dict["whole_life_assign"], target_cluster_id=0)
    # Train only on customers who already have Whole Life
    train_idx_whole = X.index.intersection(whole_life_customers)
    X_train_whole = X.loc[train_idx_whole]
    y_train_whole = y_whole.loc[train_idx_whole]
    # Predict for customers without Whole Life
    test_idx_whole = X.index.difference(whole_life_customers)
    X_test_whole = X.loc[test_idx_whole]
    y_test_whole = y_whole.loc[test_idx_whole]  # will be all 0s; we use only for scoring shape

    # Target 2: Term Life Cluster 1 (higher-income, digitally active)
    y_term = _prepare_labels_for_target(customer_table, assign_dict["term_life_assign"], target_cluster_id=1)
    train_idx_term = X.index.intersection(term_life_customers)
    X_train_term = X.loc[train_idx_term]
    y_train_term = y_term.loc[train_idx_term]
    test_idx_term = X.index.difference(term_life_customers)
    X_test_term = X.loc[test_idx_term]
    y_test_term = y_term.loc[test_idx_term]

    # Train models (example: logistic for interpretability; can add RF/XGB)
    results = {}
    for name, X_tr, y_tr, X_te, y_te in [
        ("whole_life_cluster0", X_train_whole, y_train_whole, X_test_whole, y_test_whole),
        ("term_life_cluster1", X_train_term, y_train_term, X_test_term, y_test_term),
    ]:
        if len(X_tr) < 10 or y_tr.sum() < 2:
            print(f"Skipping {name}: insufficient training data")
            continue
        # Train logistic regression for interpretability
        res = _train_and_evaluate(X_tr, y_tr, X_te, y_te, model_type="logistic", random_state=args.random_state)
        results[name] = res
        # Save propensity scores
        out_path = os.path.join(args.propensity_dir, f"propensity_{name}.csv")
        res.propensity_scores.to_csv(out_path, index=False)
        # Save model summary
        summary_path = os.path.join(args.propensity_dir, f"summary_{name}.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"Target: {name}\n")
            f.write(f"AUC: {res.auc:.4f}\n")
            f.write(f"Precision@10%: {res.precision_at_10:.4f}\n")
            f.write(f"Training positives: {int(y_tr.sum())} / {len(y_tr)}\n")
            f.write(f"Test customers: {len(y_te)}\n")
        print(f"Saved propensity for {name}: AUC={res.auc:.3f}, Precision@10%={res.precision_at_10:.3f}")

    # Optional: combine propensity scores into one file for downstream use
    combined = None
    for name, res in results.items():
        df = res.propensity_scores.copy()
        df = df.rename(columns={"propensity": f"propensity_{name}"})
        if combined is None:
            combined = df
        else:
            combined = combined.merge(df, on="CustomerID", how="outer")
    if combined is not None:
        combined_path = os.path.join(args.propensity_dir, "propensity_combined.csv")
        combined.to_csv(combined_path, index=False)
        print(f"Combined propensity scores written to: {combined_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
