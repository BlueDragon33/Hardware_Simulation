# Full prototype source bundle

Thư mục này giữ một snapshot nén của toàn bộ prototype đã tạo trong giai đoạn ESP32 Virtual Lab V1–V5 và các thử nghiệm 3D.

Do connector GitHub hiện tại không tải binary ZIP trực tiếp, ZIP được lưu dưới dạng nhiều phần base64 trong `base64/`.

Khôi phục toàn bộ source:

```bash
python tools/rebuild_sources.py
```

Script sẽ tạo:

- `archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip`
- `recovered_prototypes/` chứa toàn bộ source đã giải nén.

Các bản trong bundle gồm V1, V2, V3, V4, V5, 3D Three.js prototype, 3D Offline prototype và Visual Prototype 1.
