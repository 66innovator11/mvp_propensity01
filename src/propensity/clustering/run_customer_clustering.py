import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..utils.paths import get_resource_path


@dataclass(frozen=True)
class ClusteringResult:
    assignments: pd.DataFrame
    profile: pd.DataFrame
    k: int
    silhouette: float


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
    customer_path = get_resource_path("customer_profile.csv", data_dir)
    policy_path = get_resource_path("insurance_products.csv", data_dir)
    txn_path = get_resource_path("transactions.csv", data_dir)
    events_path = get_resource_path("customer_events.csv", data_dir)

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


def _choose_k_and_fit(df: pd.DataFrame, id_col: str, k_min: int, k_max: int, random_state: int) -> tuple[Pipeline, int, float]:
    x = df.drop(columns=[id_col])

    numeric_cols = [c for c in x.columns if pd.api.types.is_numeric_dtype(x[c])]
    categorical_cols = [c for c in x.columns if c not in numeric_cols]

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

    best_k = None
    best_score = -np.inf
    best_pipeline = None

    n = len(df)
    k_upper = min(k_max, max(2, n - 1))
    k_lower = min(k_min, k_upper)

    for k in range(k_lower, k_upper + 1):
        model = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
        pipe = Pipeline(steps=[("prep", preprocessor), ("model", model)])
        pipe.fit(x)
        labels = pipe.named_steps["model"].labels_
        if len(set(labels)) < 2:
            continue
        x_trans = pipe.named_steps["prep"].transform(x)
        score = float(silhouette_score(x_trans, labels))
        if score > best_score:
            best_score = score
            best_k = k
            best_pipeline = pipe

    if best_pipeline is None or best_k is None:
        best_k = 2
        best_pipeline = Pipeline(steps=[("prep", preprocessor), ("model", KMeans(n_clusters=best_k, random_state=random_state, n_init="auto"))])
        best_pipeline.fit(x)
        x_trans = best_pipeline.named_steps["prep"].transform(x)
        labels = best_pipeline.named_steps["model"].labels_
        best_score = float(silhouette_score(x_trans, labels)) if len(set(labels)) > 1 else float("nan")

    return best_pipeline, int(best_k), float(best_score)


def _profile_clusters(df: pd.DataFrame, id_col: str, cluster_col: str) -> pd.DataFrame:
    tmp = df.copy()

    numeric_cols = [c for c in tmp.columns if c not in [id_col, cluster_col] and pd.api.types.is_numeric_dtype(tmp[c])]
    cat_cols = [c for c in tmp.columns if c not in [id_col, cluster_col] and c not in numeric_cols]

    parts = []
    num_profile = tmp.groupby(cluster_col)[numeric_cols].mean(numeric_only=True)
    parts.append(num_profile)

    for c in cat_cols:
        top = (
            tmp.groupby([cluster_col, c])[id_col]
            .count()
            .rename("count")
            .reset_index()
            .sort_values([cluster_col, "count"], ascending=[True, False])
        )
        top = top.groupby(cluster_col).head(1).set_index(cluster_col)
        top = top[[c, "count"]].rename(columns={c: f"{c}_top", "count": f"{c}_top_count"})
        parts.append(top)

    out = pd.concat(parts, axis=1)
    out["cluster_size"] = tmp.groupby(cluster_col)[id_col].count()
    out = out.reset_index()
    return out


def run_product_agnostic_clustering(customer_table: pd.DataFrame, k_min: int, k_max: int, random_state: int) -> ClusteringResult:
    df = customer_table.copy()

    pipeline, k, sil = _choose_k_and_fit(df, id_col="CustomerID", k_min=k_min, k_max=k_max, random_state=random_state)

    x = df.drop(columns=["CustomerID"])
    labels = pipeline.predict(x)

    assignments = df[["CustomerID"]].copy()
    assignments["cluster"] = labels

    prof_df = df.merge(assignments, on="CustomerID", how="left")
    profile = _profile_clusters(prof_df, id_col="CustomerID", cluster_col="cluster")

    return ClusteringResult(assignments=assignments, profile=profile, k=k, silhouette=sil)


def _build_product_specific_policy_features(policies: pd.DataFrame, product: str) -> pd.DataFrame:
    df = policies[policies["Product"] == product].copy()

    for c in ["CoverageAmount", "PremiumAmount", "PolicyTermYears"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["is_active_policy"] = (df["Status"].astype(str).str.lower() == "active").astype(int)
    df["is_lapsed_policy"] = (df["Status"].astype(str).str.lower() == "lapsed").astype(int)

    agg = df.groupby("CustomerID").agg(
        product_policy_count=("PolicyID", "count"),
        product_policy_active_count=("is_active_policy", "sum"),
        product_policy_lapsed_count=("is_lapsed_policy", "sum"),
        product_coverage_sum=("CoverageAmount", "sum"),
        product_coverage_mean=("CoverageAmount", "mean"),
        product_premium_sum=("PremiumAmount", "sum"),
        product_premium_mean=("PremiumAmount", "mean"),
        product_term_mean=("PolicyTermYears", "mean"),
    )

    return agg.reset_index()


def run_product_wise_clustering(customer_table: pd.DataFrame, policies: pd.DataFrame, k_min: int, k_max: int, random_state: int) -> Dict[str, ClusteringResult]:
    results: Dict[str, ClusteringResult] = {}
    products = sorted([p for p in policies["Product"].dropna().unique()])

    base_cols = [c for c in customer_table.columns if c != "Product"]
    base = customer_table[base_cols].copy()

    for product in products:
        prod_features = _build_product_specific_policy_features(policies, product)
        prod_df = base.merge(prod_features, on="CustomerID", how="inner")
        if len(prod_df) < max(10, k_min * 3):
            continue
        pipeline, k, sil = _choose_k_and_fit(prod_df, id_col="CustomerID", k_min=k_min, k_max=k_max, random_state=random_state)
        x = prod_df.drop(columns=["CustomerID"])
        labels = pipeline.predict(x)

        assignments = prod_df[["CustomerID"]].copy()
        assignments["product"] = product
        assignments["cluster"] = labels

        prof_df = prod_df.merge(assignments[["CustomerID", "cluster"]], on="CustomerID", how="left")
        profile = _profile_clusters(prof_df, id_col="CustomerID", cluster_col="cluster")

        results[product] = ClusteringResult(assignments=assignments, profile=profile, k=k, silhouette=sil)

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__)), help="Folder containing the input CSV files")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "outputs"), help="Folder to write clustering results")
    parser.add_argument("--k-min", type=int, default=2)
    parser.add_argument("--k-max", type=int, default=10)
    parser.add_argument("--random-state", type=int, default=42)

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    customers, policies, txns, events = _read_inputs(args.data_dir)
    customer_table = _assemble_customer_table(customers, policies, txns, events)

    agnostic = run_product_agnostic_clustering(customer_table, k_min=args.k_min, k_max=args.k_max, random_state=args.random_state)
    agnostic.assignments.to_csv(os.path.join(args.output_dir, "product_agnostic_assignments.csv"), index=False)
    agnostic.profile.to_csv(os.path.join(args.output_dir, "product_agnostic_cluster_profile.csv"), index=False)

    metrics = pd.DataFrame(
        [
            {
                "scope": "product_agnostic",
                "k": agnostic.k,
                "silhouette": agnostic.silhouette,
                "n_customers": int(agnostic.assignments["CustomerID"].nunique()),
            }
        ]
    )

    product_results = run_product_wise_clustering(customer_table, policies, k_min=args.k_min, k_max=args.k_max, random_state=args.random_state)

    for product, res in product_results.items():
        slug = _sanitize_filename(product)
        res.assignments.to_csv(os.path.join(args.output_dir, f"product_wise_assignments_{slug}.csv"), index=False)
        res.profile.to_csv(os.path.join(args.output_dir, f"product_wise_cluster_profile_{slug}.csv"), index=False)
        metrics = pd.concat(
            [
                metrics,
                pd.DataFrame(
                    [
                        {
                            "scope": f"product_wise::{product}",
                            "k": res.k,
                            "silhouette": res.silhouette,
                            "n_customers": int(res.assignments["CustomerID"].nunique()),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    metrics.to_csv(os.path.join(args.output_dir, "clustering_metrics.csv"), index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
