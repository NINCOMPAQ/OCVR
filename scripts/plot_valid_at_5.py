from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


DATASET_ORDER = ["ATMONTO", "Brick", "DBpedia US Civic Geography"]
COLORS = {
    "ATMONTO": "#0072B2",
    "Brick": "#D55E00",
    "DBpedia US Civic Geography": "#009E73",
}
MARKERS = {
    "ATMONTO": "o",
    "Brick": "s",
    "DBpedia US Civic Geography": "^",
}


def load_posthoc(path: Path) -> dict[str, list[tuple[int, float]]]:
    series = {dataset: [] for dataset in DATASET_ORDER}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["method"] != "Post-hoc":
                continue
            dataset = row["dataset"]
            if dataset not in series:
                raise ValueError(f"Unexpected dataset in {path}: {dataset}")
            series[dataset].append((int(row["cap"]), float(row["valid_at_5"])))
    for dataset, values in series.items():
        values.sort()
        if not values:
            raise ValueError(f"No post-hoc rows for {dataset} in {path}")
    return series


def draw_panel(ax, path: Path, title: str) -> None:
    series = load_posthoc(path)
    caps = sorted({cap for values in series.values() for cap, _ in values})
    for dataset in DATASET_ORDER:
        values = series[dataset]
        ax.plot(
            [cap for cap, _ in values],
            [valid for _, valid in values],
            color=COLORS[dataset],
            marker=MARKERS[dataset],
            linewidth=2,
            markersize=6,
            label=dataset,
        )
    ax.axhline(1.0, color="#444444", linestyle="--", linewidth=1.6, label="Pre-hoc")
    ax.set_title(title)
    ax.set_xscale("log")
    ax.set_xticks(caps, [str(cap) for cap in caps])
    ax.set_ylim(0.60, 1.015)
    ax.grid(axis="both", color="#D9D9D9", linewidth=0.7, alpha=0.8)
    ax.set_xlabel("Post-hoc retrieval candidate limit")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot post-hoc valid@5 by candidate cap")
    parser.add_argument("--minilm", type=Path, required=True)
    parser.add_argument("--bge", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()

    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "figure.dpi": 150})
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    draw_panel(axes[0], args.minilm, "all-MiniLM-L6-v2")
    draw_panel(axes[1], args.bge, "bge-large-en-v1.5")
    axes[0].set_ylabel("valid@5")

    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=4, frameon=False)
    figure.tight_layout(rect=(0, 0.11, 1, 1))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=300, bbox_inches="tight")
    if args.pdf:
        args.pdf.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(args.pdf, bbox_inches="tight")
    plt.close(figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
