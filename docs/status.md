# Wilsof current-status pointer

The authoritative live project dashboard is
[GitHub issue #16](https://github.com/tomli0/wilsof-os/issues/16).
Do not maintain a second dated project-status narrative here.

- [Issue #60](https://github.com/tomli0/wilsof-os/issues/60): remaining Daily Driver
  defects and acceptance gates.
- [Draft PR #61](https://github.com/tomli0/wilsof-os/pull/61): current private
  integration source delivery, not merge/release approval.
- [Production package-signing gate](package-signing.md),
  [recovery](recovery.md), [physical/Omarchy transition](omarchy-transition.md).
- [Artifact lifecycle and cleanup](artifact-maintenance.md): Hermes-owned sprint
  completion; read-only default, explicit approved deletion only.

Historical implementation and acceptance reports remain in
[development reports](development-reports/), [checkpoints](checkpoints/) and Git
history. A historical PASS applies only to its exact source/artifact/environment;
it does not close a later native, new-image or physical gate.

Not ready for Omarchy replacement. Preserve owner data and protected artifacts;
leave automation paused. No unattended cleanup, privileged build, trust approval,
merge or physical installation follows from a status update.
