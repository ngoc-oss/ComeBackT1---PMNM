# Báo cáo kiểm tra FreshCheck 0.5.1

Ngày chuẩn bị: 2026-09-17.

| Kiểm tra | Kết quả khi đóng gói nguồn |
|---|---|
| Python unit tests | PASS — 9/9 ngày 2026-09-17 |
| Source release audit | PASS |
| Python compileall | PASS |
| Model SHA-256 và ba nhãn | PASS qua `verify_release.py` |
| Android Gradle/JVM/lint | BLOCKED trong môi trường đóng gói: không tải được Gradle 8.9 do mạng bị giới hạn |
| Instrumentation trên AVD | NOT RUN trong môi trường đóng gói nếu không có AVD online |
| Galaxy A10s | NOT RUN nếu chưa cắm thiết bị người dùng |
| 16 KB ELF/ZIP alignment | Chỉ PASS sau `check_android_16kb.ps1` và APK Analyzer |
| Ảnh điện thoại độc lập | NOT COLLECTED nếu chưa thực hiện protocol |

Không đổi mục NOT RUN/NOT COLLECTED thành PASS nếu không có log hoặc dữ liệu thật.

Người dùng đã cung cấp ảnh `BUILD SUCCESSFUL` cho bản 0.5.0 trước đó. Vì 0.5.1 nâng dependency native,
cần chạy lại Gradle trên máy Windows có Internet; không dùng log 0.5.0 để tuyên bố build 0.5.1 PASS.
