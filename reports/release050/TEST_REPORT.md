# Báo cáo kiểm tra FreshCheck 0.5.0

Ngày: 2026-09-14.

## Đã chạy trong môi trường bàn giao

| Kiểm tra | Kết quả |
|---|---|
| Python pipeline unit tests | PASS — 8/8 |
| Kiểm tra mã không còn `FoodClassifier`/TensorFlow Lite dependency Android | PASS |
| Assets hai ONNX và config/hash còn trong source | PASS |
| Gradle compile/build 0.5.0 | BLOCKED — môi trường không có Android SDK/Gradle distribution và mạng build bị giới hạn |
| Instrumentation mới cho quality/OOD/history CSV | NOT RUN — cần AVD hoặc thiết bị |
| Galaxy A10s benchmark | NOT RUN — cần thiết bị của người dùng |
| Tập ảnh điện thoại độc lập | NOT COLLECTED — xem protocol, không tạo số liệu giả |

## Kiểm thử Android được bổ sung

`ReleaseTest` kiểm hai model ONNX, đổi miền và tái tạo Activity, ảnh lỗi, EXIF/ảnh lớn, lịch sử 50 lượt,
CSV lịch sử, ánh sáng tối/sáng, chính sách chặn nhãn Person/Car, nguồn/nhãn, benchmark 100 dòng và config thiếu.

Không được gọi source 0.5.0 là APK đã nghiệm thu cho tới khi lệnh sau PASS trong Android Studio:

```powershell
.\gradlew.bat clean :app:assembleDebug :app:connectedDebugAndroidTest
```
