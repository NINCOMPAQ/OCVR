from __future__ import annotations

import csv
import json
from pathlib import Path


def load_master_results(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_csv(results: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "ontology",
        "model",
        "strategy",
        "retrieval_limit",
        "valid_at_5",
        "success_at_5",
        "time_seconds",
        "examined",
    ]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results["rows"])


def render_latex(results: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{longtable}{llrrrr}",
        r"\caption{Master comparison of retrieval strategies across ontologies and embedding models.}",
        r"\label{tab:appendix_master_results}\\",
        "",
        r"\toprule",
        r"\textbf{Strategy} & \textbf{Retrieval Limit} & \textbf{valid@5} & \textbf{success@5} & \textbf{time (s)} & \textbf{examined} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{Strategy} & \textbf{Retrieval Limit} & \textbf{valid@5} & \textbf{success@5} & \textbf{time (s)} & \textbf{examined} \\",
        r"\midrule",
        r"\endhead",
        r"\midrule",
        r"\multicolumn{6}{r}{\emph{Continued on next page}}\\",
        r"\endfoot",
        r"\bottomrule",
        r"\endlastfoot",
    ]
    current = None
    for row in results["rows"]:
        group = (row["ontology"], row["model"])
        if group != current:
            if current is not None:
                lines.append(r"\addlinespace")
            lines.append(rf"\multicolumn{{6}}{{l}}{{\textbf{{{group[0]}, {group[1]}}}}}\\")
            current = group
        lines.append(
            f"{row['strategy']} & {row['retrieval_limit']} & "
            f"{row['valid_at_5']:.4f} & {row['success_at_5']:.4f} & "
            f"{row['time_seconds']:.4f} & {_format_examined(row['examined'])} \\\\"
        )
    lines.extend(["", r"\end{longtable}", ""])
    destination.write_text("\n".join(lines), encoding="utf-8")


def _format_examined(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"
