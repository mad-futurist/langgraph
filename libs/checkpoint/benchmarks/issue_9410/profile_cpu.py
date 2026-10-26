"""measure process cpu attribution / dispatch expression costs"""

import argparse
import ast
import cProfile
import pstats
import statistics
import time
import timeit
from pathlib import Path

from benchmarks.issue_9410.benchmark import HERE, Kind, Leaf, make_encoder, workloads
from benchmarks.issue_9410.records import write_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = workloads()["dataclass_42000"]
    result = {}
    for strategy in ("baseline", "attribute_guard", "exact_registry"):
        encode, namespace = make_encoder(strategy)
        for _ in range(3):
            encode(value)
        cpu_samples = []
        for _ in range(7):
            start = time.process_time_ns()
            encode(value)
            cpu_samples.append((time.process_time_ns() - start) / 1e6)
        profiler = cProfile.Profile(timer=time.process_time_ns, timeunit=1e-9)
        profiler.runcall(encode, value)
        stats = pstats.Stats(profiler)
        rows = [
            {
                "file": k[0],
                "function": k[2],
                "calls": v[1],
                "self_s": v[2],
                "cumulative_s": v[3],
            }
            for k, v in stats.stats.items()
        ]
        result[strategy] = {
            "unprofiled_process_cpu_samples_ms": cpu_samples,
            "unprofiled_process_cpu_median_ms": statistics.median(cpu_samples),
            "profile_total_process_cpu_s": stats.total_tt,
            "profile_functions": sorted(
                rows, key=lambda r: r["cumulative_s"], reverse=True
            ),
        }
        if strategy == "baseline":
            node = (
                ast.parse((HERE / "baseline.py.txt").read_text(encoding="utf-8"))
                .body[0]
                .body[0]
            )
            namespace["obj"] = Leaf("one", Kind.A)
            predicates = []
            while isinstance(node, ast.If):
                expr = ast.unparse(node.test)
                timer = timeit.Timer(expr, globals=namespace)
                timings = timer.repeat(repeat=5, number=10000)
                predicates.append(
                    {
                        "expression": expr,
                        "median_ns": statistics.median(timings) * 1e9 / 10000,
                    }
                )
                if len(node.orelse) != 1:
                    break
                node = node.orelse[0]
            result["baseline"]["isolated_predicates"] = predicates
    write_record(args.output, result)


if __name__ == "__main__":
    main()
