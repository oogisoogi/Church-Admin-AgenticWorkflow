#!/usr/bin/env python3
"""
P1 Hallucination Prevention — Finance Safety Validator (FS1-FS3)

Converts "triple-declared" finance autopilot prohibition into
"triple-verified" by checking all three enforcement points programmatically.

Rules:
  FS1: state.yaml config.autopilot.finance_override must be false
  FS2: finance-recorder.md must contain autopilot prohibition text
  FS3: monthly-finance-report.md must contain HitL/human confirmation steps

Usage:
    python3 scripts/validate_finance_safety.py [--project-dir .]

Output: JSON to stdout
Exit codes: 0 = completed (check 'valid' field), 1 = fatal error.
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print(json.dumps({"valid": False, "error": "PyYAML not installed"}))
    sys.exit(0)


def _read_file(path: str) -> str:
    """Read file content, return empty string on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, IOError):
        return ""


def _load_yaml(path: str):
    """Load YAML file, return None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f.read())
    except Exception:
        return None


# Patterns that indicate autopilot prohibition
_AUTOPILOT_PROHIBITION_RE = [
    re.compile(r"(?i)permanently\s+disabled"),
    re.compile(r"(?i)autopilot.*disabled"),
    re.compile(r"(?i)never\s+operates?\s+under\s+autopilot"),
    re.compile(r"autopilot.*금지"),
]

# Patterns that indicate HitL/human confirmation
_HITL_RE = [
    re.compile(r"(?i)human\s+(?:review|confirmation|approval)"),
    re.compile(r"(?i)HitL"),
    re.compile(r"\(human\)"),
]


# ---------------------------------------------------------------------------
# FS1: state.yaml finance override
# ---------------------------------------------------------------------------

def check_fs1(project_dir: str) -> dict:
    """FS1: state.yaml config.autopilot.finance_override must be false."""
    errors = []

    state = _load_yaml(os.path.join(project_dir, "state.yaml"))
    if not state:
        return {
            "rule": "FS1", "name": "State YAML Finance Override",
            "passed": False, "errors": ["state.yaml not found or invalid"],
        }

    config = state.get("church", {}).get("config", {})
    autopilot = config.get("autopilot", {})
    finance_override = autopilot.get("finance_override")

    if finance_override is None:
        errors.append(
            "state.yaml missing config.autopilot.finance_override field"
        )
    elif finance_override is not False:
        errors.append(
            f"CRITICAL: finance_override is {finance_override!r} — must be "
            "false. Financial data without human review is prohibited."
        )

    return {
        "rule": "FS1",
        "name": "State YAML Finance Override",
        "passed": len(errors) == 0,
        "value": finance_override,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# FS2: Agent spec autopilot prohibition
# ---------------------------------------------------------------------------

def check_fs2(project_dir: str) -> dict:
    """FS2: finance-recorder.md must contain autopilot prohibition text."""
    errors = []

    agent_path = os.path.join(
        project_dir, ".claude/agents/finance-recorder.md"
    )
    content = _read_file(agent_path)

    if not content:
        return {
            "rule": "FS2", "name": "Agent Spec Autopilot Prohibition",
            "passed": False, "errors": ["finance-recorder.md not found"],
        }

    matched = [p.pattern for p in _AUTOPILOT_PROHIBITION_RE if p.search(content)]

    if not matched:
        errors.append(
            "finance-recorder.md does not contain any autopilot prohibition "
            "text (e.g., 'permanently disabled', 'autopilot 금지')"
        )

    return {
        "rule": "FS2",
        "name": "Agent Spec Autopilot Prohibition",
        "passed": len(errors) == 0,
        "matched_patterns": matched,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# FS3: Workflow HitL steps
# ---------------------------------------------------------------------------

def check_fs3(project_dir: str) -> dict:
    """FS3: monthly-finance-report.md must contain HitL/human confirmation."""
    errors = []

    workflow_path = os.path.join(
        project_dir, "workflows/monthly-finance-report.md"
    )
    content = _read_file(workflow_path)

    if not content:
        return {
            "rule": "FS3", "name": "Workflow HitL Steps",
            "passed": False,
            "errors": ["monthly-finance-report.md not found"],
        }

    hitl_count = sum(1 for p in _HITL_RE for _ in p.findall(content))

    if hitl_count == 0:
        errors.append(
            "monthly-finance-report.md has no HitL/human confirmation "
            "patterns — all finance outputs require human approval"
        )

    # Count explicit (human) step markers
    human_steps = len(re.findall(r"\(human\)", content))
    if human_steps == 0:
        errors.append(
            "monthly-finance-report.md has 0 (human) steps — "
            "finance workflow must have explicit human approval gates"
        )

    return {
        "rule": "FS3",
        "name": "Workflow HitL Steps",
        "passed": len(errors) == 0,
        "hitl_matches": hitl_count,
        "human_steps": human_steps,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_checks(project_dir: str) -> dict:
    """Run all FS1-FS3 checks and return structured result."""
    checks = [
        check_fs1(project_dir),
        check_fs2(project_dir),
        check_fs3(project_dir),
    ]

    all_passed = all(c["passed"] for c in checks)

    return {
        "validator": "validate_finance_safety",
        "valid": all_passed,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": sum(1 for c in checks if c["passed"]),
            "failed": sum(1 for c in checks if not c["passed"]),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="P1 Finance Safety Validator (FS1-FS3)"
    )
    parser.add_argument(
        "--project-dir", default=".",
        help="Church-admin project directory (default: current dir)",
    )
    args = parser.parse_args()

    output = run_all_checks(args.project_dir)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(json.dumps({"valid": False, "error": str(e)}))
        sys.exit(1)
