# Hardware_Simulation

Kho lưu trữ toàn bộ các thử nghiệm mô phỏng phần cứng đã xây dựng trong giai đoạn prototype.

## Mục tiêu

Xây dựng một **Virtual Hardware / Electronics Lab** cho ESP32 và các phần cứng nhúng, kết hợp:

- mô phỏng mạch điện và breadboard;
- ESP32 GPIO / PWM / ADC / sensor simulation;
- netlist và MNA circuit solver;
- code editor / firmware workflow;
- giao diện 3D trực quan;
- về sau chuyển renderer chất lượng cao sang Unity, giữ engine mô phỏng làm backend.

## Nguyên tắc lưu trữ

Các phiên bản cũ được giữ nguyên để có thể đối chiếu, tái sử dụng hoặc lấy lại ý tưởng. Không xóa prototype chỉ vì giao diện chưa đạt yêu cầu.

Các thư mục `prototypes/` chứa tiến trình V1–V5; `visual/` chứa các thử nghiệm 3D; `docs/` ghi lại hướng phát triển tiếp theo.


## Operational sovereignty

Hardware_Simulation adopts **Universal Constitution 1.2.0** at **B2**.

Default posture: **LOCAL_CORE**.

- Circuit, GPIO/PWM/ADC/sensor and firmware simulation must remain usable on the local machine.
- Unity or another renderer may improve visualization but does not own simulation truth.
- Google Drive or equivalent may optionally back up/export project artifacts.
- AI may assist with explanation, code or design, but is optional intelligence.
- A paid/cloud runtime must not become mandatory for basic simulation when the local engine can satisfy the requirement.

Canonical dependency posture: `.blueprint/dependency-budget.json`.
