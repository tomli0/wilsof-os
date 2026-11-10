import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "installer-architecture.md"
PLAN_SCHEMA = ROOT / "schemas" / "installation-plan.schema.json"


def test_installation_plan_schema_keeps_blank_default_and_explicit_replacement_boundary():
    schema = json.loads(PLAN_SCHEMA.read_text(encoding="utf-8"))
    props = schema["properties"]
    assert props["schema"]["const"] == "wilsof.install-plan/v1"
    # Authorized replacement supersedes the old unconditional blank-only rule;
    # absence of the explicit mode must still require an empty target.
    conditional = schema['allOf'][0]
    assert conditional['if']['required'] == ['installation_mode']
    assert conditional['else']['properties']['target']['properties']['expected_empty']['const'] is True
    assert conditional['then']['properties']['target']['properties']['expected_empty']['const'] is False
    assert conditional['then']['properties']['target']['required'] == ['existing']
    assert props["layout"]["properties"]["mode"]["const"] == "whole-disk"
    assert props["layout"]["properties"]["table"]["const"] == "gpt"
    assert props["layout"]["properties"]["firmware"]["const"] == "uefi"
    assert props["account"]["properties"]["password_in_plan"]["const"] is False
    assert props["executor"]["properties"]["adapter"]["const"] == "archinstall"


def test_architecture_records_required_unknown_and_revalidation_states():
    content = DOC.read_text(encoding="utf-8")
    for required in (
        "unknown never becomes a fabricated supported profile",
        "immediately before any future destructive operation",
        "Install recommended drivers",
        "Codecs are a separate, unchecked option",
        "Whole-disk installation erases all data, including Windows",
        "2014 Intel MacBook",
        "destructive, VM-113-specific prototype",
    ):
        assert required in content
