from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import load_dataset, load_experiment
from .datasets import download_dataset, verify_dataset
from .render import load_master_results, render_csv, render_latex


def _data_path(config, data_dir: Path) -> Path:
    return data_dir / config.filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ontology-retrieval")
    parser.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    parser.add_argument("--data-dir", type=Path, default=Path(os.getenv("ONTOLOGY_RETRIEVAL_DATA_DIR", "datasets")))
    sub = parser.add_subparsers(dest="command", required=True)

    data = sub.add_parser("data")
    data_sub = data.add_subparsers(dest="data_command", required=True)
    for name in ("download", "verify"):
        command = data_sub.add_parser(name)
        command.add_argument("config", type=Path)

    index = sub.add_parser("index")
    index.add_argument("experiment", type=Path)
    index.add_argument("--replace", action="store_true")
    index.add_argument("--resume", action="store_true")

    verify_index = sub.add_parser("verify-index")
    verify_index.add_argument("experiment", type=Path)

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("experiment", type=Path)
    evaluate.add_argument("--output", type=Path, required=True)

    render = sub.add_parser("render")
    render.add_argument("results", type=Path)
    render.add_argument("--latex", type=Path)
    render.add_argument("--csv", type=Path)

    assemble = sub.add_parser("assemble")
    assemble.add_argument("runs", type=Path, nargs="+")
    assemble.add_argument("--output", type=Path, required=True)

    compare = sub.add_parser("compare")
    compare.add_argument("actual", type=Path)
    compare.add_argument("expected", type=Path)

    average = sub.add_parser("average")
    average.add_argument("runs", type=Path, nargs="+")
    average.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "data":
        config = load_dataset(args.config.resolve())
        path = _data_path(config, args.data_dir)
        result = download_dataset(config, path) if args.data_command == "download" else verify_dataset(path, config)
        print(result)
    elif args.command == "index":
        from .index import build_collection

        experiment = load_experiment(args.experiment.resolve())
        print(
            build_collection(
                experiment,
                _data_path(experiment.dataset, args.data_dir),
                args.qdrant_url,
                args.replace,
                args.resume,
            )
        )
    elif args.command == "verify-index":
        from .index import verify_collection

        print(json.dumps(verify_collection(load_experiment(args.experiment.resolve()), args.qdrant_url), indent=2))
    elif args.command == "evaluate":
        from .evaluate import run_experiment

        result = run_experiment(load_experiment(args.experiment.resolve()), args.qdrant_url)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    elif args.command == "render":
        result = load_master_results(args.results)
        if args.latex:
            render_latex(result, args.latex)
        if args.csv:
            render_csv(result, args.csv)
    elif args.command == "assemble":
        from .assemble import assemble_runs

        result = assemble_runs(args.runs)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    elif args.command == "compare":
        from .compare import compare_master_results

        actual = load_master_results(args.actual)
        expected = load_master_results(args.expected)
        differences = compare_master_results(actual, expected)
        if differences:
            print("\n".join(differences))
            return 1
        print("All deterministic paper-v1 values match the baseline.")
    elif args.command == "average":
        from .average import average_runs, write_average_csv

        write_average_csv(average_runs(args.runs), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
