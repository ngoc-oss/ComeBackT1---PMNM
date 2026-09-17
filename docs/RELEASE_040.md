# FreshCheck 0.4.0 — bản APK có sẵn model

Mục tiêu: người dùng chỉ cần cài APK trên Android 8 trở lên, không cần Python, Android Studio, tài khoản hay tải dataset/model. Bản APK được ký để cài thử; chưa phải chứng nhận an toàn thực phẩm hoặc bản phát hành Google Play.

## Thay đổi

- Giao diện tiếng Việt với thẻ giới thiệu xanh lá, các vùng chọn ảnh và kết quả riêng, nút thao tác lớn.
- Nút thư viện khác màu nút chụp ảnh; ba thanh điểm có màu xanh/vàng/đỏ và nhãn chữ.
- Tự cuộn đến vùng kết quả khi đã nhận ảnh hoặc phân tích xong.
- Giữ nhóm thịt/quả khi tái tạo Activity; phiên ảnh hiện tại phải chọn lại sau xoay màn hình.
- Ảnh hỏng xóa ảnh/kết quả cũ và khóa phân tích, tránh vô tình chạy lại ảnh trước đó.
- Mục Nguồn dữ liệu & mô hình hiển thị công bố, xuất xứ checkpoint và giới hạn.

## Nguồn model và dữ liệu

Thịt: Meat Freshness Prediction, arXiv 2305.00986 (preprint), liên kết đến TheLohia/Phteven. Checkpoint tác giả tại commit b31e61f43f8c608f119d379daa5b76768b50c5b3; ONNX INT8 là chuyển đổi của FreshCheck. Dữ liệu Kaggle của Vinayak Shanawad với Fresh/Half-Fresh/Spoiled. Không gọi preprint là bài tạp chí phản biện.

Quả: FruitQ, DOI 10.1007/s11042-023-16058-6, Multimedia Tools and Applications (2024; online 2023). FruQ-DB, Zenodo 7224690, DOI 10.5281/zenodo.7224690, có Fresh/Mild/Rotten. MobileNetV3 Small do FreshCheck huấn luyện trên bộ này; KHÔNG phải checkpoint tác giả bài FruitQ. Dùng FP32, không phân phối bản quả INT8 thất bại.

Không đổi chín/xanh/quá chín hoặc Good/Bad/Mixed thành ba nhãn tươi/hư. NGHI NGỜ là ánh xạ lớp trung gian; CHƯA ĐỦ CƠ SỞ là từ chối do confidence thấp. Cả hai mô hình chỉ phân loại dấu hiệu ngoại quan trong phạm vi nguồn.

## Cài trên Samsung A10s

Chép APK vào điện thoại → mở trong Tệp của bạn → cho phép cài từ ứng dụng đó nếu được hỏi → Cài đặt → mở FreshCheck → chọn Thịt đỏ hoặc Quả → Chụp ảnh/Chọn thư viện → Kiểm tra thực phẩm.

Nếu có lỗi xung đột chữ ký với bản debug cũ, gỡ bản FreshCheck cũ rồi cài bản này (lịch sử cũ sẽ bị xóa). Không gỡ trước khi thực sự gặp xung đột. Không cần máy ảo Pixel 6. Không dùng .tar.gz để cài vào điện thoại.

## Build từ mã nguồn

JDK 17, Android SDK 35, Build Tools 34.0.0, Gradle 8.9 (wrapper có checksum). Gói hoàn chỉnh chứa sẵn model ở android/app/src/main/assets. Mở thư mục android trong Android Studio, đồng bộ Gradle và Run. Hoặc trong thư mục android:

```powershell
.\gradlew.bat assembleDebug testDebugUnitTest
```

Kiểm thử Android cần thiết bị/emulator đã kết nối:

```powershell
.\gradlew.bat connectedDebugAndroidTest
```

Dependencies tải từ Google Maven/Maven Central theo cấu hình Gradle. Không cần dữ liệu huấn luyện khi build/chạy app.

## Giới hạn nghiệm thu

Kết quả chạy emulator phải được ghi riêng với A10s thật. Benchmark software emulator không thể dùng để khẳng định tốc độ điện thoại tầm trung. Test theo ảnh của FruQ có nguy cơ gần trùng video giữa các split, chưa chứng minh độc lập mẫu vật. Repo/release Internet, khảo sát UX và toàn bộ thể lệ cuộc thi vẫn cần bằng chứng riêng.

Bảng kết quả thực chạy của bản 0.4.0 nằm trong reports/release040 và báo cáo bàn giao. Không lấy kế hoạch kiểm thử làm kết quả đã đạt.
