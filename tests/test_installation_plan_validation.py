"""Exercise the installation-plan contract without probing or modifying disks."""

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/installation-plan.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


@pytest.fixture
def plan():
    document = (ROOT / "docs/installer-architecture.md").read_text()
    examples = [
        json.loads(block)
        for block in re.findall(r"```json\n(.*?)\n```", document, re.S)
    ]
    example = next(
        example for example in examples
        if example.get("schema") == "wilsof.install-plan/v1"
    )
    return copy.deepcopy(example)


def test_documented_plan_validates(plan):
    Draft202012Validator.check_schema(SCHEMA)
    VALIDATOR.validate(plan)


@pytest.mark.parametrize("partitions", [
    [], ["ESP"], [None, None], ["root", "ESP"],
    ["ESP", "root", "home"], ["ESP", "home"],
    ["ESP", {"mountpoint": "/"}], [{"name": "ESP"}, "root"],
    ["ESP", "root", None], ["ESP", "root", "root"],
])
def test_rejects_unreviewed_partition_layout(plan, partitions):
    plan["layout"]["partitions"] = partitions
    assert not VALIDATOR.is_valid(plan)


@pytest.mark.parametrize("enabled", [False, True])
def test_accepts_non_secret_encryption_choice(plan, enabled):
    plan["encryption"] = {"enabled": enabled}
    VALIDATOR.validate(plan)


@pytest.mark.parametrize("encryption", [
    {}, {"password": "synthetic-test-value"},
    {"enabled": True, "password": "synthetic-test-value"},
    {"enabled": True, "passphrase": "synthetic-test-value"},
    {"enabled": False, "password": "synthetic-test-value"},
    {"enabled": True, "key_file": "/example/test-key"},
    {"enabled": True, "credentials": {"passphrase": "synthetic-test-value"}},
    {"enabled": True, "options": {}},
    {"enabled": "true"}, {"enabled": 1}, {"enabled": None},
])
def test_rejects_secret_or_malformed_encryption_choice(plan, encryption):
    plan["encryption"] = encryption
    assert not VALIDATOR.is_valid(plan)
