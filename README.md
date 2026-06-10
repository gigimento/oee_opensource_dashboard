# OEE Open Source Dashboard

Real-time SMT production intelligence dashboard for OEE monitoring, shift tracking, and machine analytics.

Powered by Streamlit — connects directly to your existing MES/SQL database or runs with built-in demo data.

## Features

- **Live OEE Calculation** — Availability, Performance, Quality per machine with animated SVG gauges
- **Shift Dashboard** — 8-hour shift view with hourly production distribution vs target
- **Machine Breakdown** — Per-machine OEE tables, head performance metrics, and build speed analysis
- **Production Charts** — Stacked bar (production + scrap) and line charts with hourly granularity
- **Line Status Widgets** — Run time, shift time remaining, downtime tally
- **Top Error Feeders** — Component placement error analysis with PPM ranking
- **TV Mode** — Fullscreen layout for production floor displays
- **Auto-refresh** — Configurable auto-reload (every 5 minutes, with JS fallback)
- **Demo Mode** — Embedded sample data for evaluation without a database

## Tech Stack

- **Python** — Streamlit, pandas, matplotlib, pyodbc
- **Database** — Microsoft SQL Server (MES/SQUAD schema)
- **Visualization** — Custom SVG gauges, matplotlib charts, Dark Industrial theme

## Quick Start

```bash
pip install streamlit pandas matplotlib pyodbc
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### Demo Mode (No Database Required)

The dashboard ships with realistic embedded demo data. Check the **Demo** checkbox in the toolbar to explore all features without connecting to a database.

### Run Scripts

| Script | Purpose |
|---|---|
| `run_app.bat` | Double-click to launch (Windows) |
| `run_app.ps1` | PowerShell launcher |
| `run_app.py` | Python launcher (opens browser automatically) |

## Database Configuration

Edit the connection string in `app.py`:

```python
CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=SQUAD;"
    r"Trusted_Connection=yes;"
)
```

The dashboard expects a Hanwha SQUAD MES schema (`Custom_MachineRunFact`, `Custom_ProgramCycleTime`, `FMS_ErrorData`). Adjust the SQL queries in `app.py` to match your database structure.

## CLI Analytics

The `squad_analytics.py` script provides a terminal-based OEE analysis:

```bash
python squad_analytics.py --date 2026-06-10
python squad_analytics.py --date 2026-06-10 --errors
```

## Project Structure

```
oee_opensource_dashboard/
├── app.py                  # Main Streamlit dashboard
├── squad_analytics.py      # CLI analytics tool
├── db_explorer.py          # Database schema explorer
├── run_app.py              # Python launcher
├── run_app.bat             # Windows batch launcher
├── run_app.ps1             # PowerShell launcher
├── .gitignore
└── README.md
```

## Customization

- **Theme** — All CSS variables are defined in the `css_block` at the top of `app.py`. Colors, fonts, and layout can be adjusted inline.
- **Line Filter** — The dashboard filters by `LineCd = '003LINE'`. Change this in the SQL query to monitor a different production line.
- **Shift Hours** — Currently set to 08:00–16:00. Update the `HOUR` filter in the query and the `shift_start`/`shift_end` timestamps.

## Database Schema (Required Tables)

The dashboard queries the following views/tables. Adapt the SQL if your schema differs:

- `Custom_MachineRunFact` — Production run data (boards, cycle times, errors per machine)
- `Custom_ProgramCycleTime` — Ideal cycle time per program/line
- `FMS_ErrorData` — Feeder-level placement error logs

## License

MIT — free to use, modify, and distribute.
