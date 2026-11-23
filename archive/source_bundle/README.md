# Full prototype source bundle

Thư mục này giữ **snapshot đầy đủ** của toàn bộ prototype đã tạo trong giai đoạn ESP32 Virtual Lab V1–V5 và các thử nghiệm 3D.

Do luồng connector hiện tại phù hợp nhất với nội dung text, ZIP nguồn được lưu dưới dạng các phần base64 trong `base64/`. Phần `part007` được chia thành `part007.txt` + `part007b.txt`; script khôi phục dùng thứ tự tên file nên tự ghép đúng.

## Khôi phục toàn bộ source

```bash
python tools/rebuild_sources.py
```

Script sẽ tạo:

- `archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip`
- `recovered_prototypes/` chứa toàn bộ source đã giải nén.

## Kiểm tra toàn vẹn

SHA-256 của ZIP lịch sử đã xác minh độc lập (khôi phục 2026-11-24):

```text
293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f
```

Checksum cũng được lưu tại `archive/source_bundle/SHA256SUMS.txt`.

## Nội dung snapshot

- ESP32 Virtual Lab V1 — basic firmware/LED prototype
- V2 — interactive wiring
- V3 — sensors, OLED, logic analyzer
- V4 — breadboard netlist, PWM/ADC/RC
- V5 — educational MNA circuit solver
- 3D Three.js prototype
- 3D offline prototype
- Visual Prototype 1
- tài liệu định hướng dự án

Các bản cũ được giữ nguyên để sau này có thể bóc tách, tái sử dụng hoặc hợp nhất phần tốt nhất vào kiến trúc mới.
## Hồ sơ nguồn gốc bản phục hồi 2026-11-24

- **Nguồn kiểm chứng:** đối chiếu byte từng file trong ZIP tổng hợp với tám gói ZIP prototype độc lập đã được tạo trong lịch sử dự án, kết quả **18/18 file nguồn trùng khớp**, bao gồm V1–V5 và ba thử nghiệm 3D. Hai file `docs/` còn lại thuộc snapshot; chúng không được tính vào 18 đối chiếu độc lập.
- ZIP nguồn tổng hợp có **80.334 byte**, **31 ZIP entries**, **20 file**, `ZipFile.testzip()` không phát hiện lỗi CRC.
- Trước phục hồi: `part011.txt` có một ký tự base64 khác nguồn chuẩn tại offset 5609; `part016.txt` có đoạn cuối lệch, dài 2120 ký tự thay vì 2112. Cả hai đã được phục hồi dựa trên ZIP kiểm chứng; toàn bộ 15 phần còn lại giữ nguyên.
- Manifest cũ chứa SHA-256 `2930182a96a9c442d331ecbefaa358b5eb280df3598929cf9ff2e01ce5a6d4ab`, **không khớp với ZIP đã chứng thực**. Manifest được cập nhật **chỉ sau khi** các phần source sửa đã được xác minh bằng Git blob SHA-1 so với dữ liệu nguồn gốc và SHA-256 toàn ZIP được tính lại. Không phải thao tác thay checksum đơn độc.
- Cổng bảo vệ: `tools/rebuild_sources.py` trên Draft PR #6 kiểm tra SHA-256, base64, đường dẫn ZIP, CRC và không ghi đè file có sẵn trước khi giải nén. Hãy lấy cả PR #6 khi kiểm thử PR phục hồi này.
- Kiểm thử độc lập: `python -m unittest discover -s tests/archive -p 'test_*.py' -v`; bảo toàn archive: `tests/archive/test_canonical_bundle.py`.
- Đây chỉ là **source-integrity VERIFIED**, không chứng minh GUI WebGL, firmware ESP32, solver MNA, offline UI hay nghiệm thu sản phẩm. Các cổng đó vẫn **UNVERIFIED/BLOCKED** theo Issue #4.
