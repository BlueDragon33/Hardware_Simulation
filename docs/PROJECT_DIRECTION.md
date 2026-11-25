# Project direction

## Kết luận từ giai đoạn prototype web

Các bản V1–V5 là thử nghiệm chưa được kiểm chứng đầy đủ về thao tác GPIO, wiring, sensor simulation, breadboard topology, netlist và MNA prototype. Tuy nhiên các thử nghiệm 3D web hiện tại chưa đạt chuẩn hình ảnh của video tham chiếu thứ hai.

## Hướng tiếp theo

- Giữ `prototypes/v5_mna_solver` làm nền tảng tham khảo cho simulation engine.
- Không tiếp tục tăng phiên bản HTML chỉ để làm đẹp hình ảnh.
- Tách kiến trúc thành `simulation-core` và `renderer`.
- Renderer hiện hành: Three.js/WebGL bundle local; Unity 6 là adapter có điều kiện khi có bằng chứng về giới hạn chất lượng hoặc hiệu năng và quyết định riêng.
- Vertical slice hiện tại: ESP32 DevKit reference + BB400 + LED + R/C + hai jumper; giữ phạm vi P0/P1 đã nghiệm thu.
- Khi visual đạt chuẩn mới nối simulation core vào renderer.

## Các tầng dự kiến

1. `simulation-core/` — netlist, MNA/SPICE, GPIO/PWM/ADC, sensor models.
2. `firmware/` — parser/emulator ESP32, sau này có thể dùng QEMU/WASM hoặc engine phù hợp.
3. Renderer adapter — Three.js hiện hành, Unity tùy chọn; các đường dẫn module tương lai chỉ là đề xuất.
4. `assets/` — model/texture/material PBR.
5. `archive/` hoặc `prototypes/` — giữ nguyên các thử nghiệm lịch sử.


## Dependency posture

Future work follows Constitution ACTIVE 1.3.0:

`LOCAL SIMULATION CORE → OPTIONAL RENDERER/AI/SYNC`

The simulation engine and canonical electrical/project state remain local and portable. Remote rendering, cloud compute, Google Drive and AI providers may be added only as replaceable adapters with explicit exit paths. They must not become hidden prerequisites for basic simulation.

Master Plan và ADR: `docs/HARDWARE_SIMULATION_MASTER_PLAN.md`. Các thư mục dự kiến không phải source hiện hành; không tạo scaffold để khớp sơ đồ.
