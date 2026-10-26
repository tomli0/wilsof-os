"""Guard the reviewed-source and post-cleanup build evidence instructions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_preflight_checks_explicit_approved_commit_before_root_build():
    document = (ROOT / "docs/iso.md").read_text()
    check = 'test "$(git rev-parse HEAD)" = "$WILSOF_APPROVED_COMMIT"'
    assert check in document
    assert document.index(check) < document.index("sudo WILSOF_ISO_WORKDIR=")
    assert "independently approved" in document


def test_post_build_validation_does_not_require_removed_work_directory():
    document = (ROOT / "docs/iso.md").read_text()
    checks = document.split("3. After a successful command", 1)[1].split("4. To revert", 1)[0]
    assert "ls -ld /srv/wilsof-iso-out" in checks
    assert "ls -ld /srv/wilsof-iso-work" not in checks
    assert "mkarchiso -r" in checks
