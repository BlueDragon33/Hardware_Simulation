# HS-G0-001 — Offline runtime remediation (review candidate)

This is an **evidence-only runtime build**, not G1 visual acceptance, production, or an ESP32 binary emulator. It has no effect on the historical archive's bytes.

## Build

- Install Node 22+ and Python 3.11+.
- From a trusted source checkout: `npm ci --no-audit --no-fund` with pinned `three@0.161.0` / `esbuild@0.24.2`. These are **build-time dependencies**, not runtime CDN requirements. The tracked package-lock.json pins the build dependency graph; prior same-runner deterministic bundle evidence is in Issue #4.
- `npm run build:offline` runs the SHA-256-guarded archive restorer, copies exactly four prototype entrypoints into `runtime_dist/`, inserts mobile layout remediation without touching the archived HTML, and produces `runtime_dist/vendor/three-runtime.iife.js` and Three.js MIT license.
- After build, serve `runtime_dist` on localhost; **disconnect network** and verify no third-party request is made by the browser. Installation/build requires npm access once; normal runtime does not. Source SHA: `293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f`.
- Open `runtime_dist/index.html` through local HTTP. Never use `file://` results as guaranteed behavior.

## Mobile behavior

At viewports up to 600px, the control strip uses two columns at the top of the scene. Tooltips and the live inspector move to the sidebar below the editor without losing their original DOM nodes or updates; their original position is restored on resizing to desktop. The mobile scene no longer has an inspector surface covering the Engineering button.

## Governance

- Build output is a generated artifact, not canonical source. The local project's archive and netlist remain separate from render state.
- QA checks must verify actual visible canvas, interactions, screenshot and blocked external resource requests. Smoke success is not human visual acceptance, numerical oracle proof, or broad offline guarantee.
- Source archive stays immutable. All edits on independent Draft PR, no merge/ratify/publish.

## Recovery and evidence boundary
Build output is replaceable; do not place user projects in runtime_dist. FC02 run 45658272185 reproduced retry failure: nonempty recovered_prototypes is rejected by restore guard before runtime build. Proposed bounded fix reuses an exact byte-verified extraction without rewriting it; extra, missing or changed files fail closed. On interrupted generated-output build, re-run the pinned build; if extraction itself differs, preserve it and use a clean trusted checkout. Retest required before declaring recovery verified. Historical browser route isolation is not OS network disconnection. Do not claim physical air-gap or electrical correctness.
