# Hardware Simulation — Product Architecture & Stage Plan
Status: FC01 CONTRACT CANDIDATE / OWNER G0 ACCEPTANCE PENDING / NOT RELEASED
Date: 2026-11-23
Scope: BlueDragon33/Hardware_Simulation
Inspected main HEAD: fbd57ee106b5e55081bcafbeb7204b8b5a4fb823
Canonical law: BlueDragon33/Software-Blueprint-Hub/docs/UNIVERSAL-CONSTITUTION.md at inspected main, policy blueprint-os:universal-century-grade v1.3.0 (ACTIVE)
Local adoption: .blueprint/constitution-adoption.json, B2 PRODUCT, enforced.
Operating posture: LOCAL_CORE, offline-first, source-only existing adoption; offline visual runtime evidenced; scoped Owner P0/P1 accepted on original SHAs; full product acceptance UNVERIFIED.

## 1. Product Profile (candidate)
**Goal:** Build a practical, accurate, visually legible, interactive hardware/electronics laboratory, beginning with ESP32 DevKit and breadboard. Visual reference is the user's second video and robotics-lab-app/#nano; neither source grants asset/code copying rights.

**Users/jobs:** learners and engineers inspect a high-quality 3D board; identify readable pins and PCB landmarks; orbit/pan/zoom; connect and disconnect realistic Dupont leads; edit code; run clearly scoped simulated functionality; measure electrical state; save/reopen portable projects locally.

**Success:** No empty 3D canvas; accurate mapping of pin identity to rendered socket; predictable CAD-like mouse/touch/keyboard controls; readable silkscreen under zoom; physically plausible cables and connectors; offline scene launch after install; topology/voltage measurements correspond to an independently tested engine; honest capability labels. User approval is separate from CI.

**Non-goals in first slice:** no photorealistic marketing mockup, no unverified CPU/firmware emulator, no cloud requirement, no AI as circuit truth, no bulk-board library, no paid dependencies or production publication.

## 2. Architecture and authority boundaries
```
Portable local project (schema/version, provenance, undo/redo)
       |
       v
Editor/controller -- input/picking/snap/layout --> 3D renderer adapter (Three.js/WebGL)
       |
       +--> electrical graph/netlist --> numerical core (verified DC/RC/MNA)
       |
       +--> firmware adapter (capability-labelled interpreter/emulator/toolchain)
       |
       +--> measurements / probes / diagnostics
       |
       +--> optional AI assistance / optional export/sync
```
The local canonical project/netlist state is not owned by the Three.js scene, by AI, by a remote website, or by chat prompts. Rendering cannot silently generate electrical truth. Use stable IDs for pins/components/wires and versioned, portable project JSON. Distinguish visual animation, simplified model and validated electrical result. Preserve old prototypes as **unverified historical sources**, not proof of functional runtime.

**Visual decision:** prioritize bundled Three.js/WebGL (NOT CDN-only or CSS pseudo-3D); build one board, not eight. Unity/PBR authoring is a conditional adapter if reference-quality metrics or asset workflow make WebGL unsuitable; neither choice changes core data contracts.

**Dependency budget:** prefer zero-spend/free locally reproducible tools, pin packages and licenses; disclose exact license/provenance of 3D/texture reference assets; offline core must not depend on Vercel, cloud AI, online model services, external CDNs or remote approval.

## 3. Incremental stage gates
| Gate | Output/vertical slice | Evidence for decision |
| --- | --- | --- |
| G0 Foundation | audited inventory, B2 Product Profile, architecture/ADR, asset licensing plan, QA matrix, scoped WorkPackage | exact main SHA, archive integrity/restore, contract review; no feature PASS inferred |
| G1 Visual quality | ONE accurate ESP32 DevKit 3D, high-quality PCB/silkscreen, camera/select/focus | actual Chromium 1440/800/390 screenshots, keyboard/focus, anti-aliasing, GPU errors, offline boot; owner compares to visual reference |
| G2 Wiring UX | breadboard sockets, real-shaped jumper endpoints, drag-to-connect, remove/undo, snap | exact-node picking, topology mismatch tests, no ambiguous clicks, usability on desktop/touch |
| G3 Electrical correctness | portable graph/netlist and tested DC/RC/PWM/ADC solver, probes and scope | numerical oracle cases, conservation checks, open/short errors, deterministic tests, no fabricated readings |
| G4 Firmware boundary | clearly identified supported ESP32 code execution path, safe compile/upload UX | documented supported instruction/API set, binary-vs-interpretation truth labels, regression evidence |
| G5 Learning lab | devices/sensors, repeatable lessons, save/load/export, diagnostics | actual local/offline journey, restart, backup/restore, user testing |
| G6 Hardening | performance/accessibility, data migration, resilience, security & maintenance | exact-revision CI+real UX+offline, risk-based independent review |
| G7 Release candidate | stable artifact with manual human release gate | owner acceptance, explicit Production authority and tested rollback |

**Gates are dependency ordered, not calendar promises.** Blocked means fix blocker before growing scope. A stage is not PASS because a document or screenshot exists.

## 4. Visual reference acceptance for G1
- Correct ESP32 DevKit V1 form factor, pin headers/labels, USB connector, shield, buttons and PCB landmarks; if a source dimension is uncertain, flag it rather than invent.
- CAD-style controls: left select/drag, middle pan, right orbit, wheel zoom, double-click focus; keyboard tab, escape and visible focus.
- Hover/pick and inspector share the SAME pin ID, with measurement state separately identified as simulated/unverified/validated.
- One coherent layout at 1440, 800 and 390 px; prevent UI overlays from covering the scene; include empty/loading/error/no-WebGL fallback.
- Bundled runtime works without network after install; report fallback capabilities honestly. Smoothness and GPU/FPS must be measured on named test equipment, not asserted.
- Real browser render and human comparison to references are required. NO image mockups substituted for runtime evidence.

## 5. WorkPackage HS-G0-001 (original scope, current closeout in Issue #4)
**Objective:** reconcile source/prototype inventory with current repository and confirm the offline runtime baseline before new 3D implementation.
**Allowed:** read-only verification; add scoped docs/tests on feature branch; verify source archive restore and checksum; identify existing executable entrypoint; select renderer packaging plan.
**Forbidden:** change Constitution, grant PASS without evidence, merge, ratify, publish, create paid resources, use external AI as circuit authority.
**Output:** exact commit SHA(s), observed test log, real blockers, one recommended next action.
**Exit:** if G0 evidence remains incomplete, keep G1 BLOCKED; do not jump to broad 3D asset implementation.

## 6. Governance
Apply Constitution 1.3.0 §§1–10 and R1/R3/R4 as relevant, plus local constitution adoption and dependency budget. Prompt is an execution projection, never canonical. Use a fresh live HEAD/diff check before editing. Keep real human review separate from work authorization and release authority. Local simulation and user project data survive loss of network. No merge/release by this draft.

## 7. FC01 — Foundation contract reconciliation (2026-11-25)
Authority: Owner authorized HS-G0-FINAL-CLOSEOUT in chat; Issue #4 checkpoint 7165360615; exact parent 44399f2464cfae2990223f5f0c6ea74b5b069da8. Earlier P0/P1 acceptances stay scoped to recorded revisions. No G0 acceptance inferred.

ADR: retain local Three.js 0.161.0 renderer after matched Windows Chromium P0/P1/R01 evidence; Unity only after measured inadequacy and separate decision. Geometry/visual transforms are downstream projections; `runtime_dist` is generated, never canonical. Source archive SHA-256 293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f is immutable after recovery. Original procedural geometry, reference facts only, Three.js MIT license bundled; no copied third-party meshes. Reference contacts remain UNVERIFIED_CONTACT.

Domain/API contract (design, not implemented Core): project owns versioned projectId, componentId, pinId, wireId and netId; pinId scoped by componentId; never derive authority from display labels or mesh array index. Controller accepts typed SelectPin/Connect/Disconnect commands; renderer receives read-only scene snapshot and emits stable selection IDs; Core alone validates topology and computes electrical results with explicit capability/units/provenance. Firmware adapter receives only scoped simulation I/O, never claims native binary support absent evidence. Persistence is planned portable local schema with validated import, explicit version migration and non-destructive export/restore; no real user data in generated build. No API server, new modules, device access or data migration in G0.

Security: local HTTP loopback only; treat imported project/code as untrusted, validate sizes/schema/IDs, isolate future firmware execution, forbid arbitrary host/device commands; no credentials, private project data or secrets in metadata or QA. No external upload, protected mutation or publication. Future device/firmware access requires separate authority and threat review. Recovery: immutable source plus replaceable output, pinned npm ci; interrupted build recovery and error UX to be measured in FC02. No release rollback claimed.

UX: existing Engineering overview, component focus, Inspector, keyboard/camera and responsive 1440/800/390 are baseline, no P2 redesign. Preserve meaningful labels, focus, controls and truthful unavailable/failed states. §11 computed contrast normal 4.5:1, large and meaningful nontext 3:1; composited backgrounds measured or UNVERIFIED; visual acceptance separate. Use existing style owners, no new design system UI.

Management R11–R14: canonical AM project id hardware-simulation (existing app/project-registry.ts), category Kỹ thuật. `control/application-management.contract.json` is metadata-only v1 per actual AM repository-discovery protocol. All capabilities false; no endpoints or origin asserted, no remote admin/approval/backend, no enrollment or central mutation. Discovery from main/master is not available for this Draft until separately authorized integration; offline runtime independent. Future protected mode requires migration gates, scoped identities, revocation/freshness, no local bypass. No new registry.

QA: existing source restore, scoped 12/12 smoke, P0 3/3, camera 9/9, runtime 8/8 and R01 natural loop retained at tested SHAs. FC02 covers actual pin pick-to-inspector, CSS prototype contract, fresh offline boot, fault-injected WebGL/bundle failure and rebuild recovery, computed contrast. Actual OS network-disconnected boot distinct from browser route isolation. FC03 exact revision impact, artifact preservation and review applicability; no implicit transfer of P1 visual approval; FC04 human G0 decision only. Independent review remains UNVERIFIED until real review; no invented external reviewer. No G1, merge, ratify, publish, Production, costs or future features.
