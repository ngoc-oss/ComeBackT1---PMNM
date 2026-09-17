# Bản 0.2.0 — dữ liệu thật và checkpoint công khai

## Nguồn có thể truy vết

**Meat Freshness Prediction**, Sagiraju, Casanova, Chun, Lohia, Yoshiyasu, công bố arXiv ngày 01/05/2023.
[Bản công bố](https://arxiv.org/abs/2305.00986) dẫn trực tiếp đến
[repository của nhóm tác giả](https://github.com/TheLohia/Phteven).
Đây là bản preprint; chưa xác minh một phiên bản tạp chí phản biện tương ứng. Không gọi là chứng nhận của cơ quan an toàn thực phẩm.

Checkpoint thực lấy từ `flask_demo/models/resnet50_fe.pth` tại commit
`b31e61f43f8c608f119d379daa5b76768b50c5b3`.
[Tệp checkpoint của tác giả](https://github.com/TheLohia/Phteven/blob/b31e61f43f8c608f119d379daa5b76768b50c5b3/flask_demo/models/resnet50_fe.pth).
Đã khớp Git blob SHA-1 với cây commit và ghi SHA-256. Đây là ResNet-50 đã học bài toán thịt,
không phải chỉ có backbone ImageNet, không phải trọng số tạo ngẫu nhiên hoặc do FreshCheck huấn luyện lại.
Mã nhóm tác giả dùng MIT; giữ nguyên thông báo trong LICENSES/Phteven-MIT.txt và trong assets APK.

## Dữ liệu thật

[Meat Freshness Image Dataset — Vinayak Shanawad](https://www.kaggle.com/datasets/vinayakshanawad/meat-freshness-image-dataset).
Metadata từ API Kaggle khai báo **CC0: Public Domain**; lưu bản metadata trong gói dữ liệu.
Đây là khai báo của người đăng, không phải xác nhận kiểm nghiệm nhãn hoặc đảm bảo mọi quyền nguồn ảnh đã được thẩm định độc lập.
Không sửa nhãn để đủ lớp. File `_classes.csv` của nguồn chứa trực tiếp Fresh, Half-Fresh, Spoiled.

| Nhãn nguồn | Nhãn nội bộ FreshCheck | Giao diện | Train nguồn | Valid nguồn | Tổng |
|---|---|---|---:|---:|---:|
| Fresh | fresh | TƯƠI | 675 | 178 | 853 |
| Half-Fresh | suspicious | NGHI NGỜ — Half-Fresh | 630 | 159 | 789 |
| Spoiled | spoiled | HƯ | 510 | 114 | 624 |
| Tổng | | | 1.815 | 451 | 2.266 |

Ảnh RGB 416×416, nguồn ghi đã auto-orient và resize, không augmentation.
Các số đếm được kiểm từ file tải thật; có chênh nhỏ với số ghi trong bài báo, không sửa số để trùng bài.
Đã decode toàn bộ ảnh và không phát hiện bản trùng pixel chính xác. Chưa loại trừ ảnh gần trùng.
Nguồn không cung cấp mã từng miếng thịt hoặc lô chụp, vì vậy không thể chứng minh split độc lập theo mẫu vật.

**Phạm vi: ảnh thịt đỏ.** Không tuyên bố model này phân loại được cá, rau, trái cây, món ăn nấu chín hoặc mọi thực phẩm.
Half-Fresh được giữ như một mức ngoại quan của nguồn và ghi rõ trong app. Không diễn giải là ngưỡng vi sinh được công nhận.

## Chuyển đổi và kiểm chứng

Model gốc xuất logits theo thứ tự **Spoiled / Half-Fresh / Fresh**. Mã tích hợp đổi thứ tự thành
Fresh / Half-Fresh / Spoiled trước softmax, bên trong ONNX, để khớp project.
Tiền xử lý theo code tác giả: resize cạnh ngắn 256 → center crop 224 → RGB → chia 255 →
normalize mean [0.485,0.456,0.406], std [0.229,0.224,0.225]. Normalize nằm trong ONNX, app đưa RGB [0,255].
Không tái huấn luyện checkpoint. Bản INT8 là bản chuyển đổi của FreshCheck, không phải tệp INT8 được tác giả công bố nguyên gốc.

Kiểm 30 ảnh thật: PyTorch và ONNX FP32 cùng nhãn cả 30 ảnh;
sai lệch xác suất lớn nhất 0,0000026822. INT8 dùng 120 ảnh train nguồn làm calibration, không lấy valid để calibration.
Đánh giá cả FP32 và INT8 trên toàn bộ 451 ảnh valid của nguồn; không điều chỉnh checkpoint/ngưỡng theo kết quả.

| Chỉ số đo lại | ONNX FP32 | ONNX INT8 dùng trong app |
|---|---:|---:|
| Accuracy, mọi ảnh | 87,58% | 87,80% |
| Macro-F1 | 0,8700 | 0,8751 |
| Recall HƯ | 100% | 100% |
| HƯ bị đoán TƯƠI | 0/114 | 0/114 |
| Kích thước file | 93,98 MB | 24,06 MB |
| Coverage ở ngưỡng 0,70 | 35,70% | 35,25% |
| Accuracy trong phần được chấp nhận | 99,38% | 99,37% |
| Host CPU inference p50 | 29,42 ms | 12,59 ms |
| Host CPU inference p95 | 41,83 ms | 16,29 ms |

MB dùng 1.000.000 bytes. Các số trên do chạy lại trong phiên làm việc này, không chép thành tích của bài báo.
Accuracy chính tính trước từ chối. Ngưỡng 0,70 vẫn là mặc định chưa hiệu chỉnh;
khoảng 64,75% ảnh bị từ chối, vì vậy chưa đạt mục tiêu coverage ≥50% đặt ở đề cương.
Không giảm ngưỡng dựa vào valid đã dùng đánh giá để làm đẹp kết quả; cần tập hiệu chỉnh độc lập mới.
Recall HƯ 100% chỉ đúng cho 114 ảnh trong lần thử này, không phải bảo đảm trên thực phẩm ngoài thực tế.
Latency là máy tính CPU 4 threads, **không phải điện thoại**.

Confusion matrix INT8, hàng là nhãn thật, cột là dự đoán:

| | TƯƠI | Half-Fresh | HƯ |
|---|---:|---:|---:|
| TƯƠI | 163 | 12 | 3 |
| Half-Fresh | 13 | 119 | 27 |
| HƯ | 0 | 0 | 114 |

## Cài và chạy

Gói source, gói model và gói dataset là các file tách biệt để giữ nguồn và quyền sử dụng rõ ràng.
Giải nén model bundle; thư mục `model` chứa ONNX INT8 và config.

```powershell
python scripts/install_published_model.py --bundle "D:\FreshCheck-published-models\model"
cd android
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest
```

Thay đường dẫn bằng thư mục thật đã giải nén. APK kèm bàn giao đã có ONNX INT8, không phải APK thiếu model 0.1.0.
App ưu tiên ONNX nếu `published_model_config.json` có mặt. Để quay về MobileNetV2 TFLite,
cài model TFLite theo README rồi bỏ `published_model_config.json` và `published_meat.onnx` trước build.

Muốn tái lập conversion/evaluation, cài torch/torchvision CPU từ kênh PyTorch chính thức và requirements riêng:

```powershell
py -3.11 -m venv .venv-published
.\.venv-published\Scripts\python.exe -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv-published\Scripts\python.exe -m pip install onnx==1.17.0 onnxruntime==1.20.1 Pillow numpy
.\.venv-published\Scripts\python.exe ml/published_meat.py --checkpoint "D:\FreshCheck-published-models\original\resnet50_fe.pth" --data "D:\FreshCheck-real-data\Meat Freshness.v1-new-dataset.multiclass"
```

Thử nhanh một ảnh bằng ONNX mà không cần cài PyTorch:

```powershell
python -m pip install onnxruntime==1.20.1 Pillow numpy
python ml/predict_published.py --bundle "D:\FreshCheck-published-models\model" --image "D:\anh-thit.jpg"
```

Đã chạy lệnh single-image trên ảnh thật và nhận scores/nhãn từ model, không dùng dữ liệu giả.
Model gốc được nạp bằng `weights_only=True`, kiểm SHA-256 trước khi dùng.
Không cần huấn luyện lại để sử dụng checkpoint này. Script xuất lại FP32/INT8 và báo cáo từ ảnh thật.
`import_published_data.py` tạo index giữ nhãn/split nguồn và để group_id trống; không bịa mã mẫu vật.

## Việc còn phải làm trước nghiệm thu

Cài APK lên điện thoại thật; kiểm camera, crop, nhãn, CSV, offline và bộ nhớ;
đối chiếu preprocessing Android–Python; đo p50/p95 trên máy tầm trung; thu dữ liệu mới độc lập để
kiểm ngoại miền, hiệu chỉnh ngưỡng và xác nhận chất lượng nhãn với người có chuyên môn.
ONNX Runtime Android 1.30.0 được khai báo cho ứng dụng 0.5.1; báo cáo chuyển đổi cũ dùng host 1.20.1;
chưa có kiểm chứng runtime trên điện thoại cho hai bản này.
Giữ nghiên cứu gốc trong trích dẫn; không trình bày checkpoint của tác giả như mô hình nhóm mình tự huấn luyện.

SHA-256 checkpoint gốc:
`777a6239b0948acbf9354f0734e21cfc5467dad7b4364435189830d7ff9c7d57`

SHA-256 archive dữ liệu tải từ Kaggle:
`dfd69db4995f634ca43e4152cd47905eb3a8a180b223404bb5a2bc1f87423740`

SHA-256 ONNX INT8:
`d8ef55440e48106b7c6a8c3633b67e49f8526bb8ebed0f455d692e57c8d7d572`


## Build Android 0.2.0

Đã build assembleDebug thành công với ONNX INT8 trong assets. 3 JVM unit tests qua, không lỗi.
Chưa chạy camera/inference trên thiết bị Android thật; build không thay thế kiểm thử runtime.
