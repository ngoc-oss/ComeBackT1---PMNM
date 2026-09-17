# Bổ sung quả vào FreshCheck 0.3.0

## Trạng thái đáp ứng yêu cầu

- Đã tìm nguồn dữ liệu thật, ba nhãn có sẵn, có DOI và bài báo tạp chí.
- Bộ quả: FruQ-DB v1, tác giả Abayomi-Alli Olusola và Robertas Damaševičius, Zenodo 19/10/2022, DOI **10.5281/zenodo.7224690**.
- Công bố: Olusola O. Abayomi-Alli, Robertas Damaševičius, Sanjay Misra, Adebayo Abayomi-Alli. **FruitQ: a new dataset of multiple fruit images for freshness evaluation**. *Multimedia Tools and Applications* 83, 11433–11460 (2024), xuất bản trực tuyến 28/06/2023. DOI **10.1007/s11042-023-16058-6**.
- **Chưa xác minh được checkpoint do tác giả bài báo phát hành. Model quả đi kèm là model thử nghiệm FreshCheck huấn luyện, KHÔNG phải checkpoint chính thức hoặc kết quả tái lập nguyên bản bài báo.**
- Model thịt Phteven 0.2.0 và số đo cũ được giữ riêng. Không gộp hai bộ vào một accuracy hoặc dùng model thịt để dự đoán quả.

## Nguồn truy xuất

1. [Dữ liệu gốc Zenodo](https://zenodo.org/records/7224690).
2. [Bài báo trên Springer Nature](https://link.springer.com/article/10.1007/s11042-023-16058-6).
3. [Tải FruQ-DB.zip chính thức](https://zenodo.org/records/7224690/files/FruQ-DB.zip?download=1).
4. [Metadata gốc, gồm giấy phép](https://zenodo.org/api/records/7224690).

Zenodo công bố 5.647 ảnh: Fresh 2.182, Mild 1.364, Rotten 2.101. Đây là **số theo mô tả nguồn**; số đếm thực tế, trùng ảnh và split được ghi trong `reports/fruitq/audit.json` sau khi giải nén. File gốc 241.067.015 bytes, MD5 công bố `1a942c2d49dc302bacef155561e1f9a8`. Mã chuẩn bị dữ liệu từ chối archive sai MD5.

Nguồn mô tả 11 nhóm: chuối, dưa chuột, nho, hồng (kaki), đu đủ, đào, lê, ớt, dâu tây, cà chua, dưa hấu. Đây là danh sách của bộ dữ liệu, **không phải bằng chứng model đã được đánh giá riêng đầy đủ trên từng loại**. Bản FruQ-DB phân thư mục theo chất lượng; chưa xác minh ánh xạ tên file tới từng loại/video. Vì vậy ứng dụng dùng lựa chọn “Nhóm quả FruQ-DB”, không giả vờ tự nhận diện loại quả.

## Ba nhãn có sẵn

| Nhãn nguồn | Nhãn model | Giao diện |
|---|---|---|
| Fresh | fresh | TƯƠI |
| Mild | suspicious | NGHI NGỜ · mức Mild của nguồn |
| Rotten | spoiled | HƯ |

Mild là mức trung gian trong phân loại nguồn. Việc hiển thị “NGHI NGỜ” là ánh xạ của dự án; không có ngưỡng kiểm nghiệm vi sinh được xác minh để khẳng định hai khái niệm tương đương về an toàn thực phẩm. Không tự tạo nhãn từ mức confidence. Điểm cao nhất dưới 0,70 trả “CHƯA ĐỦ CƠ SỞ”, không biến thành lớp Mild. Không đổi nhãn chín xanh/chín/quá chín thành ba nhãn tươi/hư.

## Dữ liệu thật nhưng phạm vi thực nghiệm hạn chế

Ảnh là khung hình trích từ video time-lapse thật theo công bố của tác giả, đã tiền xử lý. Chúng không phải bộ ảnh chụp thực địa độc lập bằng nhiều điện thoại. Metadata nguồn tuyên bố CC BY 4.0 và liệt kê video YouTube; dự án giữ attribution, nguồn và giấy phép, không tuyên bố đã xác minh độc lập quyền của mọi video gốc. Nội dung ảnh không được tạo bằng AI trong dự án.

Chuẩn bị dữ liệu giữ nhãn gốc, kiểm tra ảnh đọc được, tính hash pixel sau giải mã, loại bản trùng hoàn toàn và chia 70/15/15 theo lớp với seed 2026. Không đoán mã video hoặc mã mẫu từ tên file. **Các khung hình gần nhau vẫn có thể qua nhiều tập**. Do đó phép đo test hiện tại chỉ là kiểm tra nội bộ; không dùng để khẳng định khả năng tổng quát hóa trên quả mới hoặc tuyên bố “đạt độ chính xác bài báo”.

Để nghiệm thu thực tế: bổ sung ảnh điện thoại của mẫu quả mới; có ít nhất hai người gán nhãn theo rubric; ghi specimen_id/video_id/location; tách toàn bộ mẫu/video khỏi train; báo confusion matrix, macro-F1, HƯ→TƯƠI, coverage và accuracy trên ảnh được chấp nhận. Không chọn ngưỡng bằng test. Đo riêng từng loại quả khi có nhãn loại đáng tin cậy.

## Model thử nghiệm của dự án

MobileNetV3 Small pretrained ImageNet của torchvision, giữ backbone cố định và huấn luyện đầu Linear 576→3 trên FruQ-DB. Đây là transfer learning thật, không dùng trọng số ngẫu nhiên để giả model đã huấn luyện. Chọn epoch bằng macro-F1 validation, test chỉ dùng sau lựa chọn. Script lưu checkpoint `.pth`, training log, manifest, ONNX FP32, ONNX INT8 QDQ, metrics và predictions. Không lấy số trong bài báo làm số đo dự án.

Tiền xử lý: EXIF transpose → RGB → resize toàn ảnh 224×224 bilinear → float NHWC RGB 0..255. ONNX chứa đổi NCHW, chia 255 và chuẩn hóa ImageNet mean (0,485;0,456;0,406), std (0,229;0,224;0,225), softmax. Ba đầu ra đúng thứ tự fresh/suspicious/spoiled. Không dùng crop của model thịt cho model quả.

APK sử dụng **FP32**, được chọn trước khi xem test; INT8 dùng để so sánh, calibration chỉ lấy 120 ảnh train. Bản FP32 nhỏ nhờ kiến trúc MobileNet, không phải nhờ đổi tên file. Có kiểm tra chênh lệch xác suất PyTorch↔ONNX trên 30 ảnh thật. So sánh Android↔Python trên cùng ảnh và benchmark điện thoại vẫn cần thiết vì thư viện resize có thể khác nhau.

## Chạy từ mã nguồn

Trong thư mục gốc dự án:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install onnx==1.17.0 onnxruntime==1.20.1 numpy Pillow
python ml/fruitq.py --archive /path/FruQ-DB.zip --data data/raw/fruitq --output artifacts/fruitq --epochs 80
python scripts/install_fruit_model.py --model-dir artifacts/fruitq
```

Với gói model 0.3.0 đã huấn luyện, bỏ bước huấn luyện: `python scripts/install_bundle.py --bundle /path/to/FreshCheck-0.3.0-models` cài cả thịt và quả. Hoặc cài riêng quả bằng `python scripts/install_fruit_model.py --model-dir /path/to/FreshCheck-0.3.0-models/fruit`.

```bash
python ml/predict_fruit.py --model-dir /path/to/FreshCheck-0.3.0-models/fruit --image /path/to/fruit.png
```

Giữ model thịt đã cài, sau đó build Android theo README. Cài cả hai gói model nếu build từ source release mới. Trong ứng dụng chọn **Thịt đỏ · Phteven** hoặc **Quả · FruQ-DB thử nghiệm** trước khi phân tích. Chuyển miền sẽ đóng session cũ, nạp model đúng và xóa điểm hiển thị cũ. Model quả không nhận diện thực phẩm bất kỳ hoặc nhận biết loại quả tự động.

## Checklist bổ sung cho báo cáo/cuộc thi

| Hạng mục | Bằng chứng | Giới hạn |
|---|---|---|
| Nguồn chính thống | DOI Zenodo + bài tạp chí Springer | Không đồng nghĩa chứng nhận an toàn |
| Nhãn có sẵn | Fresh / Mild / Rotten trong dữ liệu | Mild được ánh xạ rõ ràng |
| Model huấn luyện | Checkpoint của FreshCheck + log + script | Chưa có checkpoint tác giả bài báo |
| Tái lập | MD5 archive, SHA256 model, seed, manifest | Random frame split có nguy cơ rò rỉ video |
| Chạy offline | ONNX FP32 trong APK | Cần thử trên điện thoại thật |
| Đánh giá | Metrics JSON, prediction CSV, benchmark trong app | Không gộp số thịt/quả hoặc lấy số bài báo |
| Mã nguồn mở | MIT cho mã dự án; notice CC BY/BSD riêng | Giấy phép dữ liệu/trọng số không tự chuyển thành MIT |
| Release | Source tar.gz, model và data riêng | Release Internet/GitHub vẫn phải được phát hành thực tế |

## Kết quả chạy thực tế trong phiên làm việc 11/09/2026

Đã tải và kiểm MD5 thành công: 5.647 ảnh gốc. Loại 637 bản trùng pixel hoàn toàn (đều thuộc Fresh), còn 5.010 ảnh: Fresh 1.545, Mild 1.364, Rotten 2.101. Train 3.505, validation 752, test 753. Không có ảnh hỏng hoặc xung đột nhãn ở nhóm ảnh trùng được phát hiện.

| Model | Accuracy nội bộ | Macro-F1 | Dung lượng | CPU máy chạy p50 / p95 | Đưa vào APK |
|---|---:|---:|---:|---:|---|
| FP32 | 99.60% | 0.9956 | 3.73 MB | 3.74 / 4.53 ms | Có |
| INT8 QDQ | 35.99% | 0.2647 | 1.25 MB | 3.43 / 4.28 ms | Không; độ chính xác suy giảm nghiêm trọng |

INT8 dự đoán HƯ→TƯƠI 226/316 ảnh test; đây là kết quả lượng tử hóa thất bại, **không dùng thực tế**. Giữ log/metrics để minh bạch, không chỉ báo model nhỏ hơn.

FP32: HƯ→TƯƠI 0/316 trong tập nội bộ, coverage ngưỡng 0,70 là 98,67%; không suy ra tỷ lệ này trên ảnh đời thực. Độ lệch xác suất PyTorch/ONNX lớn nhất trên 30 ảnh là 0,000004232.

**Các số tốc độ là CPU máy chạy thí nghiệm, không phải điện thoại tầm trung. Accuracy cao trên frame split có thể bị nâng bởi tương đồng video/nền; chưa có test theo mẫu quả/video độc lập. Chưa nghiệm thu thực địa.**


## Kiểm tra build Android 0.3.0

Build `assembleDebug` và `testDebugUnitTest` thành công; 3 kiểm thử JVM đạt. Đã mở APK để kiểm tra SHA256 cả hai model và các notice giấy phép; không gói model quả INT8 thất bại. APK khoảng 118,93 MB. **Chưa chạy camera, chuyển model và suy luận trên điện thoại/emulator trong phiên này.** Cần kiểm thử thiết bị thật trước khi nộp kết quả tốc độ/độ ổn định.
