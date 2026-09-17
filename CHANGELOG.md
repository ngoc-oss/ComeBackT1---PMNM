# Changelog

Mọi thay đổi đáng chú ý được ghi theo phiên bản. Dự án dùng Semantic Versioning.

## 0.5.1 — 2026-09-17

- Làm sạch gói nguồn, loại tệp `.kotlin`/build sinh cục bộ và thêm kiểm tra release tự động.
- Bổ sung hướng dẫn Android Studio, AVD, Samsung A10s, checklist PoF và GitHub Release theo tag.
- CI chạy Python tests, kiểm tra gói, Android lint, JVM unit test và build APK theo ABI.
- Nâng ONNX Runtime Android từ 1.20.0 lên 1.30.0; thêm quy trình kiểm tra APK 16 KB.
- Chuẩn hóa README để tách ứng dụng ONNX hiện tại khỏi pipeline TensorFlow Lite nghiên cứu cũ.
- Bổ sung mẫu issue tính năng, hỗ trợ, quy tắc ứng xử và Dependabot.

## 0.5.0 — 2026-09-14

- Thêm kiểm tra tối, sáng, tương phản và độ nét trước inference.
- Thêm bộ lọc ảnh ngoài phạm vi bằng ML Kit offline, kèm trạng thái chặn và chụp lại.
- Thêm thông tin runtime/model/hash/thời gian, nút Chụp lại và xuất lịch sử CSV.
- Chuyển phần chữ giao diện tĩnh sang `strings.xml`; bỏ TensorFlow Lite khỏi Android runtime.
- Cấu hình APK theo armeabi-v7a, arm64-v8a, x86, x86_64 và universal.
- Thêm protocol đánh giá độc lập bằng ảnh Galaxy A10s; chưa tuyên bố metric trước khi thu thập thật.

## 0.4.0 — 2026-09-13

- Đóng sẵn model thịt ONNX INT8 và model quả ONNX FP32 trong một APK offline.
- Thiết kế lại giao diện cho màn hình 720×1520, có chọn miền, camera/thư viện và thẻ kết quả.
- Thêm màn hình nguồn, lịch sử cục bộ, benchmark 10 warmup + 100 lần và xuất CSV.
- Khóa phân tích khi ảnh lỗi; xử lý EXIF/ảnh lớn; lưu miền model khi Activity tái tạo.
- Thêm kiểm thử Android cho hai model, đổi model, ảnh hỏng, EXIF, lịch sử, nguồn/nhãn và CSV.

## 0.3.0 — 2026-09-11

- Bổ sung nguồn FruQ-DB Zenodo và ba nhãn Fresh/Mild/Rotten.
- Thêm pipeline huấn luyện/xuất/đánh giá model quả FreshCheck, tách khỏi checkpoint thịt.
- Thêm chọn miền trên Android và tiền xử lý ONNX riêng theo model.
- Ghi rõ nguy cơ rò rỉ frame video và việc không có checkpoint quả do tác giả bài báo phát hành.

## 0.2.0

- Bổ sung 2.266 ảnh Meat Freshness với nhãn Fresh/Half-Fresh/Spoiled.
- Bổ sung checkpoint ResNet-50 của Phteven, chuyển ONNX và kiểm tra parity.
- Thêm ONNX Runtime Android, model assets, script cài và hồ sơ nguồn gốc.

## 0.1.0

- Tạo Android Kotlin, pipeline MobileNetV2, hợp đồng ba nhãn, tài liệu, MIT/SPDX và CI ban đầu.
- Đây là bản chuẩn bị mã nguồn, chưa phải release công khai và chưa có số đo thiết bị thực.
