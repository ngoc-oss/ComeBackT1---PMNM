# Cài FreshCheck 0.5.1 trên Samsung Galaxy A10s

## Cách nhanh nhất

1. Tải `FreshCheck-0.5.1-armeabi-v7a.apk` (nhẹ hơn) hoặc `FreshCheck-0.5.1-universal.apk` vào điện thoại.
2. Mở **Tệp của bạn** → **Tải về** → chạm APK.
3. Nếu Samsung chặn, chọn **Cài đặt** trong thông báo → bật **Cho phép từ nguồn này**
   cho Tệp của bạn hoặc trình duyệt vừa tải file → quay lại và chọn **Cài đặt**.
4. Mở **FreshCheck**. Chọn **Thịt đỏ** hoặc **Quả · FruQ-DB thử nghiệm**.
5. Chọn **Chụp ảnh** hoặc **Thư viện**, chụp một mẫu đủ sáng, rồi bấm **Kiểm tra thực phẩm**.

Không cần tải model/data riêng; hai model đã nằm trong APK. Không mở `.tar.gz` trên điện thoại.
Nếu báo xung đột chữ ký với FreshCheck cũ, chỉ khi đó mới gỡ bản cũ rồi cài lại; lịch sử cũ sẽ mất.

## Cài qua USB từ Windows

Trên A10s: **Cài đặt** → **Thông tin điện thoại** → **Thông tin phần mềm** → chạm 7 lần
**Số hiệu bản tạo** → nhập mã khóa → quay lại **Cài đặt cho người phát triển** → bật **Gỡ lỗi USB**.
Cắm cáp dữ liệu, chọn **Cho phép gỡ lỗi USB** trên điện thoại. Trong PowerShell có Android SDK:

```powershell
adb devices
adb install -r .\FreshCheck-0.5.1-armeabi-v7a.apk
```

Nếu `adb devices` không thấy máy: đổi cáp/cổng USB, chọn chế độ **Truyền tệp**, cài Samsung USB Driver,
rút cắm lại và chấp nhận khóa RSA trên điện thoại. Android Studio phải mở thư mục `android`, không mở
riêng gói `models`; sau Gradle Sync chọn tên điện thoại ở thanh thiết bị rồi Run.

## Đo tốc độ thật

Chọn một ảnh → phân tích một lần → **Đo tốc độ · Xuất CSV**. App chạy 10 lượt warmup và 100 lượt đo,
rồi mở hộp chia sẻ `benchmark.csv`. Gửi file sang máy tính và báo p50/p95 riêng cho thịt và quả.
Không dùng số emulator làm số A10s. Giữ pin trên 30%, tắt tiết kiệm pin và để máy nguội trước mỗi lượt.

## Phạm vi sử dụng

Kết quả chỉ phản ánh dấu hiệu nhìn thấy trong ảnh. Không phát hiện được mọi vi sinh vật, độc tố,
chất ô nhiễm hoặc hư hỏng bên trong. Nếu mùi, nhớt, bao bì phồng, quá hạn hoặc có dấu hiệu bất thường,
không dùng kết quả TƯƠI để quyết định ăn.

## Kiểm tra trên máy ảo Android Studio

Tạo AVD API 26 trở lên với system image **x86_64**, cài `FreshCheck-0.5.1-x86_64.apk`.
Trong Camera của AVD có thể chọn webcam hoặc Virtual scene. Bản ARM dành cho A10s không phải
lựa chọn phù hợp cho emulator x86_64; bản universal chạy được trên cả hai nhưng lớn hơn.
