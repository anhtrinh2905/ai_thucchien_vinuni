# Reflection — Day 17 (≤ 200 words)

Answer briefly, in your own words. This is graded on reasoning, not length.

1. **The flywheel.** Day 13 emitted agent traces; today you turned them into an
   eval set and DPO pairs that Day 22 will train on. Which step in
   `traces → Bronze → datasets` would break most silently in production if you
   got it wrong — and how would you detect it?

2. **Decontamination.** Your run dropped 2 of 3 preference pairs because their
   prompts were in the eval set. What concretely goes wrong if you *skip* this
   step and train on those pairs? How would the lie show up in your metrics?

3. **Point-in-time.** The naive join leaked a future `lifetime_spend` into the
   training row. Describe one feature in a system you know that would be
   dangerous to join without an `ASOF`/point-in-time guard.

4. **Graph vs vector.** From `kg_demo.py`, name one question the knowledge graph
   answers well that flat chunk retrieval (`embed.py`) would struggle with, and
   one where the graph is overkill.

1. **Flywheel.** Bước dễ hỏng nhất là gán `split='eval'` khi flatten trace → Bronze. Nếu nhãn sai, prompt eval lọt vào tập train mà pipeline vẫn chạy bình thường. Phát hiện bằng audit: so khớp prompt trong `preference_pairs.jsonl` với `eval_golden.jsonl`, và theo dõi eval tăng đột biến trong khi production không cải thiện.

2. **Decontamination.** Bỏ bước này, model DPO học trùng prompt eval → benchmark đánh giá cao giả (memorization). Metric eval “đẹp” nhưng agent vẫn sai trên câu hỏi mới tương tự.

3. **Point-in-time.** Feature `lifetime_spend` hoặc “số đơn 30 ngày qua” nếu join giá trị mới nhất thay vì ASOF sẽ nhìn thấy chi tiêu tương lai — model offline tốt, deploy thì thiếu dữ liệu thật.

4. **Graph vs vector.** KG trả lời tốt câu multi-hop: “Widget ship từ đâu?” (widget → accessory → Hanoi). Vector đủ cho câu 1-hop: “Widget return trong bao lâu?” — một chunk đã chứa đủ fact.
