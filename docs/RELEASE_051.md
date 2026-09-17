# FreshCheck 0.5.1 — điều kiện nghiệm thu

## Chức năng có trong mã nguồn

- Hai model ONNX cho thịt đỏ và nhóm quả FruQ-DB, cùng hợp đồng ba nhãn TƯƠI/NGHI NGỜ/HƯ.
- Suy luận offline, chọn camera/thư viện, xác nhận ảnh và nút chụp lại.
- Kiểm tra quá tối, quá sáng, tương phản thấp, mờ và bộ lọc nhãn ngoài phạm vi.
- Hiển thị model/version/hash/thời gian; lịch sử 50 lượt; xuất lịch sử và benchmark CSV.
- APK tách armeabi-v7a, arm64-v8a, x86_64 và universal.
- Unit test Python/JVM, instrumentation test, lint, CI, release workflow và kiểm toán source release.

## Lệnh kiểm tra trên Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_android_051.ps1
```

Lệnh chỉ thành công đầy đủ khi có JDK/SDK đúng, thiết bị hoặc AVD online và kiểm tra 16 KB đạt.
Dùng `-SkipDeviceTests` chỉ khi ghi rõ instrumentation **NOT RUN**, không được đổi thành PASS.

## Điều kiện tạo release chính thức

1. `python -m unittest discover -s tests -v` PASS.
2. `python scripts/verify_release.py` PASS.
3. Gradle test, lint và assemble PASS.
4. `connectedDebugAndroidTest` PASS trên AVD x86_64.
5. APK ARM cài, mở, camera/thư viện/inference/CSV PASS trên Galaxy A10s.
6. `check_android_16kb.ps1` và cột Alignment trong APK Analyzer PASS.
7. Có ảnh điện thoại độc lập và báo cáo accuracy/F1/confusion matrix không rò rỉ frame.
8. Repository public có commit/Issues thật; tag `v0.5.1`; GitHub Release chứa tar.gz, APK và SHA256SUMS.

## Giới hạn khoa học

Checkpoint thịt có nguồn tác giả Phteven. Model quả do FreshCheck huấn luyện trên FruQ-DB công bố,
không phải checkpoint do tác giả bài FruitQ phát hành. Bộ lọc ngoài phạm vi và chất lượng ảnh là hàng rào
giảm lỗi, không chứng minh ảnh thuộc phân phối huấn luyện. Ứng dụng không thay thế kiểm nghiệm an toàn thực phẩm.
