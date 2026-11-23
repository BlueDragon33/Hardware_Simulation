# HS-G0-001 — Authorized Chromium offline QA attempt

**Date:** 2026-11-24 (Europe/Berlin); executed at 2026-11-23T21:20:40Z.
**Verdict:** PARTIAL / BLOCKED BY ADMINISTRATOR POLICY. No REAL-UX-VERIFIED claim.
**Single canonical ledger:** BlueDragon33/Hardware_Simulation Issue #4.
**Observed main:** fbd57ee106b5e55081bcafbeb7204b8b5a4fb823.
**PR #6:** 7bd10a234448d9f905f762ddb7dc2486d43706d7.
**PR #7:** 6aeb73416a18f15c2e8001a6ba58182619ffc67d.
**Constitution:** Blueprint OS 1.3.0 ACTIVE; B2; LOCAL_CORE; ZERO-SPEND.

## Test source

Restored from archive with SHA-256:
293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f.
Python 3.13.5 archive regression: `python -m unittest discover -s tests/archive -p 'test_*.py' -v`: **6/6 PASS**.
Python stdlib HTTP server returned **200 for all four entrypoints**, proving local files are served before the browser-level block.

## Actual Chromium instrumentation

- Chromium **144.0.7559.96**, `/usr/bin/chromium`, standard Playwright headless launch; no `--no-sandbox`, no modified enterprise policy.
- Local ephemeral HTTP origin `127.0.0.1`; all non-local requests intercepted and aborted to prevent external dependencies.
- Four entrypoints: V5 MNA, offline Canvas 3D, legacy Three.js 3D, CSS Visual Prototype 1.
- Three viewports each: **1440x900**, **800x900**, **390x844**.
- **12/12 browser `page.goto()` attempts failed** with `net::ERR_BLOCKED_BY_ADMINISTRATOR`, before DOM/JS app execution. The same block was separately reproduced via `file://` for V5.
- No application screenshot, no real console/JS execution evidence, no pointer or keyboard interaction, no frame time/FPS or WebGL quality measurements can be claimed.
- Browser error screenshots obtained at **800x900** and **390x844**, showing the administrator block. Screenshot at **1440x900** failed with `Page.captureScreenshot: Unable to capture screenshot`. These two PNG files are diagnostic error-page evidence only (retained in conversation QA artifact); they are **NOT** screenshots of ESP32 visual software.

## Offline dependency audit (static, distinct from runtime)

- V5 MNA HTML: no literal external script or stylesheet URL found.
- Offline Canvas 3D HTML: no literal external script or stylesheet URL found.
- CSS Visual Prototype 1 HTML: no literal external script or stylesheet URL found.
- Legacy Three.js prototype: **requires remote `https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js`**, a known offline-first **product blocker** for that prototype unless dependencies are bundled.
- Absence of a literal URL is not proof of offline runtime; all 4 still require genuine authorized browser testing.

## Scope/gates

**PASS:** archive checksum/CRC, 6 archive regressions, 4 Python HTTP responses.
**BLOCKED (environment):** all 12 Chromium navigation attempts; screenshots of actual application.
**KNOWN OFFLINE PRODUCT BLOCKER:** CDN Three.js dependency of legacy prototype.
**UNVERIFIED:** rendered UI at 1440/800/390; mouse/keyboard, WebGL/fallback, MNA numerical output, real ESP32 firmware and visual acceptance.
**G0 overall:** PARTIAL/BLOCKED. **G1:** BLOCKED.
No merging/ratification/publication/Production, no cost, no attempted policy bypass.

Machine-readable matrix: `docs/evidence/HS-G0-001-CHROMIUM-OFFLINE-QA-2026-11-24.json`.

## One next action

Perform one authorized offline Chromium QA pass on Windows/local permitted Chromium using the recovered exact archive and the same 4x3 matrix. Verify actual UI with screenshot/console/interaction and external-request interception. If a policy still blocks, report exactly one blocker and do not fake PASS or alter security settings. Do not implement G1 while this verification remains blocked.
