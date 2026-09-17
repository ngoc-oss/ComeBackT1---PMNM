# Tiêu chí đánh giá nghiên cứu và sản phẩm

Các con số dưới đây là **mục tiêu đề xuất**, không phải kết quả đã đạt hoặc yêu cầu chính thức của cuộc thi.
Chưa có dữ liệu thật/thiết bị thật nên chưa điền điểm hiệu năng. Không dùng độ chính xác train để chứng minh chất lượng.

## Ma trận nghiệm thu

| Hạng mục | Cách đo | Mục tiêu đề xuất | Minh chứng phải lưu |
|---|---|---|---|
| Chất lượng dữ liệu | Đếm nhãn/group, kiểm tra trùng, nguồn và quyền | Đủ 3 nhãn; không group trùng giữa split; nguồn rõ ràng | manifest, dataset_report, dataset card |
| Nhất quán nhãn | Hai người chấm cùng ảnh | Kappa ≥0,75, xử lý bất đồng | Bảng nhãn độc lập và biên bản |
| Phân loại | Test độc lập theo mẫu vật | Accuracy ≥85%, macro-F1 ≥0,85 | JSON và confusion matrix |
| Lỗi quan trọng | Recall HƯ và tỷ lệ HƯ bị đoán TƯƠI | Recall HƯ ≥90%; HƯ→TƯƠI ≤5% | Ma trận và ảnh lỗi |
| Từ chối khi thiếu tự tin | Coverage và accepted accuracy | Mục tiêu validation ≥50% / ≥90%; báo lại test | Ngưỡng, manifest hash, scores |
| Sau lượng tử hóa | Cùng test, FP32 so FP16/INT8 | Macro-F1 giảm ≤2 điểm phần trăm | 3 báo cáo, model hash |
| Kích thước | Số byte .tflite | INT8 ≤10 MB | File và SHA-256 |
| Tốc độ inference | Điện thoại tầm trung, CPU 4 threads | p95 ≤500 ms | CSV từng lần, thông tin máy |
| Phản hồi người dùng | Đo từ bấm phân tích tới kết quả, bao gồm xử lý theo mô tả | p95 ≤2 giây | Video/log, định nghĩa điểm bắt đầu/kết thúc |
| Offline | Chế độ máy bay, có model hợp lệ | Chụp/chọn và phân tích hoạt động | Video demo |
| Ổn định | 100 lần phân tích nhiều ảnh, ảnh lớn và hủy camera | Không crash/ANR | Biên bản và logcat |
| UI/UX | 10–15 người dùng, nhiệm vụ chụp→hiểu kết quả | ≥90% hoàn thành; SUS ≥75 | Phiếu khảo sát ẩn danh |
| Riêng tư | Kiểm manifest, thử hoạt động | Không cần Internet; xóa lịch sử được | Manifest, kiểm thử |

Macro-F1 là trung bình F1 của ba nhãn; báo precision, recall, F1 từng lớp và số mẫu.
Lỗi HƯ→TƯƠI = số mẫu thật HƯ bị dự đoán TƯƠI / tổng mẫu thật HƯ.
Coverage = số ảnh được trả nhãn / tổng ảnh; accepted accuracy = tỷ lệ đúng trong số được trả nhãn.
Không loại ảnh khó khỏi mẫu số accuracy chính. Nếu một lớp thiếu trong test thì không tuyên bố kết quả đại diện 3 lớp.

## Thiết kế thí nghiệm

1. Đóng băng test theo group trước train; chọn hyperparameters/epochs/ngưỡng chỉ trên train/validation.
2. Baseline: MobileNetV2 đóng băng backbone; tiếp theo fine-tune; so mô hình float và lượng tử hóa.
3. Cố định seed, input size, danh sách lớp, dữ liệu đại diện và cấu hình thiết bị. Ghi phiên bản TensorFlow/Keras.
4. So FP32/FP16/INT8 cùng tập ảnh; báo kết quả từng loại trái cây và ánh sáng.
5. Tập ngoài miền: địa điểm, camera và nền mới. Báo riêng, không gộp để che suy giảm.
6. Rà tối thiểu 30 lỗi hoặc toàn bộ nếu ít hơn; ghi lỗi do crop, nhãn, nền, độ chín, mờ hay ngoài phạm vi.
7. Nếu cần khoảng tin cậy: bootstrap theo **group**, không bootstrap ảnh độc lập khi nhiều ảnh cùng một mẫu.
   Pipeline hiện chưa tự tính bootstrap/kappa/SUS; đây là bước nghiên cứu bổ sung được ghi rõ.

## Quy trình benchmark điện thoại

Ghi model máy/chip/RAM, phiên bản Android, mức pin, trạng thái sạc, nhiệt độ nếu có,
model hash, variant, APK version, threads. Dùng tối thiểu một máy tầm trung thật; tốt hơn là ba cấu hình.
Khởi động nguội để đo model loading/cold-start riêng; app benchmark không bao gồm thời gian nạp model.

Với mỗi variant, mở app → chọn cùng ảnh → đo 10 warmup +100 lần → lưu CSV.
Lặp 5 ảnh đại diện, mỗi ảnh 3 phiên; nghỉ khi máy nóng, giữ cùng điều kiện.
CSV trong app đo `Interpreter.run`; không gồm resize/đọc ảnh/chụp/UI.
App hiện cũng hiện thời gian xử lý và thời gian tới callback UI sau bấm phân tích,
nhưng chưa đo thời điểm frame thực sự vẽ ra màn hình. Cần video hoặc công cụ profiling để xác nhận UX latency đầy đủ.

Ghi p50/p95, số mẫu, phương pháp percentile. App dùng nearest-rank.
Chạy cùng một ảnh 100 lần là microbenchmark, không chứng minh độ chính xác hay hiệu năng toàn bộ hành trình.
Với bộ test trên điện thoại, cần thêm kiểm thử batch/instrumentation hoặc ghi nhận thủ công theo case;
script `evaluate.py` đo test trên host, không giả là kết quả điện thoại.

## Kiểm thử chức năng thực tế

| ID | Thao tác | Kết quả mong đợi |
|---|---|---|
| F01 | Cài bản không có model | UI mở, thông báo thiếu model, khóa phân tích |
| F02 | Model/hash sai | Báo lỗi và không suy luận |
| F03 | Chọn ảnh hợp lệ, model thật | Hiện crop đúng, 3 scores và nhãn/ngưỡng đúng |
| F04 | Hủy camera/thư viện | Không crash, giữ trạng thái hợp lý |
| F05 | Ảnh EXIF quay/đối xứng | Hiển thị đúng hướng; kiểm ảnh đối chiếu |
| F06 | Ảnh hỏng / kích thước lớn | Thông báo hoặc nạp có downsample, không ANR |
| F07 | Bấm phân tích liên tục | Nút khóa khi bận; inference tuần tự |
| F08 | Xoay màn hình khi chụp/suy luận | Không crash; URI camera được lưu; ảnh/kết quả phiên phân tích có thể phải chọn lại |
| F09 | Điểm thấp | CHƯA ĐỦ CƠ SỞ, không đổi thành NGHI NGỜ |
| F10 | Lịch sử / xóa / khởi động lại | Lưu tối đa 50 kết quả, xóa sau xác nhận |
| F11 | Chế độ máy bay | Inference hoạt động với assets hợp lệ |
| F12 | Benchmark và chia sẻ CSV | 100 hàng dữ liệu + header, hash và thời gian đúng |
| F13 | Ảnh không phải thực phẩm | Ghi tỷ lệ nhận nhầm; bản này chưa có bộ reject ngoài miền |
| F14 | Cỡ chữ lớn / TalkBack | Nút vẫn truy cập được, thứ tự đọc hợp lý, người dùng hiểu giới hạn |

## Bảng báo cáo để điền

| Model | Accuracy | Macro-F1 | Recall HƯ | HƯ→TƯƠI | Coverage | MB | Phone p50/p95 ms |
|---|---|---|---|---|---|---|---|
| FP32 | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| FP16 | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| INT8 | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |


## Bổ sung quả — phiên bản 0.3.0

Xem [FRUITQ.md](FRUITQ.md) cho nguồn Zenodo/Springer, ba nhãn Fresh/Mild/Rotten, model thử nghiệm FreshCheck, lệnh huấn luyện và quy trình đánh giá. Model quả không phải checkpoint của tác giả bài báo. Đánh giá nội bộ theo khung hình có nguy cơ rò rỉ video; chưa thay thế kiểm thử điện thoại hoặc tập mẫu độc lập. Kết quả thịt giữ riêng, không gộp với quả.
