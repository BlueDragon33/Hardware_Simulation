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

SHA-256 của ZIP gốc:

```text
2930182a96a9c442d331ecbefaa358b5eb280df3598929cf9ff2e01ce5a6d4ab
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