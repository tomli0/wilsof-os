# Wilsof agent rules

Read CONTRIBUTING.md and docs/artifact-maintenance.md before allocating resources.
GitHub issue #16 is the only authoritative current project status; #60 tracks
release acceptance. Historical reports are evidence, not current instructions.

## Independent implementation

Wilsof OS must be developed independently of Omarchy. Do not copy, port, adapt,
translate or repackage any Omarchy code, scripts or configuration, and do not add
Omarchy as a build, installation or runtime dependency. Shared software must come
directly from its original upstream with traceable provenance and applicable
licenses. Review uncertain inherited provenance before claiming independence;
functional tests do not establish code origin. Keep existing Omarchy installations
untouched. Historical migration or replacement goals do not override this scope.

## Delivery and preservation

1. Clean as you go. Every task retires its own verified disposable resources
   after preserving essential results. Perform authorized safe cleanup in the
   same session; a concrete dependency/authentication blocker is the exception.
2. Reuse the appropriate active branch. Create a short-lived branch only for
   independently reviewable work. No report-only branches or test-only branches.
3. Reconcile completed PRs/issues before unrelated work. Preserve unique WIP;
   archive and verify original refs before authorized retirement. Never force-push.
4. Evidence must be proportional: exact inputs, result, minimal reproducer and
   necessary failure evidence, not unlimited full-size intermediate copies.
5. Register owner/workflow, creation time, purpose, classification, dependencies,
   cleanup condition and storage budget before allocation. Use one host-wide
   artifact catalog and the normal build/QA entrypoints. Do not use a fresh catalog
   to hide existing artifacts. Check capacity; no automatic storage expansion.
6. Defaults: two active ISOs (reference/candidate), two disposable QA disks, one
   build workspace, 6 GiB cache, seven-day ordinary logs, 256 MiB diagnostic bundle
   per unresolved failure. Protected historical exceptions need individual reasons;
   numeric limits never authorize deleting recovery, signing material or backings.
7. Resolve routine technical problems autonomously within owner authorization.
   If sudo needs a terminal, prepare one exact consolidated command and continue
   independent work. Never bypass authentication or expand infrastructure.
8. Cleanup/source/CI success is not ISO, runtime, hardware or release acceptance.
   No new build, merge, release or physical operation follows from a status report.

Keep automation paused unless separately authorized. Publish one concise verified
close-out on #16: what works, broken items, release blockers, next technical action,
owner intervention. Include actual storage delta and preservation, not estimates
presented as reclaimed space. No repeated 12-part reports for unchanged state.
