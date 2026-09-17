# Kiến trúc và hợp đồng mô hình

## Thành phần

| Thành phần | Trách nhiệm |
|---|---|
| MainActivity | UI, camera/gallery Activity Result, điều phối worker, trạng thái nút |
| Images | Decode có downsample, EXIF orientation, center crop, bilinear resize |
| FoodClassifier | Xác minh config/hash, tensor encoding, TFLite CPU inference, benchmark |
| Decision | Ánh xạ nhãn và quy tắc từ chối theo điểm |
| HistoryStore | SharedPreferences, tối đa 50 kết quả, xóa theo yêu cầu |
| prepare_data | Kiểm manifest, provenance, exact duplicate, split theo group |
| train/export | Transfer learning, fine-tune, xuất 3 variant |
| evaluate/calibrate | Metric toàn test, lựa chọn ngưỡng validation có model hash |

Không có backend. Không có quyền INTERNET trong manifest.
Camera dùng ứng dụng camera hệ thống với FileProvider URI; không truy cập camera trực tiếp nên không khai báo CAMERA.
Chọn ảnh qua hệ thống không cần quyền đọc toàn bộ bộ nhớ. Ảnh chụp tạm là `cache/captures/capture.jpg`, ghi đè lần sau.
Lịch sử lưu scores/nhãn/thời gian/version, không lưu ảnh. File chia sẻ chỉ trong thư mục exports của cache.
Android backup bị tắt để tránh sao lưu lịch sử ngoài ý định của app.

## Tensor contract v1

- Input [1,224,224,3], NHWC, RGB. Crop hình vuông chính giữa rồi resize bilinear.
- Giá trị logic [0,255]; layer Rescaling trong mô hình chuyển sang [-1,1]. Android không chia 255 thêm lần nữa.
- Output [1,3], softmax, đúng thứ tự fresh/suspicious/spoiled; không sắp xếp theo tên folder tự động.
- FLOAT32 giữ nguyên input. UINT8/INT8: q = round(real/scale + zeroPoint), clamp theo kiểu số.
- Dequantization: real = (q-zeroPoint)*scale; scale/zeroPoint đọc từ tensor thực.
- Model config gồm version, SHA-256, input_size/range/crop, nhãn, food_types và threshold.
- Hash chỉ kiểm khớp model/config, không chứng minh nguồn đáng tin hoặc độ chính xác.
- Threshold mặc định 0,70 chưa hiệu chỉnh; calibrate dùng validation của đúng model hash.

Pillow và Android có thể khác nhẹ thuật toán nội suy/downsample. Trước release phải so cùng 20 ảnh
theo đầu ra Python và Android (nhất là ảnh EXIF và ảnh lớn), xem chênh scores và nhãn.
Chưa có đối chiếu tensor tự động xuyên nền tảng trong bản này.

## Đồng thời và vòng đời

Interpreter không dùng đồng thời: toàn bộ load/classify/benchmark/close qua một single-thread executor.
UI cập nhật main thread; nút bị khóa khi bận. onDestroy xếp close sau tác vụ đang chạy.
URI chụp được giữ trong saved state; ảnh đã chọn và kết quả hiển thị chưa phục hồi sau recreation,
người dùng có thể phải chọn lại. Lịch sử kết quả đã hoàn thành vẫn tồn tại.
Để nâng cấp UX khi xoay màn hình, chuyển state/worker sang ViewModel và SavedStateHandle.

## iOS / ONNX

Đã chọn nhánh TensorFlow Lite cho phiên bản Android đầu tiên.
iOS có thể dùng TensorFlow Lite Swift, tuân thủ cùng tensor contract và lập kiểm thử golden input.
ONNX cần pipeline conversion được kiểm chứng op set, input layout và runtime tương ứng;
không đổi đuôi tệp .tflite thành .onnx. Hai phần mở rộng này chưa triển khai.


## Bổ sung quả — phiên bản 0.3.0

Xem [FRUITQ.md](FRUITQ.md) cho nguồn Zenodo/Springer, ba nhãn Fresh/Mild/Rotten, model thử nghiệm FreshCheck, lệnh huấn luyện và quy trình đánh giá. Model quả không phải checkpoint của tác giả bài báo. Đánh giá nội bộ theo khung hình có nguy cơ rò rỉ video; chưa thay thế kiểm thử điện thoại hoặc tập mẫu độc lập. Kết quả thịt giữ riêng, không gộp với quả.
