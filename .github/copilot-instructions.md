## Quick orientation

This repository contains small, self-contained Python scripts for plotting and data visualization (primarily Plotly). The two primary scripts are:

- `plot_bode_plotly.py` — reads CSV files with frequency/magnitude columns and writes interactive HTML Bode magnitude plots. Focus for changes: CSV parsing (delimiter sniffing, comment/blank-line handling), numeric coercion, and Plotly layout options.
- `test.py` — a simple Plotly example generating three-phase sine waves; useful as a minimal runnable example and reference for Plotly usage patterns in the repo.

## Architecture and data flow (big picture)

- Scripts are single-file command-line style tools (no package structure). Input usually comes from the current working directory (e.g., `plot_bode_plotly.main()` globs `*.csv`). Output is written to the same folder or an explicit `out_dir`/`out_path`.
- `plot_bode_plotly.py` flow: read file -> sniff delimiter -> parse header labels -> parse numeric rows (skip empty/comment rows) -> create Plotly traces -> write HTML with embedded plotly.js.

## Patterns & conventions to follow

- CSV parsing: be conservative. The code intentionally attempts to parse messy CSVs (different delimiters, comma-as-decimal). Preserve the existing fallbacks: `csv.Sniffer()` then [",", ";", "\t", " "] fallback; accept `#` comment rows and skip blank rows.
- Data shape expectations: most functions assume exactly two numeric columns (frequency x, magnitude y). Validate and raise clear errors when this is violated (see `read_labels_and_data`).
- Logging / user output: existing scripts use plain `print()` for errors and progress. When adding new functionality keep this lightweight stdout behavior rather than heavy logging frameworks.
- Plotly output: HTML files are written with `include_plotlyjs=True` for offline viewing. Keep this behavior unless the change explicitly aims to stream plotly from CDN.

## Developer workflows (how-to run & debug)

- Quick run (interactive): open a terminal in the script folder and run the script. Example (PowerShell):

```powershell
python .\plot_bode_plotly.py
```

It looks for `*.csv` in the current working directory and produces `bode_all.html` or individual `*_bode.html` outputs.

- Minimal dev dependencies: the code uses `plotly` and `numpy` (the latter only in `test.py`). If you need to install:

```powershell
pip install plotly numpy
```

- Tests: there are no automated tests in the repo. For quick checks, run `test.py` to ensure Plotly rendering works and run `plot_bode_plotly.read_labels_and_data` interactively with sample CSVs.

## Files to inspect when making changes

- `plot_bode_plotly.py` — CSV parsing, delimiter sniffing (`sniff_delimiter`), row handling, and write path logic. Any change to CSV handling should update or add unit tests (if you add tests) and preserve the robust fallback behavior.
- `test.py` — a runnable example showing how Plotly traces are constructed; useful for small UI/layout changes.
- `README.md` — general repo description (currently minimal). Use it for higher-level docs if you add more scripts or dependencies.

## Integration points & external dependencies

- plotly (required for all plotting). HTML files are standalone (include JS). No web server is required.
- numpy is used in `test.py` only; plot_bode_plotly avoids heavy numeric libs.

## Small actionable examples for the agent

- If adding support for more than two columns in `plot_bode_plotly.py`, update `read_labels_and_data` to return additional columns and update `plot_overlay` to accept multiple y-series; ensure `columns = columns[:2]` logic is adjusted or intentionally preserved.
- When improving delimiter detection, preserve the existing `try csv.Sniffer()` fallback order and ensure comment/blank row skipping remains intact.

## What to avoid

- Don’t assume package structure or imports — scripts run as top-level files and rely on CWD file discovery.
- Don’t remove `include_plotlyjs=True` without noting that HTML output will then require network access to load plotly.

## If you need more context

- Ask for typical input CSV samples (delimiter, header row format) and the target Python version. Also tell us whether you want HTML files to use CDN `plotly.js` instead of embedding.

---

Please review and tell me if you'd like these instructions expanded (examples for unit tests, a requirements.txt, or a CI run command). 
