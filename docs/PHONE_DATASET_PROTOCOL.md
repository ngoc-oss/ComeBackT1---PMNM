# Quy trình tập đánh giá độc lập bằng điện thoại

Mục tiêu là đo khả năng khái quát thực địa, không dùng ảnh này để huấn luyện hay chọn ngưỡng trước khi
khóa báo cáo test đầu tiên. Không thể thay bước này bằng ảnh lấy lại từ FruQ-DB hoặc frame cùng video.

## Thu thập

- Tối thiểu 30 mẫu vật lý mỗi lớp cho từng miền; mỗi mẫu chụp 3 điều kiện sáng và 2 góc bằng Galaxy A10s.
- Gán `specimen_id` duy nhất cho cùng một quả/miếng thịt. Mọi ảnh của một mẫu phải nằm cùng một split.
- Thêm tối thiểu 100 ảnh ngoài phạm vi: người, xe, bàn ghế, bao bì, ảnh màn hình và món ăn hỗn hợp.
- Nhãn độ tươi do ít nhất hai người gán độc lập theo tiêu chí ghi trước; bất đồng đưa vào danh sách rà soát.
- Không chứa khuôn mặt/dữ liệu riêng tư trong bản công bố; ghi sự đồng ý và giấy phép cho từng ảnh.

## Cấu trúc

Đặt ảnh ngoài Git theo `phone_eval/images/`, sao chép `data/phone_eval_manifest.example.csv` thành
`phone_eval/manifest.csv`. Tính SHA-256, kiểm tra ảnh trùng/gần trùng và đóng băng manifest trước khi chạy.

## Báo cáo

Báo accuracy, macro-F1, confusion matrix và riêng lỗi HƯ→TƯƠI theo miền. Với ảnh ngoài phạm vi báo tỷ lệ
chặn; với ảnh hợp lệ báo tỷ lệ chặn nhầm. Báo tỷ lệ bị từ chối do tối/sáng/mờ riêng, cùng p50/p95 inference
trên A10s. Không gộp số từ emulator vào số thiết bị thật.
