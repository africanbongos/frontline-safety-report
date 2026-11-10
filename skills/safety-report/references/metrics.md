# Safety metrics reference: rates, conventions, lead indicators, benchmarks

Verified 16 Oct 2026. "(verify)" marks common practice that was not confirmed against a primary source. Always state the base (per 1,000,000 hours, per 200,000 hours, per 100,000 workers) next to any rate: the same workforce produces very different numbers under different conventions.

---

## 1. Frequency rate conventions by region

### General form

Rate = (number of cases in period / exposure in period) x base

| Region | Base | Typical headline metrics |
|---|---|---|
| Australia, NZ | 1,000,000 hours worked | LTIFR, TRIFR, MTIFR, AIFR |
| US | 200,000 hours worked (100 FTE x 40 h x 50 weeks) | TRIR / TCIR, DART, LTIR (DAFW rate) |
| UK | 100,000 workers (official stats) or 100,000 hours (company AFR) | Incidence rate, AFR |
| International mining (ICMM) | 1,000,000 hours | TRIFR, FFR |

Conversion: a per-1,000,000-hour rate = per-200,000-hour rate x 5 (e.g. TRIR 2.0 = TRIFR 10.0). A per-100,000-hour AFR = per-1,000,000-hour rate / 10.

### Australia and New Zealand (AS 1885.1 convention)

AS 1885.1-1990 "Measurement of occupational health and safety performance - Describing and reporting occupational injuries and disease" (the National Standard for workplace injury and disease recording) is listed as a historical (no longer current) standard by its publisher, but remains the de facto basis for AU LTIFR. NZ practice generally follows the same per-million-hours convention (verify; no NZ statutory definition).

Definitions (AS 1885.1 for LTI; the rest are industry convention, verify against company definitions):
- **LTI (lost time injury)**: work-related injury or disease resulting in death, permanent disability, or time lost from work of one full day or shift or more after the day of injury (verify exact AS 1885.1 wording; some secondary sources paraphrase as "more than 24 hours").
- **MTI (medical treatment injury)**: injury requiring treatment by a medical practitioner or other health professional beyond first aid, with no lost time (no full shift lost).
- **RWI (restricted work injury)**: injury where the person returns on restricted or alternate duties and cannot do their full normal role, no full shift lost.
- **FAI (first aid injury)**: treated with first aid only; not recordable.
- **Recordable (TRI)**: fatalities + LTIs + RWIs + MTIs (company definitions vary on whether fatalities and RWIs are included; state it).

Formulas (hours = total hours worked by all workers in scope, including overtime; contractor inclusion must be stated):
- **LTIFR** = (number of LTIs x 1,000,000) / hours worked
- **TRIFR** = ((fatalities + LTIs + RWIs + MTIs) x 1,000,000) / hours worked
- **MTIFR** = (number of MTIs x 1,000,000) / hours worked
- **AIFR (all injury frequency rate)** = ((TRIs + FAIs) x 1,000,000) / hours worked (convention, verify)
- **Severity / average time lost rate (AU)** = total days or shifts lost / number of LTIs (convention; AS 1885.1 refers to an "average time lost rate", exact formula verify)

Worked example (AU): 2,400,000 hours; 3 LTIs, 2 RWIs, 7 MTIs, 25 FAIs, no fatalities.
- LTIFR = 3 x 1,000,000 / 2,400,000 = 1.25
- TRIFR = (3 + 2 + 7) x 1,000,000 / 2,400,000 = 5.0
- MTIFR = 7 x 1,000,000 / 2,400,000 = 2.92
- AIFR = (12 + 25) x 1,000,000 / 2,400,000 = 15.4

Sources: https://webstore.ansi.org/Standards/SAI/18851990 ; https://en.wikipedia.org/wiki/LTIFR ; https://pimcore.icmm.com/website/publications/pdfs/health-and-safety/2025/benchmarking-safety-data-2024.pdf?cb=112368

### United States (OSHA / BLS convention)

Case definitions come from 29 CFR 1904 (see jurisdictions.md): a recordable case is death, days away, restricted work or transfer, medical treatment beyond first aid, loss of consciousness, or a significant diagnosed condition.

- **TRIR / TCIR** = (total OSHA recordable cases x 200,000) / hours worked
- **DART rate** = (cases with days away, restricted work or job transfer x 200,000) / hours worked
- **LTIR / DAFWII rate** = (cases with days away from work x 200,000) / hours worked (convention)
- **Severity rate** = (total lost workdays x 200,000) / hours worked (convention; days counted as calendar days, capped at 180 per case under 1904.7(b)(3)) (verify any specific standard)

BLS worked example (ABC Company, 200 employees): 7 recordable cases, 400,000 hours: TCIR = 7 x 200,000 / 400,000 = 3.5. 3 DART cases: DART = 3 x 200,000 / 400,000 = 1.5.

Sources: https://www.bls.gov/iif/overview/compute-nonfatal-incidence-rates.htm ; https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XVII/part-1904/subpart-C/section-1904.7

### United Kingdom

- **Incidence rate (HSE official statistics)** = (number of reportable injuries / average number of workers) x 100,000. HSE says comparing rates per 100,000 workers is preferable to raw counts.
- **AFR (accident frequency rate)**, widely used by UK contractors = (number of RIDDOR reportable injuries x 100,000) / hours worked (industry convention; not defined in legislation; some firms count only over-7-day plus specified injuries, others include all lost time. Verify the client's definition).

Worked example (UK): 1,200 workers, 2,100,000 hours, 4 RIDDOR reportable injuries.
- Incidence rate = 4 / 1,200 x 100,000 = 333 per 100,000 workers
- AFR = 4 x 100,000 / 2,100,000 = 0.19

Sources: https://www.hse.gov.uk/statistics/fatals-overview.htm

---

## 2. Rolling 12-month rate method

Rolling 12-month rate (R12) for month m = (sum of cases in months m-11 to m) x base / (sum of hours in months m-11 to m).

- Sum numerator and denominator separately. Do not average 12 monthly rates (months with low hours distort the average).
- Recalculate every month; the oldest month drops out.
- Use actual hours where possible; if estimating (e.g. headcount x standard hours), say so.
- Reclassify cases when status changes (e.g. MTI becomes LTI after a later shift lost) and restate prior months.
- Show the monthly count alongside R12 so a single event is visible.

Worked example (AU TRIFR): last 12 months total 9 recordable injuries and 1,850,000 hours. R12 TRIFR = 9 x 1,000,000 / 1,850,000 = 4.86. Next month adds 1 TRI and 160,000 hours while the dropped month had 2 TRIs and 150,000 hours: new totals 8 TRIs, 1,860,000 hours, R12 TRIFR = 4.30.

Small-population caution: under about 1,000,000 hours a year a single LTI moves LTIFR by 1.0 or more; report counts and days since last event alongside rates.

---

## 3. Lead indicators (definitions and good-practice formulas)

OSHA defines leading indicators as "proactive, preventive, and predictive measures" of the performance of safety activities, and lagging indicators as measures of past events (injuries, illnesses, fatalities). OSHA recommends SMART indicators (Specific, Measurable, Accountable, Reasonable, Timely). The formulas below are good practice; set targets per organisation.

| Indicator | Formula | Notes |
|---|---|---|
| Inspections completed % | inspections completed in period / inspections scheduled in period x 100 | OSHA example. Count only scheduled items due in the period. |
| Actions closed on time % | corrective actions closed by due date / corrective actions due in period x 100 | Complement: % actions overdue = overdue open actions / total open actions x 100 (OSHA example goal 10% or less). |
| Hazards abated within target % | hazards abated within target window / hazards identified x 100 | OSHA example (same day, week or month window by risk rating). |
| Worker-reported hazards actioned within 48 h % | reports with corrective action started within 48 h / total reports x 100 | OSHA example. |
| Investigations with root cause % | investigations with documented root cause analysis / total investigations x 100 | OSHA example. |
| Critical control verification rate | critical control verifications completed / verifications planned x 100; plus control effectiveness = verifications finding control in place and effective / verifications completed x 100 | Concept from ICMM Critical Control Management guidance; report both completion and failure findings. |
| Near miss reporting ratio | near misses reported / recordable injuries (same period) | Higher is generally better (reporting culture); also track near misses per 200,000 or 1,000,000 hours. Convention, no standard target. |
| HiPo ratio | HiPo events / total incidents reported x 100 | Track HiPo count and % with completed investigation and actions closed. |
| Training currency % | workers with all required training in date / workers requiring that training x 100 | OSHA example: % attending required refresher training. |
| Average time to acknowledge hazard report | sum of (acknowledgement time - report time) / number of reports | OSHA example. |

Sources: https://www.osha.gov/sites/default/files/OSHA_Leading_Indicators.pdf ; https://www.osha.gov/leading-indicators ; https://hub.icmm.com/website/publications/pdfs/health-and-safety/2015/guidance_ccm-good-practice.pdf

---

## 4. Published benchmark rates (verified figures only)

### Australia: Safe Work Australia, Key WHS Statistics Australia 2025

- Worker fatalities, calendar 2024: 188 traumatic injury fatalities; 1.3 per 100,000 workers.
- Serious claims (one working week or more off work), 2023-24 preliminary: 146,700 claims; **6.8 per million hours worked**; 10.9 per 1,000 filled jobs.

Serious claims frequency rate by industry (per million hours worked, 2023-24p):

| Industry | Frequency rate | Incidence (per 1,000 filled jobs) |
|---|---|---|
| Agriculture, forestry and fishing | 10.0 | 18.8 |
| Public administration and safety | 9.6 | 16.3 |
| Manufacturing | 9.4 | 17.1 |
| Health care and social assistance | 9.4 | 13.3 |
| Construction | 9.3 | 17.7 |
| Transport, postal and warehousing | 9.0 | 16.2 |
| Arts and recreation services | 7.9 | 10.1 |
| Wholesale trade | 7.6 | 13.7 |
| Accommodation and food services | 7.0 | 8.3 |
| Mining | 6.7 | 14.9 |
| Other services | 6.3 | 10.4 |
| Education and training | 6.2 | 9.1 |
| Electricity, gas, water and waste services | 6.0 | 11.1 |
| Retail trade | 5.5 | 7.4 |
| Administrative and support services | 5.0 | 8.4 |
| Rental, hiring and real estate services | 4.0 | 7.2 |
| Information media and telecommunications | 1.8 | 3.1 |
| Professional, scientific and technical services | 1.2 | 2.2 |
| Financial and insurance services | 0.8 | 1.5 |

Caution: these are workers' compensation serious claims (1+ week off), roughly comparable to an LTIFR with a one-week threshold, not to a company LTIFR (one shift threshold) or TRIFR. Preliminary figures are revised.

Source: https://data.safeworkaustralia.gov.au/sites/default/files/2025-10/Key_Work_Health_and_Safety_Statistics_Austraila_2025.pdf

### United States: BLS Survey of Occupational Injuries and Illnesses, 2024

- Private industry TCIR 2024: **2.3 per 100 full-time workers** (down from 2.4 in 2023; lowest since the series began in 2003). 2.5 million cases.

Total recordable injury and illness rate by sector, 2024 (per 100 full-time workers):

| Sector | Rate |
|---|---|
| Transportation and warehousing | 4.4 |
| Agriculture, forestry, fishing and hunting | 3.9 |
| Arts, entertainment and recreation | 3.9 |
| Health care and social assistance | 3.4 |
| Retail trade | 3.0 |
| Manufacturing | 2.7 |
| Accommodation and food services | 2.6 |
| Construction | 2.2 |
| Wholesale trade | 2.2 |
| Utilities | 1.9 |
| Other services | 1.9 |
| Administrative, support and waste services | 1.8 |
| Educational services | 1.7 |
| Real estate and rental and leasing | 1.6 |
| Mining, quarrying, oil and gas extraction | 1.2 |
| Information | 0.7 |
| Professional, scientific and technical services | 0.7 |
| Management of companies | 0.5 |
| Finance and insurance | 0.3 |

Sources: https://www.bls.gov/opub/ted/2026/2-5-million-workplace-injuries-and-illnesses-in-private-industry-in-2024-down-3-1-percent-from-2023.htm ; https://www.bls.gov/charts/injuries-and-illnesses/number-and-rate-of-nonfatal-work-injuries-and-illnesses-by-industry.htm

### Global mining: ICMM Safety Performance Report 2024 data

- All ICMM members 2024: TRIFR **2.29** per million hours (6,446 recordable injuries over 2,811,767,985 hours); fatality frequency rate 0.015 (42 fatalities). Company TRIFRs ranged from 0.91 (Barrick) to 7.64 (Alcoa). ICMM uses per-million-hours rates; definitions in ICMM Health and Safety Performance Indicators guidance (2021).

Source: https://pimcore.icmm.com/website/publications/pdfs/health-and-safety/2025/benchmarking-safety-data-2024.pdf?cb=112368

### Great Britain: HSE

- 126 workers killed in work-related accidents in 2025/26 (RIDDOR, as labelled by HSE; construction 25, agriculture, forestry and fishing 22, manufacturing 18). HSE overview also cites 59,219 employer-reported non-fatal injuries to employees and 964,000 workers with work-related stress, depression or anxiety. Rates per 100,000 workers were not captured in this research (verify in the HSE annual report).

Sources: https://www.hse.gov.uk/statistics/fatals-overview.htm ; https://www.hse.gov.uk/statistics/overview.htm

---

## 5. Severity classification (common practice)

No regulator mandates a single severity scale; the following is common practice (verify against the client's own risk matrix).

- **Actual severity**: the outcome that occurred (e.g. 1 first aid, 2 medical treatment, 3 lost time or restricted, 4 permanent impairment or serious injury, 5 fatality). Drives lagging metrics (LTIFR, TRIFR).
- **Potential severity**: the most credible worst outcome had the event unfolded differently (e.g. one or two failed controls away), rated on the same scale. Drives learning priority, investigation depth and lead metrics.
- Rate potential on credible, not worst-imaginable, outcome; record the reasoning (e.g. "load dropped 4 m into an exclusion zone that was occupied 10 minutes earlier").
- **HiPo (high potential incident or event)**: any incident or near miss whose credible potential outcome is a fatality or permanent life-altering injury, regardless of actual outcome. IOGP's HiPo reporting covers events "which had the potential to result in a fatality". Many organisations also tag events where a critical control failed or was absent. HiPos typically trigger a formal investigation (e.g. ICAM or equivalent), senior leader review and sharing of learnings.
- Related: **SIF / SIF potential (serious injury and fatality)** is the term used in many US programs for the same concept (verify source).
- Separate severity from **notifiability**: a HiPo with no injury may or may not be notifiable (e.g. dangerous incident under model WHS s37, dangerous occurrence under RIDDOR Schedule 2); check jurisdictions.md.

Sources: https://idms.iogp.org/Documents/845 ; https://www.iogp.org/bookstore/product/safety-performance-indicators-2017-data-high-potential-event-reports/
