# Issue 9410: isolated serializer dispatch experiments

This directory accompanies [the research report](../../issue_9410_findings.md)
for [LangGraph issue 9410](https://github.com/langchain-ai/langgraph/issues/9410).
It preserves positive performance results and the counterexamples that prevent
treating the tested fast paths as a universally safe production change.
Production serializer code is unchanged. These experiments are research code.

## Contents

| File | Purpose |
|---|---|
| `benchmark.py` | Workloads, isolated H1–H4 variants, timing and optional CPU profiles |
| `baseline.py.txt` | Original `_msgpack_default` function from commit `a25bfafe4858d2a85bede09ba83f9a591d1f1133` |
| `profile_cpu.py` | Separate CPU attribution and H5 predicate microbenchmarks |
| `records.py` | Portable path metadata and compact JSON, applied after timing |
| `verify.py` | Read-only checks of stored statistics, raw samples and baseline digest |
| `summarize.py` | Format stored numbers into Markdown; does not modify the report |
| `results/*.json` | Historical samples, environment metadata and text profile summaries |
| `measurements.md` | Generated historical comparison tables |
| `validation.md` | Historical and publication-preparation validation record |
| `../../tests/test_jsonplus_dispatch.py` | Differential compatibility tests and rejected-hypothesis counterexamples |

`runs/` and binary `.prof` files are ignored. Use `runs/` for new output so the
historical records remain intact. The original binaries, execution logs and
starting user patch were archived locally before cleanup; they are not needed
to reproduce the published experiments. Numeric fields in the historical JSON
are unchanged. Absolute source/executable/editable-project paths were replaced
with logical paths or placeholders. Full text profile rows remain available.

## Requirements and setup

Run all commands from `libs/checkpoint`, not the repository root. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/) first. Setup needs
network access to install Python and packages. Python >=3.10 is supported by the
library; these experiments were executed on CPython 3.10.22, 3.11.17, 3.12.10,
3.13.17 and 3.14.9 on Windows x86-64. POSIX commands below are supplied for
portability and were not executed on a POSIX host during this investigation.

The main matrix uses `ormsgpack==1.12.2`, `langchain-core==1.6.5`, and this
checkout's editable checkpoint 4.3.0. The reported-issue dependency cross-check
uses ormsgpack 1.12.1. Other dependencies come from the project's `dev` group.
`results/environment_311.json` preserves the original 3.11 package versions;
this is not a hermetic lock for every interpreter. Python 3.11.6 was not tested.

Windows PowerShell:

```powershell
uv python install 3.11.17
uv venv --python 3.11.17 .venvs/issue-9410-311
$benchPy = '.venvs/issue-9410-311/Scripts/python.exe'
uv pip install --python $benchPy -e . --group dev 'ormsgpack==1.12.2' 'langchain-core==1.6.5'
$env:PYTHONHASHSEED = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

POSIX shell:

```sh
uv python install 3.11.17
uv venv --python 3.11.17 .venvs/issue-9410-311
bench_py=.venvs/issue-9410-311/bin/python
uv pip install --python "$bench_py" -e . --group dev 'ormsgpack==1.12.2' 'langchain-core==1.6.5'
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
```

Keep the seed fixed before starting Python. Replace the interpreter version and
environment suffix to repeat on another version. On 3.10, the fixture uses the
`str, Enum` mixin because `StrEnum` is unavailable. Run with `python -m` as shown:
command-line fixtures use `__main__` type names, while imported fixtures use a
longer module name and produce different metadata/payload sizes.

## Smoke test, baseline and full comparison

A smoke test checks execution, not performance. From the PowerShell setup:

```powershell
& $benchPy -m benchmarks.issue_9410.benchmark --output benchmarks/issue_9410/runs/smoke.json --workloads small --runs 2 --warmups 1
& $benchPy -m benchmarks.issue_9410.verify --results-dir benchmarks/issue_9410/runs
```

Baseline on the issue-shaped tree:

```powershell
& $benchPy -m benchmarks.issue_9410.benchmark --output benchmarks/issue_9410/runs/baseline_311.json --strategies baseline --workloads dataclass_42000 --runs 21 --warmups 3
```

All eight strategies and seven workloads (an expensive run):

```powershell
& $benchPy -m benchmarks.issue_9410.benchmark --output benchmarks/issue_9410/runs/matrix_311.json --runs 21 --warmups 3
```

For POSIX, replace `& $benchPy` with `"$bench_py"` in these and subsequent
commands. Available workloads are `dataclass_42000`, `send_42000`, `mixed`,
`small`, `large_nested`, `exact_types`, and `native`. `--workloads` selects one
or more; omitting it selects all. The ordinary tree contains 2,000 Node and
40,000 Leaf objects with enum values. The larger tree adds padding and 20
container levels; its historical payload is 7,539,253 bytes, below the private
~9 MiB payload in the issue. That private dataset is unavailable.

## Run individual hypotheses

Each comparison should include its baseline in the same process:

```powershell
& $benchPy -m benchmarks.issue_9410.benchmark --output benchmarks/issue_9410/runs/attribute_guard_311.json --strategies baseline attribute_guard --workloads dataclass_42000 --runs 21 --warmups 3
```

Replace `attribute_guard` and the output filename to select another variant:

| Hypothesis | CLI strategy | Experimental change |
|---|---|---|
| Reference | `baseline` | Frozen original dispatch |
| H1 | `attribute_guard` | `hasattr(node)` / `hasattr(arg)` before protocol check |
| H1 | `version_guard` | Attribute guard only before Python 3.12 |
| H1 | `static_guard` | Static member-presence precheck |
| H2 | `dataclass_first` | Move dataclass branch before SendProtocol |
| H2 | `guarded_dataclass` | Early dataclass branch if the dynamic member guard fails |
| H3 | `exact_registry` | Exact UUID/Decimal/date handlers after existing duck-typed branches; original fallback |
| H4 | `type_cache` | Deliberately unsafe cache of protocol conformance by type |

H5 is the separate diagnostic below, not an additional serializer strategy.
Unknown types and subclasses in H3 still reach the original dispatch. H4's
regular workloads contain stable per-type attributes; its correctness tests
show why a speedup there cannot establish safety.

By default only `baseline` and `attribute_guard` are profiled when selected.
To profile another selected strategy, add `--profile-strategies baseline exact_registry`
(or another identifier from the table). CPU profiles run after latency sampling.
Binary profiles are written next to the JSON and remain ignored.

```powershell
& $benchPy -m benchmarks.issue_9410.profile_cpu --output benchmarks/issue_9410/runs/cpu_311.json
```

This diagnostic uses three warmups, seven unprofiled CPU samples, a separate
CPU profile, and five 10,000-iteration repeats for each predicate. Its fixtures
are imported, so do not combine its absolute latencies with the CLI matrix.
Historical predicate diagnostics retain medians only, not the five raw timeit
repeat durations; independent verification of those medians needs a rerun.

To repeat the issue dependency cross-check, install `ormsgpack==1.12.1` into a
separate environment using the setup above, then run the baseline/guard command.
The historical main matrix used 1.12.2 consistently; the separate 1.12.1 check
is not a controlled measurement of the difference between package versions.

## Correctness and project checks

```powershell
& $benchPy -m pytest tests/test_jsonplus.py tests/test_jsonplus_dispatch.py
& $benchPy -m benchmarks.issue_9410.verify --check-source
```

The latter command validates all historical samples/statistics and compares the
frozen function AST to the current production dispatch. A mismatch after a
future source change needs review; do not replace the snapshot automatically.
The snapshot SHA-256 is
`f12b8b42266fcbed8ab9eea1f4c2214f2542a6b84b5d3bd5bec1f5bfa31ac18d`.
It matches the original source commit's function AST; comments/line numbers
are not part of the AST comparison.

With GNU Make and uv available, follow the library's Makefile:

```sh
make format
make lint
make test TEST='--ignore=tests/test_redis_cache.py'
```

`uv run` in Make uses the project environment, which may differ from the
explicit benchmark interpreter. On Windows the lint recipes need a POSIX shell:
run Make from Git Bash or supply `SHELL=bash` with Bash on PATH. Redis tests
require a reachable local service and their fixtures can clear a database.
The investigation did not start or modify Redis; that integration file remains
unverified. Run it only in an appropriate existing test environment.

Tests have no latency thresholds. Passing candidate tests can mean that a
rejected candidate's counterexample was reproduced. The UUID monkeypatch in
one test is explicit and fixture-scoped; encoder variants themselves never
replace production globals.

## Verify records and regenerate summaries

Historical evidence, without remeasurement:

```powershell
& $benchPy -m benchmarks.issue_9410.verify --check-source
& $benchPy -m benchmarks.issue_9410.summarize
```

For fresh output, keep the summary separate:

```powershell
& $benchPy -m benchmarks.issue_9410.summarize --results-dir benchmarks/issue_9410/runs --output benchmarks/issue_9410/runs/measurements.md
```

The summary reads stored medians/p95/ratios and formats them; it never measures
or overwrites the main research report. CPU-only and dependency-list JSON are
not workload matrices and are skipped. A comparison run without a selected
baseline has no stored speedup; the summary prints `n/a`.

## Isolation, interpretation and limitations

`make_encoder` parses the frozen function into an AST and applies one named
transformation. Each encoder gets a copy of the production module globals,
its own compiled callback and a cloned recursive `_msgpack_enc` and public
`dumps_typed` function. Nested extensions therefore use the selected variant.
The baseline depends on the checkout's options/globals/decoder as well as its
frozen callback: reproduce against the stated source commit for fidelity.
`baseline.py.txt` is stored as text to preserve the original function unchanged.

Setup, object construction and compilation are outside timing. Three warmups
precede 21 interleaved measurements in seeded shuffled order. GC is disabled
and restored afterward. Wall time uses `perf_counter_ns`; CPU samples and
cProfile use `process_time_ns`. p95 is nearest rank (sample 20 of 21). Profile
cumulative times overlap, and the profiler's overhead is substantial. Windows
CPU-clock quantization can produce zero CPU samples for tiny payloads.

The workstation had no fixed CPU affinity, frequency or external-load control.
There are no confidence intervals or statistical significance claims. Treat
small differences and cross-version rankings cautiously. Byte equality for the
regular workloads does not prove equivalence for arbitrary Python objects.

The historical 3.11 run resumed after the first workload. `--resume` checks
Python/dependencies/hash seed/sample settings/baseline hash, but does not check
all strategy/workload choices; it restarts the random-order sequence and skips
already recorded workloads. It does not reproduce an uninterrupted process's
cache state or schedule. Use fresh complete runs for new controlled comparisons.
No resume behavior or timed loop was changed during publication preparation.

No native `langgraph.types.Send`, complete graph, downstream-library integration,
PyPy, free-threaded Python, or operating-system replication was tested. The
conclusion is limited: no universally safe optimization for the target workload
was established among the tested candidates. No experimental path is presented
as ready for production.
