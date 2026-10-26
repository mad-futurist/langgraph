"""run with `python -m benchmarks.issue_9410.benchmark --output results.json`.
"""

from __future__ import annotations

import argparse
import ast
import copy
import cProfile
import dataclasses
import gc
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import pstats
import random
import statistics
import sys
import time
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import FunctionType
from typing import Any
from uuid import UUID

from benchmarks.issue_9410.records import write_record
from langgraph.checkpoint.serde import jsonplus
from langgraph.checkpoint.serde.types import SendProtocol

HERE = Path(__file__).parent
STRATEGIES = (
    "baseline",
    "attribute_guard",
    "version_guard",
    "static_guard",
    "dataclass_first",
    "guarded_dataclass",
    "exact_registry",
    "type_cache",
)


class Kind(str, Enum):
    # Equivalent str/Enum mixin on 3.10; use actual StrEnum on 3.11+ below.
    A = "a"


if sys.version_info >= (3, 11):
    from enum import StrEnum

    class Kind(StrEnum):  # type: ignore[no-redef]
        A = "a"


@dataclasses.dataclass
class Leaf:
    code: str
    kind: Kind


@dataclasses.dataclass
class Node:
    name: str
    leaves: list[Leaf]


class SendLike:
    __slots__ = ("node", "arg", "timeout")
    __hash__ = object.__hash__

    def __init__(self, node: str, arg: Any, timeout: float | None = None):
        self.node, self.arg, self.timeout = node, arg, timeout

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SendLike) and (
            self.node,
            self.arg,
            self.timeout,
        ) == (other.node, other.arg, other.timeout)


def _condition(text: str) -> ast.expr:
    return ast.parse(text, mode="eval").body


def make_encoder(strategy: str) -> tuple[Callable[[Any], tuple[str, bytes]], dict]:
    """Clone globals so nested extension encoding uses the same isolated variant."""
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    tree = ast.parse((HERE / "baseline.py.txt").read_text(encoding="utf-8"))
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    branches = []
    branch = function.body[0]
    while isinstance(branch, ast.If):
        branches.append(branch)
        if len(branch.orelse) != 1:
            break
        branch = branch.orelse[0]
    send = next(
        b for b in branches if ast.unparse(b.test) == "isinstance(obj, SendProtocol)"
    )
    dc = next(
        b for b in branches if ast.unparse(b.test) == "dataclasses.is_dataclass(obj)"
    )
    namespace = dict(vars(jsonplus))
    namespace["_getattr_static"] = __import__("inspect").getattr_static
    namespace["_absent"] = object()
    cache: dict[type, bool] = {}

    def cached_send(obj: Any) -> bool:
        cls = type(obj)
        if cls not in cache:
            cache[cls] = isinstance(obj, SendProtocol)
        return cache[cls]

    namespace["_cached_send"] = cached_send
    guard = 'hasattr(obj, "node") and hasattr(obj, "arg")'
    if strategy == "attribute_guard":
        send.test = _condition(f"{guard} and isinstance(obj, SendProtocol)")
    elif strategy == "version_guard":
        send.test = _condition(
            f"(sys.version_info >= (3, 12) or ({guard})) and isinstance(obj, SendProtocol)"
        )
    elif strategy == "static_guard":
        send.test = _condition(
            '_getattr_static(obj, "node", _absent) is not _absent and '
            '_getattr_static(obj, "arg", _absent) is not _absent and '
            "isinstance(obj, SendProtocol)"
        )
    elif strategy == "dataclass_first":
        send.test, dc.test = dc.test, send.test
        send.body, dc.body = dc.body, send.body
    elif strategy == "guarded_dataclass":
        early = copy.deepcopy(dc)
        early.test = _condition(f"dataclasses.is_dataclass(obj) and not ({guard})")
        early.orelse = [send]
        branches[branches.index(send) - 1].orelse = [early]
    elif strategy == "type_cache":
        send.test = _condition("_cached_send(obj)")
    elif strategy == "exact_registry":
        # Keep all earlier duck-typed checks. Unknown types and subclasses use
        # the unchanged fallback; no dataclass/protocol decisions are registered.
        registry = {}
        for i, b in enumerate(branches):
            test = ast.unparse(b.test)
            names = {
                "isinstance(obj, UUID)": (UUID,),
                "isinstance(obj, decimal.Decimal)": (Decimal,),
                "isinstance(obj, date)": (date,),
            }.get(test)
            if names:
                handler = ast.parse("def handler(obj): pass").body[0]
                handler.body = copy.deepcopy(b.body)
                module = ast.fix_missing_locations(
                    ast.Module(body=[handler], type_ignores=[])
                )
                exec(compile(module, f"<{strategy}_handler_{i}>", "exec"), namespace)
                for cls in names:
                    registry[cls] = namespace["handler"]
        namespace["_exact_handlers"] = registry
        path_branch = next(
            b
            for b in branches
            if ast.unparse(b.test) == "isinstance(obj, pathlib.Path)"
        )
        early = ast.parse(
            "if (handler := _exact_handlers.get(type(obj))) is not None:\n"
            "    return handler(obj)"
        ).body[0]
        early.orelse = [path_branch]
        branches[branches.index(path_branch) - 1].orelse = [early]
    tree = ast.fix_missing_locations(tree)
    exec(compile(tree, f"<issue_9410_{strategy}>", "exec"), namespace)
    namespace["_msgpack_enc"] = FunctionType(jsonplus._msgpack_enc.__code__, namespace)
    dumps = FunctionType(jsonplus.JsonPlusSerializer.dumps_typed.__code__, namespace)
    serde = jsonplus.JsonPlusSerializer(allowed_msgpack_modules=True)
    return lambda obj: dumps(serde, obj), namespace


def workloads() -> dict[str, Any]:
    tree = [
        Node(str(i), [Leaf(str(j), Kind.A) for j in range(20)]) for i in range(2000)
    ]
    padded = [
        Node(str(i), [Leaf(str(j) + "x" * 134, Kind.A) for j in range(20)])
        for i in range(2000)
    ]
    nested: Any = padded
    for i in range(20):
        nested = {"level": i, "children": [nested]}
    return {
        "dataclass_42000": tree,
        "send_42000": [SendLike("worker", i) for i in range(42000)],
        "mixed": [
            [tree[i], SendLike("worker", i, 1.5), Decimal(i), Kind.A, UUID(int=i)]
            for i in range(1000)
        ],
        "small": tree[:1],
        "large_nested": nested,
        "exact_types": [
            [UUID(int=i), Decimal(i), date(2026, 1, 1)] for i in range(14000)
        ],
        "native": [{"name": str(i), "values": list(range(20))} for i in range(2000)],
    }


def profile(encode: Callable, value: Any, output: Path) -> dict:
    profiler = cProfile.Profile(timer=time.process_time_ns, timeunit=1e-9)
    profiler.runcall(encode, value)
    profiler.dump_stats(str(output))
    stats = pstats.Stats(profiler)
    rows = [
        {
            "file": key[0],
            "line": key[1],
            "function": key[2],
            "primitive_calls": v[0],
            "calls": v[1],
            "self_s": v[2],
            "cumulative_s": v[3],
        }
        for key, v in stats.stats.items()
    ]
    return {
        "total_s": stats.total_tt,
        "functions": sorted(rows, key=lambda r: r["cumulative_s"], reverse=True),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=21)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument(
        "--strategies", nargs="+", choices=STRATEGIES, default=STRATEGIES
    )
    parser.add_argument("--workloads", nargs="+")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--profile-strategies",
        nargs="+",
        choices=STRATEGIES,
        default=("baseline", "attribute_guard"),
    )
    args = parser.parse_args()
    if args.runs < 2 or args.warmups < 1:
        parser.error("use at least two runs and one warmup")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "environment": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "pythonhashseed": os.environ.get("PYTHONHASHSEED", "random"),
            "dependencies": {
                k: importlib.metadata.version(k)
                for k in ("ormsgpack", "langchain-core", "langgraph-checkpoint")
            },
            "runs": args.runs,
            "warmups": args.warmups,
            "gc": "disabled during warmups, timing and profiling; restored afterward",
            "p95": "nearest rank: sorted samples[ceil(0.95*n)-1]",
            "profile_timer": "process_time_ns (process CPU); separate from wall timing",
            "baseline_sha256": hashlib.sha256(
                (HERE / "baseline.py.txt").read_bytes()
            ).hexdigest(),
        },
        "workloads": {},
    }
    if args.resume and args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        for key in (
            "python",
            "dependencies",
            "runs",
            "warmups",
            "pythonhashseed",
            "baseline_sha256",
            "profile_timer",
        ):
            if previous["environment"][key] != result["environment"][key]:
                parser.error(f"cannot resume with changed {key}")
        result["workloads"] = previous["workloads"]
    encoders = {s: make_encoder(s)[0] for s in args.strategies}
    baseline = make_encoder("baseline")[0]
    values = workloads()
    rng = random.Random(9410)
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for name, value in values.items():
            if args.resume and name in result["workloads"]:
                continue
            if args.workloads and name not in args.workloads:
                continue
            expected = baseline(value)
            record = {"payload_bytes": len(expected[1]), "strategies": {}}
            samples: dict[str, list[float]] = {s: [] for s in encoders}
            cpu_samples: dict[str, list[float]] = {s: [] for s in encoders}
            for encode in encoders.values():
                for _ in range(args.warmups):
                    encode(value)
            # Interleave candidates in a reproducibly shuffled order to reduce drift.
            for _ in range(args.runs):
                order = list(encoders)
                rng.shuffle(order)
                for s in order:
                    cpu_start = time.process_time_ns()
                    start = time.perf_counter_ns()
                    encoders[s](value)
                    samples[s].append((time.perf_counter_ns() - start) / 1e6)
                    cpu_samples[s].append((time.process_time_ns() - cpu_start) / 1e6)
            for s, encode in encoders.items():
                median = statistics.median(samples[s])
                measurement = {
                    "median_ms": median,
                    "p95_ms": sorted(samples[s])[math.ceil(0.95 * args.runs) - 1],
                    "samples_ms": samples[s],
                    "process_cpu_samples_ms": cpu_samples[s],
                    "process_cpu_median_ms": statistics.median(cpu_samples[s]),
                    "byte_identical": encode(value) == expected,
                    "profile": profile(
                        encode,
                        value,
                        args.output.with_name(f"{args.output.stem}_{name}_{s}.prof"),
                    )
                    if s in args.profile_strategies
                    else None,
                }
                record["strategies"][s] = measurement
                print(
                    f"{name:18} {s:20} {median:9.3f} ms p95={measurement['p95_ms']:.3f} identical={measurement['byte_identical']}",
                    flush=True,
                )
            base_ms = record["strategies"].get("baseline", {}).get("median_ms")
            if base_ms:
                for measurement in record["strategies"].values():
                    measurement["speedup"] = base_ms / measurement["median_ms"]
            result["workloads"][name] = record
            write_record(args.output, result)
    finally:
        if gc_was_enabled:
            gc.enable()


if __name__ == "__main__":
    main()
