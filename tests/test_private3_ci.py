"""The active approved delivery branch must receive exact-head push CI."""
from pathlib import Path
import re


def test_private3_delivery_push_runs_existing_validation():
    workflow = Path(__file__).resolve().parents[1] / '.github/workflows/validate.yml'
    content = workflow.read_text()
    match = re.search(r'push:\n\s+branches: \[([^\]]+)\]', content)
    assert match is not None
    assert 'integration/private3-20261107' in [s.strip() for s in match.group(1).split(',')]
    assert 'python -m pytest -q' in content
    assert 'contents: read' in content
