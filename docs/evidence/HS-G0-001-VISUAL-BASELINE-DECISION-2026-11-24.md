# HS-G0-001 — Visual Baseline Decision & HS-G0-V01 WorkPackage
Date: 2026-11-24
Status: **VISUAL BASELINE BLOCKED / G0 PARTIAL / G1 NOT AUTHORIZED**
Repository: BlueDragon33/Hardware_Simulation
Canonical ledger: **Issue #4 exclusively**
Branch: plan/hs-g0-001-visual-baseline-20261124 (documents only, based on Draft PR #11)
Inspected main: `fbd57ee106b5e55081bcafbeb7204b8b5a4fb823`
Exact accepted-for-camera-test candidate (NOT product accepted): Draft PR #11 `c9ac22b49cbdd365600e383eb54e34bdaf7ade13`
Law: Blueprint OS Universal Constitution 1.3.0 ACTIVE, B2 / LOCAL_CORE / ZERO-SPEND / offline-first. No release authority.

## 1. Evidence actually inspected
1. **Source of truth:** GitHub PR #6–#11, Issue #4 OPEN, local constitutional adoption, full master architecture proposal. All observed PR heads matched the previously pinned SHAs on 2026-11-24; main unchanged.
2. **Actual runtime frames:** Windows-hosted Chromium 141.0.7390.37, run [45404055032](https://github.com/BlueDragon33/Hardware_Simulation/actions/runs/45404055032), artifact ID **14925580120**, checksum of downloaded ZIP `ba95a6d4e8dde1d1c8e661f2ca44ea86b3df10fd36e4bda40d2c2915189b401b`. Source HTML of archived Three.js/Canvas/CSS prototypes was independently inspected from the SHA-pinned 31-entry ZIP.
3. **QA matrix:** `camera_qa_report.json` read and confirmed **9/9** real camera keyboard + pointer state PASS across 1440x900, 800x900, 390x844 (three 3D renderers). Camera QA and 8 runtime regressions are **NOT visual acceptance**.
4. **Reference videos supplied in conversation:** `Mô phỏng board arduino(1).mp4` (15.02 sec, landscape) and `Mô phỏng thực tế.mp4` (20.54 sec, portrait, recorded instrument/scope and interactive circuit UI). Contact frames inspected at approximately 8%, 30%, 56%, 81% of each clip. They show an immersive electronics workbench with breadboard/jumpers, code panels and oscilloscope traces. Source video compression and filming-of-screen limit objective pixel-quality comparisons.
5. **User-selected external reference:** [Robotics Lab #nano](https://robotics-lab-app.vercel.app/#nano); live public page text verified on 2026-11-24. It exposes **3/4, Top, Bottom, Front**, Rotate, Labels, Find the part, Assemble it; describes code/procedural models with Three.js/WebGL and a separate pin-to-pin workbench. This site is primarily a Nano reference at #nano, not a same-board pixel-perfect ESP32 target. The page was inspected as public HTML; its live WebGL canvas was **not** captured head-to-head in the same test environment. No invented pixel similarity, FPS or geometry measurements.
6. **Screenshot anchors:** `keyboard_three_1440x900.png` SHA-256 `407282d772b0e1011662fdb0702fabcb6b390ee69632edcb7a6aced7156fca3c`; `keyboard_three_390x844.png` SHA-256 `2baffbb6242d8cb488bd82c27a3270b1162ddb05e7aefb62550fe0c33017bc6b`. The actual artifact also contains 800px and equivalent Canvas/CSS screenshots.
7. **Provenance rules:** original videos are user-provided conversation material, not copied to GitHub; CI screenshot artifact may expire and must be re-generated with pinned SHA. Third-party Robotics Lab assets/code are not licensed for copying by this reference.

## 2. Evidence-grounded visual gap matrix

| ID | Severity | Evidence / observation | Distinction |
|---|---|---|---|
| VIS-P0-01 | **P0 BLOCKER** | The ESP32/breadboard circuit extends beyond the right viewport boundary in the **390x844** Three.js screenshot. Reset/default framing fails to show the complete circuit on mobile. | Actual pixel-visible issue; no screenshot-based count of hidden holes is asserted. |
| VIS-P0-02 | **P0 BLOCKER** | `R1 220Ω`, `C1 100µF` and `NODE OUT` label boxes visibly overlap on top of breadboard/components; hard to trace which lead belongs to which component. | Original source uses fixed-position Three.js sprites (`makeLabel`); the Canvas version draws fixed-position projected labels (`label3D`). |
| VIS-P1-03 | P1 CORE FIDELITY | ESP32 DevKit is represented with boxlike PCB, grey module and large simplified gold headers. The USB port, EN/BOOT, module shield/antenna, SMD arrangement and readable PCB silkscreen cannot be reliably identified from the screenshot. | Neither certified pin pitch nor model CAD/board provenance currently demonstrated. Do not guess dimensions or claim pin mapping. |
| VIS-P1-04 | P1 CORE FIDELITY | Breadboard shows hole pattern and colored rails but little socket depth, center gutter detail or physically anchored jumper endpoints. | No verified hole-to-netlist visual truth. |
| VIS-P1-05 | P1 CORE FIDELITY | Jumper wires and R/C/LED bodies are simplified; lead insertion and cable termination are difficult to inspect. | Visual connection ≠ verified electrical connection; keep separate. |
| VIS-P1-06 | P1 CORE FIDELITY | Materials/lighting/shadows have basic prototype quality; scene lacks the visual differentiation and polish of the supplied references. | Qualitative assessment only; do not assign unsupported similarity percentages. |
| VIS-P2-07 | P2 EXTENDED VIEWER | Current 3D UI has Normal/Engineering/Top/Reset; reference page offers explicit 3/4/Bottom/Front and labels/part discovery/assembly. | Functional reference features, not all required within G0. |
| VIS-P2-08 | P2 FUTURE INSTRUMENTATION | Reference video shows readable waveform/oscilloscope instrumentation and editor integration not proven to be functionally equivalent in this demo. | Not included in HS-G0-V01, not silently declared simulator accuracy. |

**Overall decision:** VISUAL BASELINE **BLOCKED**, owner visual acceptance **PENDING**; static comparison and runtime screenshots are not permission to self-approve the owner's qualitative gate. G0 remains PARTIAL/BLOCKED and G1 must remain BLOCKED.

## 3. Proposed measurable acceptance rubric (targets, NOT results)

The following are **future acceptance gates** to be measured in real Chromium on the exact candidate SHA using 1440x900, 800x900, 390x844. Proposed limits are not claimed to have passed.

| Gate | Objective, instrumented acceptance condition | Evidence artifact |
|---|---|---|
| V-01 default viewport framing **P0** | After load and Reset Camera, all visible required ESP32 board, breadboard, connected wires and LED/resistor/capacitor bounds are inside the **unobscured render viewport** with ≥16 CSS px left/right and ≥12 CSS px top/bottom at all three sizes; nothing critical clipped by HUD or side panel. Reset works after orbit/zoom. | Screenshot before/after reset, browser-computed bounds and source SHA. |
| V-02 labels legible and unambiguous **P0** | Engineering labels for the 4 existing named nodes have zero intersection with each other's bounding boxes, control panels and the focal components; leader lines/pins identify the target; at 390px collapse nonselected labels or reposition without losing keyboard-accessible labels. Minimum label text 12 CSS px on mobile and contrast ≥4.5:1 for normal text where applicable. | Automated projected 2D box intersection and computed contrast/typography, plus 390/800/1440 screenshots. |
| V-03 CAD camera + selection preserved | All 9 previously passing keyboard/pointer camera cases remain PASS; focus visible, selected-node label follows camera on orbit, Escape resets. No loss of button or pointer functionality. | Existing 3×3 Windows QA + new label position assertions, JSON log and screenshot. |
| V-04 mobile touch/control occlusion | Mobile 390px: primary buttons are reachable without scrolling the render viewport; no fixed overlay occupies required hardware viewing area; interactive controls ≥44×44 CSS px where layout permits. | Playwright visibility/overlap and tap target measurements, screenshot. |
| V-05 detailed board identity **P1 future** | A documented licensed board reference supports dimensions, GPIO pin ordering and USB/antenna/EN/BOOT footprint. All proposed pin IDs correspond to the circuit/netlist identity, and the silkscreen is readable in an appropriate close view. | Source/licensing record, per-part screenshot, mechanical/pin map tests, owner signoff. |
| V-06 realism and performance **P1 future** | PCB/headers, socket geometry, cable insertion, resistor/LED/capacitor materials, shadows and highlights are independently reviewed in screenshots at all sizes; report measured frame-time/FPS/device capability rather than assumed values. | Side-by-side evidence, measured browser trace/FPS, owner verdict. |

**Note:** precise screenshot-to-reference pixel similarity is not a valid automatic gate here: references are different hardware, camera framing and captured media. A human visual gate remains mandatory.

## 4. Single bounded remediation WorkPackage — HS-G0-V01 (PROPOSED, NOT IMPLEMENTED)

**Goal:** Fix only **VIS-P0-01 default framing** and **VIS-P0-02 Engineering label overlap** for the **generated runtime** (Three.js first, Canvas/CSS sanity) while preserving the live code/solver/firmware boundaries and existing camera controls.

**Implementation boundary:**
- Create a new independent review branch based on exact reviewed PR #11 state. Do not edit the historical `archive/source_bundle`, restored `recovered_prototypes`, or V5 electrical/firmware source.
- Implement scene framing from known model/screen-space bounds on load/reset and resize. Honor 1440/800/390, available viewport after mobile HUD. Do not simply change global zoom until components disappear.
- Add a deterministic, collision-aware Engineering label layout anchored to actual projected component coordinates with viewport clamping. For 390px, show one selected label expanded and expose the others via accessible focus/select; do not hide factual information permanently.
- Keep `Normal` and `Engineering` modes, Tab/Arrow/Shift+Arrow/+/-/Escape controls and pointer orbit/zoom intact. No new sensors, simulated firmware, electrical solver changes, PBR rebuild or broad architecture refactor.
- Extend Windows browser QA to compute real projected model bounds, label rectangles and click/tap availability; capture 3×3 screenshots and console logs. Fail-closed on missing geometry/bounds; no permissive visual mocks.
- Real proof required: V-01, V-02, V-03 and V-04 above on exactly pinned candidate with source hash, no external requests and untouched archive.

**Non-goals:** P1 photorealism, exact CAD board provenance, oscilloscope, new camera view modes, electrical truth, numerical solver acceptance. These remain future scope and cannot be counted as G0 PASS by implication.

**Approval:** Proposed review package only. No owner approval, G0 PASS, G1 opening, merge/ratification/Production or publication is authorized.

## Exactly ONE NEXT ACTION

Execute **HS-G0-V01 P0 visual remediation** on an independent Draft branch: fit the entire circuit within the unobscured 390/800/1440 viewport at default/reset and eliminate overlapping Engineering labels; run real Windows Chromium V-01–V-04 visual assertions and submit screenshots to Issue #4 for a human decision. Keep G0 overall BLOCKED and G1 NOT AUTHORIZED.
