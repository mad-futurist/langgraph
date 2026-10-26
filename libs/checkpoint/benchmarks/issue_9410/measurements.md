# Issue 9410: recorded measurements

Bundled results/ files are historical; custom input may contain fresh or smoke runs.
This appendix formats stored statistics; it does not recompute or rerun them.
Wall latency, unprofiled process CPU and instrumented CPU profiles are separate.
Speedup is relative to that workload's baseline; matching workload bytes do
not establish compatibility for the adversarial cases in the regression tests.
Display precision is three decimal places for milliseconds and two for ratios;
the JSON retains the original precision and all raw latency/CPU samples.

## ormsgpack_1121_311.json

Python: `3.11.17 (main, Oct 21 2026, 17:46:24) [MSC v.1944 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.1', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-10-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 550.447 | 751.911 | 500.000 | 1.00x | Identical | Reference |
| attribute_guard | 168.672 | 207.624 | 140.625 | 3.26x | Identical | Rejected: descriptor reads; nominal conformance |

## results_310.json

Python: `3.10.22 (main, Oct  9 2026, 15:18:58) [MSC v.1944 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.2', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-10-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 494.098 | 794.748 | 453.125 | 1.00x | Identical | Reference |
| attribute_guard | 148.452 | 294.450 | 140.625 | 3.33x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 165.863 | 249.582 | 156.250 | 2.98x | Identical | Rejected: same changes before 3.12 |
| static_guard | 333.640 | 480.404 | 281.250 | 1.48x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 171.444 | 290.678 | 156.250 | 2.88x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 169.638 | 246.444 | 156.250 | 2.91x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 505.825 | 772.382 | 468.750 | 0.98x | Identical | Regular cases pass; misses target workload |
| type_cache | 169.328 | 278.066 | 156.250 | 2.92x | Identical | Rejected: per-instance conformance |

## results_311.json

Python: `3.11.17 (main, Oct 21 2026, 17:46:24) [MSC v.1944 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.2', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-10-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 1027.715 | 1197.470 | 906.250 | 1.00x | Identical | Reference |
| attribute_guard | 314.561 | 343.629 | 281.250 | 3.27x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 327.129 | 357.726 | 281.250 | 3.14x | Identical | Rejected: same changes before 3.12 |
| static_guard | 650.479 | 775.269 | 609.375 | 1.58x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 303.333 | 338.812 | 281.250 | 3.39x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 308.498 | 340.858 | 296.875 | 3.33x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 1050.212 | 1140.957 | 968.750 | 0.98x | Identical | Regular cases pass; misses target workload |
| type_cache | 314.876 | 370.110 | 296.875 | 3.26x | Identical | Rejected: per-instance conformance |

### send_42000 (1,385,619 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 727.743 | 902.760 | 656.250 | 1.00x | Identical | Reference |
| attribute_guard | 780.412 | 931.400 | 593.750 | 0.93x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 819.516 | 1146.567 | 656.250 | 0.89x | Identical | Rejected: same changes before 3.12 |
| static_guard | 1277.303 | 1629.248 | 1015.625 | 0.57x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 788.688 | 846.420 | 625.000 | 0.92x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 800.563 | 949.619 | 640.625 | 0.91x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 759.033 | 859.553 | 703.125 | 0.96x | Identical | Regular cases pass; misses target workload |
| type_cache | 95.367 | 109.574 | 78.125 | 7.63x | Identical | Rejected: per-instance conformance |

### mixed (1,203,399 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 564.229 | 663.733 | 468.750 | 1.00x | Identical | Reference |
| attribute_guard | 196.052 | 251.137 | 171.875 | 2.88x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 207.612 | 340.586 | 156.250 | 2.72x | Identical | Rejected: same changes before 3.12 |
| static_guard | 398.774 | 526.079 | 312.500 | 1.41x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 203.283 | 344.014 | 171.875 | 2.78x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 188.968 | 284.371 | 156.250 | 2.99x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 568.926 | 749.978 | 468.750 | 0.99x | Identical | Regular cases pass; misses target workload |
| type_cache | 177.456 | 282.403 | 156.250 | 3.18x | Identical | Rejected: per-instance conformance |

### small (1,068 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.496 | 1.605 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.108 | 0.188 | 0.000 | 4.61x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.111 | 0.220 | 0.000 | 4.47x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.243 | 0.495 | 0.000 | 2.04x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.111 | 0.298 | 0.000 | 4.47x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.101 | 0.189 | 0.000 | 4.91x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.430 | 0.928 | 0.000 | 1.15x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.117 | 0.435 | 0.000 | 4.26x | Identical | Rejected: per-instance conformance |

### large_nested (7,539,253 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 1076.892 | 1731.140 | 890.625 | 1.00x | Identical | Reference |
| attribute_guard | 333.986 | 430.927 | 265.625 | 3.22x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 351.465 | 439.898 | 281.250 | 3.06x | Identical | Rejected: same changes before 3.12 |
| static_guard | 669.010 | 842.732 | 531.250 | 1.61x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 314.206 | 421.777 | 281.250 | 3.43x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 346.422 | 569.251 | 265.625 | 3.11x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 1085.216 | 1772.410 | 859.375 | 0.99x | Identical | Regular cases pass; misses target workload |
| type_cache | 321.631 | 524.935 | 281.250 | 3.35x | Identical | Rejected: per-instance conformance |

### exact_types (1,374,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 109.158 | 191.771 | 93.750 | 1.00x | Identical | Reference |
| attribute_guard | 101.036 | 134.557 | 78.125 | 1.08x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 108.453 | 130.741 | 93.750 | 1.01x | Identical | Rejected: same changes before 3.12 |
| static_guard | 107.335 | 210.821 | 78.125 | 1.02x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 105.807 | 170.263 | 93.750 | 1.03x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 104.838 | 172.412 | 93.750 | 1.04x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 89.534 | 116.920 | 78.125 | 1.22x | Identical | Regular cases pass; misses target workload |
| type_cache | 105.271 | 141.494 | 93.750 | 1.04x | Identical | Rejected: per-instance conformance |

### native (80,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.412 | 3.270 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.400 | 4.035 | 0.000 | 1.03x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.372 | 1.561 | 0.000 | 1.11x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.441 | 4.230 | 0.000 | 0.93x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.426 | 2.196 | 0.000 | 0.97x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.398 | 3.421 | 0.000 | 1.04x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.379 | 5.063 | 0.000 | 1.09x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.406 | 1.312 | 0.000 | 1.01x | Identical | Rejected: per-instance conformance |

## results_312.json

Python: `3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.2', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-11-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 449.010 | 502.108 | 375.000 | 1.00x | Identical | Reference |
| attribute_guard | 262.059 | 415.958 | 234.375 | 1.71x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 453.737 | 550.853 | 375.000 | 0.99x | Identical | Rejected: same changes before 3.12 |
| static_guard | 413.288 | 469.141 | 343.750 | 1.09x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 251.702 | 283.373 | 218.750 | 1.78x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 280.703 | 394.413 | 234.375 | 1.60x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 464.673 | 576.686 | 375.000 | 0.97x | Identical | Regular cases pass; misses target workload |
| type_cache | 261.377 | 374.804 | 234.375 | 1.72x | Identical | Rejected: per-instance conformance |

### send_42000 (1,385,619 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 122.990 | 272.994 | 93.750 | 1.00x | Identical | Reference |
| attribute_guard | 130.054 | 182.643 | 109.375 | 0.95x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 118.919 | 243.419 | 109.375 | 1.03x | Identical | Rejected: same changes before 3.12 |
| static_guard | 367.035 | 606.580 | 312.500 | 0.34x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 136.371 | 187.622 | 93.750 | 0.90x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 130.487 | 194.125 | 109.375 | 0.94x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 131.159 | 307.568 | 93.750 | 0.94x | Identical | Regular cases pass; misses target workload |
| type_cache | 95.948 | 137.485 | 78.125 | 1.28x | Identical | Rejected: per-instance conformance |

### mixed (1,203,399 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 136.673 | 243.411 | 109.375 | 1.00x | Identical | Reference |
| attribute_guard | 76.236 | 128.378 | 62.500 | 1.79x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 117.106 | 188.218 | 109.375 | 1.17x | Identical | Rejected: same changes before 3.12 |
| static_guard | 130.201 | 193.076 | 109.375 | 1.05x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 78.652 | 121.121 | 62.500 | 1.74x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 86.482 | 149.443 | 78.125 | 1.58x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 115.189 | 199.103 | 109.375 | 1.19x | Identical | Regular cases pass; misses target workload |
| type_cache | 77.088 | 144.945 | 78.125 | 1.77x | Identical | Rejected: per-instance conformance |

### small (1,068 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.135 | 0.394 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.082 | 0.091 | 0.000 | 1.64x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.135 | 0.238 | 0.000 | 1.00x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.131 | 0.283 | 0.000 | 1.03x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.083 | 0.124 | 0.000 | 1.63x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.084 | 0.224 | 0.000 | 1.61x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.138 | 0.206 | 0.000 | 0.98x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.084 | 0.159 | 0.000 | 1.61x | Identical | Rejected: per-instance conformance |

### large_nested (7,539,253 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 220.068 | 259.079 | 203.125 | 1.00x | Identical | Reference |
| attribute_guard | 130.127 | 162.044 | 125.000 | 1.69x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 214.629 | 243.631 | 203.125 | 1.03x | Identical | Rejected: same changes before 3.12 |
| static_guard | 214.526 | 233.364 | 187.500 | 1.03x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 133.586 | 154.208 | 125.000 | 1.65x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 139.759 | 169.109 | 125.000 | 1.57x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 224.754 | 253.777 | 203.125 | 0.98x | Identical | Regular cases pass; misses target workload |
| type_cache | 139.361 | 161.277 | 125.000 | 1.58x | Identical | Rejected: per-instance conformance |

### exact_types (1,374,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 60.269 | 77.655 | 46.875 | 1.00x | Identical | Reference |
| attribute_guard | 62.016 | 78.836 | 62.500 | 0.97x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 61.916 | 71.312 | 62.500 | 0.97x | Identical | Rejected: same changes before 3.12 |
| static_guard | 61.638 | 71.695 | 62.500 | 0.98x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 59.639 | 80.934 | 46.875 | 1.01x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 62.957 | 73.477 | 46.875 | 0.96x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 56.607 | 69.826 | 62.500 | 1.06x | Identical | Regular cases pass; misses target workload |
| type_cache | 59.028 | 71.238 | 62.500 | 1.02x | Identical | Rejected: per-instance conformance |

### native (80,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.324 | 0.678 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.331 | 0.579 | 0.000 | 0.98x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.332 | 2.813 | 0.000 | 0.98x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.321 | 0.563 | 0.000 | 1.01x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.321 | 1.020 | 0.000 | 1.01x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.328 | 7.239 | 0.000 | 0.99x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.315 | 0.532 | 0.000 | 1.03x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.322 | 0.600 | 0.000 | 1.01x | Identical | Rejected: per-instance conformance |

## results_313.json

Python: `3.13.17 (main, Oct 21 2026, 17:48:10) [MSC v.1944 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.2', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-11-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 213.953 | 242.230 | 203.125 | 1.00x | Identical | Reference |
| attribute_guard | 142.528 | 171.636 | 125.000 | 1.50x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 215.686 | 261.147 | 203.125 | 0.99x | Identical | Rejected: same changes before 3.12 |
| static_guard | 212.075 | 244.759 | 187.500 | 1.01x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 136.725 | 165.594 | 125.000 | 1.56x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 144.952 | 164.207 | 125.000 | 1.48x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 223.788 | 254.488 | 187.500 | 0.96x | Identical | Regular cases pass; misses target workload |
| type_cache | 138.967 | 174.380 | 125.000 | 1.54x | Identical | Rejected: per-instance conformance |

### send_42000 (1,385,619 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 85.385 | 137.467 | 62.500 | 1.00x | Identical | Reference |
| attribute_guard | 97.582 | 142.796 | 62.500 | 0.88x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 86.879 | 162.448 | 78.125 | 0.98x | Identical | Rejected: same changes before 3.12 |
| static_guard | 300.754 | 490.600 | 203.125 | 0.28x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 93.775 | 771.484 | 78.125 | 0.91x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 99.956 | 169.305 | 62.500 | 0.85x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 88.702 | 111.037 | 62.500 | 0.96x | Identical | Regular cases pass; misses target workload |
| type_cache | 71.895 | 176.460 | 62.500 | 1.19x | Identical | Rejected: per-instance conformance |

### mixed (1,203,399 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 154.048 | 366.245 | 140.625 | 1.00x | Identical | Reference |
| attribute_guard | 98.397 | 245.770 | 78.125 | 1.57x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 168.876 | 325.529 | 156.250 | 0.91x | Identical | Rejected: same changes before 3.12 |
| static_guard | 154.132 | 508.592 | 125.000 | 1.00x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 114.135 | 394.629 | 78.125 | 1.35x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 109.577 | 322.039 | 78.125 | 1.41x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 204.564 | 573.730 | 171.875 | 0.75x | Identical | Regular cases pass; misses target workload |
| type_cache | 113.489 | 213.297 | 93.750 | 1.36x | Identical | Rejected: per-instance conformance |

### small (1,068 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.201 | 0.710 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.097 | 0.431 | 0.000 | 2.07x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.191 | 5.003 | 0.000 | 1.05x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.222 | 4.053 | 0.000 | 0.90x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.103 | 0.471 | 0.000 | 1.96x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.102 | 0.406 | 0.000 | 1.98x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.221 | 3.383 | 0.000 | 0.91x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.102 | 1.038 | 0.000 | 1.96x | Identical | Rejected: per-instance conformance |

### large_nested (7,539,253 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 449.025 | 538.715 | 390.625 | 1.00x | Identical | Reference |
| attribute_guard | 271.940 | 354.954 | 250.000 | 1.65x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 455.728 | 529.516 | 375.000 | 0.99x | Identical | Rejected: same changes before 3.12 |
| static_guard | 431.292 | 636.429 | 375.000 | 1.04x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 275.068 | 328.074 | 234.375 | 1.63x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 290.015 | 357.231 | 234.375 | 1.55x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 475.198 | 581.278 | 406.250 | 0.94x | Identical | Regular cases pass; misses target workload |
| type_cache | 274.020 | 316.425 | 265.625 | 1.64x | Identical | Rejected: per-instance conformance |

### exact_types (1,374,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 55.569 | 70.344 | 46.875 | 1.00x | Identical | Reference |
| attribute_guard | 52.485 | 70.082 | 46.875 | 1.06x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 54.087 | 66.971 | 46.875 | 1.03x | Identical | Rejected: same changes before 3.12 |
| static_guard | 54.900 | 66.600 | 46.875 | 1.01x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 49.311 | 80.700 | 46.875 | 1.13x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 52.383 | 68.668 | 46.875 | 1.06x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 46.781 | 60.612 | 46.875 | 1.19x | Identical | Regular cases pass; misses target workload |
| type_cache | 50.846 | 71.016 | 46.875 | 1.09x | Identical | Rejected: per-instance conformance |

### native (80,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.313 | 0.372 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.317 | 0.543 | 0.000 | 0.99x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.315 | 0.372 | 0.000 | 0.99x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.322 | 0.904 | 0.000 | 0.97x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.322 | 0.485 | 0.000 | 0.97x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.314 | 0.393 | 0.000 | 1.00x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.310 | 0.331 | 0.000 | 1.01x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.320 | 0.458 | 0.000 | 0.98x | Identical | Rejected: per-instance conformance |

## results_314.json

Python: `3.14.9 (main, Oct 21 2026, 17:48:58) [MSC v.1944 64 bit (AMD64)]`; dependencies: `{'ormsgpack': '1.12.2', 'langchain-core': '1.6.5', 'langgraph-checkpoint': '4.3.0'}`.
Warmups: 3; samples: 21; p95: nearest rank: sorted samples[ceil(0.95*n)-1].
Platform: `Windows-11-10.0.26200-SP0`; hash seed: `0`.

### dataclass_42000 (2,138,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 295.911 | 470.382 | 250.000 | 1.00x | Identical | Reference |
| attribute_guard | 196.463 | 368.611 | 156.250 | 1.51x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 325.891 | 560.048 | 234.375 | 0.91x | Identical | Rejected: same changes before 3.12 |
| static_guard | 287.548 | 524.967 | 234.375 | 1.03x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 196.939 | 433.600 | 156.250 | 1.50x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 194.256 | 315.224 | 156.250 | 1.52x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 318.518 | 685.524 | 234.375 | 0.93x | Identical | Regular cases pass; misses target workload |
| type_cache | 184.957 | 302.262 | 156.250 | 1.60x | Identical | Rejected: per-instance conformance |

### send_42000 (1,385,619 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 138.190 | 288.181 | 93.750 | 1.00x | Identical | Reference |
| attribute_guard | 127.849 | 302.047 | 93.750 | 1.08x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 136.821 | 262.478 | 93.750 | 1.01x | Identical | Rejected: same changes before 3.12 |
| static_guard | 408.791 | 837.480 | 296.875 | 0.34x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 137.227 | 335.345 | 93.750 | 1.01x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 140.955 | 316.598 | 78.125 | 0.98x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 128.644 | 235.830 | 93.750 | 1.07x | Identical | Regular cases pass; misses target workload |
| type_cache | 101.084 | 227.453 | 78.125 | 1.37x | Identical | Rejected: per-instance conformance |

### mixed (1,203,399 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 144.060 | 302.740 | 125.000 | 1.00x | Identical | Reference |
| attribute_guard | 96.812 | 147.632 | 93.750 | 1.49x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 160.882 | 270.609 | 125.000 | 0.90x | Identical | Rejected: same changes before 3.12 |
| static_guard | 141.397 | 242.893 | 125.000 | 1.02x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 93.012 | 169.272 | 78.125 | 1.55x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 101.251 | 186.016 | 93.750 | 1.42x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 152.030 | 285.559 | 125.000 | 0.95x | Identical | Regular cases pass; misses target workload |
| type_cache | 100.314 | 192.827 | 78.125 | 1.44x | Identical | Rejected: per-instance conformance |

### small (1,068 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.137 | 0.373 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.089 | 0.504 | 0.000 | 1.53x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.138 | 0.213 | 0.000 | 0.99x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.132 | 0.226 | 0.000 | 1.04x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.088 | 0.256 | 0.000 | 1.55x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.089 | 0.123 | 0.000 | 1.54x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.145 | 0.751 | 0.000 | 0.95x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.090 | 0.152 | 0.000 | 1.52x | Identical | Rejected: per-instance conformance |

### large_nested (7,539,253 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 527.455 | 637.717 | 437.500 | 1.00x | Identical | Reference |
| attribute_guard | 328.937 | 374.797 | 281.250 | 1.60x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 538.058 | 688.965 | 453.125 | 0.98x | Identical | Rejected: same changes before 3.12 |
| static_guard | 472.054 | 673.156 | 406.250 | 1.12x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 336.637 | 460.763 | 265.625 | 1.57x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 337.112 | 379.292 | 281.250 | 1.56x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 527.298 | 861.403 | 437.500 | 1.00x | Identical | Regular cases pass; misses target workload |
| type_cache | 327.608 | 390.925 | 265.625 | 1.61x | Identical | Rejected: per-instance conformance |

### exact_types (1,374,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 54.239 | 75.028 | 46.875 | 1.00x | Identical | Reference |
| attribute_guard | 54.737 | 71.035 | 46.875 | 0.99x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 63.445 | 76.412 | 46.875 | 0.85x | Identical | Rejected: same changes before 3.12 |
| static_guard | 58.253 | 67.621 | 62.500 | 0.93x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 54.649 | 69.400 | 46.875 | 0.99x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 54.549 | 64.502 | 46.875 | 0.99x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 48.445 | 60.951 | 46.875 | 1.12x | Identical | Regular cases pass; misses target workload |
| type_cache | 56.097 | 65.720 | 46.875 | 0.97x | Identical | Rejected: per-instance conformance |

### native (80,893 bytes)

| Strategy | Wall median ms | Wall p95 ms | CPU median ms | Speedup | Workload bytes | Compatibility risk |
|---|---:|---:|---:|---:|---|---|
| baseline | 0.266 | 0.435 | 0.000 | 1.00x | Identical | Reference |
| attribute_guard | 0.350 | 0.635 | 0.000 | 0.76x | Identical | Rejected: descriptor reads; nominal conformance |
| version_guard | 0.274 | 0.936 | 0.000 | 0.97x | Identical | Rejected: same changes before 3.12 |
| static_guard | 0.303 | 0.467 | 0.000 | 0.88x | Identical | Rejected: dynamic members; nominal conformance |
| dataclass_first | 0.348 | 0.611 | 0.000 | 0.76x | Identical | Rejected: changes precedence/constructor record |
| guarded_dataclass | 0.272 | 0.521 | 0.000 | 0.98x | Identical | Rejected: descriptor reads; nominal conformance |
| exact_registry | 0.334 | 0.566 | 0.000 | 0.80x | Identical | Regular cases pass; misses target workload |
| type_cache | 0.258 | 0.631 | 0.000 | 1.03x | Identical | Rejected: per-instance conformance |
