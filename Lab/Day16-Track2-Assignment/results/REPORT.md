### Thông tin sinh viên

- Tên: Trịnh Thị Lan Anh
- Mã SV: 2A202600737
- Ngày: 18/06/2026

### Báo cáo

- Do tài khoản AWS mới không có quota GPU (G/VT = 0), em triển khai phương án dự phòng LightGBM trên t3.micro. Training mất X giây, AUC-ROC = Y. Inference 1 dòng Z ms. So với g4dn.xlarge + vLLM, phương án này không cần GPU quota, chi phí thấp hơn ($0.07/giờ vs ~$0.57/giờ), nhưng training chậm hơn do 1 vCPU và 1 GB RAM.