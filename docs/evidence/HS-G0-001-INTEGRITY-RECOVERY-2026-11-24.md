# HS-G0-001 Source Integrity Recovery — 2026-11-24

Status: ARCHIVE_SOURCE_INTEGRITY VERIFIED in isolated local QA; G0 overall PARTIAL/BLOCKED; G1 NOT AUTHORIZED.
Canonical ledger: BlueDragon33/Hardware_Simulation Issue #4. Constitution ACTIVE 1.3.0, B2, LOCAL_CORE, ZERO-SPEND.
Inspected main fbd57ee106b5e55081bcafbeb7204b8b5a4fb823. Parent Draft PR #6 head 7bd10a234448d9f905f762ddb7dc2486d43706d7.
Recovery branch: repair/hs-g0-001-source-integrity-20261124; no main mutation, merge, Production or publication.

## Verified provenance, before changing any checksum

The consolidated local snapshot was compared byte-for-byte to 8 independent individual prototype ZIPs originally created in the conversation: V1–V5 and 3 separate 3D prototype archives. All 18 / 18 corresponding source files match (including original index, README, V3 app.js and style.css). The 2 snapshot docs are not included in that independent 18-file comparison.
Original consolidated source ZIP: 80,334 bytes, 31 ZIP entries, 20 files, Python ZipFile.testzip() PASS.
Trusted source ZIP SHA-256: 293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f.
Old GitHub manifest declared a different digest: 2930182a96a9c442d331ecbefaa358b5eb280df3598929cf9ff2e01ce5a6d4ab. The old 17 GitHub base64 fragments decoded to 80,340 bytes with SHA-256 1ad7e2a8456e6823cdf39e1e9c4712bd013f0ae8f0c55ce2e98da20f7a090388; central directory could not be read beyond entry 24.

## Repair scope

- part011.txt: corrected one base64 character at zero-based offset 5609, s to k. Read-back Git blob SHA-1 a3d8fd8f99615c9410b2338e58a9aff172cb91da matches trusted source.
- part016.txt: restored the corrupted suffix from verified original, 2120 -> 2112 characters. Read-back Git blob d877675766a5c4475a3d1023d807a02d8e311665 matches trusted source.
- All 15 other fragments unchanged; 17 / 17 source parts now match the original split Git blob identities.
- SHA256SUMS.txt corrected to the measured trusted ZIP SHA only after source file provenance and in-memory whole-ZIP SHA-256 verification, not as a stand-alone checksum change.
- README provenance updated. One regression test added; parent Draft PR #6 has fail-closed restore and five existing tests.

## Exact verification

Remote GitHub fragment read-back 17 / 17 SHA-1 Git blobs matched independently computed local fragment Git blob SHA-1. In-memory V8 SHA-256 of patched remote fragments gave the full original ZIP SHA exactly and central directory contained 31 / 31 valid entries.
Isolated local mirror: /mnt/data/hs-g0-001/recovery-mirror.
Restore script exact Git blob bdc8dc6f68ece5589cf5bd880c66750117c30a85, existing 5 regression tests exact blob 550f1b901cbccdbe93bcc28e8c14035d508a1bfc, new test exact blob 915c9b9e790c471e7343df1ad9bd5f49cf433614.
python tools/rebuild_sources.py: RESTORED, SHA256 VERIFIED, 31 ZIP entries.
Python ZipFile.testzip(): PASS; 20 extracted files.
python -m unittest discover -s tests/archive -p 'test_*.py' -v: 6 tests run, 6 PASS.
No GitHub-hosted CI or real browser UX check was run on this branch. Prior local Chromium HTTP and file navigation failed ERR_BLOCKED_BY_ADMINISTRATOR; no bypass was attempted.

## Gate result

Source provenance PASS (18/18); source parts PASS (17/17); ZIP SHA-256/CRC/restoration PASS (offline mirror matching GitHub part bytes); archive regression 6/6 PASS.
Offline Chromium UI: BLOCKED BY ENVIRONMENT. MNA/firmware numerical behavior: UNVERIFIED. 3D visual QA/owner acceptance: UNVERIFIED.
G0 overall PARTIAL/BLOCKED; G1 remains BLOCKED.

ONE NEXT ACTION: obtain/use authorized Chromium offline QA environment, run real locally served V5 and 3D prototype entrypoints at 1440/800/390, capture real runtime error states, and update Issue #4. Do not bypass administrator policy, merge, publish or call Product PASS.
