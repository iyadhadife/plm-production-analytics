# Cross analyses MES × PLM × ERP

Code: `backend/app/analytics/`. Route: `GET /api/analyses/<name>`. Opened from the **🔗 Cross analyses** button in the frontend.

## 1. How the three files are linked

| Key | MES_Extraction | PLM_DataSet | ERP_Equipes_Airplus |
|---|---|---|---|
| Part | `Référence` (list `A511;A337;…`, exploded to one row per part) | `Code / Référence` | – |
| Station | `Poste` (1 to 56) | – | `Poste de montage` ("Poste N" = home team, 2 to 3 people) |
| Time | `Date`, `Heure Début`, `Temps Prévu`, `Temps Réel` | `Délai Approvisionnement`, `Temps CAO` | `Coût horaire (€)` |

The source files are in French, so their column names stay in French. The code refers to them through
`backend/app/processing/columns.py`.

Indicators computed for each MES operation (`backend/app/analytics/model/`):

- **Overrun** (min and %) = actual time − planned time
- **Value of committed parts** (€) = sum of the PLM purchase costs of the consumed parts
- **Max criticality and max lead time** = the worst part consumed by the operation
- **Actual labour cost and overrun cost** (€) = cumulative hourly cost of the ERP team × duration
- **Team experience score**: Beginner = 1, Confirmed = 2, Expert = 3
- **Exposure** (€·h) = value of the tied-up parts × hours of delay
- **Incident family** and **root-cause themes**, derived by keyword matching on the free-text MES columns
  (`backend/app/analytics/constants.py`)

## 2. Analyses

| # | Analysis (`/api/analyses/…`) | Business question | Method |
|---|---|---|---|
| 1 | `overview` | Where does the line stand? | KPIs, planned/actual cumulative **S-curve**, delay by step, top operations by € exposure |
| 2 | `priority-matrix` | Which stations should be addressed first? | **Priority matrix** overrun × parts value (log axis), bubbles = lost minutes, colour = criticality, quadrants on the medians, priority score |
| 3 | `pareto` | Which incidents cost the most? | **80/20 Pareto** of incident families, family × step heatmap, frequency of root causes |
| 4 | `experience` | Does team experience matter? | Scatter plot + **linear regression and Pearson r**, boxes by team composition, hourly cost by level |
| 5 | `supply-risk` | Which parts can stop the line? | **Parts risk matrix** lead time × cost × consumption, exposure by supplier, risk score (criticality × lead time × dependency) |
| 6 | `timeline` | How does the delay propagate? | Planned vs actual **Gantt** coloured by criticality, with team and incident on hover |

## 3. First findings on the sample data

- All 56 operations exceed their planned time: +41 % overall, about 9 h of drift. The delay is systemic.
- 4 incident families out of 7 account for about 80 % of the lost minutes: shop-floor environment, IT systems &
  automation, quality & metrology, and tooling. The most cited root cause is ageing / obsolescence.
- No clear link between the experience of the home teams and the delay (r ≈ 0.04). Act on equipment before
  reassigning teams.
- The direct labour overrun is small (under €1,000). However, delays tie up high-value parts: station 27 (engines)
  holds about €10M of parts.
- 6 critical references have a lead time ≥ 25 days (D142, D088, D234, A437, A423, A623). They are candidates for
  safety stock or dual sourcing. Safran Engines alone accounts for about 47 % of the consumed value.

## 4. Generating the reports without the frontend

```bash
cd backend
python -m app.analytics            # writes backend/analyses_html/*.html
```

## 5. Possible next steps

- Use the ERP `Rotation` column (week × station) to know who actually worked each day, instead of the home team.
- Replace the keyword classification with an LLM classification (Gemini is already wired for the chatbot).
- Add an inventory carrying cost (annual rate) to turn the €·h exposure into a financial cost.
- Add a bottleneck analysis with a cycle time per step and a critical-path computation.
