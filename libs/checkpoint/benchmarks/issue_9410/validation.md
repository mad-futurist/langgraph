# Issue 9410 validation record

## Historical investigation

These checks precede publication preparation. Their original transcripts are
preserved in the local archive, rather than published as large machine-specific
logs. No timing below is a new performance measurement.

| Check | Recorded result |
|---|---|
| `make format` | Passed |
| `make lint` with Git Bash as Make's shell | Passed |
| `pytest tests/test_jsonplus.py` on CPython 3.11.17 | 104 passed |
| `pytest tests/test_jsonplus_dispatch.py` on 3.10.22, 3.11.17, 3.12.10, 3.13.17, 3.14.9 | 193 passed per version |
| Unrestricted `make test` | Interrupted after missing-Redis connection retries; not a pass |
| `make test TEST='--ignore=tests/test_redis_cache.py'` on 3.12.10 | 445 passed |

The performance matrix contains 234 recorded strategy/workload comparisons:
eight strategies on seven workloads for 3.11–3.14, eight on the 3.10 dataclass
workload, and baseline/attribute guard on 3.11 with ormsgpack 1.12.1. The full
matrix uses ormsgpack 1.12.2 and langchain-core 1.6.5. Raw CPU samples and text
profile summaries are retained. Binary profiles are omitted from publication.

## Publication preparation

The initial Git audit found no staged changes and no tracked source diff.
Only the known research artifacts were untracked. The current local branch
was left unchanged; no staging, commit, push, PR or GitHub comment was made.
All 125 original research files were copied to a local archive and hash-checked
before cleanup, including the original user guard patch. Unrelated caches,
virtual environments and files were not cleaned.

Completed evidence checks before editing:

- Frozen callback AST equals the original function at commit
  `a25bfafe4858d2a85bede09ba83f9a591d1f1133`.
- The recorded baseline SHA-256 matches every workload result file.
- All 234 stored wall medians, nearest-rank p95 values, CPU medians, speedups,
  sample counts and byte-comparison flags agree with the raw records.
- All 90 binary profiles were readable; their originals remain archived.
- Portable JSON retains every numeric field and sample unchanged. Only path
  strings and whitespace changed; no performance statistics were replaced.

Fresh smoke output belongs in ignored `runs/`; it does not replace historical
performance data. Current checks executed during publication preparation:

| Command/check | Result |
|---|---|
| README Windows `uv python install`, `uv venv`, `uv pip install` setup | Passed in a fresh ignored 3.11.17 environment, with the documented dependency pins |
| `python -m pytest tests/test_jsonplus.py tests/test_jsonplus_dispatch.py -q --tb=short -o addopts=''` in that environment | 297 passed |
| Standalone `tests/test_jsonplus_dispatch.py` on 3.10.22, 3.12.10, 3.13.17, 3.14.9 | 193 passed per interpreter; 3.11 cases are also included in the 297 above |
| `make format` | Passed |
| `make lint` with Git Bash as Make's shell | Ruff formatting/import checks and ty passed |
| `make test TEST='--ignore=tests/test_redis_cache.py'` on 3.12.10 | 445 passed |
| Benchmark `--workloads small --runs 2 --warmups 1`, all eight strategies, plus H3 alone | Passed; workload bytes identical in all nine comparisons |
| `verify --results-dir benchmarks/issue_9410/runs` | Nine smoke comparisons verified |
| `verify --check-source` | 234 historical comparisons and current production AST verified; no record changed |
| `summarize` and custom `--results-dir` / `--output` | Historical and smoke summaries generated; main report unaffected |
| Historical CPU diagnostic samples | All three stored CPU medians agree with their seven samples |
| Numeric preservation and isolation audit | Every historical numeric leaf preserved; encoder, workload and profile functions AST-identical to their archived originals |
| Git review | No staged changes, no production/dependency diff, no whitespace errors |

No failing publication check remains. Initial scratch validation artifacts were
not included in the publication package. The raw performance matrix was not
rerun: the measurement methodology and experimental implementations did not
change. Metadata serialization is applied outside timing; summary changes only
affect presentation. Predicate diagnostics retain medians without raw timeit
repeat durations, an explicit evidence limitation.

POSIX execution, Redis integration, real core Send/graph behavior and downstream
integration remain unverified. A read-only TCP connection check to
127.0.0.1:6379 timed out. The unrestricted Redis-dependent suite was not retried;
no service or database was started or modified. No current failures were hidden
by changing test expectations, and no timing thresholds were added.
