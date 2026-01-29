import argparse
import os
import random
import sys
from typing import Optional

import pandas as pd
import requests

# ---------------------------
# Data loading helpers
# ---------------------------
def _read_inputs(data_dir: str):
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


def _assemble_customer_table(customers: pd.DataFrame, policies: pd.DataFrame, txns: pd.DataFrame, events: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Reuse the same feature engineering as clustering/propensity."""
    import re
    import numpy as np

    def _income_band_to_numeric(value: str) -> float:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return np.nan
        s = str(value).strip().replace(",", "").replace("–", "-")
        if s.startswith("<"):
            m = re.search(r"(\d+)", s)
            return float(m.group(1)) * 500.0 if m else np.nan
        if s.startswith(">"):
            m = re.search(r"(\d+)", s)
            return float(m.group(1)) * 1150.0 if m else np.nan
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
        return m.group(1) if m else "unknown"

    # Demographics
    cust = customers.copy()
    cust["IncomeBandNumeric"] = cust["IncomeBand"].apply(_income_band_to_numeric)
    if "Postcode" in cust.columns:
        cust["PostcodeArea"] = cust["Postcode"].apply(_postcode_to_area)
        cust = cust.drop(columns=["Postcode"])

    # Policy aggregates
    pol = policies.copy()
    for c in ["CoverageAmount", "PremiumAmount", "PolicyTermYears"]:
        pol[c] = pd.to_numeric(pol[c], errors="coerce")
    max_date = pol["PolicyStartDate"].max()
    if pd.isna(max_date):
        max_date = pd.Timestamp("2025-01-01")
    pol["is_active"] = (pol["Status"].astype(str).str.lower() == "active").astype(int)
    pol["policy_age_days"] = (max_date - pol["PolicyStartDate"]).dt.days
    pol_agg = pol.groupby("CustomerID").agg(
        policy_count=("PolicyID", "count"),
        policy_active_count=("is_active", "sum"),
        coverage_sum=("CoverageAmount", "sum"),
        coverage_mean=("CoverageAmount", "mean"),
        premium_sum=("PremiumAmount", "sum"),
        premium_mean=("PremiumAmount", "mean"),
        term_mean=("PolicyTermYears", "mean"),
        policy_age_days_min=("policy_age_days", "min"),
        policy_age_days_max=("policy_age_days", "max"),
    ).reset_index()

    # Transaction aggregates
    txn = txns.copy()
    txn["Amount"] = pd.to_numeric(txn["Amount"], errors="coerce")
    txn["is_credit"] = (txn["TransactionType"].astype(str).str.lower() == "credit").astype(int)
    txn["is_debit"] = (txn["TransactionType"].astype(str).str.lower() == "debit").astype(int)
    txn["credit_amount"] = np.where(txn["is_credit"] == 1, txn["Amount"], 0.0)
    txn["debit_amount"] = np.where(txn["is_debit"] == 1, txn["Amount"], 0.0)
    txn["txn_month"] = txn["TransactionDate"].dt.to_period("M").astype(str)

    txn_base = txn.groupby("CustomerID").agg(
        txn_count=("TransactionID", "count"),
        credit_sum=("credit_amount", "sum"),
        debit_sum=("debit_amount", "sum"),
        amount_mean=("Amount", "mean"),
        active_months=("txn_month", "nunique"),
        txn_last_date=("TransactionDate", "max"),
    )
    txn_base["net_flow"] = txn_base["credit_sum"] - txn_base["debit_sum"]
    txn_base["credit_share"] = txn_base["credit_sum"] / (txn_base["credit_sum"] + txn_base["debit_sum"]).replace(0, np.nan)
    txn_base["avg_credit_per_month"] = txn_base["credit_sum"] / txn_base["active_months"].replace(0, np.nan)
    txn_base["avg_debit_per_month"] = txn_base["debit_sum"] / txn_base["active_months"].replace(0, np.nan)
    txn_base["avg_txn_per_month"] = txn_base["txn_count"] / txn_base["active_months"].replace(0, np.nan)

    max_txn_date = txn["TransactionDate"].max()
    if pd.isna(max_txn_date):
        max_txn_date = pd.Timestamp("2025-01-01")
    txn_base["days_since_last_txn"] = (max_txn_date - txn_base["txn_last_date"]).dt.days
    txn_base = txn_base.drop(columns=["txn_last_date"]).reset_index()

    # Event aggregates
    event_agg = None
    if events is not None and not events.empty:
        ev = events.copy()
        ev_counts = ev.pivot_table(index="CustomerID", columns="Event", values="Year", aggfunc="count", fill_value=0).add_prefix("event_count_").reset_index()
        ev_last = ev.groupby("CustomerID")["Year"].max().rename("event_last_year").reset_index()
        event_agg = ev_counts.merge(ev_last, on="CustomerID", how="left")

    # Merge
    out = cust.merge(pol_agg, on="CustomerID", how="left").merge(txn_base, on="CustomerID", how="left")
    if event_agg is not None:
        out = out.merge(event_agg, on="CustomerID", how="left")
    return out


# ---------------------------
# LLM helpers
# ---------------------------
def _ollama_generate(prompt: str, model: str = "llama3.2:3b", timeout: int = 30) -> Optional[str]:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.4, "num_predict": 300}
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama request failed: {e}", file=sys.stderr)
        return None


# ---------------------------
# Narrative builders
# ---------------------------
def _build_customer_360(row: pd.Series) -> str:
    parts = []
    if pd.notna(row["Age"]):
        parts.append(f"Age {int(row['Age'])}")
    if pd.notna(row["Gender"]):
        parts.append(row["Gender"])
    if pd.notna(row["City"]):
        parts.append(f"lives in {row['City']}")
    if pd.notna(row["IncomeBand"]):
        parts.append(f"income band {row['IncomeBand']}")
    if pd.notna(row["CreditScore"]):
        parts.append(f"credit score {int(row['CreditScore'])}")
    if pd.notna(row["policy_count"]):
        parts.append(f"holds {int(row['policy_count'])} policies")
    if pd.notna(row["coverage_sum"]) and row["coverage_sum"] > 0:
        parts.append(f"total coverage £{row['coverage_sum']:,.0f}")
    if pd.notna(row["premium_sum"]) and row["premium_sum"] > 0:
        parts.append(f"total premiums £{row['premium_sum']:,.0f}")
    if pd.notna(row["net_flow"]) and row["net_flow"] > 0:
        parts.append(f"positive net cash flow £{row['net_flow']:,.0f}")
    if pd.notna(row["avg_txn_per_month"]) and row["avg_txn_per_month"] > 0:
        parts.append(f"averages {row['avg_txn_per_month']:.1f} transactions per month")
    return "; ".join(parts) + "."


def _build_product_narrative(target_product: str, cluster_profile: pd.Series) -> str:
    return (
        f"The target product is {target_product}. "
        f"Customers like this cluster (size {int(cluster_profile['cluster_size'])}) "
        f"typically have income around £{cluster_profile['IncomeBandNumeric']:,.0f}, "
        f"credit share {cluster_profile['credit_share']*100:.0f}%, "
        f"net cash flow £{cluster_profile['net_flow']:,.0f}, "
        f"and policy coverage £{cluster_profile['coverage_mean']:,.0f}. "
        f"They tend to be {cluster_profile['Gender_top'].lower()} and live in {cluster_profile['City_top']}."
    )


def _build_email_prompt(customer_360: str, product_narrative: str, target_product: str) -> str:
    return (
        f"You are a skilled insurance marketer. Write a concise, professional outreach email to a customer. "
        f"Use ONLY the facts below. Do not invent any details. "
        f"Explain why {target_product} may be useful now or in the future based on these facts. "
        f"Keep it under 150 words. Include a clear call to action.\n\n"
        f"Customer profile: {customer_360}\n\n"
        f"Product and peer insights: {product_narrative}\n\n"
        f"Email:"
    )


# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__)), help="Folder with input CSVs")
    parser.add_argument("--propensity-dir", default=os.path.join(os.path.dirname(__file__), "propensity_outputs"), help="Folder with propensity CSVs")
    parser.add_argument("--outputs-dir", default=os.path.join(os.path.dirname(__file__), "outreach_outputs"), help="Folder to write outreach artifacts")
    parser.add_argument("--model", default="llama3.2:3b", help="Ollama model name")
    args = parser.parse_args()

    os.makedirs(args.outputs_dir, exist_ok=True)

    # Load propensity table with rationale
    rationale_path = os.path.join(args.propensity_dir, "propensity_summary_with_rationale.csv")
    rationale_df = pd.read_csv(rationale_path, index_col=0)

    # Load propensity scores and filter to medium band (0.6–0.9)
    combined_path = os.path.join(args.propensity_dir, "propensity_combined.csv")
    combined_df = pd.read_csv(combined_path)

    # Determine target product per cluster
    target_map = {
        "whole_life_cluster0": "Whole Life",
        "term_life_cluster1": "Term Life",
    }

    # Randomly pick one customer from the table
    chosen = rationale_df.sample(1).iloc[0]
    target_key = chosen.name
    target_product = target_map.get(target_key, "Unknown")
    print(f"Chosen target: {target_key} ({target_product})")

    # Load full customer table
    customers, policies, txns, events = _read_inputs(args.data_dir)
    cust_table = _assemble_customer_table(customers, policies, txns, events)

    # Load propensity scores for the target
    propensity_col = f"propensity_{target_key}"
    prop_df = combined_df[["CustomerID", propensity_col]].dropna()
    # Filter to medium band (0.6–0.9)
    medium_df = prop_df[(prop_df[propensity_col] >= 0.6) & (prop_df[propensity_col] < 0.9)]
    if medium_df.empty:
        print("No customers in medium band for this target.")
        return 1

    # Randomly pick a customer from medium band
    chosen_customer_id = medium_df.sample(1)["CustomerID"].iloc[0]
    cust_row = cust_table[cust_table["CustomerID"] == chosen_customer_id].iloc[0]

    # Load cluster profile for narrative
    if "whole_life" in target_key:
        profile_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), "outputs"), "product_wise_cluster_profile_whole_life.csv"))
        cluster_id = 0
    elif "term_life" in target_key:
        profile_df = pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), "outputs"), "product_wise_cluster_profile_term_life.csv"))
        cluster_id = 1
    else:
        profile_df = pd.DataFrame()
        cluster_id = 0
    cluster_profile = profile_df[profile_df["cluster"] == cluster_id].iloc[0] if not profile_df.empty else pd.Series()

    # Build narratives
    customer_360 = _build_customer_360(cust_row)
    product_narrative = _build_product_narrative(target_product, cluster_profile)

    # Generate email via LLM
    email_prompt = _build_email_prompt(customer_360, product_narrative, target_product)
    email_body = _ollama_generate(email_prompt, model=args.model) or "LLM generation failed."

    # Save artifacts
    artifacts = {
        "customer_id": chosen_customer_id,
        "target_product": target_product,
        "customer_360": customer_360,
        "product_narrative": product_narrative,
        "email_body": email_body,
        "key_reasons_for_nudge": chosen["business_rationale"],
    }
    out_path = os.path.join(args.outputs_dir, f"outreach_{chosen_customer_id}_{target_key}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Personalized Outreach: {chosen_customer_id}\n\n")
        f.write(f"## Target Product\n{target_product}\n\n")
        f.write(f"## Customer 360 View\n{customer_360}\n\n")
        f.write(f"## Peer Insights (Why similar customers bought)\n{product_narrative}\n\n")
        f.write(f"## Key Reasons for Nudge\n{chosen['business_rationale']}\n\n")
        f.write(f"## Draft Email\n\n{email_body}\n")
    print(f"Outreach artifact saved to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
