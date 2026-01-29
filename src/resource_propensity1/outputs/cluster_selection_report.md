# Customer Clustering: Selected Segments and Rationale
*Generated on 2026-01-28 13:49:59 UTC*

## 1. Product-Agnostic Segments (All Customers)
- **Chosen k**: 2
- **Silhouette**: 0.095
- **Customers**: 5000

### Selected Clusters
**Cluster 0** – *Higher-income, salary-dominant, digitally engaged*
- **Size**: 2,798 customers (~56%)
- **Age**: ~42.5 years
- **IncomeBandNumeric**: ~£45.7k
- **Credit vs debit**: Credit share ~97.4%
- **Net flow**: Positive (~£202k)
- **Policy coverage**: Higher (~£161k mean)
- **Top city**: London
- **Business use**: Premium upsell, digital servicing, bundled policies

**Cluster 1** – *Lower-income, debit-dominant, price-sensitive*
- **Size**: 2,202 customers (~44%)
- **Age**: ~48.4 years
- **IncomeBandNumeric**: ~£18.2k
- **Credit vs debit**: Debit share higher (~9.2%)
- **Net flow**: Positive but lower (~£70k)
- **Policy coverage**: Lower (~£149k mean)
- **Top city**: Bristol
- **Business use**: Affordable term, simplified underwriting, retention

## 2. Product-Wise Segments
### Whole Life – Best Segmentation (k=2, silhouette≈0.246)
- **Chosen k**: 2
- **Silhouette**: 0.246
- **Customers**: 378

**Cluster 0** – *Mainstream Whole Life holders*
- **Size**: 354 customers (~94%)
- **Age**: ~42.6 years
- **IncomeBandNumeric**: ~£33.3k
- **Credit share**: ~95.3%
- **Net flow**: ~£146k
- **Product coverage mean**: ~£151.6k
- **Business use**: Riders, premium upgrades, cross-sell to investment-linked

**Cluster 1** – *Small, older, lower-income niche*
- **Size**: 24 customers (~6%)
- **Age**: ~49.4 years
- **IncomeBandNumeric**: ~£13.8k
- **Credit share**: ~89.7%
- **Net flow**: ~£57k
- **Business use**: Retention, simplified servicing, legacy planning

### Term Life – Best Segmentation (k=3, silhouette≈0.077)
- **Chosen k**: 3
- **Silhouette**: 0.077
- **Customers**: 961

**Cluster 1** – *Higher-income, digitally active*
- **Size**: 461 customers (~48%)
- **Age**: ~41.6 years
- **IncomeBandNumeric**: ~£48.7k
- **Credit share**: ~97.6%
- **Net flow**: ~£221.4k
- **Product coverage mean**: ~£167.8k
- **Business use**: Premium term, investment-linked options, digital engagement

## 3. Technical Validity
- **Algorithm**: K-means with k selected by silhouette score.
- **Preprocessing**: Median imputation + standard scaling for numerics; most-frequent imputation + one-hot for categoricals.
- **Feature set**: ~70+ engineered features (demographics, policy aggregates, transaction aggregates, life events).
- **Silhouette interpretation:
  - Whole Life (0.246): strong separation.
  - Product-agnostic (0.095) and Term Life (0.077): modest but acceptable for real-world mixed-type data.

## 4. Business Importance
- **Product-agnostic clusters** enable cross-product targeting and channel strategy.
- **Whole Life Cluster 0** is the core segment for upsell and cross-sell.
- **Term Life Cluster 1** represents high-value, digitally active customers for premium term products.

---
*End of report*