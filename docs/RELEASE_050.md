# FreshCheck 0.5.0 — phạm vi nghiệm thu

## Thay đổi có thể kiểm chứng

- Chặn ảnh quá tối, quá sáng, tương phản thấp hoặc có chỉ số nét thấp trước inference.
- Dùng model gắn nhãn ảnh ML Kit đóng gói trong APK để chặn nhãn ngoài phạm vi mạnh như người và xe.
- Có nút **Chụp lại** tại kết quả; hiển thị runtime, phiên bản, hash model và ba mốc thời gian.
- Lịch sử tối đa 50 lượt có thể xuất CSV; benchmark vẫn xuất 100 lượt inference.
- Android chỉ còn ONNX Runtime; build tạo APK ARM, x86_64 và universal.

## Giới hạn bắt buộc công bố

Bộ lọc ML Kit là hàng rào hỗ trợ, không phải bộ phát hiện OOD được hiệu chỉnh trên phân phối FreshCheck.
Các ngưỡng tối/sáng/mờ là heuristic. Model quả chưa có đánh giá độc lập bằng ảnh điện thoại; không được
ghi số accuracy thực địa cho đến khi hoàn tất quy trình `PHONE_DATASET_PROTOCOL.md`.

Ba nhãn vẫn ánh xạ đúng nguồn: Fresh→TƯƠI, Half-Fresh/Mild→NGHI NGỜ, Spoiled/Rotten→HƯ.
Ứng dụng không phát hiện vi sinh vật, độc tố, chất gây dị ứng hoặc hư hỏng bên trong.

## Ma trận APK

| Gói | Thiết bị | ABI |
|---|---|---|
| armeabi-v7a | Galaxy A10s nếu hệ điều hành 32-bit | armeabi-v7a |
| arm64-v8a | Galaxy A10s nếu hệ điều hành 64-bit và đa số máy mới | arm64-v8a |
| x86_64 | Android Studio Emulator | x86_64 |
| universal | Dùng chung | bốn ABI |

## Điều kiện phát hành

Chỉ đánh dấu release đạt khi Gradle build thành công, `connectedDebugAndroidTest` đạt trên ít nhất một
AVD x86_64 API 26+ và APK ARM được cài/chạy/benchmark trên A10s. Kết quả chưa chạy không được ghi là PASS.
