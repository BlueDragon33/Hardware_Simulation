# HS-G0-001 — Owner Visual Checkpoint and bounded P1 WorkPackage
2026-11-24 | Blueprint OS 1.3.0 ACTIVE | B2 PRODUCT | LOCAL_CORE | ZERO-SPEND | offline-first

**Decision: VISUAL BASELINE BLOCKED/PARTIAL; owner signoff PENDING, G0 PARTIAL/BLOCKED, G1 NOT AUTHORIZED.**
Canonical ledger: Issue #4 only. This is a document-only review, not an authorization to implement, merge, ratify or publish.

## 1. Exact pinned evidence

- Main observed: fbd57ee106b5e55081bcafbeb7204b8b5a4fb823. Draft PR #6–#13 heads matched pinned values at preflight.
- Current screenshot source: Draft PR #13 HEAD ab4ed2a18b74bec317db01713856546d8b955d26, Windows Chromium run https://github.com/BlueDragon33/Hardware_Simulation/actions/runs/45408347766, artifact 14925749719, artifact digest sha256:7a2f269437c35e975539d2511847774c7acd9154e19d9295590e149a19c956b6.
- Exact PNG files: three_1440x900.png sha256:32094432565d6b4147c0538477c217eb40cb60335e44996cfb6112c999bbf5c5; three_800x900.png sha256:0e0aa9bff3e8e43e2c62b65e3b6d4569206c3b00083d6cf849f17822138aeacf; three_390x844.png sha256:17c800c8bf8c84563fb95c7b4d2ed726489b2f9853493e69471a734bab50be74.
- Original run JSON is retained intact, reported MEASURED_V01_P0_PASS_NOT_OWNER_ACCEPTED (3/3) and narrowed camera regression (9/9), 8/8 existing runtime regression. This confirms measured model framing and *partial* label collision assertions only, not total visual acceptance.
- The original user-provided videos (Mô phỏng board arduino(1).mp4 and Mô phỏng thực tế.mp4) were inspected in the conversation; they are NOT copied into GitHub. Reference website https://robotics-lab-app.vercel.app/#nano states procedural Three.js/WebGL with component discovery and different camera views. No pixel similarity percentage or identical board CAD is claimed.

### Newly found P0 false-negative in the previous acceptance gate

The real 800px screenshot shows NODE OUT badge drawn over the ESP32 DevKit V1 Inspector card; C1 badge also intrudes at that card's left edge. The generated visual QA code only collects .overlay, #hsCameraKeyboardStatus, and .hud into its label/control collision check, omitting visible .inspector/.tip/floating panes. The prior labelsHitControls=false does NOT mean zero occlusion of all UI panels. Do not overwrite historical logs; add a new test and re-evaluate this uncovered P0 case. The 390px full model remains within the measured safe screen bounds but is small enough that pins/sockets cannot be inspected at default zoom.

**P0 owner verdict remains PENDING; baseline technically BLOCKED for complete collision-free UI.**

## 2. Source-grounded hardware fidelity reference (no unverified assumptions)

The original renderer calls the carrier ESP32 DevKit V1; its code draws 2 groups × 15 gold pins with arbitrary BoxGeometry PCB 2.45 × 4.45 scene units and pin center pitch 0.245 scene units. There is no recorded physical mm scale or exact variant. DOIT DevKit V1 commonly exists in 30- and 36-pin variants and many clones differ: https://www.circuitstate.com/tutorials/getting-started-with-espressif-esp32-wifi-bluetooth-soc-using-doit-esp32-devkit-v1-development-board/ .

**Provisional board reference only:** Wokwi DOIT 30-pin board metadata has graphic dimensions 28.2 × 53.0 mm, 2.54 mm adjacent header pitch, pin D2/GPIO2 at x=26.8 mm, y=33.74 mm measured from the artwork's top-left: https://github.com/wokwi/wokwi-boards/blob/main/boards/esp32-devkit-v1/board.json . Do not confuse drawing coordinates with a manufacturer-certified dimension for every clone. Do not copy third-party 3D/2D artwork.

**Manufacturer module data:** if actual module is ESP32-WROOM-32, Espressif specifies 18 × 25.5 × 3.1 mm for the module, which is NOT the carrier size: https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html . Verify markings before claiming module-specific truth. Espressif's ESP32-DevKitC V4 is a different board with its own guide and must not silently replace DOIT V1: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html .

**Breadboard reference:** BusBoard Prototype Systems BB400 datasheet https://www.mouser.com/datasheet/3/271/1/BPS-DAT-%28BB400%29-Datasheet.pdf specifies 84 × 47.6 mm, 2.54 mm insertion-hole pitch, 300 central contact holes + four 25-hole power rails = 400, white ABS housing and nickel-plated phosphor bronze interior contacts. Current renderer labels the object 400-point but actually draws only 10 × 24 = 240 dark cylinders and red/blue rails without insertion sockets. Do not label the source mockup physically accurate.

**Jumper connector reference:** Pololu male-female jumpers use 0.1 inch/2.54 mm connectors: https://www.pololu.com/product/3840/specs . DOIT male pin to breadboard requires a female receptacle on the header and a male insertion pin in a specific breadboard hole, if this is the selected wire type. The original renderer has just two suspended curved tubes, with no verified end-connector/slot mapping. Keep existing two virtual netlist connections unchanged; mark unproven visual endpoints UNVERIFIED_CONTACT.

**Materials:** manufacturer BB400 ABS/plated phosphor bronze is source-grounded; matte PCB solder mask/metal USB housing/shield/header caps, LED epoxy and cable jacket should be procedurally modeled without inventing manufacturer-specific roughness values. Retain provenance/license records; never copy Robotics Lab assets or proprietary meshes.

## 3. Proposed HS-G0-P1-001 — limited hardware model fidelity WorkPackage (NOT AUTHORIZED)

**Goal:** upgrade only the EXISTING ESP32 DOIT 30-pin, 400-point breadboard, two existing jumper wires, and current R1 220Ω, C1 100uF and red LED in the generated Three.js runtime. No new electronics/sensors, electrical netlist rewiring, solver code, firmware, oscilloscope, additional camera modes, architecture rewrite or production deployment.

1. Owner/model provenance gate: select exact 30-pin board photo/part or approve provisional Wokwi DOIT 30-pin outline as REFERENCE_ONLY; distinguish clone-specific USB/UART and mechanical tolerances. Publish a local model-provenance manifest (source URL, board variant, pin count, mm scale, asset license, confidence) before geometry work.
2. Use one explicit millimeter-to-world transform, then create 30 header pins with unique IDs, source-grounded 2.54 mm pitch and correct D2=GPIO2 identity. Add correctly proportioned WROOM shield/antenna outline, USB, EN, BOOT, visible silkscreen and LED; verify pin order against approved source, without changing GPIO simulation.
3. Replace placeholder 240-hole appearance with EXACTLY 400 socket openings: 300 central + four rails of 25, a central gutter, row/column/rail identifiers, recessed contacts and correct 2.54 mm pitch. Batch/instance hole geometries to keep WebGL performance stable.
4. For the two existing jumper tubes, define read-only from/to terminal IDs; draw physically plausible 2.54 mm female-on-header and male-in-socket ends with strain relief/bends. When physical source netlist mapping is not established, mark endpoint data UNVERIFIED_CONTACT and fail closed instead of inventing connectivity.
5. Render existing resistor, capacitor and LED with identifiable body orientation and inserted leads. Resistor 220Ω should visually match an actual 220Ω band pattern (for example red/red/brown/gold) rather than the current artistic brown/black/red placeholder; do NOT change the 220Ω simulation constant. Show capacitor polarity only for confirmed electrolytic type and LED cathode polarity without claiming unverified polarity wiring.
6. Improve local procedural material differentiation, PCB silkscreen, metal pins and plastic sockets; build detailed close-up views using existing camera zoom without new mode. Keep keyboard/pointer regression PASS and no external browser asset requests.

### Proposed measurable P1 gates (targets, not current results)
- Mechanical geometry matches an explicitly approved board reference: header spacing 2.54 mm within ±0.05 mm computational model tolerance, 30 unique pin bodies with pinID, WROOM-32 footprint where applicable; carrier footprint matches selected source dimensions within documented source tolerances (reference-only geometry must remain labeled).
- Exactly 400 individually addressable breadboard sockets: 300 + 100 rails. Every inserted existing component lead and wire end must have a named socket/pin anchor; no floating ends in inspector/picking metadata.
- Each of the existing R1/C1/LED identities remains correct and readable at close zoom, without changed electrical constants/firmware results; source/orientation and PBR material provenance documented.
- Measured Chromium Windows 1440×900, 800×900, 390×844: geometry/camera bounds, full Inspector+label/control overlap coverage, 0 external requests, 0 JS page errors; 9/9 prior camera regression and 8/8 prior runtime regression preserved, plus new mechanical and socket-count assertions.
- Actual screenshots comparing the exact source-identified hardware and the owner's quality reference, explicit human visual acceptance. No unmeasured FPS or reference similarity claim.

**Scope/fail-closed boundaries:** P1 work remains planned, not implemented or approved. It cannot waive the P0 800px Inspector issue. Archived ZIP source sha256:293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f stays byte-identical. No merge/ratification/publish/Production.

## 4. Exactly one NEXT ACTION

**HS-G0-V02 INSPECTOR COLLISION GATE:** in a separate review branch, eliminate NODE OUT/C1 overlap with the visible Inspector at 800px, expand Chromium DOM rectangle assertions to enumerate all visible Inspector/Help/Toolbar/HUD/label/picker surfaces, and capture fresh 1440/800/390 screenshots on the pinned candidate. Present those screenshots for OWNER VISUAL SIGNOFF before authorizing the separately defined P1 WorkPackage. Keep G0 PARTIAL/BLOCKED, G1 NOT AUTHORIZED, and P1 NOT YET APPROVED.
