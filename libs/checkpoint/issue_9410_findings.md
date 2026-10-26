# Issue 9410: serializer dispatch research

**The bottleneck is reproduced, but no universally safe optimization was
established among the tested candidates.** Keep production dispatch unchanged.

These are historical measurements at commit
`a25bfafe4858d2a85bede09ba83f9a591d1f1133` (checkpoint 4.3.0).
See the [reproduction guide](benchmarks/issue_9410/README.md),
[full comparison](benchmarks/issue_9410/measurements.md) and
[raw records](benchmarks/issue_9410/results/). All 234 recorded comparisons were
verified; publication preparation changed no numeric values.

## Root cause and setup

[Issue 9410](https://github.com/langchain-ai/langgraph/issues/9410) concerns a
private ~9 MiB tree. Our public-shaped fixture has 2,000 Nodes and 40,000 Leaves:
2,138,893 encoded bytes; the padded nested workload has 7,539,253 bytes.

On Python 3.11, each dataclass reaches `SendProtocol` before the dataclass
branch. The workload makes 82,000 callbacks: 40,000 enums bypass that check,
while 42,000 dataclasses trigger 84,000 protocol-member collections. Protocol
checking accounts for 53.3% of instrumented CPU time; unprofiled baseline CPU
median is 906.250 ms. Python 3.12 caches members and uses static lookup, changing
both cost and descriptor/dynamic-attribute behavior.

Host: Windows x86-64, build 26200, six logical CPUs;
`Intel64 Family 6 Model 213 Stepping 1, GenuineIntel`. Main dependencies:
ormsgpack 1.12.2 and langchain-core 1.6.5. Python versions appear below.

Setup is outside timing: three warmups, 21 interleaved samples, seeded order,
`PYTHONHASHSEED=0`, GC disabled. Wall time uses `perf_counter_ns`; CPU samples
and separate cProfile runs use `process_time_ns`. p95 is sample 20 of 21.
Eight strategies cover seven workloads on 3.11–3.14; 3.10 covers dataclasses.
Variants compile the frozen callback into separate recursive encoder globals;
production code is not patched.

## Hypotheses

| Hypothesis | Experiment | Decision |
|---|---|---|
| H1 | Dynamic, version-gated and static member guards | Speed measured; equivalence rejected by descriptor, dynamic-member and nominal-subclass tests |
| H2 | Dataclass first; guarded early dataclass branch | Faster on plain dataclasses; precedence changes or guard counterexamples prevent compatibility |
| H3 | Exact UUID/Decimal/date handlers after duck checks | Limited benefit on exact-type distribution; no target dataclass benefit; broad registry unproven |
| H4 | Cache protocol conformance solely by type | Uniform-instance speed does not survive per-instance member differences; rejected |
| H5 | Whole-encode profiles and predicate microbenchmarks | Protocol cost dominates the 3.11 profile; other dispatch/preparation remains; broader optimization unproven |

## Historical results

### Python 3.11: 42,000 dataclasses

Payload: 2,138,893 bytes. Matching regular-workload bytes do not establish
compatibility for arbitrary objects.

| Strategy | Median ms | p95 ms | Speedup | Correctness | Compatibility risk |
|---|---:|---:|---:|---|---|
| baseline | 1027.715 | 1197.470 | 1.00x | Workload bytes identical | Reference |
| attribute_guard | 314.561 | 343.629 | 3.27x | Workload bytes identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 327.129 | 357.726 | 3.14x | Workload bytes identical | Rejected: same changes before 3.12 |
| static_guard | 650.479 | 775.269 | 1.58x | Workload bytes identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 303.333 | 338.812 | 3.39x | Workload bytes identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 308.498 | 340.858 | 3.33x | Workload bytes identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 1050.212 | 1140.957 | 0.98x | Workload bytes identical | Regular cases pass; unchanged fallback; misses target workload |
| type_cache | 314.876 | 370.110 | 3.26x | Workload bytes identical | Rejected: per-instance conformance |

The Send-heavy guard median was 780.412 ms versus 727.743 ms baseline.
The exact registry achieved 1.22x on UUID/Decimal/date values, without removing
the target dataclass checks.

### Cross-version dataclass measurements

Independent builds/runs on one host; not controlled interpreter-only comparisons.

| Python | Baseline median / p95 ms | Guard median / p95 ms | Guard speedup | Baseline / guard CPU median ms |
|---|---:|---:|---:|---:|
| 3.10.22 | 494.098 / 794.748 | 148.452 / 294.450 | 3.33x | 453.125 / 140.625 |
| 3.11.17 | 1027.715 / 1197.470 | 314.561 / 343.629 | 3.27x | 906.250 / 281.250 |
| 3.12.10 | 449.010 / 502.108 | 262.059 / 415.958 | 1.71x | 375.000 / 234.375 |
| 3.13.17 | 213.953 / 242.230 | 142.528 / 171.636 | 1.50x | 203.125 / 125.000 |
| 3.14.9 | 295.911 / 470.382 | 196.463 / 368.611 | 1.51x | 250.000 / 156.250 |

### Instrumented CPU evidence

Profile times include substantial overhead. Cumulative times overlap; do not
add protocol/member-collection or recursive callback times together.

| Python | Send protocol checks | Member collections | Protocol CPU ms | Profile total CPU ms | Protocol share | Dispatch self ms | packb self ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3.10.22 | 42,000 | 84,000 | 4140.625 | 7218.750 | 57.4% | 1515.625 | 203.125 |
| 3.11.17 | 42,000 | 84,000 | 6250.000 | 11734.375 | 53.3% | 2296.875 | 390.625 |
| 3.12.10 | 42,000 | 0 | 1359.375 | 7406.250 | 18.4% | 2531.250 | 375.000 |
| 3.13.17 | 42,000 | 0 | 625.000 | 4109.375 | 15.2% | 1562.500 | 109.375 |
| 3.14.9 | 42,000 | 0 | 1000.000 | 5406.250 | 18.5% | 1640.625 | 328.125 |

The isolated H5 predicate diagnostic recorded 7,379.3 ns for the protocol check
versus 59.6 ns for dataclass detection. These are not additive encode savings;
raw timeit repeats were not retained.

With ormsgpack 1.12.1 on Python 3.11.17: baseline 550.447 ms median /
751.911 ms p95; guard 168.672 ms / 207.624 ms (3.26x). This separate run is not
a controlled comparison of ormsgpack versions.

## Compatibility findings

- Dynamic guards add descriptor reads and can change bytes. On 3.12+, a property
  raising `AttributeError` can change a baseline exception into dataclass encoding.
  Version gating leaves descriptor changes on older Python.
- Static guards reject older-Python `__getattr__` conformance. Both presence
  guards can reject explicit/registered protocol subclasses that `isinstance`
  accepts despite missing members.
- Dataclass-first changes overlapping Send-like objects from positional
  extension 1 to keyword extension 2, altering bytes and restored extra fields.
  A guarded dataclass branch retains guard counterexamples.
- Type-only caching fails when same-class instances expose different members.
  The exact registry preserves earlier duck checks and subclass fallback, but
  does not solve the dataclass bottleneck.

Tests cover tags, bytes, round trips, exceptions, attribute reads, inheritance,
slots and mixed collections. Passing rejected-candidate tests demonstrate
counterexamples not safety.

