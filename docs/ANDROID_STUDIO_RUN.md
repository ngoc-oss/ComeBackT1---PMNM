# Chạy FreshCheck bằng Android Studio

## Công cụ cố định

- Android Studio có SDK Platform 35 và Build Tools 35.0.0.
- Gradle JDK: Temurin/JBR 17 hoặc 21; **không dùng JDK 25 với Gradle 8.9**.
- Mở đúng thư mục `FreshCheck-0.5.1/android`, không mở thư mục gói model.

## Build sạch

Trong Terminal của Android Studio trên Windows:

```powershell
.\gradlew.bat --version
.\gradlew.bat clean :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
```

Kết quả hợp lệ phải có `BUILD SUCCESSFUL`. APK nằm tại `app/build/outputs/apk/debug/`:

- `app-x86_64-debug.apk`: emulator x86_64;
- `app-armeabi-v7a-debug.apk`: Samsung A10s và máy ARM 32-bit;
- `app-arm64-v8a-debug.apk`: máy ARM64;
- `app-universal-debug.apk`: bản dùng chung.

## Máy ảo ổn định

Nếu Pixel 6 API 35 treo, tạo AVD **Pixel 4, API 33, Google APIs, x86_64**. Chọn 4 CPU,
RAM 4 GB, Graphics `Hardware`/`Automatic`. Nếu không boot được, đổi riêng Graphics sang `Software`,
Wipe Data rồi Cold Boot. Chỉ nhấn Run app sau khi AVD đã vào màn hình chính.

## Samsung Galaxy A10s

1. Bật Developer options và USB debugging.
2. Cắm cáp dữ liệu, chọn truyền tệp và chấp nhận khóa RSA trên điện thoại.
3. Chạy `adb devices`; trạng thái phải là `device`, không phải `unauthorized`.
4. Chọn A10s trên thanh thiết bị và Run. Có thể cài trực tiếp APK armeabi-v7a hoặc universal.

## Kiểm thử chức năng

```powershell
.\gradlew.bat :app:connectedDebugAndroidTest
```

Kiểm thủ công: chọn thịt/quả, camera, thư viện, ba kết quả, ảnh tối/sáng/mờ, ảnh người/xe,
chụp lại, lịch sử, xóa lịch sử, xuất CSV, benchmark và chạy offline sau khi tắt mạng.

## Kiểm tra Android 16 KB

Sau khi build universal APK:

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\check_android_16kb.ps1
```

Mở thêm **Build > Analyze APK**, kiểm tra cột Alignment của mọi tệp `.so`. Không phát hành cho thiết bị
16 KB nếu còn mục `UNALIGNED`. Samsung A10s dùng trang nhớ 4 KB nhưng release mới vẫn phải kiểm tra 16 KB.
