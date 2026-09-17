# Thư viện, nguồn và quyền sử dụng

Mã tự viết của FreshCheck: MIT, toàn văn LICENSE. Không sửa/vendoring source thư viện trong project.
Gradle/pip tải dependency thông qua kho chuẩn. APK cần đóng gói runtime để hoạt động offline.
Danh mục dưới đây là dependency trực tiếp; **chưa thay thế kiểm kê toàn bộ transitive dependencies của release**.

| Thành phần | Vai trò | Giấy phép / nguồn tra cứu |
|---|---|---|
| AndroidX Activity/Core/ExifInterface | UI lifecycle, URI, hướng ảnh | Apache-2.0; https://android.googlesource.com/platform/frameworks/support/ |
| TensorFlow / TensorFlow Lite | Train/conversion/inference | Apache-2.0; https://github.com/tensorflow/tensorflow/blob/master/LICENSE |
| Keras | CNN và huấn luyện | Apache-2.0; https://github.com/keras-team/keras/blob/master/LICENSE |
| Kotlin | Ngôn ngữ/runtime | Apache-2.0; https://github.com/JetBrains/kotlin/blob/master/license/LICENSE.txt |
| Gradle / wrapper | Build | Apache-2.0; https://github.com/gradle/gradle/blob/master/LICENSE |
| NumPy | Mảng số | BSD-3-Clause; https://github.com/numpy/numpy/blob/main/LICENSE.txt |
| Pillow | Ảnh | HPND/Pillow license; https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| scikit-learn | Split và metric | BSD-3-Clause; https://github.com/scikit-learn/scikit-learn/blob/main/COPYING |
| Matplotlib | Confusion matrix | Matplotlib license; https://matplotlib.org/stable/project/license.html |
| JUnit 4 | Unit tests JVM | EPL-1.0; https://github.com/junit-team/junit4/blob/main/LICENSE-junit.txt |
| Google ML Kit Image Labeling | Bộ lọc nhãn ảnh offline trước suy luận | Google ML Kit Terms; https://developers.google.com/ml-kit/terms |

Khi release, lưu `gradlew :app:dependencies`, `pip freeze`, và thông tin license từ artifacts đã resolve.
Giữ notice/license cần thiết trong binary distribution; bảng này không phải xác nhận pháp lý toàn bộ dependency.
Trọng số ImageNet tải ở lúc train: cần kiểm tra điều kiện phân phối model dẫn xuất theo nguồn trọng số/dữ liệu.
Dataset chưa được đóng gói và phải có dataset card/giấy phép riêng.

Gradle wrapper do Gradle tạo giữ header Apache gốc; không đổi thành MIT.
Các file metadata JSON/CSV không hỗ trợ comment được mô tả tại README/notice, không chèn comment làm hỏng định dạng.


## Bổ sung 0.2.0

- Phteven: checkpoint ResNet-50 của nhóm tác giả, giữ MIT Copyright (c) 2023 Team 9 trong LICENSES/Phteven-MIT.txt.
- ONNX / ONNX Runtime: MIT, https://github.com/onnx/onnx và https://github.com/microsoft/onnxruntime.
- PyTorch/torchvision: dùng để chuyển đổi checkpoint, giấy phép tại https://github.com/pytorch/pytorch/blob/main/LICENSE.
- Dataset Meat Freshness: CC0 theo metadata Kaggle của người đăng; không đổi thành MIT. Xem PUBLISHED_MODEL.md.

Android 0.5.1 dùng ONNX Runtime Android 1.30.0 cho hai model độ tươi; dependency TensorFlow Lite đã được bỏ khỏi APK.
TensorFlow/Keras trong bảng trên chỉ còn liên quan pipeline nghiên cứu/huấn luyện cũ.

## FruQ-DB and the experimental fruit model (0.3.0)

- Dataset: Abayomi-Alli Olusola, Robertas Damaševičius, FruQ-DB v1,
  DOI https://doi.org/10.5281/zenodo.7224690. License declared by uploader: CC BY 4.0,
  https://creativecommons.org/licenses/by/4.0/. Original images/labels retained;
  FreshCheck adds deduplication, a diagnostic split and derived trained weights.
- Fruit model: FreshCheck-trained head on torchvision MobileNetV3 Small ImageNet1K V1.
  It is not the FruitQ authors' model. Dataset attribution applies; weights are
  supplied as a research artifact with CC BY 4.0 attribution, not claimed to be
  wholly MIT. Torchvision BSD notice: LICENSES/Torchvision-BSD.txt. ImageNet
  pretraining and source dataset terms remain separate from the project's MIT code.
- No upstream fruit code/checkpoint is copied from FruitQ-GradeX or the comparative
  YOLO README repository. The former is binary quality; the latter had no available
  checkpoint in the reviewed tree. Neither satisfies the requested official
  three-label checkpoint condition.
