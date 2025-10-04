from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple, Optional

from plotly.subplots import make_subplots
import plotly.graph_objects as go


def sniff_delimiter(sample: str) -> str:
    """Best-effort CSV delimiter sniffing with sensible fallbacks."""
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t ")
        return dialect.delimiter
    except Exception:
        # Common fallbacks
        for d in [",", ";", "\t", " "]:
            if d in sample:
                return d
        return ","


def read_labels_and_data(path: Path) -> Tuple[List[str], List[List[float]]]:
    """
    Reads a CSV where the first non-empty line contains axis labels.
    Returns (labels, columns) for exactly two numeric columns: frequency (x), magnitude (y).
    """
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        # Read a small sample to sniff delimiter
        raw_lines = f.read().splitlines()

    # Find first non-empty line for labels
    non_empty_lines = [ln for ln in raw_lines if ln.strip()]
    if not non_empty_lines:
        raise ValueError(f"{path.name}: file is empty or only whitespace")

    labels_line = non_empty_lines[0]
    # Build a sample for delimiter sniffing using first few lines
    sample = "\n".join(non_empty_lines[:5])
    delimiter = sniff_delimiter(sample)

    # Parse labels (take at most two)
    labels = [tok.strip().strip('"\'') for tok in labels_line.split(delimiter)]
    labels = [lbl for lbl in labels if lbl][:2]

    # Re-read to parse numeric rows, skipping the first non-empty line only once
    columns: List[List[float]] = []
    skipped_label = False
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            # Skip entirely empty rows
            if not row or not any(cell.strip() for cell in row):
                continue
            # Handle the first non-empty line as labels and skip it
            if not skipped_label:
                skipped_label = True
                continue

            # Skip comment rows starting with '#'
            first = row[0].strip() if row else ""
            if first.startswith("#"):
                continue

            # Convert to floats; stop at 2 columns max (freq, magnitude)
            numeric: List[float] = []
            for cell in row[:2]:
                c = cell.strip()
                if not c:
                    numeric.append(float('nan'))
                    continue
                try:
                    numeric.append(float(c))
                except ValueError:
                    # Try replacing comma decimal with dot
                    try:
                        numeric.append(float(c.replace(",", ".")))
                    except ValueError:
                        # Skip row if not parseable
                        numeric = []
                        break
            if not numeric:
                continue

            # Initialize column arrays lazily
            while len(columns) < len(numeric):
                columns.append([])
            for i, v in enumerate(numeric):
                columns[i].append(v)

    if len(labels) < 2:
        raise ValueError(
            f"{path.name}: expected 2 labels (x, y) in first line, got {labels!r}"
        )

    # Ensure exactly two columns of data exist
    if len(columns) < 2:
        raise ValueError(
            f"{path.name}: expected 2 numeric columns (x, y), got {len(columns)}"
        )
    columns = columns[:2]

    return labels, columns


def plot_bode_for_file(path: Path, out_dir: Optional[Path] = None) -> Path:
    labels, cols = read_labels_and_data(path)
    stem = path.stem

    # Prepare single-axis magnitude plot (Frequency vs Magnitude)
    x, y = cols
    x_label, y_label = labels
    fig = go.Figure(
        data=[go.Scatter(x=x, y=y, mode="lines", name=stem)],
        layout=go.Layout(template="plotly_white"),
    )
    fig.update_xaxes(title_text=x_label, type="log")
    fig.update_yaxes(title_text=y_label)
    fig.update_layout(
        title=f"{stem} Bode Magnitude",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=60, r=160, t=60, b=60),
    )

    # Output path
    if out_dir is None:
        out_dir = path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}_bode.html"
    # Embed plotly.js for offline viewing
    fig.write_html(str(out_path), include_plotlyjs=True)
    return out_path


def plot_overlay(csv_files: List[Path], out_path: Optional[Path] = None) -> Path:
    """Create one HTML with all CSV magnitude traces overlaid."""
    # Use labels from the first successfully parsed file
    fig = go.Figure(layout=go.Layout(template="plotly_white"))
    x_title: Optional[str] = None
    y_title: Optional[str] = None

    added = 0
    for fp in csv_files:
        try:
            labels, cols = read_labels_and_data(fp)
            x, y = cols
            if x_title is None and len(labels) >= 2:
                x_title, y_title = labels[0], labels[1]
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=fp.stem))
            added += 1
        except Exception as e:
            print(f"✖ Skipping {fp.name}: {e}")

    if added == 0:
        raise RuntimeError("No valid CSV files to plot.")

    if x_title:
        fig.update_xaxes(title_text=x_title, type="log")
    else:
        fig.update_xaxes(type="log")
    if y_title:
        fig.update_yaxes(title_text=y_title)

    fig.update_layout(
        title="Bode Magnitude (All CSVs)",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=60, r=200, t=60, b=60),
    )

    if out_path is None:
        out_path = Path.cwd() / "bode_all.html"
    fig.write_html(str(out_path), include_plotlyjs=True)
    return out_path


def main() -> None:
    cwd = Path.cwd()
    csv_files = sorted(cwd.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in current directory.")
        return

    print(f"Found {len(csv_files)} CSV file(s). Generating combined plot...")
    try:
        out = plot_overlay(csv_files)
        print(f"✔ Combined -> {out.name}")
    except Exception as e:
        print(f"✖ Failed to create combined plot: {e}")


if __name__ == "__main__":
    main()
