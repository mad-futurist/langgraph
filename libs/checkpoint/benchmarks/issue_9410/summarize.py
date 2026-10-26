"""Render recorded statistics to Markdown; never run or recompute benchmarks."""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
RISKS = {
    "baseline": "Reference",
    "attribute_guard": "Rejected: descriptor reads; nominal conformance",
    "version_guard": "Rejected: same changes before 3.12",
    "static_guard": "Rejected: dynamic members; nominal conformance",
    "dataclass_first": "Rejected: changes precedence/constructor record",
    "guarded_dataclass": "Rejected: descriptor reads; nominal conformance",
    "exact_registry": "Regular cases pass; misses target workload",
    "type_cache": "Rejected: per-instance conformance",
}


def render(results_dir: Path) -> str:
    lines = [
        "# Issue 9410: recorded measurements",
        "",
        "Bundled results/ files are historical; custom input may contain fresh or smoke runs.",
        "This appendix formats stored statistics; it does not recompute or rerun them.",
        "Wall latency, unprofiled process CPU and instrumented CPU profiles are separate.",
        "Speedup is relative to that workload's baseline; matching workload bytes do",
        "not establish compatibility for the adversarial cases in the regression tests.",
        "Display precision is three decimal places for milliseconds and two for ratios;",
        "the JSON retains the original precision and all raw latency/CPU samples.",
        "",
    ]
    count = 0
    for path in sorted(results_dir.glob("*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(result, dict) or "workloads" not in result:
            continue
        count += 1
        env = result["environment"]
        lines.extend(
            [
                f"## {path.name}",
                "",
                f"Python: `{env['python']}`; dependencies: `{env['dependencies']}`.",
                f"Warmups: {env['warmups']}; samples: {env['runs']}; p95: {env['p95']}.",
                f"Platform: `{env['platform']}`; hash seed: `{env['pythonhashseed']}`.",
                "",
            ]
        )
        for workload, record in result["workloads"].items():
            lines.extend(
                [
                    f"### {workload} ({record['payload_bytes']:,} bytes)",
                    "",
                    "| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |",
                    "|---|---:|---:|---:|---:|---|---|",
                ]
            )
            for strategy, m in record["strategies"].items():
                speedup = f"{m['speedup']:.2f}x" if "speedup" in m else "n/a"
                lines.append(
                    f"| {strategy} | {m['median_ms']:.3f} | {m['p95_ms']:.3f} | "
                    f"{m['process_cpu_median_ms']:.3f} | {speedup} | "
                    f"{'Identical' if m['byte_identical'] else 'Different'} | {RISKS.get(strategy, 'Unreviewed')} |"
                )
            lines.append("")
    if not count:
        raise ValueError(f"no benchmark records found in {results_dir}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=HERE / "results")
    parser.add_argument("--output", type=Path, default=HERE / "measurements.md")
    args = parser.parse_args()
    summary = render(args.results_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
