#!/usr/bin/env python3
"""
Demo script for LipidData / import_data.

Usage (from repo root):
  python3 scripts/demo_lipiddata.py
  python3 scripts/demo_lipiddata.py path/to/my.csv --validate

This script will try to make the package importable by adding `src/` to sys.path,
so you don't have to `pip install -e .` to run it.
"""
from __future__ import annotations

import logging
from pathlib import Path
import argparse
import sys

# make local src importable when running from repo root
repo_root = Path(__file__).resolve().parents[1]
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import lipidmaps
from lipidmaps import import_data, LipidData

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("demo_lipiddata")


def run_demo(csv_path: Path, validate: bool = False):
    logger.info(f"Importing CSV: {csv_path} (validate={validate})")
    data: LipidData = import_data(str(csv_path), validate=validate)

    print("\n--- Summary ---")
    print(f"Type: {type(data)}")
    print(f"Successful lipids: {data.successful_import_count()}")
    print(f"Failed lipids: {data.failed_import_count()}")
    print(f"Sample names: {data.samples()}")
    print(f"Some LM IDs: {data.get_lm_ids()[:10]}")

    # Pick a lipid (first) and show value retrieval examples
    lipids = data.lipids()
    if lipids:
        first = lipids[0]
        print("\n--- Example lipid ---")
        print(f"Input name: {first.input_name}")
        print(f"Standardized: {first.standardized_name}")
        print(f"LM ID: {first.lm_id}")
        # value by name
        for s in data.samples()[:3]:
            v = data.get_value_for_lipid(first.input_name, s)
            print(f"Value for {first.input_name} in {s}: {v}")
        # value by object
        if data.samples():
            s0 = data.samples()[0]
            v2 = data.get_value_for_lipid(first, s0)
            print(f"Value for object {first.input_name} in {s0}: {v2}")

    # DataFrame export
    try:
        df = data.as_dataframe()
        print("\n--- DataFrame ---")
        print(f"DataFrame shape: {df.shape}")
        print(df.head(3))
    except Exception as exc:
        logger.warning(f"as_dataframe() failed: {exc}")

    # Group statistics
    try:
        stats = data.get_group_statistics()
        print("\n--- Group statistics ---")
        for group_name, st in list(stats.items())[:5]:
            print(f"{group_name}: samples={st['sample_count']}, lipid_coverage={st['lipid_coverage']}")
    except Exception as exc:
        logger.warning(f"get_group_statistics() failed: {exc}")

    # Serialize to dict
    dd = data.to_dict()
    print("\n--- Serialized dataset keys ---")
    print(sorted(dd.keys()))

    print("\n--- Done ---")


def build_parser():
    p = argparse.ArgumentParser(description="Demo LipidData / import_data")
    p.add_argument(
        "csv",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1] / "tests" / "data" / "inputs" / "small_demo.csv"),
        help="CSV file to import (default: tests/data/inputs/small_demo.csv)",
    )
    p.add_argument("--validate", action="store_true", help="Run data validation during import")
    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    csv_path = Path(args.csv).expanduser()
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        raise SystemExit(2)
    run_demo(csv_path, validate=args.validate)
