# Kiểm chứng 0.2.0

Đọc `PUBLISHED_MODEL.md` cho kết quả model thật, số ảnh, nguồn công bố và hạn chế.
Đã nạp checkpoint gốc strict, xuất/kiểm ONNX, lượng tử hóa INT8, chạy 451 ảnh valid nguồn.
Đã kiểm 30 ảnh PyTorch/ONNX FP32 cùng nhãn. Model/config trong assets khớp SHA-256 và mapping. Chưa kiểm runtime điện thoại.

Phần sau lưu kết quả **lịch sử bản 0.1.0**, không phải trạng thái hiện tại của gói model mới.

---

# Kiểm chứng bản bàn giao — 10/09/2026

## Đã thực hiện

| Kiểm chứng | Kết quả |
|---|---|
| 8 Python unit tests | PASS: crop RGB, clamp/quantization, nhãn từ chối, nhãn xung đột, split không trùng group, chống path traversal |
| Chuỗi ML integration | PASS: chuẩn bị dữ liệu → train head → fine-tune → xuất FP32/FP16/INT8 → chạy cả 3 model và tạo metric/confusion matrix |
| Chọn ngưỡng | PASS trên fixture: cập nhật cấu hình khi đạt mục tiêu và từ chối predictions khác model hash |
| Android assembleDebug | BUILD SUCCESSFUL; tạo APK debug |
| Android testDebugUnitTest | 3 tests PASS: mapping fresh/spoiled, uncertain khác suspicious, NaN bị từ chối |

Integration test dùng **36 ảnh nhiễu tổng hợp**, MobileNetV2 alpha 0.35 không có ImageNet weights,
1 epoch head +1 epoch fine-tune. Đây chỉ là kiểm tra chuỗi phần mềm và conversion.
Không dùng model test trong APK và không giữ các số accuracy này làm kết quả thực phẩm.
Huấn luyện model chính mặc định alpha 0.75 với ImageNet; luồng tải trọng số ImageNet chưa chạy ở đây.

Môi trường kiểm: Linux, Python 3.12.14, TensorFlow CPU 2.16.1, Keras 3.15.1,
NumPy 1.26.4, Pillow 12.3.0, scikit-learn 1.8.0, Matplotlib 3.10.8.
Android: Gradle 8.9, AGP 8.7.3, Kotlin 2.0.21, compile/target SDK 35, min SDK 26.
Dependencies trực tiếp Python khóa theo các phiên bản đã chạy; chưa cung cấp lock transitive có hash toàn bộ.

## Chưa thực hiện / không được suy diễn

- Chưa có ảnh thực phẩm/dataset hoàn chỉnh, nhãn chuyên gia hoặc trained model thực phẩm.
- Chưa cài/chạy UI, camera, EXIF, offline, benchmark trên điện thoại hay emulator; build thành công không thay thế kiểm thử runtime.
- Chưa có accuracy/macro-F1/recall thực phẩm, phone latency, bộ test ngoài miền hoặc khảo sát UX.
- Chưa đối chiếu tensor/score Python–Android trên cùng ảnh; downsample/interpolation có thể khác nhẹ.
- Chưa tạo repository công khai, release Internet, chữ ký production, hoặc kiểm kê license transitive hoàn chỉnh.
- Chưa triển khai app iOS/ONNX, nhận dạng loại thực phẩm tự động hoặc OOD detector.

APK **FreshCheck-0.1.0-ui-debug.apk** được biên dịch từ source này, không kèm model.
Ứng dụng được thiết kế để hiển thị thiếu mô hình và khóa suy luận. Không coi APK này là bản AI đã nghiệm thu.
Sau khi cài model theo README phải build lại APK và thực hiện checklist EVALUATION.md trên máy thật.


## Build Android 0.2.0

Đã build assembleDebug thành công với ONNX INT8 trong assets. 3 JVM unit tests qua, không lỗi.
Chưa chạy camera/inference trên thiết bị Android thật; build không thay thế kiểm thử runtime.


## Bổ sung quả — phiên bản 0.3.0

Xem [FRUITQ.md](FRUITQ.md) cho nguồn Zenodo/Springer, ba nhãn Fresh/Mild/Rotten, model thử nghiệm FreshCheck, lệnh huấn luyện và quy trình đánh giá. Model quả không phải checkpoint của tác giả bài báo. Đánh giá nội bộ theo khung hình có nguy cơ rò rỉ video; chưa thay thế kiểm thử điện thoại hoặc tập mẫu độc lập. Kết quả thịt giữ riêng, không gộp với quả.


## Kiểm tra build Android 0.3.0

Build `assembleDebug` và `testDebugUnitTest` thành công; 3 kiểm thử JVM đạt. Đã mở APK để kiểm tra SHA256 cả hai model và các notice giấy phép; không gói model quả INT8 thất bại. APK khoảng 118,93 MB. **Chưa chạy camera, chuyển model và suy luận trên điện thoại/emulator trong phiên này.** Cần kiểm thử thiết bị thật trước khi nộp kết quả tốc độ/độ ổn định.
