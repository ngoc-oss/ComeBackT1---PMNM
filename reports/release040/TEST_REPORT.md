# Báo cáo kiểm thử FreshCheck 0.4.0

Ngày build: 2026-09-13. Package `vn.freshcheck.app`, versionCode 4, versionName 0.4.0,
minSdk 26, target/compileSdk 35.

## Kết quả đã chạy

| Hạng mục | Kết quả | Bằng chứng |
|---|---:|---|
| Gradle `assembleDebug` | Đạt | APK 118.950.358 byte |
| Gradle `assembleDebugAndroidTest` | Đạt | Test APK được biên dịch |
| JVM DecisionTest | 3/3 đạt | mapping 3 nhãn, từ chối output lỗi, uncertainty tách biệt |
| Python pipeline unit tests | 8/8 đạt | crop, group split/dedup, traversal, quantization, score/nhãn |
| Chữ ký APK | Đạt để cài thử | APK Signature Scheme v2, Android Debug certificate |
| ABI ONNX Runtime | Đạt khi kiểm gói | arm64-v8a, armeabi-v7a, x86, x86_64 |
| Model/config trong APK | Đạt | cả hai ONNX + config + nguồn nghiên cứu |
| Quyền mạng | Không có | manifest APK không yêu cầu `android.permission.INTERNET` |
| Full Android instrumentation lần build cuối | Chưa hoàn tất | emulator không KVM vẫn `device offline` sau 5 phút |

Instrumentation APK chứa 8 test: nạp+suy luận native hai model bằng ảnh thật, đổi model/tái tạo Activity,
ảnh hỏng không dùng lại ảnh cũ, giữ/xóa lịch sử 50 mục, EXIF+ảnh lớn, nguồn+nhãn, benchmark CSV 100 dòng,
và từ chối config thiếu. Bộ test đã biên dịch; lần chạy cuối không được tính là đạt vì hạ tầng emulator
không hoàn tất boot. Một lần chạy emulator trước bản chỉnh UI cuối đã cài/mở APK thành công; không thay thế
kiểm thử trên Galaxy A10s thật.

## Đánh giá model đã có

| Model | Tập đánh giá | Accuracy | Macro-F1 | Confusion matrix |
|---|---:|---:|---:|---|
| Thịt ResNet-50 ONNX INT8 | 451 ảnh valid nguồn | 87,80% | 0,8751 | `[[163,12,3],[13,119,27],[0,0,114]]` |
| Quả MobileNetV3 Small ONNX FP32 | 753 ảnh test nội bộ | 99,60% | 0,9956 | `[[230,2,0],[0,205,0],[0,1,315]]` |

Ngưỡng 0,70: thịt coverage 35,25%, accuracy trên phần chấp nhận 99,37%; quả coverage 98,67%,
accuracy trên phần chấp nhận 100%. Các số này là đánh giá đã lưu của artifact model tương ứng,
không phải kiểm định thực địa độc lập. Tập FruQ có thể rò rỉ frame video giữa split; tập thịt không có ID
mẫu vật. Không dùng số này để khẳng định an toàn thực phẩm hoặc độ chính xác trên ảnh camera A10s.

## Hash artifact

- Model thịt: `d8ef55440e48106b7c6a8c3633b67e49f8526bb8ebed0f455d692e57c8d7d572`.
- Model quả: `d20ed8f8e875044a3cdebe7fa9215392bd5041fd159f50e19dfb76aed9ebc4fd`.
- APK: `e71b6976ca63d25aac8041678c129d77d5d6a8d20a1200b1e2c6569c8a0f7961`.

## Nghiệm thu còn bắt buộc trên A10s thật

1. Cài/mở APK; cấp camera; chụp và chọn thư viện cho cả thịt/quả.
2. Chạy 8 instrumentation test bằng `connectedDebugAndroidTest` nếu có máy phát triển kết nối.
3. Xuất benchmark CSV từng model, tối thiểu 3 phiên; báo p50/p95 và nhiệt độ/điều kiện máy.
4. Kiểm tra xoay màn hình, ảnh EXIF, ảnh lỗi, xóa lịch sử và ứng dụng nhận CSV.

Không ghi “đã kiểm thử đầy đủ trên Samsung A10s” trước khi bốn bước này có bằng chứng từ máy thật.
