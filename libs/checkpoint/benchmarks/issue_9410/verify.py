"""Validate recorded statistics against samples without modifying any records."""

import argparse
import ast
import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(results_dir: Path, check_source: bool = False) -> int:
    snapshot = (HERE / "baseline.py.txt").read_bytes()
    digest = hashlib.sha256(snapshot).hexdigest()
    if check_source:
        source = HERE.parents[1] / "langgraph/checkpoint/serde/jsonplus.py"
        original = next(
            node
            for node in ast.parse(source.read_text(encoding="utf-8")).body
            if isinstance(node, ast.FunctionDef) and node.name == "_msgpack_default"
        )
        require(
            ast.dump(original) == ast.dump(ast.parse(snapshot).body[0]),
            "snapshot differs from the working production dispatch",
        )
    checked = 0
    for path in sorted(results_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "workloads" not in data:
            continue
        env = data["environment"]
        require(env["baseline_sha256"] == digest, f"{path.name}: baseline digest")
        for name, workload in data["workloads"].items():
            baseline = workload["strategies"].get("baseline")
            for strategy, record in workload["strategies"].items():
                label = f"{path.name}/{name}/{strategy}"
                samples = record["samples_ms"]
                require(len(samples) == env["runs"], f"{label}: sample count")
                require(
                    statistics.median(samples) == record["median_ms"],
                    f"{label}: median",
                )
                require(
                    sorted(samples)[math.ceil(0.95 * len(samples)) - 1]
                    == record["p95_ms"],
                    f"{label}: nearest-rank p95",
                )
                require(
                    len(record["process_cpu_samples_ms"]) == len(samples)
                    and statistics.median(record["process_cpu_samples_ms"])
                    == record["process_cpu_median_ms"],
                    f"{label}: CPU median/count",
                )
                if baseline is not None:
                    require(
                        baseline["median_ms"] / record["median_ms"]
                        == record["speedup"],
                        f"{label}: speedup",
                    )
                require(
                    record["byte_identical"] is True,
                    f"{label}: workload byte comparison",
                )
                checked += 1
    require(checked > 0, "no benchmark records found")
    return checked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=HERE / "results")
    parser.add_argument("--check-source", action="store_true")
    args = parser.parse_args()
    count = verify(args.results_dir, args.check_source)
    print(f"Verified {count} recorded comparisons; files were not modified.")


if __name__ == "__main__":
    main()
