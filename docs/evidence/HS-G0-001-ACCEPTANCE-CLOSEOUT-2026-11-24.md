# HS-G0-001 — Acceptance Closeout Evidence (2026-11-24)

**Decision: PARTIAL / G0 BLOCKED; G1 NOT AUTHORIZED.** This is a reproducible QA checkpoint, not Product/Visual/Constitution acceptance or release authority.

## Governance and inspected pinned state
- Repository: `BlueDragon33/Hardware_Simulation`; canonical ledger **Issue #4**.
- Inspected main: `fbd57ee106b5e55081bcafbeb7204b8b5a4fb823` (unchanged).
- Draft chain: PR #6 `7bd10a234448d9f905f762ddb7dc2486d43706d7` -> PR #7 `6aeb73416a18f15c2e8001a6ba58182619ffc67d` -> PR #8 `234cd2100469fc21db168767a75ac1a8f7792acb` -> PR #9 `20abf175a9fab7740445b5dad5f6cccb0a8075a7`.
- Constitution: Blueprint OS Universal 1.3.0 ACTIVE, local adoption B2 PRODUCT / LOCAL_CORE, ZERO-SPEND/offline-first. No merge, ratify, Production or G1 expansion.
- Historical source ZIP: SHA-256 `293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f`; archive not modified.

## Exact QA evidence from Windows
- Latest run: https://github.com/BlueDragon33/Hardware_Simulation/actions/runs/45344559269 (completed SUCCESS **as evidence collection**, NOT Product PASS).
- Execution: standard GitHub hosted `windows-2025`, Chromium `141.0.7390.37`, Node 22 / Python 3.11, Playwright 1.56.0.
- Repository lockfile `package-lock.json` was generated and committed **only** on the independent QA branch; `npm ci` succeeded with exact `three@0.161.0` / `esbuild@0.24.2`. Lockfile Git blob SHA-1 `a4299782058107e0f4d6e8ba2cf603d1a0ad775f`; artifact lock source SHA-256 `181a0178f796c6bea919398ff4399de69d9567f5c5dc2a3dfc7810e0cb0fca1d`.
- Two consecutive build invocations of the local Three.js IIFE produced the same SHA-256 `f2ad67ff457c26c62c892e33c8b18d0e461bdae4264481a12c36d4b35c398ab8`. This demonstrates **bundle reproducibility on the same runner**, not cross-platform bit-for-bit reproducibility.
- `python -m unittest discover -s tests/runtime -p 'test_*.py' -v`: **4/4 PASS**.
- From a fresh incognito Chromium context **per viewport** (no persisted browser storage, service workers blocked), open locally hosted runtime and **reload** while rejecting every request outside `127.0.0.1`: **12/12 initial HTTP 200**, **12/12 reload true**, **12/12 keyboard Enter activated the basic Run/Engineering action**. Across the 12 actual browser cases: **0 JS page errors, 0 external runtime requests, 0 failed local HTTP asset requests**.
- Context-isolated browser testing DOES NOT physically disconnect the Windows runner's network adapter; build and `npm ci` require registry access before the prebuilt app runs.
- For Three.js 3D at 1440/800/390, pointer drag + wheel caused a changed screenshot, **not** an independently measured camera angle; source and prior tests show pointer handlers. No performance/FPS claim.
- Artifacts of run 45344559269:
  - `HS-G0-acceptance-evidence` ID `14898020805`; artifact SHA-256 `1b3b0e0730d2f66267f4f0b447c90f2a6b4c1e94880ef0241e0b055daaab99f7`. Contains JSON and 12 genuine application screenshots.
  - `HS-G0-lock-provenance` ID `14898175022`; artifact SHA-256 `f7ab7ec6c1b21a32947333c98fcb1dbfb5b6d4fc88f558207fdb2e40f562d2f3`.

## G0 acceptance matrix
| Gate / claim | Observed disposition |
| --- | --- |
| Archived source checksum, no mutation | PASS for source integrity |
| Local Three.js bundle, no CDN requests at browser runtime | PASS within tested HTTP/route-isolation environment |
| Pinned dependency installation (`npm ci`) | PASS on Windows runner; committed lockfile |
| Rebuilt vendor script digest identical twice | PASS, same Windows runner |
| Fresh-context start + reload at 1440/800/390 × 4 | 12/12 OBSERVED |
| Keyboard Enter for basic button action | 12/12 OBSERVED |
| Keyboard-accessible 3D camera navigation | **BLOCKED: 9/9 3D cases lack canvas keyboard focus/keyboard camera controls** |
| Accurate camera transform/angle and motion FPS | NOT_MEASURED; screenshot changes only |
| User-selected reference visual quality | **NOT ACCEPTED / BELOW REFERENCE**: see below |
| Real ESP32 compiled firmware binary, numerical SPICE/MNA accuracy | UNVERIFIED; OUT OF THIS QA |
| Full physical offline adapter-disconnect cold install | NOT_TESTED (only external requests blocked at browser runtime) |
| Owner signoff for G0 / G1 entry | PENDING HUMAN REVIEW |

## Visual acceptance comparison — grounded, not a claimed pixel-match
Sources:
- Owner's second electronics simulator video (original local video reference); observed detailed breadboard hardware, jumper connectors and integrated engineering controls.
- User's reference site https://robotics-lab-app.vercel.app/#nano : documented 3/4, Top, Bottom, Front, rotate labels, component finding and assembly; its site states procedural Three.js/WebGL models.
- Actual Windows screenshot `visual_3d_threejs_prototype_index_1440x900.png` from run #45338944044 and screenshot at 390x844 (also reproduced in current acceptance artifact).
- No quantitative pixel-level capture or FPS test of the reference site was performed. Do not assign invented similarity percentages.

Observed current gaps:
1. ESP32 PCB module, SMD details, connector realism, pin headers and silkscreen are crude compared with the reference; no verified real device dimensions or pin-grounded model provenance.
2. Floating Engineering labels overlap the breadboard and electronic components, reducing readability; at 390px some scene objects/labels are cropped near the viewport edges.
3. The 3D prototypes do not yet provide keyboard camera orbit/pan/zoom and explicit canvas focus/fallback. Nine of nine 3D viewport cases observed this accessibility gap; basic button keyboard Enter works.
4. The viewer does not yet provide equivalent 3/4/Bottom/Front physical inspection or assembly tools. Those reference features are **future-scope**, NOT G0 requirements to implement now.

**Interpretation:** the new offline WebGL runtime is a viable engineering base; it is **not** a reference-quality 3D product. G0 cannot be silently approved and G1 must not be opened based on CI success alone.

## Exactly ONE next action
**HS-G0-001 keyboard-camera remediation:** on a minimal independent review branch, add accessible focusable canvas and keyboard camera controls (orbit/pan/zoom with visible instructions, Escape reset/cancel) to the **generated 3D runtime only**, keep historical archive immutable, add browser assertions for all 3D scenes at 1440/800/390, and collect actual Windows screenshots and keydown/camera state evidence. Keep G1 BLOCKED until the separate owner visual-baseline review is explicitly decided. No merge, ratify, publish, Production, paid dependencies, or invented PASS.
