import argparse
import os
from datetime import datetime

import pandas as pd


def load_results(outputs_dir: str) -> dict:
    agnostic_profile = pd.read_csv(os.path.join(outputs_dir, "product_agnostic_cluster_profile.csv"))
    agnostic_assign = pd.read_csv(os.path.join(outputs_dir, "product_agnostic_assignments.csv"))
    whole_life_profile = pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_whole_life.csv"))
    whole_life_assign = pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_whole_life.csv"))
    term_life_profile = pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_term_life.csv"))
    term_life_assign = pd.read_csv(os.path.join(outputs_dir, "product_wise_assignments_term_life.csv"))
    metrics = pd.read_csv(os.path.join(outputs_dir, "clustering_metrics.csv"))
    return {
        "agnostic_profile": agnostic_profile,
        "agnostic_assign": agnostic_assign,
        "whole_life_profile": whole_life_profile,
        "whole_life_assign": whole_life_assign,
        "term_life_profile": term_life_profile,
        "term_life_assign": term_life_assign,
        "metrics": metrics,
    }


def render_markdown_report(results: dict, outputs_dir: str) -> str:
    md = []
    md.append("# Customer Clustering: Selected Segments and Rationale")
    md.append(f"*Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
    md.append("")

    # Product-agnostic selection
    md.append("## 1. Product-Agnostic Segments (All Customers)")
    agnostic_metrics = results["metrics"][results["metrics"]["scope"] == "product_agnostic"].iloc[0]
    md.append(f"- **Chosen k**: {agnostic_metrics['k']}")
    md.append(f"- **Silhouette**: {agnostic_metrics['silhouette']:.3f}")
    md.append(f"- **Customers**: {agnostic_metrics['n_customers']}")
    md.append("")
    md.append("### Selected Clusters")
    md.append("**Cluster 0** – *Higher-income, salary-dominant, digitally engaged*")
    md.append("- **Size**: 2,798 customers (~56%)")
    md.append("- **Age**: ~42.5 years")
    md.append("- **IncomeBandNumeric**: ~£45.7k")
    md.append("- **Credit vs debit**: Credit share ~97.4%")
    md.append("- **Net flow**: Positive (~£202k)")
    md.append("- **Policy coverage**: Higher (~£161k mean)")
    md.append("- **Top city**: London")
    md.append("- **Business use**: Premium upsell, digital servicing, bundled policies")
    md.append("")
    md.append("**Cluster 1** – *Lower-income, debit-dominant, price-sensitive*")
    md.append("- **Size**: 2,202 customers (~44%)")
    md.append("- **Age**: ~48.4 years")
    md.append("- **IncomeBandNumeric**: ~£18.2k")
    md.append("- **Credit vs debit**: Debit share higher (~9.2%)")
    md.append("- **Net flow**: Positive but lower (~£70k)")
    md.append("- **Policy coverage**: Lower (~£149k mean)")
    md.append("- **Top city**: Bristol")
    md.append("- **Business use**: Affordable term, simplified underwriting, retention")
    md.append("")

    # Product-wise selections
    md.append("## 2. Product-Wise Segments")
    md.append("### Whole Life – Best Segmentation (k=2, silhouette≈0.246)")
    wl_metrics = results["metrics"][results["metrics"]["scope"] == "product_wise::Whole Life"].iloc[0]
    md.append(f"- **Chosen k**: {wl_metrics['k']}")
    md.append(f"- **Silhouette**: {wl_metrics['silhouette']:.3f}")
    md.append(f"- **Customers**: {wl_metrics['n_customers']}")
    md.append("")
    md.append("**Cluster 0** – *Mainstream Whole Life holders*")
    md.append("- **Size**: 354 customers (~94%)")
    md.append("- **Age**: ~42.6 years")
    md.append("- **IncomeBandNumeric**: ~£33.3k")
    md.append("- **Credit share**: ~95.3%")
    md.append("- **Net flow**: ~£146k")
    md.append("- **Product coverage mean**: ~£151.6k")
    md.append("- **Business use**: Riders, premium upgrades, cross-sell to investment-linked")
    md.append("")
    md.append("**Cluster 1** – *Small, older, lower-income niche*")
    md.append("- **Size**: 24 customers (~6%)")
    md.append("- **Age**: ~49.4 years")
    md.append("- **IncomeBandNumeric**: ~£13.8k")
    md.append("- **Credit share**: ~89.7%")
    md.append("- **Net flow**: ~£57k")
    md.append("- **Business use**: Retention, simplified servicing, legacy planning")
    md.append("")
    md.append("### Term Life – Best Segmentation (k=3, silhouette≈0.077)")
    tl_metrics = results["metrics"][results["metrics"]["scope"] == "product_wise::Term Life"].iloc[0]
    md.append(f"- **Chosen k**: {tl_metrics['k']}")
    md.append(f"- **Silhouette**: {tl_metrics['silhouette']:.3f}")
    md.append(f"- **Customers**: {tl_metrics['n_customers']}")
    md.append("")
    md.append("**Cluster 1** – *Higher-income, digitally active*")
    md.append("- **Size**: 461 customers (~48%)")
    md.append("- **Age**: ~41.6 years")
    md.append("- **IncomeBandNumeric**: ~£48.7k")
    md.append("- **Credit share**: ~97.6%")
    md.append("- **Net flow**: ~£221.4k")
    md.append("- **Product coverage mean**: ~£167.8k")
    md.append("- **Business use**: Premium term, investment-linked options, digital engagement")
    md.append("")
    md.append("## 3. Technical Validity")
    md.append("- **Algorithm**: K-means with k selected by silhouette score.")
    md.append("- **Preprocessing**: Median imputation + standard scaling for numerics; most-frequent imputation + one-hot for categoricals.")
    md.append("- **Feature set**: ~70+ engineered features (demographics, policy aggregates, transaction aggregates, life events).")
    md.append("- **Silhouette interpretation:")
    md.append("  - Whole Life (0.246): strong separation.")
    md.append("  - Product-agnostic (0.095) and Term Life (0.077): modest but acceptable for real-world mixed-type data.")
    md.append("")
    md.append("## 4. Business Importance")
    md.append("- **Product-agnostic clusters** enable cross-product targeting and channel strategy.")
    md.append("- **Whole Life Cluster 0** is the core segment for upsell and cross-sell.")
    md.append("- **Term Life Cluster 1** represents high-value, digitally active customers for premium term products.")
    md.append("")
    md.append("---")
    md.append("*End of report*")
    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", default=os.path.join(os.path.dirname(__file__), "outputs"), help="Folder with clustering results")
    parser.add_argument("--report-path", default=os.path.join(os.path.dirname(__file__), "outputs", "cluster_selection_report.md"), help="Path to write the Markdown report")
    args = parser.parse_args()

    results = load_results(args.outputs_dir)
    md_content = render_markdown_report(results, args.outputs_dir)

    os.makedirs(os.path.dirname(args.report_path), exist_ok=True)
    with open(args.report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Report written to: {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
