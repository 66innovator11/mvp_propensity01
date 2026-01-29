import argparse
import os
import sys
from typing import Optional

import pandas as pd
import requests


def _describe_numeric(cluster_mean: float, overall_mean: float, name: str, unit: str = "") -> str:
    if cluster_mean > overall_mean * 1.15:
        return f"Higher {name} ({cluster_mean:.0f}{unit})"
    elif cluster_mean < overall_mean * 0.85:
        return f"Lower {name} ({cluster_mean:.0f}{unit})"
    else:
        return f"Average {name} ({cluster_mean:.0f}{unit})"


def _describe_categorical(cluster_top: str, cluster_top_count: int, cluster_size: int, name: str) -> str:
    pct = cluster_top_count / cluster_size * 100
    return f"Predominantly {name} {cluster_top} ({pct:.0f}%)"


def _ollama_explain(prompt: str, model: str = "llama3.2:3b", timeout: int = 10) -> Optional[str]:
    """Call local Ollama server to generate explanation."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 60}
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama request failed: {e}", file=sys.stderr)
        return None


def _build_prompt(cluster_profile: pd.Series, overall_profile: pd.Series, cluster_size: int) -> str:
    """Construct a concise prompt for Ollama."""
    return (
        "You are a senior insurance analyst. Given the cluster profile below, write a 1-sentence business rationale "
        "explaining why these customers are likely to buy the product. Focus on actionable characteristics. Keep it under 25 words.\n\n"
        f"Cluster size: {cluster_size}\n"
        f"Age: {cluster_profile['Age']:.0f} (vs overall {overall_profile['Age']:.0f})\n"
        f"Income: {cluster_profile['IncomeBandNumeric']:.0f}k (vs overall {overall_profile['IncomeBandNumeric']:.0f}k)\n"
        f"Credit share: {cluster_profile['credit_share']*100:.0f}% (vs overall {overall_profile['credit_share']*100:.0f}%)\n"
        f"Net cash flow: {cluster_profile['net_flow']/1000:.0f}k (vs overall {overall_profile['net_flow']/1000:.0f}k)\n"
        f"Policy coverage: {cluster_profile['coverage_mean']/1000:.0f}k (vs overall {overall_profile['coverage_mean']/1000:.0f}k)\n"
        f"Top gender: {cluster_profile['Gender_top']} ({cluster_profile['Gender_top_count']/cluster_size*100:.0f}%)\n"
        f"Top city: {cluster_profile['City_top']} ({cluster_profile['City_top_count']/cluster_size*100:.0f}%)\n"
        f"Top income band: {cluster_profile['IncomeBand_top']} ({cluster_profile['IncomeBand_top_count']/cluster_size*100:.0f}%)\n\n"
        "Business rationale:"
    )
def generate_explanation(cluster_profile: pd.Series, overall_profile: pd.Series, cluster_size: int, use_llm: bool = False, model: str = "llama3.2:3b") -> dict:
    if use_llm:
        prompt = _build_prompt(cluster_profile, overall_profile, cluster_size)
        llm_rationale = _ollama_explain(prompt, model=model)
        if llm_rationale:
            business = llm_rationale
        else:
            # Fallback to rule-based
            business = _rule_based_business(cluster_profile, overall_profile, cluster_size)
    else:
        business = _rule_based_business(cluster_profile, overall_profile, cluster_size)

    technical = (
        f"Cluster of {cluster_size} customers; "
        f"features include income band, credit/debit behavior, net flow, policy coverage, and demographics; "
        f"mean propensity aligns with these characteristics."
    )
    return {"business_rationale": business, "technical_validity": technical}


def _rule_based_business(cluster_profile: pd.Series, overall_profile: pd.Series, cluster_size: int) -> str:
    """Fallback rule-based business rationale."""
    # Numeric descriptors
    income_desc = _describe_numeric(cluster_profile["IncomeBandNumeric"], overall_profile["IncomeBandNumeric"], "income", "k")
    credit_share_desc = _describe_numeric(cluster_profile["credit_share"], overall_profile["credit_share"], "credit share", "%")
    net_flow_desc = _describe_numeric(cluster_profile["net_flow"], overall_profile["net_flow"], "net cash flow", "k")
    coverage_desc = _describe_numeric(cluster_profile["coverage_mean"], overall_profile["coverage_mean"], "policy coverage", "k")
    age_desc = _describe_numeric(cluster_profile["Age"], overall_profile["Age"], "age")

    # Categorical descriptors
    gender_desc = _describe_categorical(cluster_profile["Gender_top"], cluster_profile["Gender_top_count"], cluster_size, "gender")
    city_desc = _describe_categorical(cluster_profile["City_top"], cluster_profile["City_top_count"], cluster_size, "city")
    income_band_desc = _describe_categorical(cluster_profile["IncomeBand_top"], cluster_profile["IncomeBand_top_count"], cluster_size, "income band")

    # Business articulation
    business_parts = [
        income_desc,
        f"{credit_share_desc} and {net_flow_desc}",
        f"{coverage_desc} and {age_desc}",
        f"{gender_desc} and {city_desc}",
        f"{income_band_desc}"
    ]
    return "; ".join(business_parts) + "."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-llm", action="store_true", help="Use local Ollama LLM to generate business rationales")
    parser.add_argument("--model", default="llama3.2:3b", help="Ollama model name")
    args = parser.parse_args()

    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    # Load profiles
    agnostic_profile = pd.read_csv(os.path.join(outputs_dir, "product_agnostic_cluster_profile.csv"))
    whole_life_profile = pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_whole_life.csv"))
    term_life_profile = pd.read_csv(os.path.join(outputs_dir, "product_wise_cluster_profile_term_life.csv"))

    # Compute overall averages from product-agnostic
    overall = agnostic_profile.mean(numeric_only=True)

    # Example: Whole Life Cluster 0
    wl_c0 = whole_life_profile[whole_life_profile["cluster"] == 0].iloc[0]
    wl_c0_size = wl_c0["cluster_size"]
    wl_explain = generate_explanation(wl_c0, overall, wl_c0_size, use_llm=args.use_llm, model=args.model)

    # Example: Term Life Cluster 1
    tl_c1 = term_life_profile[term_life_profile["cluster"] == 1].iloc[0]
    tl_c1_size = tl_c1["cluster_size"]
    tl_explain = generate_explanation(tl_c1, overall, tl_c1_size, use_llm=args.use_llm, model=args.model)

    explanations = {
        "whole_life_cluster0": wl_explain,
        "term_life_cluster1": tl_explain,
    }

    # Save
    out_path = os.path.join(os.path.dirname(__file__), "propensity_outputs", "auto_explanations.csv")
    rows = []
    for key, val in explanations.items():
        rows.append({"target": key, "business_rationale": val["business_rationale"], "technical_validity": val["technical_validity"]})
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"Auto-generated explanations saved to: {out_path}")
    for key, val in explanations.items():
        print(f"\n{key}:")
        print(f"  Business: {val['business_rationale']}")
        print(f"  Technical: {val['technical_validity']}")


if __name__ == "__main__":
    main()
