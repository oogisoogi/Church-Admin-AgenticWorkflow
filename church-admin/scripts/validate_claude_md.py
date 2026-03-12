#!/usr/bin/env python3
"""
P1 Hallucination Prevention — CLAUDE.md Factual Accuracy Validator (CM1-CM6)

Validates that hardcoded numbers and cross-references in CLAUDE.md
match the actual codebase. Prevents documentation drift from becoming
a systemic hallucination amplifier (CLAUDE.md is loaded into every agent's context).

Rules:
  CM1: Pattern count — SKILL.md table rows == CLAUDE.md claimed count
  CM2: Rule count — validate_*.py rule IDs == CLAUDE.md claimed count
  CM3: Agent count — .claude/agents/*.md files == CLAUDE.md Agent Roster rows
  CM4: Sole-Writer Map — guard_data_files.py SOLE_WRITER_MAP == CLAUDE.md table
  CM5: Data paths — state.yaml data_paths files exist on disk
  CM6: Finance override — state.yaml finance_override is false

Usage:
    python3 scripts/validate_claude_md.py [--project-dir .]

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


# ---------------------------------------------------------------------------
# CM1: Pattern count
# ---------------------------------------------------------------------------

def check_cm1(project_dir: str) -> dict:
    """CM1: SKILL.md intent-mapping table rows == CLAUDE.md claimed pattern count."""
    errors = []

    # Count actual patterns in SKILL.md
    skill_path = os.path.join(
        project_dir, ".claude/skills/church-admin/SKILL.md"
    )
    skill_content = _read_file(skill_path)
    if not skill_content:
        return {
            "rule": "CM1", "name": "Pattern Count",
            "passed": False, "errors": ["SKILL.md not found"],
        }

    # Count table rows that start with | " (Korean command pattern rows)
    # Skip header rows (| Korean Command Pattern) and separator rows (|---)
    pattern_rows = 0
    for line in skill_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith('| "') and "|" in stripped[3:]:
            pattern_rows += 1

    # Extract claimed count from CLAUDE.md
    claude_path = os.path.join(project_dir, "CLAUDE.md")
    claude_content = _read_file(claude_path)
    if not claude_content:
        return {
            "rule": "CM1", "name": "Pattern Count",
            "passed": False, "errors": ["CLAUDE.md not found"],
        }

    claimed_match = re.search(
        r"(\d+)\s+Korean\s+command\s+patterns", claude_content
    )
    claimed_count = int(claimed_match.group(1)) if claimed_match else None

    if claimed_count is None:
        errors.append(
            "CLAUDE.md does not contain 'N Korean command patterns' text"
        )
    elif claimed_count != pattern_rows:
        errors.append(
            f"CLAUDE.md claims {claimed_count} patterns but "
            f"SKILL.md has {pattern_rows} table rows"
        )

    return {
        "rule": "CM1",
        "name": "Pattern Count",
        "passed": len(errors) == 0,
        "actual": pattern_rows,
        "claimed": claimed_count,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CM2: Validation rule count
# ---------------------------------------------------------------------------

def check_cm2(project_dir: str) -> dict:
    """CM2: Sum of rule IDs across 5 validator scripts == CLAUDE.md claimed count."""
    errors = []

    validators = {
        "validate_members.py": r"M\d+",
        "validate_finance.py": r"F\d+",
        "validate_schedule.py": r"S\d+",
        "validate_newcomers.py": r"N\d+",
        "validate_bulletin.py": r"B\d+",
    }

    total_rules = 0
    rule_details = {}
    hooks_dir = os.path.join(project_dir, ".claude/hooks/scripts")

    for script, rule_pattern in validators.items():
        script_path = os.path.join(hooks_dir, script)
        content = _read_file(script_path)
        if not content:
            errors.append(f"{script} not found")
            continue

        # Extract rule IDs from the docstring (lines like "  M1: ...")
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if not docstring_match:
            errors.append(f"{script} has no docstring to extract rules from")
            continue

        docstring = docstring_match.group(1)
        rule_ids = sorted(set(re.findall(rf"({rule_pattern}):", docstring)))
        rule_details[script] = rule_ids
        total_rules += len(rule_ids)

    # Extract claimed count from CLAUDE.md
    claude_path = os.path.join(project_dir, "CLAUDE.md")
    claude_content = _read_file(claude_path)

    claimed_match = re.search(
        r"(\d+)\s+deterministic\s+validation\s+rules", claude_content
    )
    claimed_count = int(claimed_match.group(1)) if claimed_match else None

    if claimed_count is None:
        errors.append(
            "CLAUDE.md does not contain 'N deterministic validation rules' text"
        )
    elif claimed_count != total_rules:
        errors.append(
            f"CLAUDE.md claims {claimed_count} rules but "
            f"validators define {total_rules}"
        )

    return {
        "rule": "CM2",
        "name": "Validation Rule Count",
        "passed": len(errors) == 0,
        "actual": total_rules,
        "claimed": claimed_count,
        "details": rule_details,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CM3: Agent count
# ---------------------------------------------------------------------------

def check_cm3(project_dir: str) -> dict:
    """CM3: .claude/agents/*.md files match CLAUDE.md Agent Roster table rows."""
    errors = []

    agents_dir = os.path.join(project_dir, ".claude/agents")
    if not os.path.isdir(agents_dir):
        return {
            "rule": "CM3", "name": "Agent Count",
            "passed": False, "errors": [".claude/agents/ directory not found"],
        }

    actual_agents = sorted(
        f for f in os.listdir(agents_dir) if f.endswith(".md")
    )
    actual_basenames = [f.replace(".md", "") for f in actual_agents]

    # Parse CLAUDE.md Agent Roster section
    claude_path = os.path.join(project_dir, "CLAUDE.md")
    claude_content = _read_file(claude_path)

    in_roster = False
    roster_names = []
    for line in claude_content.split("\n"):
        if "### Agent Roster" in line:
            in_roster = True
            continue
        if in_roster and line.startswith("###"):
            break
        if in_roster:
            m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
            if m:
                roster_names.append(m.group(1))

    if set(actual_basenames) != set(roster_names):
        missing_from_roster = sorted(set(actual_basenames) - set(roster_names))
        extra_in_roster = sorted(set(roster_names) - set(actual_basenames))
        if missing_from_roster:
            errors.append(
                f"Agents in .claude/agents/ but not in Roster: {missing_from_roster}"
            )
        if extra_in_roster:
            errors.append(
                f"Agents in Roster but not in .claude/agents/: {extra_in_roster}"
            )

    return {
        "rule": "CM3",
        "name": "Agent Count",
        "passed": len(errors) == 0,
        "actual_count": len(actual_agents),
        "roster_count": len(roster_names),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CM4: Sole-Writer Map consistency
# ---------------------------------------------------------------------------

def check_cm4(project_dir: str) -> dict:
    """CM4: guard_data_files.py SOLE_WRITER_MAP matches CLAUDE.md table."""
    errors = []

    guard_path = os.path.join(
        project_dir, ".claude/hooks/scripts/guard_data_files.py"
    )
    guard_content = _read_file(guard_path)
    if not guard_content:
        return {
            "rule": "CM4", "name": "Sole-Writer Map",
            "passed": False, "errors": ["guard_data_files.py not found"],
        }

    # Extract SOLE_WRITER_MAP entries: "filename.yaml": "agent-name"
    guard_entries = dict(
        re.findall(r'"([^"]+\.yaml)"\s*:\s*"([^"]+)"', guard_content)
    )

    # Extract CLAUDE.md Sole-Writer Map table
    claude_path = os.path.join(project_dir, "CLAUDE.md")
    claude_content = _read_file(claude_path)

    in_sw_table = False
    claude_entries = {}
    for line in claude_content.split("\n"):
        if "### Data File Sole-Writer Map" in line:
            in_sw_table = True
            continue
        if in_sw_table and line.startswith("###"):
            break
        if in_sw_table:
            m = re.match(r"^\|\s*`data/([^`]+)`\s*\|\s*`([^`]+)`\s*\|", line)
            if m:
                claude_entries[m.group(1)] = m.group(2)

    # Compare guard → CLAUDE.md
    for fname, agent in guard_entries.items():
        if fname not in claude_entries:
            errors.append(
                f"guard_data_files.py has {fname} → {agent}, "
                "but not in CLAUDE.md table"
            )
        elif claude_entries[fname] != agent:
            errors.append(
                f"{fname}: guard says '{agent}' but "
                f"CLAUDE.md says '{claude_entries[fname]}'"
            )

    # Compare CLAUDE.md → guard (skip church-glossary.yaml — ANY agent)
    for fname, agent in claude_entries.items():
        if fname != "church-glossary.yaml" and fname not in guard_entries:
            errors.append(
                f"CLAUDE.md has {fname} → {agent}, "
                "but not in guard_data_files.py"
            )

    return {
        "rule": "CM4",
        "name": "Sole-Writer Map Consistency",
        "passed": len(errors) == 0,
        "guard_entries": guard_entries,
        "claude_entries": claude_entries,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CM5: Data paths existence
# ---------------------------------------------------------------------------

def check_cm5(project_dir: str) -> dict:
    """CM5: state.yaml data_paths all point to existing files."""
    errors = []

    state = _load_yaml(os.path.join(project_dir, "state.yaml"))
    if not state:
        return {
            "rule": "CM5", "name": "Data Paths",
            "passed": False, "errors": ["state.yaml not found or invalid"],
        }

    data_paths = state.get("church", {}).get("data_paths", {})
    if not data_paths:
        errors.append("state.yaml missing church.data_paths")

    for key, path in data_paths.items():
        full_path = os.path.join(project_dir, path)
        if not os.path.isfile(full_path):
            errors.append(f"data_paths.{key} → {path} does not exist on disk")

    return {
        "rule": "CM5",
        "name": "Data Paths Existence",
        "passed": len(errors) == 0,
        "data_paths": dict(data_paths) if data_paths else {},
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CM6: Finance override safety
# ---------------------------------------------------------------------------

def check_cm6(project_dir: str) -> dict:
    """CM6: state.yaml finance_override must be false."""
    errors = []

    state = _load_yaml(os.path.join(project_dir, "state.yaml"))
    if not state:
        return {
            "rule": "CM6", "name": "Finance Override",
            "passed": False, "errors": ["state.yaml not found or invalid"],
        }

    config = state.get("church", {}).get("config", {})
    autopilot = config.get("autopilot", {})
    finance_override = autopilot.get("finance_override")

    if finance_override is None:
        errors.append("state.yaml missing config.autopilot.finance_override")
    elif finance_override is not False:
        errors.append(
            f"CRITICAL: config.autopilot.finance_override is "
            f"{finance_override!r}, must be false"
        )

    return {
        "rule": "CM6",
        "name": "Finance Override Safety",
        "passed": len(errors) == 0,
        "finance_override": finance_override,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_checks(project_dir: str) -> dict:
    """Run all CM1-CM6 checks and return structured result."""
    checks = [
        check_cm1(project_dir),
        check_cm2(project_dir),
        check_cm3(project_dir),
        check_cm4(project_dir),
        check_cm5(project_dir),
        check_cm6(project_dir),
    ]

    all_passed = all(c["passed"] for c in checks)

    return {
        "validator": "validate_claude_md",
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
        description="P1 CLAUDE.md Factual Accuracy Validator (CM1-CM6)"
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
