# Project direction

## Kết luận từ giai đoạn prototype web

Các bản V1–V5 chứng minh được nhiều phần logic quan trọng: thao tác GPIO, wiring, sensor simulation, breadboard topology, netlist và MNA prototype. Tuy nhiên các thử nghiệm 3D web hiện tại chưa đạt chuẩn hình ảnh của video tham chiếu thứ hai.

## Hướng tiếp theo

- Giữ `prototypes/v5_mna_solver` làm nền tảng tham khảo cho simulation engine.
- Không tiếp tục tăng phiên bản HTML chỉ để làm đẹp hình ảnh.
- Tách kiến trúc thành `simulation-core` và `renderer`.
- Renderer mục tiêu: Unity 6, model 3D PBR thật, camera CAD, spline jumper wire, socket snapping.
- Prototype Unity đầu tiên chỉ cần ESP32 DevKit + breadboard + LED + điện trở + jumper wire, ưu tiên chất lượng hình ảnh và UX trước.
- Khi visual đạt chuẩn mới nối simulation core vào renderer.

## Các tầng dự kiến

1. `simulation-core/` — netlist, MNA/SPICE, GPIO/PWM/ADC, sensor models.
2. `firmware/` — parser/emulator ESP32, sau này có thể dùng QEMU/WASM hoặc engine phù hợp.
3. `unity-client/` — 3D renderer, interaction, camera, snapping, measurement UI.
4. `assets/` — model/texture/material PBR.
5. `archive/` hoặc `prototypes/` — giữ nguyên các thử nghiệm lịch sử.
