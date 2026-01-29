import argparse
import os

import pandas as pd

from ..utils.paths import get_output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--propensity-dir", default=os.path.join(os.path.dirname(__file__), "propensity_outputs"), help="Folder with propensity CSVs")
    parser.add_argument("--output-path", default=get_output_path("propensity_summary_by_band.csv", os.path.join(os.path.dirname(__file__), "propensity_outputs")), help="Path to write summary table")
    args = parser.parse_args()

    # Load combined propensity
    combined_path = os.path.join(args.propensity_dir, "propensity_combined.csv")
    df = pd.read_csv(combined_path)

    # Define propensity bands
    bins = [0.0, 0.6, 0.9, 1.0]
    labels = ["Low", "Medium", "High"]
    for col in ["propensity_whole_life_cluster0", "propensity_term_life_cluster1"]:
        df[f"{col}_band"] = pd.cut(df[col], bins=bins, labels=labels, right=False, include_lowest=True)

    # Count customers by band for each product
    summary = {}
    for prod in ["whole_life_cluster0", "term_life_cluster1"]:
        band_counts = df[f"propensity_{prod}_band"].value_counts().reindex(labels, fill_value=0)
        summary[prod] = band_counts

    summary_df = pd.DataFrame(summary).T
    # Filter to Medium only (exclude Low and High)
    medium_only = summary_df[["Medium"]].rename(columns={"Medium": "Medium customers"})
    # Add percentage of total customers in medium band
    total_customers = len(df)
    medium_only["% of total"] = (medium_only["Medium customers"] / total_customers * 100).round(1)

    # Save
    medium_only.to_csv(args.output_path)
    print(f"Propensity summary (Medium band only) written to: {args.output_path}")
    print(medium_only)

    # Load auto-generated explanations
    auto_path = get_output_path("auto_explanations.csv", os.path.join(os.path.dirname(__file__), "propensity_outputs"))
    auto_df = pd.read_csv(auto_path)
    # Map target to rationale
    rationale_map = {
        "whole_life_cluster0": {
            "business_rationale": auto_df.loc[auto_df["target"] == "whole_life_cluster0", "business_rationale"].iloc[0],
            "technical_validity": auto_df.loc[auto_df["target"] == "whole_life_cluster0", "technical_validity"].iloc[0],
        },
        "term_life_cluster1": {
            "business_rationale": auto_df.loc[auto_df["target"] == "term_life_cluster1", "business_rationale"].iloc[0],
            "technical_validity": auto_df.loc[auto_df["target"] == "term_life_cluster1", "technical_validity"].iloc[0],
        },
    }
    rationale = pd.DataFrame(rationale_map).T

    # Combine counts with rationale
    final_table = medium_only.join(rationale)
    rationale_path = get_output_path("propensity_summary_with_rationale.csv", os.path.join(os.path.dirname(__file__), "propensity_outputs"))
    final_table.to_csv(rationale_path)
    print(f"\nTable with rationale written to: {rationale_path}")
    print(final_table)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
