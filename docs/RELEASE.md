# Build và phát hành có minh chứng

## Tạo repository và dùng thật

Sau khi giải nén, tạo repository mới trên GitHub/GitLab bằng tài khoản của nhóm, chọn public khi sẵn sàng chia sẻ.
Không có repository công khai được tạo tự động trong lần bàn giao này.

```bash
git init
git add .
git commit -m "Add FreshCheck Android and ML implementation"
git branch -M main
git remote add origin YOUR_REAL_REPOSITORY_URL
git push -u origin main
```

Thay URL bằng repository thật. Kiểm tra `.gitignore` trước push, không đưa raw data/private paths/khóa ký.
Tạo Issues cho thu thập dữ liệu, lỗi thực tế, kiểm thử thiết bị. CI chạy khi push/PR; cập nhật README bằng URL thực.
Một commit ban đầu không thay thế quá trình phát triển; lưu lịch sử công việc tiếp theo thật.

## Build sạch

Clone vào thư mục mới → tạo venv → cài requirements → unit tests → prepare/train/export/evaluate hoặc
tải model đã được nhóm cấp quyền phát hành → kiểm SHA-256 → install_model → Gradle assembleDebug/test.
Hướng dẫn chi tiết tại README. Android Studio tạo local.properties theo máy; không commit file này.
App cài lên điện thoại vẫn hoạt động ngoài source vì model nằm trong assets.

Gradle wrapper 8.9 là công cụ nguồn mở chuẩn. Không cần công cụ build tự viết.
Script packaging chỉ đóng gói file, không thay compiler/Gradle.

## Trước tag

1. Hoàn thành test trên model thực phẩm và máy thật; lưu reports và video. Đọc docs/VALIDATION.md để không nhầm smoke test với hiệu năng.
2. Xác nhận license dataset/model/dependencies, giữ notice cần thiết.
3. Với APK release: dùng Android Studio Generate Signed Bundle / APK, tạo và giữ keystore ngoài repo.
   Bản debug dùng để thử; không phải bản production ký chính thức.
4. Cập nhật versionCode/versionName, CHANGELOG và model card cùng model hash.
5. Đóng gói source dạng tar.gz theo tiêu chí ảnh; model/APK có checksum và thông tin nguồn riêng.

```bash
python scripts/package_release.py --version 0.1.0
git add .
git commit -m "Prepare verified 0.1.0 release"
git tag -a v0.1.0 -m "FreshCheck 0.1.0"
git push origin main --tags
```

Chỉ chạy commit khi có thay đổi thật. Tạo Release trên web từ tag v0.1.0,
đính kèm tar.gz, SHA256SUMS, APK/model được quyền chia sẻ và báo cáo kết quả.
Release phải tạo trước hạn nộp theo ảnh; không giả mạo ngày.
`package_release.py` **không đăng Internet và không tự tạo release**, chỉ tạo file local.

## Model card khi phát hành

Ghi: nhãn và định nghĩa, loại thực phẩm, train data license/version/group counts,
validation threshold và mục tiêu, test accuracy/macro-F1/recall HƯ, lỗi HƯ→TƯƠI,
điện thoại benchmark, model hash/size/variant, giới hạn ngoài miền,
người phụ trách và ngày đánh giá. Giữ status research nếu chưa nghiệm thu thực tế.
