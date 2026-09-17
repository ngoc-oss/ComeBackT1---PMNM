# Đối chiếu tiêu chí trong hai ảnh người dùng cung cấp

Checklist thao tác cuối cùng cho bản hiện tại: [POF_CHECKLIST.md](POF_CHECKLIST.md).

Hai ảnh thể hiện phần PoF với tổng tối đa **50 điểm**. Không có đầy đủ trang 1/4, 4/4
và phần cuối trang 3; chưa thể xác nhận toàn bộ tiêu chí cuộc thi hay tự chấm tổng điểm.
Các mục chính nhìn thấy có điểm 5 + 10 + 5 + 10 + 10 + 10 = 50.
Giữ nguyên cách hiểu từ ảnh; ban tổ chức quyết định chấm và cách cộng/trừ thực tế.

| Mục nhìn thấy | Tối đa | Đã chuẩn bị trong project | Minh chứng vẫn cần |
|---|---:|---|---|
| Quản lý mã nguồn trên Internet | 5 | .gitignore, hướng dẫn Git, CI, mẫu Issues/PR | Repository công khai có web viewer và commit phát triển thật |
| Giấy phép OSI-approved | 10 | LICENSE MIT đầy đủ, SPDX trong mã tự viết, thông báo mục đích, THIRD_PARTY_NOTICES | Kiểm quyền dữ liệu/trọng số và giấy phép transitive trước release |
| Ít nhất một release | 5 | Version 0.1.0, CHANGELOG, script tạo tar.gz, quy trình tag/release | Tạo release thật trước hạn; ảnh/trang release công khai |
| Cài đặt, biên dịch từ mã nguồn | 10 | README lệnh train/build, Gradle, requirements; không đường dẫn cố định trong app | Build sạch trên máy khác; cài APK ở ngoài thư mục mã nguồn |
| Thư viện và gói đính kèm | 10 | Dependencies khai báo qua Gradle/pip, danh mục giấy phép | Danh sách dependency thực tế, thông báo giấy phép trong APK/release |
| Tài liệu và giao tiếp | 10 | README, CONTRIBUTING, CHANGELOG, tài liệu nghiên cứu, issue/PR templates | Issues được dùng thật, lịch sử sửa lỗi, kênh trao đổi thật |

## Các nguy cơ trừ điểm thể hiện trong ảnh

- Repository không có web viewer hoặc không truy cập mở: ảnh ghi -3 cho từng trường hợp;
  có hệ thống nhưng thực tế không dùng: -5. Không tạo commit giả hoặc lùi ngày để làm minh chứng.
- Thiếu giấy phép từng tệp mã; giấy phép không tương thích; thiếu thông báo mục đích;
  thiếu toàn văn giấy phép: ảnh ghi -5 cho mỗi mô tả. Header mã tự viết dẫn tới LICENSE.
- Không có phát hành: -5; không phát hành theo version: -3.
  Ảnh ghi định dạng không mở với ví dụ zip, rar, arj: -3.
  Vì vậy ưu tiên **tar.gz** cho source phát hành theo chính ảnh, dù ZIP thường được sử dụng rộng rãi.
- Thiếu hướng dẫn build: -5. Cấu hình bằng sửa header; không cấu hình được trước build;
  công cụ build nguồn đóng/tự tạo; chương trình không chạy ngoài source: ảnh ghi -5 mỗi mô tả.
  Dự án dùng Gradle, Kotlin, Android SDK tiêu chuẩn; Android Studio là IDE tùy chọn.
- Phần bundling có các mô tả về không tận dụng thư viện có sẵn, phát hành kèm dependencies,
  hoặc sửa mã nguồn dependency. Project không vendor/sửa mã dependencies; Gradle tự đóng gói runtime cần cho Android.
  Cần hỏi ban tổ chức cách áp dụng tiêu chí bundling cho APK vốn phải chứa runtime.
- Phần tài liệu thấy rõ bug tracker và changelog, cùng dòng README bị cắt phía dưới.
  Không tự suy diễn những dòng không nhìn thấy.

## Mục đích giấy phép

MIT cho phép sử dụng, nghiên cứu, sửa đổi và phân phối mã với điều kiện giữ thông báo bản quyền/giấy phép.
Toàn văn trong LICENSE; [OSI xác nhận MIT](https://opensource.org/license/mit).
Giấy phép mã không thay thế quyền của ảnh, dataset, trọng số ImageNet hoặc thư viện.

## Hồ sơ nên có trước hạn

Link repository công khai; tag và release tar.gz; APK đã kiểm thử có model thật và quyền phân phối;
README build sạch; video demo offline; dataset/model card; bảng kết quả thực đo;
ảnh lịch sử commits/issues; thông báo dependency; đề cương và phân công đóng góp.
Không có đủ các minh chứng này thì không tuyên bố đạt 50/50.


## Bổ sung quả — phiên bản 0.3.0

Xem [FRUITQ.md](FRUITQ.md) cho nguồn Zenodo/Springer, ba nhãn Fresh/Mild/Rotten, model thử nghiệm FreshCheck, lệnh huấn luyện và quy trình đánh giá. Model quả không phải checkpoint của tác giả bài báo. Đánh giá nội bộ theo khung hình có nguy cơ rò rỉ video; chưa thay thế kiểm thử điện thoại hoặc tập mẫu độc lập. Kết quả thịt giữ riêng, không gộp với quả.
