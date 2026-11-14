# Update and recovery design

Wilsof RC4 is **TEST ONLY**, not an approved production update release.
The tested image and source identities are recorded in
[Getting started](getting-started.md).

The detailed [version-pinned update and recovery design](https://github.com/tomli0/wilsof-os/blob/357b0b09d0333c8875a3d4d4ca8db417343d032e/docs/update-transition.md)
is maintained with the RC4 development source. It documents coherent signed
snapshot transitions, fail-closed boot-artifact checks, and explicit repair.
That engineering document includes historical planning context; consult
[project status #16](https://github.com/tomli0/wilsof-os/issues/16) for the current
acceptance decision.

Publishing the README on `main` does not merge the RC4 OS implementation, approve
production trust, or authorize replacing an existing installation.
