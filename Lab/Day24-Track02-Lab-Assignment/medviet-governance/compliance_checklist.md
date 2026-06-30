# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | ✅ Done | Infra Team |
| Audit logging | CloudTrail + API access logs | ✅ Done | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | ✅ Done | Security Team |

## F. Technical Solutions cho các mục Todo

### Audit logging
- **Giải pháp:** FastAPI middleware ghi log mọi API request (user, role, resource, action, timestamp, IP) vào PostgreSQL audit table. Export sang ELK/CloudWatch với retention 2 năm theo NĐ13.
- **Implementation:** Middleware `AuditLogMiddleware` trong `src/api/main.py`, bảng `audit_logs` với index theo `user_id` và `timestamp`.

### Breach detection
- **Giải pháp:** Prometheus + Grafana monitor các anomaly: spike 401/403 errors, bulk download >1000 records, access ngoài giờ làm việc, failed login attempts.
- **Implementation:** Custom metrics trong FastAPI (`api_access_denied_total`, `bulk_export_count`), alert rules trong Grafana gửi Slack/PagerDuty trong 15 phút khi threshold vượt ngưỡng.

### Data Localization
- **Giải pháp:** Deploy toàn bộ stack trên AWS ap-southeast-1 (Singapore) hoặc Viettel Cloud (VN). S3 bucket policy deny cross-region replication ra ngoài VN.
- **Implementation:** Terraform config với `region = "ap-southeast-1"`, OPA policy deny export restricted data ra ngoài VN (đã implement trong `opa_policy.rego`).

### Explicit Consent
- **Giải pháp:** Consent management API với bảng `patient_consents` (patient_id, consent_type, granted_at, revoked_at). Chỉ cho phép training khi `consent_type = 'ai_training'` và `revoked_at IS NULL`.
- **Implementation:** Endpoint `POST /api/consent` và `DELETE /api/consent/{patient_id}` với audit trail.

### Breach Notification
- **Giải pháp:** Incident response runbook tự động: khi Prometheus alert fire → PagerDuty → Security team acknowledge trong 1h → báo cáo Bộ TT&TT trong 72h qua form chuẩn NĐ13.
- **Implementation:** PagerDuty integration + template báo cáo sự cố trong Confluence.
