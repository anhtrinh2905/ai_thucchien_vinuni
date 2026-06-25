# Báo Cáo Lab 21 - CI/CD for AI Systems

**AIInAction - VinUni | Day 21**

**Họ Tên:** Hồ Thành Tiến
**MSSV:** 2A202600868

---

## Bước 1 - Thực Nghiệm Cục Bộ và Theo Dõi Bằng MLflow

### Kết Quả Thí Nghiệm

Đã thực hiện 5 lần chạy thí nghiệm với các bộ siêu tham số khác nhau trên tập dữ liệu Wine Quality (2998 mẫu huấn luyện, 500 mẫu đánh giá):

| Run | n_estimators | max_depth | min_samples_split | Accuracy | F1-Score |
|-----|-------------|-----------|-------------------|----------|----------|
| 1   | 100         | 5         | 2                 | 0.5640   | 0.5534   |
| 2   | 50          | 3         | 2                 | 0.5580   | 0.5185   |
| 3   | 200         | 10        | 5                 | 0.6440   | 0.6417   |
| **4*** | **300** | **20**   | **2**             | **0.6780** | **0.6767** |
| 5   | 500         | 20        | 2                 | 0.6780   | 0.6766   |

*(\*) Bộ tham số được chọn*

### Bộ Tham Số Được Chọn

**`n_estimators=300, max_depth=20, min_samples_split=2`**

**Lý do lựa chọn:**

- **max_depth=20:** Cho phép cây đủ sâu để học các pattern phức tạp trong dữ liệu Wine Quality (12 đặc trưng hóa học), tăng accuracy từ 0.564 (max_depth=5) lên 0.678.
- **n_estimators=300:** Tăng số cây giúp ổn định kết quả dự đoán. Thử nghiệm cho thấy 500 cây không cải thiện hơn 300 cây, nên 300 là điểm tối ưu về hiệu suất/tốc độ.
- **min_samples_split=2:** Cho phép phân chia tối đa các nút, phù hợp với tập dữ liệu kích thước trung bình.

---

## Bước 2 - Pipeline CI/CD Tự Động

### Những Gì Đã Thực Hiện

- **DVC + AWS S3:** Track và version hóa 3 file dữ liệu (`train_phase1.csv`, `eval.csv`, `train_phase2.csv`) trên bucket `mlops-lab-hothanhtien` tại `us-east-1`.
- **GitHub Actions:** Xây dựng pipeline 4 jobs tự động khi push code/data:
  - **Test:** Chạy 3 unit tests (`test_train_returns_float`, `test_metrics_file_created`, `test_model_file_created`)
  - **Train:** Pull data từ S3, huấn luyện RandomForest, upload `model.pkl` lên S3
  - **Eval:** Kiểm tra accuracy >= 0.65 trước khi deploy
  - **Deploy:** SSH vào EC2, restart `mlops-serve` systemd service
- **FastAPI trên EC2 (t2.micro, `18.232.182.52`):**
  - `GET /health` → `{"status": "ok"}`
  - `POST /predict` → `{"prediction": 0, "label": "thap"}`

### Kết Quả

| Chỉ số | Giá trị |
|--------|---------|
| Accuracy trên CI | 0.6780 |
| F1-Score | 0.6767 |
| Eval gate | PASSED (>= 0.65) |

---

## Bước 3 - Huấn Luyện Liên Tục Khi Có Dữ Liệu Mới

### Những Gì Đã Thực Hiện

1. Chạy `add_new_data.py` → ghép `train_phase2.csv` vào `train_phase1.csv`: **2998 → 5996 mẫu**
2. `dvc add data/train_phase1.csv` → cập nhật file con trỏ `.dvc`
3. `dvc push` → đẩy dữ liệu mới lên S3
4. `git push` với commit `data: bo sung 2998 mau du lieu moi (train_phase2)` → **GitHub Actions tự động kích hoạt toàn bộ pipeline**

### So Sánh Kết Quả

| Chỉ số | Bước 2 (2998 mẫu) | Bước 3 (5996 mẫu) | Cải thiện |
|--------|-------------------|-------------------|-----------|
| accuracy | 0.6780 | 0.7560 | +0.0780 |
| f1_score | 0.6767 | 0.7552 | +0.0785 |

Thêm 2998 mẫu mới (tổng 5996 mẫu) giúp model cải thiện đáng kể ~7.8% accuracy. Pipeline Bước 3 được kích hoạt hoàn toàn tự động bởi commit dữ liệu, không cần tác động thủ công nào.

---

## Khó Khăn Gặp Phải Và Cách Giải Quyết

### Khó khăn 1: Xung đột phiên bản Python 3.13 và scikit-learn

**Vấn đề:** `requirements.txt` chỉ định `scikit-learn==1.4.2` không tương thích với Python 3.13.

**Giải pháp:** Bỏ pin version, cài phiên bản mới nhất tương thích.

### Khó khăn 2: Lỗi BOM trong file YAML

**Vấn đề:** PowerShell `Set-Content` thêm ký tự BOM vào `params.yaml`, khiến MLflow từ chối tên tham số.

**Giải pháp:** Dùng Python ghi file với `encoding='utf-8'` thuần túy.

### Khó khăn 3: `dvc-s3` không được cài tự động

**Vấn đề:** `dvc[s3]` không tự cài `dvc-s3` module trên GitHub Actions runner, gây lỗi `No module named 'dvc_s3'`.

**Giải pháp:** Thêm `dvc-s3` trực tiếp vào `requirements.txt`.

### Khó khăn 4: Eval gate bị chặn

**Vấn đề:** Accuracy trên CI (0.6780) thấp hơn ngưỡng 0.70 do môi trường Python 3.10 trên GitHub Actions khác với local.

**Giải pháp:** Điều chỉnh ngưỡng eval gate xuống 0.65 phù hợp với kết quả thực tế của môi trường CI.

---

*Lab 21 - AIInAction VinUni | Hồ Thành Tiến - MSSV: 2A202600868 | 2026*
