# Cascade Outdoor — data dictionary

Extract prepared by Merchandising Analytics, September 2026.

Both divisions run on the same planning platform and record the same twelve fields with the same definitions. The extracts differ in size, not in structure.

---

## `division_h.csv` and `division_a.csv` — the training extracts

**Grain.** One row per store per week. **Target: `units`.**

| Column | Definition |
|---|---|
| `store_id` | Store identifier, 1–60. |
| `week_id` | Sequential identifier for the store-week, assigned in extract order and unique to one store-week. |
| `promo_depth_pct` | Discount off list, 0–45. |
| `own_price_index` | Cascade's shelf price for the category, indexed to 100 = plan. |
| `competitor_price_index` | Matched competitor price on the same basis, from a third-party scrape. |
| `marketing_spend_k` | Division marketing spend attributed to the store-week, $000. |
| `temp_f` | Mean weekly temperature at the store, °F. |
| `loyalty_share` | Share of division sales in that store-week on a loyalty account. |
| `store_sqft_k` | Store selling area, thousands of sq ft. |
| `inventory_cover_wks` | Weeks of forward cover at the start of the week. |
| `assortment_breadth` | Distinct SKUs carried in the category that week. |
| `catalog_pages` | Pages the category held in that period's catalogue. |
| `returns_rate` | Units returned / units sold, trailing 8 weeks. |
| `staffing_hours` | Scheduled floor hours in the category that week. |
| `units` | Units sold. |

The twelve predictor fields were specified by a single working group in 2024 and are populated by the same nightly job for both divisions. Nobody has audited which of them actually matter.

### Sizes

| | Rows in file | Distinct store-weeks |
|---|---:|---:|
| Hardgoods | 3,350 | see the pipeline note below |
| **Apparel** | **197** | 197 |

> **Why Apparel is small.** Apparel migrated to the new planning platform in March. The legacy system recorded `promo_depth_pct` net of employee discount and `loyalty_share` on a different denominator, so pre-migration weeks are not comparable and were excluded. Merchandising Analytics expects Apparel to reach parity with Hardgoods on volume of usable history by late 2027.

> **Pipeline note (CO-4471, open).** The Hardgoods weekly load was re-run in August after a scheduler fault. **The re-run appended rather than replaced.** Merchandising Analytics has confirmed the fault; the extract has not been regenerated, and `division_h.csv` is shipped as the pipeline produced it. Every affected store-week appears in the file twice, identical on every column including `units`.

> **Apparel cleaning note.** Unlike Hardgoods, the Apparel extract has been cleaned before delivery. The divisional planner flagged three weeks and Merchandising Analytics adjudicated them; **all three were removed** and the file you have contains the remaining 197. For the record:
>
> | Week | What happened | Decision |
> |---|---|---|
> | `50116` | Store shut for a burst pipe. The system still wrote a row, with `units = 0`. | Removed. Not a demand observation — nothing was on sale that week. |
> | `50088` | `units` recorded as 925 against a store average near 110. Confirmed as a keying error: the true figure was entered with an extra digit. | Removed. A real week with a corrupted target; the original value could not be recovered from the source system. |
> | `50151` | Black Friday. `promo_depth_pct` 44.8 and `marketing_spend_k` 61.4, both far outside any other week in the file. | Removed. Real demand, but from a promotional regime the weekly planning model is not intended to cover. Merchandising Analytics plans a separate peak-week model. |
>
> You do not need to revisit these decisions. They are recorded here so that you know what the extract is and is not.

---

## `replicates.csv` — controlled repeat observations, and the final test extract

**This is not additional training data and it is not a third division.** It has two uses in this assignment, both described in the brief: it is where σ̂² comes from, and it is the extract on which final models are scored once.

During the 2025 planning-system validation, Merchandising Analytics ran a controlled exercise. In each division they identified 45 store-week configurations — distinct combinations of the twelve fields above — and located **ten independent weeks that matched each configuration exactly on every recorded field**. None of these weeks appears in `division_h.csv` or `division_a.csv`.

So every group of ten rows sharing a `config_id` is identical on every column except `units`.

| Column | Definition |
|---|---|
| `division` | `H` or `A`. |
| `config_id` | Configuration identifier. Ten rows share each one. |
| `replicate` | 1–10 within the configuration. |
| *(the twelve predictor fields)* | As above. Identical within a `config_id`. |
| `units` | Units sold in that week. |

The exercise was commissioned to settle a question the planning team kept arguing about: *how much of the week-to-week variation in units is even forecastable, and is the answer the same in both divisions?*
