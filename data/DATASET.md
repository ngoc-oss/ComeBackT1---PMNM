# Kế hoạch và quy trình bộ dữ liệu

## Phạm vi

Khởi đầu táo / chuối / cam, chụp từng vật thể. Mục tiêu lập kế hoạch: 4.500–9.000 ảnh,
ít nhất khoảng 500 ảnh mỗi tổ hợp 3 loại × 3 trạng thái; tăng số mẫu vật độc lập thay vì chụp hàng trăm ảnh cùng một quả.
Đây là số lượng đề xuất, **chưa phải dữ liệu đã thu thập**. Báo cáo số quả/lô độc lập, không chỉ số ảnh.
Không dùng số ngày bảo quản làm nhãn tự động: điều kiện và giống thực phẩm khác nhau.

## Định nghĩa nhãn ngoại quan

| Nhãn | Hướng dẫn gán nhãn |
|---|---|
| fresh | Chưa có dấu hiệu hư ngoại quan theo hướng dẫn riêng cho loại; không đồng nghĩa kiểm nghiệm an toàn |
| suspicious | Có biến đổi ngoại quan nhẹ/chưa rõ như nhăn, đổi màu bất thường cần kiểm tra; phải có ảnh thực và tiêu chí thống nhất |
| spoiled | Có dấu hiệu hư rõ quan sát được theo tiêu chí của loại thực phẩm |

Đốm nâu trên chuối chín không tự động là hư. Cần phân biệt chín, dập, mất nước, mốc và hư;
ghi nhận phụ trong sổ nhãn và xử lý bất đồng với người có chuyên môn thực phẩm.
Nhóm không thể gán chắc chắn phải để riêng để rà soát, không ép vào suspicious để lấp thiếu dữ liệu.
Nếu nguồn công khai chỉ có fresh/rotten: không tự chia đôi điểm model thành lớp suspicious.
Cần bổ sung lớp giữa thật hoặc công bố bài toán chỉ có hai nhãn.

## Thu thập

1. Mỗi mẫu vật có mã cố định `group_id`; mọi ngày/góc chụp của cùng mẫu thuộc một group.
2. Chụp nhiều thiết bị, ánh sáng trong/ngoài nhà, nền đa dạng, khoảng cách hợp lý. Không dùng lọc màu.
3. Ghi food_type, ngày/giờ, nguồn, tác giả, điều kiện chụp/bảo quản và quyền sử dụng.
4. Không để watermark, tên nhãn, bao bì hoặc nền cố định trở thành dấu hiệu đoán lớp.
5. Hai người gán nhãn độc lập cho tối thiểu 20% dữ liệu; tính Cohen's kappa và giải quyết bất đồng.
6. Không nếm mẫu nghi hư; quy trình xử lý mẫu cần được người phụ trách hướng dẫn.

Manifest bắt buộc: `path,label,food_type,group_id,source,license`; cột bổ sung được giữ lại.
`path` tính từ `--root`; `license` phải là quyền thực tế, không chép tùy ý từ file mẫu.
Đối với dữ liệu tải ngoài: kiểm tra trang gốc, phiên bản, nguồn ảnh và giấy phép; giấy phép nền tảng chưa chắc cấp quyền cho mọi ảnh.
Gói hiện tại không tải hoặc tái phân phối dataset bên thứ ba.

## Tiền xử lý và chia dữ liệu

Script đọc được ảnh → EXIF transpose → RGB → kiểm tra kích thước ≥64 → hash pixel chống trùng.
Nhãn xung đột trên ảnh giống nhau gây lỗi, không âm thầm chọn một nhãn.
Chia theo group với seed cố định, kiểm tra mọi split có đủ 3 nhãn. Tỷ lệ thực tế có thể lệch 70/15/15.
Kiểm tra `dataset_report.json`, rà near-duplicate bằng tiếp xúc trực quan hoặc bổ sung perceptual hash.
Chưa có thuật toán near-duplicate tự động trong bản này.
Crop trung tâm vuông, resize bilinear 224×224 khi nạp train/eval; giữ ảnh gốc để truy vết.
Augmentation chỉ train, không chạy lên validation/test trước khi chia.

## Test bổ sung

Giữ một tập ngoài miền từ điện thoại, ánh sáng, nền và nơi thu thập mới.
Lưu ảnh không phải thực phẩm, nhiều vật, mờ/tối riêng; kiểm tra tỷ lệ model vẫn nhận nhầm tự tin.
Không dùng ngưỡng softmax như bảo đảm phát hiện ảnh ngoài miền. Để mở rộng, bổ sung mô hình phát hiện
vật thể/loại thực phẩm hoặc lớp reject đã thu thập đúng, và đánh giá độc lập.

## Dataset card cần hoàn thành

Tên/version; URL/giấy phép; người thu thập; số ảnh và số group mỗi loại/nhãn; cách gán nhãn;
kappa; loại thiết bị; điều kiện bảo quản; cân bằng dữ liệu; dữ liệu bị loại; hạn chế;
hash manifest; ngày đóng băng test; người được quyền truy cập. Chưa có số liệu thì ghi “chưa đo”.
