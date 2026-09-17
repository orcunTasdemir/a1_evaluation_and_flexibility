# `member_months.csv` — data dictionary

Extract prepared by the Membership Analytics team, **March 2026**.
Source systems: Billing (Zuora), Product Analytics (app event stream), Zendesk, Salesforce.

**Grain.** One row per **member per calendar month** in which the member was active at any point during that month. A member appears once for every month they were on the book. Members who cancel stop appearing after the month in which they cancelled.

**Window.** January 2024 through December 2025. All outcomes have matured: the last snapshot month is December 2025, whose 60-day outcome window closed at the end of February 2026, before this extract was pulled.

---

## Columns

| Column | Type | Source | Definition |
|---|---|---|---|
| `member_id` | int | Billing | Stable member identifier. |
| `snapshot_month` | str | Billing | The calendar month the row describes. *Note: this field was written by three different pipeline versions over the extract window and the formatting is not consistent.* |
| `signup_month` | str | Billing | Month the member's first paid subscription started. |
| `acquisition_channel` | str | Salesforce | How the member was acquired: `organic`, `paid_search`, `partner_gym`, `corporate`. The `corporate` channel covers members enrolled through an employer wellness contract; the first such contract went live in February 2025. |
| `plan_tier` | str | Billing | `basic`, `plus`, or `elite`. |
| `monthly_price` | float | Billing | List price of the plan in USD. Does not reflect promotional discounts. |
| `city_tier` | str | Salesforce | `metro`, `suburban`, `rural`. Self-reported at signup. |
| `tenure_months` | int | Billing | Completed months since `signup_month`, as of the start of `snapshot_month`. |
| `sessions_last_30d` | int | Product Analytics | Completed workout sessions logged in the 30 days ending on the **last day of the previous month**. |
| `app_opens_last_30d` | float | Product Analytics | App launches over the same 30-day window. |
| `avg_session_minutes` | float | Product Analytics | Mean session length over the same window. |
| `days_since_last_login` | float | Product Analytics | Days between the member's last app login and the **last day of the previous month**. Capped at 90. |
| `support_tickets_last_30d` | int | Zendesk | Tickets opened by the member over the same 30-day window. |
| `payment_failures_last_90d` | int | Billing | Declined or failed charge attempts in the 90 days ending on the **last day of the previous month**. A failure is recorded when the card issuer declines; it does not imply the member intended to cancel. |
| `referrals_made` | int | Product Analytics | Successful referrals, same 30-day window. |
| `winback_offer_sent` | int | Salesforce | `1` if the Retention team contacted this member about this month. **The Retention team works from the at-risk list that Membership Analytics circulates on the third business day after month close.** |
| `exit_survey_started` | int | Product Analytics | `1` if the member opened the cancellation exit survey. |
| `churn_next_60d` | int | Billing | **Target.** `1` if the member's subscription terminated within 60 days of the end of `snapshot_month`. |

---

## Known issues logged against this extract

- **NLF-2231** — The March 2025 load was re-run after a partition failure. The re-run was not idempotent. *Status: open.*
- **NLF-2198** — `snapshot_month` formatting varies by pipeline version. *Status: won't fix, downstream consumers handle it.*

## Notes from the analyst who pulled it

> Left all columns in — figured the model can decide what's useful. Didn't do anything about NLF-2231, shouldn't matter for modelling. Corporate members are a small slice so I didn't look at them separately.
