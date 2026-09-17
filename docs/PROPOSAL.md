# Đề cương triển khai FreshCheck

## 1. Tên đề tài

Nghiên cứu và ứng dụng AI trong nhận diện và đánh giá chất lượng thực phẩm bằng hình ảnh trên thiết bị di động.
Tên sản phẩm: FreshCheck. Phạm vi hiện tại: thịt đỏ (checkpoint Phteven) và nhóm quả FruQ-DB (model thử nghiệm của FreshCheck); đánh giá riêng từng miền.

## 2. Bài toán và giá trị

Người dùng chụp một thực phẩm, hệ thống phân tích ngay trên Android và trả TƯƠI / NGHI NGỜ / HƯ
hoặc từ chối khi chưa đủ cơ sở. Mục tiêu là hỗ trợ sàng lọc ngoại quan, giảm thao tác thủ công,
hoạt động khi thiếu Internet và giữ ảnh trên thiết bị. Kết quả không xác nhận an toàn tiêu thụ.

## 3. Câu hỏi nghiên cứu

- CNN nhẹ có phân biệt ba mức ngoại quan trên dữ liệu mới từ mẫu vật chưa thấy không?
- Fine-tuning có cải thiện macro-F1 so với head-only trên cùng backbone và dữ liệu không?
- INT8 giảm dung lượng/thời gian bao nhiêu và đánh đổi recall lớp HƯ ra sao?
- Ngưỡng từ chối trên validation thay đổi độ bao phủ và độ chính xác thế nào?
- Ánh sáng/nền/camera khác có làm giảm hiệu năng? Người dùng có hiểu nhãn và giới hạn không?

## 4. Phương pháp

Thu thập dữ liệu có nguồn và quyền sử dụng → gán nhãn theo tiêu chí ngoại quan của loại →
chia group train/validation/test → CNN pretrained ImageNet → fine-tune → xuất TFLite →
đánh giá cùng test → tích hợp app → đo thiết bị → phân tích lỗi.
Ưu tiên nghiên cứu được tái lập: cố định split, seed, model hash, phiên bản và cấu hình.

Pipeline hiện triển khai MobileNetV2 (alpha 0.75), input RGB 224×224, class weighting,
early stopping, fine-tuning, FP32/FP16/INT8. Không sử dụng LLM/API chatbot để đoán chất lượng.
TensorFlow Lite đáp ứng nhánh “TFLite hoặc ONNX Mobile” trong yêu cầu; không cần triển khai cả hai để có MVP.

## 5. Chức năng

Camera hệ thống chụp ảnh full-size vào URI tạm; chọn ảnh; sửa hướng EXIF;
hiện khung crop đúng input; chọn loại thực phẩm được hỗ trợ; phân tích trên worker thread;
hiện nhãn và scores; lịch sử tối đa 50 kết quả; xóa lịch sử; benchmark và chia sẻ CSV.
App không yêu cầu tài khoản/Internet và không gửi ảnh ra server.
Thiếu model hoặc hash sai sẽ khóa suy luận; không có chế độ kết quả ngẫu nhiên.

## 6. Thiết kế UI/UX

Giao diện tiếng Việt, nền sáng, xanh cho fresh, vàng cho suspicious/uncertain, đỏ cho spoiled;
luôn kèm chữ để không phụ thuộc nhận biết màu. Tác vụ theo thứ tự chọn thực phẩm → ảnh → kết quả.
Ảnh input hiển thị vuông; nút lớn, progress khi xử lý, thông báo lỗi có hướng xử lý.
Người dùng thấy trạng thái model nghiên cứu và giới hạn; scores ghi “điểm mô hình”.
Chưa kiểm thử TalkBack/cỡ chữ lớn trên máy thật; có case nghiệm thu cụ thể.

## 7. Tiến độ đề xuất tám tuần

| Tuần | Công việc | Đầu ra |
|---|---|---|
| 1 | Chốt phạm vi, tiêu chí nhãn, repo/issue, pilot | Đề cương, hướng dẫn nhãn, dữ liệu thử |
| 2–3 | Thu thập và gán nhãn, rà nguồn/trùng | Dataset card, manifest đóng băng |
| 4 | Baseline/fine-tune, phân tích lỗi validation | Model/Keras, log, cấu hình |
| 5 | Lượng tử hóa, chọn ngưỡng, đánh giá test | TFLite variants, báo cáo metric |
| 6 | Tích hợp model, chạy Android, sửa lỗi | APK thử nghiệm |
| 7 | Benchmark thiết bị, khảo sát UX, test ngoài miền | CSV, video, bảng kết quả |
| 8 | Hoàn thiện docs/license, build sạch, release | Hồ sơ dự thi có minh chứng |

## 8. Ứng dụng thực tế và mở rộng

Thử nghiệm sàng lọc trái cây trong hộ gia đình, cửa hàng nhỏ, hỗ trợ đào tạo quan sát chất lượng.
Trước áp dụng thực tế cần kiểm nghiệm với chuyên gia và dữ liệu đại diện, theo dõi lỗi và giới hạn trách nhiệm.
Không quảng bá như thiết bị kiểm nghiệm vi sinh hoặc thay thế quy trình kiểm soát an toàn thực phẩm.
Hướng tiếp: phát hiện loại/vùng thực phẩm, ảnh ngoài miền, nhiều vật thể, giải thích vùng chú ý,
tích hợp nhiệt độ/thời gian bảo quản và kiểm nghiệm ngoài ảnh, đánh giá đa địa điểm.
iOS có thể tái dùng model TFLite và hợp đồng input/output; UI/camera/benchmark phải triển khai và kiểm thử riêng.

## 9. Sản phẩm bàn giao và phần còn thiếu

Gói hiện có source Android/ML/tests/docs/CI. Dữ liệu thật, model chuyên thực phẩm,
hiệu năng điện thoại, khảo sát UX và release công khai phải hoàn thành để thành sản phẩm dự thi nghiệm thu.
Không đưa số liệu tổng hợp kiểm thử phần mềm vào bảng kết quả nghiên cứu thực phẩm.


## Bổ sung quả — phiên bản 0.3.0

Xem [FRUITQ.md](FRUITQ.md) cho nguồn Zenodo/Springer, ba nhãn Fresh/Mild/Rotten, model thử nghiệm FreshCheck, lệnh huấn luyện và quy trình đánh giá. Model quả không phải checkpoint của tác giả bài báo. Đánh giá nội bộ theo khung hình có nguy cơ rò rỉ video; chưa thay thế kiểm thử điện thoại hoặc tập mẫu độc lập. Kết quả thịt giữ riêng, không gộp với quả.
