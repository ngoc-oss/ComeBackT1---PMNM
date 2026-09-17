# Checklist PoF trước khi nộp

Checklist này tách rõ phần có trong mã nguồn và minh chứng chỉ có thể tạo trên dịch vụ/thiết bị thật.

| Tiêu chí | Trạng thái trong gói 0.5.1 | Việc bắt buộc trước khi nộp |
|---|---|---|
| Quản lý mã nguồn Internet | Sẵn sàng: CI, Issues/PR templates, `.gitignore` | Đẩy lên repository **public**, dùng commit/Issues thật |
| OSI-approved license | Đạt ở mã tự viết: MIT, toàn văn `LICENSE`, SPDX | Giữ license/notices trong release; rà dependency đã resolve |
| Ít nhất một release | Sẵn sàng: SemVer, changelog, workflow tag | Tạo tag `v0.5.1` và GitHub Release trước hạn |
| Build từ mã nguồn | Có wrapper, JDK/SDK cố định, lệnh build sạch | Build trên máy sạch và lưu log `BUILD SUCCESSFUL` |
| Thư viện/bundling | Gradle/pip chuẩn; không vendor/sửa source thư viện | Xuất dependency reports và kiểm tra license transitive |
| Tài liệu/giao tiếp | README, support, security, changelog, bug tracker | Dùng Issues thật; lưu đường dẫn và lịch sử xử lý |
| Sản phẩm Android | Hai model, ba nhãn, offline, guard, CSV, ABI splits | Chạy instrumentation và test thủ công trên AVD/A10s |
| Đánh giá model | Có báo cáo host và protocol ảnh độc lập | Thu ảnh điện thoại độc lập; báo accuracy/F1/confusion matrix |
| Hiệu năng thiết bị | Có benchmark CSV 10 warmup + 100 lần | Đo p50/p95 trên A10s; không dùng số host thay số điện thoại |
| Android 16 KB | Có dependency mới và script kiểm tra | `zipalign` + APK Analyzer phải PASS trước công bố hỗ trợ |

Không thể tạo trung thực repository public, release, lịch sử Issue, số đo A10s hoặc tập ảnh độc lập chỉ bằng
việc sửa file ZIP/TAR. Những mục đó phải được thực hiện thật và giữ link/log làm minh chứng.
