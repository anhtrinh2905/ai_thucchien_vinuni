# Reflection — Lab 20 (Personal Report)

> **Đây là báo cáo cá nhân.** Mỗi học viên chạy lab trên laptop của mình, với spec của mình. Số liệu của bạn không so sánh được với bạn cùng lớp — chỉ so sánh **before vs after trên chính máy bạn**. Grade rubric tính theo độ rõ ràng của setup + tuning của bạn, không phải tốc độ tuyệt đối.

---

**Họ Tên:** Trịnh Thị Lan Anh
**Cohort:** A2026-K2
**Ngày submit:** 2026-06-25

---

## 1. Hardware spec (từ `00-setup/detect-hardware.py`)

- **OS:** macOS 26 (Darwin 25.3.0, arm64)
- **CPU:** Apple M4
- **Cores:** 10 physical / 10 logical
- **CPU extensions:** ARM NEON + SME (ARM_FMA, FP16_VA, MATMUL_INT8, DOTPROD, ACCELERATE)
- **RAM:** 16.0 GB (unified memory)
- **Accelerator:** Apple Metal (GPU recommendedMaxWorkingSetSize ≈ 12.7 GB)
- **llama.cpp backend đã chọn:** Metal (`-DGGML_METAL=on`)
- **Recommended model tier:** Llama-3.2-3B-Instruct (Q4_K_M)

**Setup story** (≤ 80 chữ): Hai chỗ phải sửa. (1) Trong PATH có Homebrew LLVM `clang-21`, nó mặc định tìm `MacOSX26.sdk` không tồn tại → gevent + llama-cpp-python build fail. Fix: ép `CC=/usr/bin/clang`, `SDKROOT=$(xcrun --show-sdk-path)` (SDK 15.5). (2) Repo bartowski không có file `Q2_K` → đổi sang `unsloth/Llama-3.2-3B-Instruct-GGUF` (có cả Q4_K_M lẫn Q2_K cùng tên file).

---

## 2. Track 01 — Quickstart numbers (từ `benchmarks/01-quickstart-results.md`)

Settings: `n_threads=10`, `n_ctx=2048`, `n_batch=512`, `n_gpu_layers=99` (full Metal offload).

| Model | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode rate (tok/s) |
|---|--:|--:|--:|--:|--:|
| Llama-3.2-3B-Instruct-Q4_K_M | 8482 | 72 / 170 | 24.6 / 26.2 | 1645 / 1767 / 1796 | 40.7 |
| Llama-3.2-3B-Instruct-Q2_K   | 1342 | 75 / 178 | 23.7 / 26.1 | 1564 / 1817 / 1858 | 42.2 |

**Một quan sát** (≤ 50 chữ): Trên Metal, Q2_K chỉ nhanh hơn Q4_K_M ~3.7% (42.2 vs 40.7 tok/s) chứ không phải "rẻ một nửa" như kỳ vọng từ file size. Vì decode bị giới hạn bởi băng thông bộ nhớ thống nhất, mà cả hai đều fit; vài bit/weight ít hơn của Q2_K không bù nổi chất lượng tệ đi → Q4_K_M đáng đánh đổi.

---

## 3. Track 02 — llama-server load test

Server Python (`python -m llama_cpp.server`, Metal, Q4_K_M, `--n_ctx 2048 --n_gpu_layers 99`). Mix tải: 80% prompt ngắn, 20% prompt RAG dài. Số liệu lấy từ `benchmarks/locust-10_stats.csv` và `locust-50_stats.csv`.

| Concurrency | Total RPS | E2E P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|--:|--:|--:|--:|--:|--:|
| 10 | 0.41 | 18000 | 27000 | 29000 | 0 |
| 50 | 0.47 | 27000 | 46000 | 46000 | 0 |

(Các request không streaming nên latency báo là full-response time, không tách TTFB.)

**Batching observation** (từ `record-metrics.py` trên **native** server có `/metrics`, port 8081, `--parallel 4 --cont-batching`): dưới tải, `llamacpp:requests_processing` đạt đỉnh **4** (đầy cả 4 slot), `llamacpp:requests_deferred` lên tới **8** (queue vượt công suất), và `llamacpp:n_busy_slots_per_decode` đạt đỉnh **≈ 3.91** — nghĩa là continuous batching nhồi gần 4 sequence vào *mỗi* bước decode. Bằng chứng: `benchmarks/02-server-metrics.csv` (34 mẫu) + `benchmarks/02-metrics-excerpt.txt` (`tokens_predicted_total=2343`).

**Reflection:** Từ 10 → 50 user, throughput gần như đứng yên (0.41 → 0.47 req/s) trong khi P95 gần gấp đôi (27s → 46s), 0 lỗi. Đây đúng là chữ ký **saturation**: 1 model 3B trên 1 GPU M4 đã chạm trần ngay từ 10 user, thêm concurrency chỉ kéo dài hàng đợi chứ không tăng **goodput@SLO**. Nếu SLO là "P95 < 5s" thì server đã miss ngay ở 10 user.

---

## 4. Track 03 — Milestone integration

`python 03-milestone-integration/pipeline.py` chạy end-to-end 3 query, in provenance context + timings (xem `benchmarks/03-pipeline-output.txt`).

- **N16 (Cloud/IaC):** _stub_ — chạy localhost only, llama-server trên :8080, không có IaC.
- **N17 (Data pipeline):** _stub_ — không có pipeline; corpus nạp in-memory.
- **N18 (Lakehouse):** _stub_ — `TOY_DOCS` in-memory (list dict), chưa nối Delta/Iceberg/SQLite.
- **N19 (Vector + Feature Store):** _stub_ — retrieval bằng keyword-overlap trên `TOY_DOCS`, chưa nối vector index thật.

(3/4 piece là stub có chủ đích; phần "thật" của track này là **N20 serving**: lời gọi OpenAI-compat tới llama-server đang chạy bằng model GGUF Metal.)

**Nơi tốn nhiều ms nhất** trong pipeline (đo bằng `time.perf_counter`):

- embed: _N/A_ (không dùng embedder; retrieval là keyword overlap)
- retrieve: ~0.0–0.1 ms
- llama-server: 954 – 2685 ms (P50 ≈ 1.0 s)

**Reflection** (≤ 60 chữ): Bottleneck nằm gọn ở **llama-server (decode)** — chiếm > 99.9% thời gian; retrieve gần như free vì là in-memory keyword match. Khớp kỳ vọng: với pipeline RAG nhỏ, generation luôn là phần đắt nhất; khi nối N19 vector store thật thì retrieve sẽ tăng nhưng vẫn nhỏ hơn decode một bậc.

---

## 5. Bonus — The single change that mattered most

**Change:** GPU offload — chạy llama.cpp (build từ source, Metal) với `-ngl 0` (CPU thuần) so với `-ngl 99` (offload toàn bộ 28 layer lên Metal). Đo bằng `llama-bench` (xem `benchmarks/bonus-gpu-offload-sweep.md`).

**Before vs after:**

```
before (-ngl 0,  CPU only):    6.0 tok/s   (tg, Llama-3.2-3B Q4_K_M)
after  (-ngl 99, full Metal): 39.5 tok/s
speedup: ~6.6×
```

Toàn bộ curve: `-ngl 0 → 6.0`, `8 → 16.5`, `16 → 12.6`, `24 → 25.4`, `32 → 30.9`, `99 → 39.5` tok/s (16 hơi thấp do nhiễu với `-r 2`, nhưng xu hướng đơn điệu tăng rất rõ).

**Tại sao nó work:** Decode tự hồi quy là bài toán **memory-bandwidth-bound**: mỗi token sinh ra phải đọc lại toàn bộ trọng số của mọi layer từ bộ nhớ. 10 CPU core của M4 chia sẻ băng thông LPDDR thấp hơn nhiều so với GPU, và matmul throughput của CPU SIMD (NEON) thua xa khối ALU của GPU. Khi offload tất cả layer lên Metal, trọng số + KV cache nằm trên đường băng thông cao của GPU, và mỗi bước decode dùng compute song song của GPU thay vì 10 core bị nghẽn. Vì là Apple Silicon **unified memory**, "đẩy lên GPU" không tốn copy qua PCIe — chỉ là đổi bộ xử lý đọc cùng vùng RAM, nên speedup gần như toàn bộ đến từ bandwidth + compute của GPU. Đường cong cũng cho thấy partial offload (`-ngl 8/24/32`) đã thắng CPU rõ rệt: mỗi layer chuyển lên GPU là một phần memory traffic được chuyển sang đường nhanh hơn, và vì model fit hẳn trong 12.7 GB working set nên `-ngl 99` là nhanh nhất, không có điểm gãy do tràn VRAM.

---

## 6. (Optional) Điều ngạc nhiên nhất

Trên Metal, Q2_K gần như không nhanh hơn Q4_K_M (42.2 vs 40.7 tok/s) — trái với trực giác "quant nhỏ hơn = nhanh hơn nhiều". Quant chủ yếu mua lại **RAM/disk**, còn tốc độ thì bị memory-bandwidth chặn ở cùng một trần; nên knob đáng giá nhất hóa ra là *GPU offload*, không phải *chọn quant*.

---

## 7. Self-graded checklist

- [x] `hardware.json` đã commit
- [x] `models/active.json` đã commit (path Q4_K_M + Q2_K resolves)
- [x] `benchmarks/01-quickstart-results.md` đã commit
- [x] `benchmarks/02-server-results.md` + `02-server-metrics.csv` (record-metrics) đã commit
- [x] `benchmarks/bonus-gpu-offload-sweep.md` đã commit (1 sweep)
- [ ] Ít nhất 6 screenshots trong `submission/screenshots/` (xem `submission/screenshots/README.md`) — **cần bạn chụp**
- [ ] `make verify` exit 0 (chạy ngay trước khi push)
- [ ] Repo trên GitHub ở chế độ **public**
- [ ] Đã paste public repo URL vào VinUni LMS

---

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Nếu private, grader không xem được → 0 điểm.
