import argparse
import json
import os
import sys
from typing import Dict, List, Optional

import pandas as pd
import requests


def _ollama_generate(prompt: str, model: str = "llama3.2:3b", timeout: int = 45) -> Optional[str]:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 800}
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama request failed: {e}", file=sys.stderr)
        return None


def _load_clustering_results(outputs_dir: str) -> Dict[str, pd.DataFrame]:
    return {
        "agnostic_profile": pd.read_csv(os.path.join(outputs_dir, "product_agnostic_cluster_profile.csv")),
        "agnostic_assign": pd.read_csv(os.path.join(outputs_dir, "product_agnostic_assignments.csv")),
        "whole_life_profile": pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_whole_life.csv")),
        "whole_life_assign": pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_whole_life.csv")),
        "term_life_profile": pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_term_life.csv")),
        "term_life_assign": pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_term_life.csv")),
        "metrics": pd.read_csv(os.path.join(outputs_dir, "clustering_metrics.csv")),
    }


def _summarize_cluster(profile_row: pd.Series) -> str:
    parts = []
    if pd.notna(profile_row["Age"]):
        parts.append(f"Mean age {profile_row['Age']:.1f}")
    if pd.notna(profile_row["IncomeBandNumeric"]):
        parts.append(f"Income ~£{profile_row['IncomeBandNumeric']:,.0f}")
    if pd.notna(profile_row["credit_share"]):
        parts.append(f"Credit share {profile_row['credit_share']*100:.0f}%")
    if pd.notna(profile_row["net_flow"]):
        parts.append(f"Net flow £{profile_row['net_flow']:,.0f}")
    if pd.notna(profile_row["coverage_mean"]):
        parts.append(f"Coverage £{profile_row['coverage_mean']:,.0f}")
    if pd.notna(profile_row["Gender_top"]):
        parts.append(f"Mostly {profile_row['Gender_top'].lower()}")
    if pd.notna(profile_row["City_top"]):
        parts.append(f"Top city {profile_row['City_top']}")
    return "; ".join(parts) + "."


def _build_clustering_report_prompt(results: Dict[str, pd.DataFrame]) -> str:
    prompt = (
        "You are a senior insurance analytics analyst. Write a clear, concise business report summarizing the clustering results. "
        "For each cluster (product-agnostic and product-wise), provide: 1) a short name, 2) a brief description of the group’s demographics and behavior, 3) business importance. "
        "Use the statistics provided. Keep the report under 500 words. Use markdown headings.\n\n"
    )
    # Product-agnostic
    agnostic_metrics = results["metrics"][results["metrics"]["scope"] == "product_agnostic"].iloc[0]
    prompt += f"## Product-Agnostic Segments (k={agnostic_metrics['k']}, silhouette={agnostic_metrics['silhouette']:.3f})\n\n"
    for _, row in results["agnostic_profile"].iterrows():
        cid = int(row["cluster"])
        size = int(row["cluster_size"])
        summary = _summarize_cluster(row)
        prompt += f"### Cluster {cid} (Size: {size})\n{summary}\n\n"
    # Product-wise
    for product in ["Whole Life", "Term Life"]:
        key = product.lower().replace(" ", "_") + "_profile"
        assign_key = product.lower().replace(" ", "_") + "_assign"
        profile_df = results[key]
        assign_df = results[assign_key]
        metric_row = results["metrics"][results["metrics"]["scope"] == f"product_wise::{product}"].iloc[0]
        prompt += f"## {product} Segments (k={metric_row['k']}, silhouette={metric_row['silhouette']:.3f})\n\n"
        for _, row in profile_df.iterrows():
            cid = int(row["cluster"])
            size = int(row["cluster_size"])
            summary = _summarize_cluster(row)
            prompt += f"### Cluster {cid} (Size: {size})\n{summary}\n\n"
    prompt += "End of report."
    return prompt


def _build_model_report_prompt(insights_dir: str) -> str:
    prompt = (
        "You are a senior data science analyst. Write a concise report on the propensity models used. "
        "Include: 1) model name, 2) reason for selection, 3) top predictors with relative importance, 4) any derived features. "
        "Keep it under 400 words. Use markdown headings.\n\n"
    )
    for target in ["whole_life_cluster0", "term_life_cluster1"]:
        path = os.path.join(insights_dir, f"feature_importance_{target}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            top_features = df.head(5)[["feature", "abs_importance"]].to_dict(orient="records")
            prompt += f"## Model for {target.replace('_', ' ').title()}\n\n"
            prompt += "Model: Logistic Regression (interpretable, calibrated probabilities).\n\n"
            prompt += "Reason: Chosen for interpretability and to provide propensity scores for targeting.\n\n"
            prompt += "Top predictors:\n"
            for row in top_features:
                prompt += f"- {row['feature']}: importance {row['abs_importance']:.4f}\n"
            prompt += "\nDerived features include income band numeric, postcode area, net cash flow, credit/debit shares, and event counts.\n\n"
    prompt += "End of report."
    return prompt


def _build_propensity_report_prompt(propensity_dir: str, results: Dict[str, pd.DataFrame]) -> str:
    # Load combined propensity and filter medium band
    combined_path = os.path.join(propensity_dir, "propensity_combined.csv")
    combined_df = pd.read_csv(combined_path)
    medium_rows = []
    for col in ["propensity_whole_life_cluster0", "propensity_term_life_cluster1"]:
        if col in combined_df.columns:
            sub = combined_df[(combined_df[col] >= 0.6) & (combined_df[col] < 0.9)][["CustomerID", col]]
            sub = sub.rename(columns={col: "propensity"})
            sub["target"] = col.replace("propensity_", "").replace("_cluster0", "").replace("_cluster1", "")
            medium_rows.append(sub)
    medium_df = pd.concat(medium_rows, ignore_index=True)
    # Summarize counts
    summary = medium_df["target"].value_counts().to_dict()
    prompt = (
        "You are a senior insurance analyst. Write a brief report summarizing the cross-sell opportunity based on propensity scores. "
        "Include a table of the best product-wise clusters and the count of non-customers with propensity 0.6–0.9. "
        "Explain why these clusters were chosen using their statistics. Keep it under 300 words. Use markdown.\n\n"
        "## Propensity-Based Cross-Sell Targets\n\n"
        f"- Whole Life Cluster 0: {summary.get('whole_life', 0)} non-customers with propensity 0.6–0.9.\n"
        f"- Term Life Cluster 1: {summary.get('term_life', 0)} non-customers with propensity 0.6–0.9.\n\n"
        "These clusters were chosen because they represent high-propensity, medium-likelihood segments. "
        "Whole Life Cluster 0 customers tend to have higher income, strong credit share, and stable coverage, indicating low risk and receptiveness to premium products. "
        "Term Life Cluster 1 customers show higher income, strong net cash flow, and digital engagement, making them ideal for premium term offerings. "
        "Targeting these groups maximizes conversion efficiency while avoiding very high or low propensity extremes.\n\n"
        "End of report."
    )
    return prompt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", default=os.path.join(os.path.dirname(__file__), "outputs"), help="Folder with clustering results")
    parser.add_argument("--propensity-dir", default=os.path.join(os.path.dirname(__file__), "propensity_outputs"), help="Folder with propensity outputs")
    parser.add_argument("--insights-dir", default=os.path.join(os.path.dirname(__file__), "insights_outputs"), help="Folder with model insights")
    parser.add_argument("--reports-dir", default=os.path.join(os.path.dirname(__file__), "llm_reports"), help="Folder to write LLM-generated reports")
    parser.add_argument("--model", default="llama3.2:3b", help="Ollama model name")
    args = parser.parse_args()

    os.makedirs(args.reports_dir, exist_ok=True)

    # 1) Clustering report
    results = _load_clustering_results(args.outputs_dir)
    clustering_prompt = _build_clustering_report_prompt(results)
    clustering_report = _ollama_generate(clustering_prompt, model=args.model) or "Failed to generate clustering report."
    clustering_path = os.path.join(args.reports_dir, "1_clustering_analysis_report.md")
    with open(clustering_path, "w", encoding="utf-8") as f:
        f.write(clustering_report)
    print(f"Clustering report saved to {clustering_path}")

    # 2) Model report
    model_report_prompt = _build_model_report_prompt(args.insights_dir)
    model_report = _ollama_generate(model_report_prompt, model=args.model) or "Failed to generate model report."
    model_path = os.path.join(args.reports_dir, "2_propensity_model_report.md")
    with open(model_path, "w", encoding="utf-8") as f:
        f.write(model_report)
    print(f"Model report saved to {model_path}")

    # 3) Propensity cross-sell report
    propensity_prompt = _build_propensity_report_prompt(args.propensity_dir, results)
    propensity_report = _ollama_generate(propensity_prompt, model=args.model) or "Failed to generate propensity report."
    propensity_path = os.path.join(args.reports_dir, "3_propensity_cross_sell_report.md")
    with open(propensity_path, "w", encoding="utf-8") as f:
        f.write(propensity_report)
    print(f"Propensity cross-sell report saved to {propensity_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
