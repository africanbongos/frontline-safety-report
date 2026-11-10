# Safety Report & KRIs (by Frontline)

Turn messy safety data into a monthly safety report and KRI scorecard your board can read in 2 minutes. Works in Claude and ChatGPT.

## What it does

- Asks for your regulator, industry, audience and period
- Reads your incident log, actions, inspections and hours worked (any format: paste, CSV or Excel)
- Produces: headline, lead and lag indicators, LTIFR/TRIFR, top incidents with a notifiability check, patterns, overdue actions, 3 insights, 3 recommendations, and board decisions
- Flags gaps in your data

Supports model WHS laws (AU), WorkSafe Victoria, WorkSafe NZ, US OSHA and UK HSE.

## What you get in v2

- **Real deliverables, not just chat**: a live Excel workbook (formulas, dropdowns, traffic lights), clean charts, and for executives or boards a document you can circulate
- **Numbers you can defend**: every rate calculated in code with the right convention for your jurisdiction (AU/NZ per 1,000,000 hours, US per 200,000 hours)
- **Legal checks built in**: notifiable incident tests and terminology for Australian WHS laws, Victoria, New Zealand, US OSHA and UK RIDDOR
- **Expert reference packs**: fatal risks, critical controls and lead indicators for 12 industries, plus risk and investigation methods

## Try it

Install the plugin, then say: "Build my monthly safety report" and paste your data. No data? Say "sample".

## Make it live

Connect Frontline to build this report automatically every month from live data: https://getfrontline.io

## Disclaimer

Outputs are a starting point, not legal advice. Check figures and obligations against your own records and current legislation.

## What this plugin runs

The skill includes three readable Python helper scripts in `skills/safety-report/scripts/`: `incident_tools.py` (cleans and summarises the data you upload, using pandas), `charts.py` (draws charts with matplotlib) and `xlsx_builder.py` (builds the Excel output with openpyxl, and if LibreOffice is installed, runs it locally in headless mode to recalculate formulas). They work only on files in your session. They make no network calls and fetch nothing from the internet.
