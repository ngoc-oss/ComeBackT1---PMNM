# FreshCheck 0.5.1 — APK offline cho thịt và quả

Đây là bản bàn giao Android có sẵn hai model ONNX trong APK. Người dùng Android 8.0+
(API 26, gồm Samsung Galaxy A10s Android 9) chỉ cần cài APK, không cần tải model hay dữ liệu.
Xem `docs/RELEASE_051.md`, `docs/ANDROID_STUDIO_RUN.md`, `docs/INSTALL_SAMSUNG_A10S.md` và
`reports/release050/TEST_REPORT.md` trước khi nghiệm thu.

Bản 0.5.1 có kiểm tra ảnh tối/sáng/mờ, bộ lọc nhãn ảnh ngoài phạm vi (ML Kit chạy
trên máy), nút chụp lại, thông tin model/thời gian, xuất lịch sử CSV và APK tách ABI.
Bộ lọc chỉ giảm lỗi rõ ràng như người/xe; nó không phải bằng chứng ảnh thuộc phân phối huấn luyện.

Ba kết quả hiển thị là **TƯƠI / NGHI NGỜ / HƯ**. `NGHI NGỜ` ánh xạ lớp nguồn trung gian
Half-Fresh (thịt) hoặc Mild (quả); trạng thái điểm thấp `CHƯA ĐỦ CƠ SỞ` không bị đổi thành
NGHI NGỜ. Ứng dụng đánh giá dấu hiệu ngoại quan, không phải thiết bị kiểm nghiệm an toàn thực phẩm.

## Nguồn model trong APK

- Thịt: checkpoint ResNet-50 do repository Phteven phát hành; FreshCheck chuyển sang ONNX INT8.
- Quả: MobileNetV3 Small do FreshCheck huấn luyện từ FruQ-DB Zenodo 7224690. Đây **không phải**
  checkpoint do tác giả bài FruitQ công bố; ứng dụng và màn hình nguồn ghi rõ giới hạn này.

## Bản model/dữ liệu 0.3.0 làm nền cho 0.4.0

Bổ sung quả dùng dữ liệu FruQ-DB đã công bố trên Zenodo/Springer. **Model quả do FreshCheck huấn luyện; chưa xác minh được checkpoint của tác giả bài báo.** Ba nhãn nguồn Fresh/Mild/Rotten; xem [nguồn, cách chạy và giới hạn](docs/FRUITQ.md). Model thịt 0.2.0 được giữ nguyên.

- Cài cả hai model từ gói 0.3.0: `python scripts/install_bundle.py --bundle /path/to/FreshCheck-0.3.0-models`.
- Hoặc cài model quả: `python scripts/install_fruit_model.py --model-dir /path/to/FreshCheck-fruit-model`.
- Cài model thịt bằng hướng dẫn 0.2.0 bên dưới. Source tar.gz không gói trọng số/dữ liệu; tải các gói riêng.
- Build từ thư mục `android`: `gradlew.bat assembleDebug testDebugUnitTest` trên Windows.
- Chọn miền thực phẩm trong app trước khi chụp/phân tích.
- Xem `reports/fruitq` cho số đo thực tế; không dùng số bài báo làm accuracy dự án.

## Tài liệu bản thịt 0.2.0

# FreshCheck 0.2.0 — model thịt đã huấn luyện, dữ liệu thật ba nhãn

**Đọc `docs/PUBLISHED_MODEL.md` trước.** Bản này bổ sung checkpoint ResNet-50 công khai của nhóm tác giả Phteven,
2.266 ảnh Meat Freshness và ONNX INT8. Gói model/dataset tải riêng; APK 0.2.0 đã kèm model.
Model hỗ trợ thịt đỏ; nguồn nghiên cứu là preprint arXiv, không phải chứng nhận an toàn thực phẩm.

Cài model từ thư mục giải nén bằng `python scripts/install_published_model.py --bundle DUONG_DAN_THU_MUC_MODEL`,
sau đó mở `android` bằng Android Studio. Kết quả kiểm 451 ảnh nguồn: accuracy INT8 87,80%, macro-F1 0,8751;
chưa kiểm runtime/latency điện thoại. Nhãn NGHI NGỜ được ánh xạ có chú thích từ Half-Fresh của nguồn.

Phần dưới là pipeline **MobileNetV2 tự huấn luyện** từ bản 0.1.0, vẫn được giữ để nghiên cứu/so sánh.
Các ghi chú “chưa có model” ở phần đó chỉ áp dụng model MobileNetV2 tự huấn luyện, không áp dụng checkpoint Phteven bổ sung.

---

# FreshCheck — nhận diện dấu hiệu tươi / hư trên Android

Project nghiên cứu cho đề tài **“Nghiên cứu và ứng dụng AI trong nhận diện và đánh giá chất lượng thực phẩm”**.
Ứng dụng hiện tại dùng Kotlin Android + ONNX Runtime, xử lý hoàn toàn offline. Phần MobileNetV2/TensorFlow
Lite phía dưới là pipeline nghiên cứu cũ được giữ để tái lập thí nghiệm, không được đóng vào APK 0.5.1.

## Luồng MobileNetV2 tự huấn luyện (giữ từ bản 0.1.0)

Đã triển khai mã ứng dụng, pipeline dữ liệu/huấn luyện/xuất mô hình, đánh giá và tài liệu mã nguồn mở.
**Chưa có bộ dữ liệu thực phẩm thực tế và mô hình đã huấn luyện trên thực phẩm trong gói này.**
App không trả kết quả giả khi thiếu model. Bộ kiểm thử dùng ảnh nhiễu tổng hợp chỉ để kiểm tra luồng mã,
không chứng minh độ chính xác thực phẩm. Xem `docs/VALIDATION.md` để biết chính xác những gì đã chạy.

Phạm vi khởi đầu đề xuất: ảnh từng quả táo, chuối, cam có biểu hiện ngoại quan.
Chưa tuyên bố hỗ trợ thịt/cá, thực phẩm chế biến hoặc mọi loại thực phẩm.
Chọn `food_type` chỉ ghi nhận loại do người dùng xác nhận, chưa phải mô hình nhận dạng chủng loại.

Ba nhãn học có giám sát: `fresh` → TƯƠI; `suspicious` → NGHI NGỜ; `spoiled` → HƯ.
`uncertain` → CHƯA ĐỦ CƠ SỞ là trạng thái từ chối khi điểm thấp, **không phải nhãn NGHI NGỜ**.
Điểm softmax không phải xác suất thực phẩm an toàn. Ngưỡng thấp không phải bộ phát hiện ảnh ngoài miền.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| android/ | App chụp/chọn ảnh, suy luận trên thiết bị, lịch sử, benchmark CSV |
| ml/ | Chuẩn bị dữ liệu, train/fine-tune, export FP32/FP16/INT8, đánh giá, chọn ngưỡng |
| data/ | Manifest mẫu, hướng dẫn thu thập và nhãn |
| scripts/ | Cài model, smoke test, đóng gói release |
| tests/ | Kiểm thử chia dữ liệu, lượng tử hóa, crop và quyết định |
| docs/ | Đề cương, tiêu chí đánh giá, kiến trúc, release, kiểm chứng |
| .github/ | CI, mẫu issue và pull request |

## 1. Chuẩn bị trên Windows / VS Code

Cài Python 3.11 hoặc 3.12 (64-bit), JDK 17 hoặc 21 và Android Studio có Android SDK 35,
Build Tools 35.0.0. Không dùng JDK 25 với Gradle wrapper 8.9.
VS Code phù hợp sửa mã Python; dùng Android Studio mở thư mục `android` để chạy điện thoại.
Các phiên bản được chọn cố định để tái lập, không tuyên bố là phiên bản mới nhất.
Lần cài đầu cần Internet để tải dependencies và trọng số ImageNet. App chạy offline sau khi build có model.

Mở PowerShell tại thư mục `FreshCheck`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ml/requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Các lệnh `python` dưới đây cần chạy trong venv; trên Windows có thể thay bằng `.\.venv\Scripts\python.exe`.
Trên Linux: `python3 -m venv .venv`, `source .venv/bin/activate`, rồi `pip install -r ml/requirements.txt`.
`tensorflow-cpu` ưu tiên pipeline CPU tái lập. Muốn huấn luyện GPU trên NVIDIA, dùng môi trường TensorFlow CUDA
phù hợp trong WSL2/Linux, khóa phiên bản và ghi lại môi trường; không giả định cài gói CPU sẽ dùng GPU.

## 2. Tạo dữ liệu thật

Đọc `data/DATASET.md`. Thu thập ảnh có quyền sử dụng; đặt trong `data/raw/`.
Tạo `data/manifest.csv` dựa trên `data/manifest.example.csv`. File mẫu chỉ minh họa tên ảnh, không có ảnh đi kèm.

```powershell
python ml/prepare_data.py --manifest data/manifest.csv --root data --out data/processed
```

Ảnh cùng một quả/lô hoặc cùng chuỗi video phải có cùng `group_id` kể cả được chụp ở ngày khác nhau.
Script loại bản sao giống hệt, phát hiện nhãn xung đột, chia train/val/test theo group ~70/15/15.
Ảnh gần trùng vẫn cần rà thủ công. Đường dẫn trong split là đường dẫn tuyệt đối; chuyển máy phải chạy prepare lại.

## 3. Huấn luyện CNN

```powershell
python ml/train.py --epochs 15 --fine-epochs 10 --batch 16 --alpha 0.75
```

MobileNetV2 ImageNet → pooling → dropout → Dense softmax 3 nhãn.
Huấn luyện head rồi fine-tune 30 layer cuối, giữ BatchNorm đóng băng; early stopping theo validation loss.
Class weights xử lý mất cân bằng. Augmentation chỉ áp dụng train; không biến đổi màu mạnh vì màu liên quan nhãn.
Model xuất dùng RGB 224×224, crop vuông trung tâm; chuẩn hóa [0,255] sang [-1,1] nằm trong graph.
Đầu ra: `artifacts/model.keras`, cấu hình train, CSV loss/accuracy mỗi epoch.

## 4. Xuất TensorFlow Lite và chọn ngưỡng

```powershell
python ml/export.py
python ml/evaluate.py --model artifacts/export/food_int8.tflite --manifest data/processed/val.csv --out reports/validation.json
python ml/calibrate.py --validation-predictions reports/validation.npz
```

Xuất FP32, FP16 và INT8; INT8 dùng dữ liệu đại diện lấy cân bằng từ train.
Mục tiêu chọn ngưỡng mặc định: accuracy trên phần được chấp nhận ≥90%, coverage ≥50% trên validation.
Nếu không đạt, script dừng và giữ cấu hình cũ: cần cải thiện dữ liệu/model hoặc ghi rõ mục tiêu chưa đạt.
Không chọn ngưỡng trên test. Ngưỡng này chỉ hỗ trợ từ chối, không hiệu chỉnh xác suất an toàn.

## 5. Đánh giá test độc lập

```powershell
python ml/evaluate.py --model artifacts/export/food_float32.tflite --out reports/test_float32.json
python ml/evaluate.py --model artifacts/export/food_float16.tflite --out reports/test_float16.json
python ml/evaluate.py --model artifacts/export/food_int8.tflite --out reports/test_int8.json --threshold 0.70
```

Thay `0.70` bằng ngưỡng thực tế trong `artifacts/export/model_config.json` sau bước 4.
Accuracy/F1/confusion matrix tính trên mọi ảnh, chưa loại ảnh bị từ chối;
coverage/accepted_accuracy tách riêng. So sánh FP32/FP16/INT8 trên cùng test, không gộp host latency thành phone latency.
Kết quả gồm JSON, PNG confusion matrix và NPZ predictions. Báo cáo theo loại và lỗi HƯ→TƯƠI.

## 6. Cài model vào Android, build và chạy

```powershell
python scripts/install_model.py
cd android
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest
```

Mở Android Studio → Open → chọn `android` → Gradle Sync → cắm điện thoại bật USB debugging → Run.
Nếu dùng CLI, thiết lập `ANDROID_HOME` đến SDK hoặc tạo `android/local.properties` bằng Android Studio.
APK universal: `android/app/build/outputs/apk/debug/app-universal-debug.apk`.
APK điện thoại: `app-armeabi-v7a-debug.apk` hoặc `app-arm64-v8a-debug.apk`; emulator:
`app-x86_64-debug.apk`. Galaxy A10s dùng bản ARM hoặc universal.
Không cần sửa header mã nguồn để cấu hình. Không cần backend, khóa API hoặc tài khoản.
Trong ứng dụng: chọn loại → chụp/chọn ảnh → kiểm tra khung crop → xác nhận → xem kết quả.
Chỉ có cấu hình và model đúng SHA-256 mới được nạp. Build thiếu model vẫn mở UI nhưng khóa suy luận.

Để so tốc độ variant: `python scripts/install_model.py --variant float16`, build lại và lưu CSV riêng.
Ngưỡng phải chọn lại theo từng model nếu đánh giá hành vi từ chối. Bản Android 0.5.1 dùng ONNX Runtime
cho cả model thịt và quả; không đóng TensorFlow Lite runtime vào APK. iOS vẫn là hướng mở rộng,
chưa có mã ứng dụng iOS trong gói.

## 7. Đo trên thiết bị

App có nút **Đo tốc độ · Xuất CSV**, chạy 10 warmup + 100 lần, CPU 4 threads.
CSV ghi thiết bị, Android API, model hash/version, từng thời gian inference. Xem `docs/EVALUATION.md`.
Lặp nhiều ảnh, nhiều phiên đo; báo riêng p50/p95 inference và độ trễ từ thao tác tới kết quả.
Đo UI hiện tại không bao gồm mở camera, chụp và giải mã ảnh; cần video/stopwatch cho hành trình đầy đủ.

## 8. Đóng gói và nộp

Xem `docs/COMPETITION.md` và `docs/RELEASE.md`.
Mã dự án dùng MIT, header SPDX trong mã; dependency dùng giấy phép riêng.
Dataset/trọng số không tự động trở thành MIT. Không đẩy ảnh có thông tin riêng tư hoặc khóa ký lên Git.
Cần repository công khai, lịch sử commit thật, Issues và ít nhất một release trước hạn nộp.

## Nguồn kỹ thuật

- [MobileNet và MobileNetV2 — Keras](https://keras.io/api/applications/mobilenet/)
- [Quantization INT8 — Google AI Edge](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_integer_quant)
- [Android Gradle Plugin 8.7 / JDK 17 / Gradle 8.9](https://developer.android.com/build/releases/agp-8-7-0-release-notes)
- [TakePicture — Android Activity Result](https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContracts.TakePicture)
- [MIT — Open Source Initiative](https://opensource.org/license/mit)

Tra cứu ngày 10/09/2026; mã tích hợp viết riêng cho project. Tài liệu nguồn không phải kết quả kiểm nghiệm của FreshCheck.
