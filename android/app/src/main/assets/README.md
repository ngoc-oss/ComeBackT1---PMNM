# Model assets 0.2.0

Cài gói published model bằng scripts/install_published_model.py.
App ưu tiên published_model_config.json + published_meat.onnx; ONNX chứa model ResNet-50 thực.
Nếu không có config ONNX, app thử TFLite theo model_config.json + food_model.tflite.
Xem docs/PUBLISHED_MODEL.md về nguồn, nhãn và kết quả kiểm chứng.
