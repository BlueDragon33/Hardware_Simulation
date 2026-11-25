# Chat handoff and developer-support control contract (candidate)
Status: FC01 CONTRACT CANDIDATE — applies to Hardware_Simulation sessions when adopted by project instructions; does not modify Universal Constitution.
Source: Blueprint OS v1.3.0 ACTIVE; Project B2, LOCAL_CORE.
Inspected repo main: fbd57ee106b5e55081bcafbeb7204b8b5a4fb823 (2026-11-23). Revision must be refreshed at each new turn.

## Product behavior
After every **meaningful completed work batch** (not every tool call), present ONE compact support panel, designed for ChatGPT chat first and mirrored in a project-local UI where useful:
- **Theo Hiến pháp**: opens/points to the real active Constitution and current project adoption, never claims compliance by itself.
- **Tạo prompt tiếp theo**: generates a stage-specific, copyable/editable PROJECT EXECUTION prompt from observed project/gate/revision information. It must not immediately execute.
- **Thêm yêu cầu riêng**: optional notes that are appended as *lower-precedence user constraints*; refuse conflict with canonical policy or guards.
- **Duyệt prompt**: human accepts the text as a *chat work request* only; it is NOT an authenticated project mutation, Constitutional ratification, Quality Gate PASS or Production approval.
- **Sao chép**: copies the final approved prompt for a new chat/Windows Work only if required.

Keep the panel lightweight: one summary line, two primary actions, a collapsible/editable prompt preview, optional custom requirement, and one approval/copy action. Do not fill the conversation with decorative controls.

## Every batch handoff, in order
1. `BATCH_RESULT`: DONE / PARTIAL / BLOCKED (not marketing PASS).
2. `EVIDENCE`: repository, exact inspected base/head, checks actually executed, outputs.
3. `BLOCKER`: explicit unresolved issues, no hiding.
4. `NEXT_ACTION`: exactly one smallest dependency-unblocking action.
5. `CONTROL_PANEL`: Constitution, Generate Prompt, Custom Requirement, Review/Approve, Copy.

## Generated prompt envelope (minimum)
```
FAMILY=PROJECT_EXECUTION; TEMPLATE=hardware-chat-handoff.v1
PROJECT=BlueDragon33/Hardware_Simulation
POLICY=blueprint-os:universal-century-grade@1.3.0
LEVEL=B2; DEPENDENCY=LOCAL_CORE; COST=ZERO-SPEND
BASE/HEAD=<live exact SHA to verify>
WORKPACKAGE=<canonical issue/work package, or PROPOSED if absent>
STAGE=<current gate> ; STATUS=<observed state>
EVIDENCE=<exact checks/logs>
BLOCKERS=<real unresolved blockers>
SCOPE=<one bounded objective>
ALLOWED=<bounded reads/tests/minimal edits on independent branch>
FORBIDDEN=no invented PASS; no merge/ratify/publish/Production; no security bypass
OUTPUT=<one final report, exact revision, evidence, one next action>
STALE_RULE=recheck HEAD, Constitution and canonical state; stop/regenerate if changed
USER_EXTRA=<optional non-conflicting constraints>
```

## Source-of-truth and persistence
The UI can hold editable draft text, but **does not persist canonical state**. Canonical facts live in the repository's reviewed work packages/gates/evidence, not generated prompts, localStorage, a screenshot or a chat. The chat renderer cannot guarantee controls automatically appear in unrelated new conversations; install these instructions in the project's persistent context or reopen this contract. In unsupported interfaces, include a concise text fallback with a ready-to-copy next prompt.

## Gate & permission policy
Check GitHub live HEAD before use. If a gate is blocked, generate remediation, not advancement. Restrict actions to source/test on an independent branch until reviewed. Do not treat clicking "Duyệt" as permission to merge, publish, release, ratify or waive a gate. Offline and no-cost operation is default; remote tools are optional with declared data boundary and exit.
