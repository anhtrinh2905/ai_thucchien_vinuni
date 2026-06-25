# Bonus — GPU-offload sweep

Model: `Llama-3.2-3B-Instruct-Q4_K_M.gguf`  ·  threads: `10`

| -ngl | tg128 (tok/s) |
|--:|--:|
| 0 | 6.0 |
| 8 | 16.5 |
| 16 | 12.6 |
| 24 | 25.4 |
| 32 | 30.9 |
| 99 | 39.5 |

When the model fits in VRAM, `-ngl 99` (full offload) is fastest. When it doesn't, partial offload (`-ngl 16` or `-ngl 24`) keeps the most compute on the GPU while spilling weights to RAM — usually still beats CPU-only (`-ngl 0`). Watch for the curve flattening: after the layer count covers the model's actual depth, more `-ngl` does nothing.
