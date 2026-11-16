# Wilsof reporting and current status

GitHub issue #16 is the sole authoritative current project dashboard. Issue #60
tracks remaining release acceptance. docs/status.md is a pointer, not a second
status narrative. These current rules supersede historical blanket requirements
for a new 12-part report, report commit or reporting branch on every session.

Every task closes out with one concise verified update answering:

1. What works?
2. What is broken?
3. What blocks release?
4. What is the next technical action?
5. What requires owner intervention?

Include exact source/artifact identity, actual tests/CI and their limits, measured
used/free/reclaimed bytes, protected assets, active processes/locks and automation
pause state when relevant. Retain private receipts/checkpoints for resumability.
Read external updates back at their exact IDs/commits before claiming publication.
A plan/estimate is not executed cleanup; source/CI is not ISO/runtime acceptance.

Reuse the existing issue/PR and delivery branch. No report-only branch or duplicate
status file. Only substantial new engineering evidence warrants an archived report;
keep it in the existing organized report/checkpoint directories, with exact inputs
and limitations. Do not repeat tests or create a VM/build to fill a report. Retain
necessary historical reports in Git instead of copying full archives repeatedly.

Keep secrets, raw conversations, credentials, private host details and VM disks out
of GitHub. If publication is blocked, state the exact failure and private checkpoint
path; do not fabricate a URL or schedule an implicit retry. No new worker, scheduler,
paid QA, merge, build, release or physical operation follows from a status update.
