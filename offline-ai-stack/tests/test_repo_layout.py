"""Structural tests: every file referenced by docs/scripts actually exists."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_FILES = [
    "Makefile",
    "README.md",
    "requirements.txt",
    "docker-compose.yml",
    "promptfooconfig.yaml",
    ".woodpecker.yml",
    ".env.example",
    "configs/Caddyfile",
    "configs/prom.yml",
    "configs/vllm-primary.service",
    "configs/vllm-devstral.service",
    "crews/dev_team.py",
    "crews/merge_gate.py",
    "crews/code_review.py",
    "crews/exec_review.py",
    "crews/security_review.py",
    "scripts/ingest.py",
    "scripts/security_scan.sh",
    "scripts/backup.sh",
    "scripts/claude_mem_local.py",
    "scripts/aider-mem",
    "scripts/bring-up.sh",
    "scripts/tear-down.sh",
    "scripts/voice_transcribe.py",
    "scripts/offline-prep.sh",
    "scripts/offline-doctor.sh",
    "scripts/hf-audit.sh",
    "skills/loader.py",
    "templates/PLAN.md",
    "templates/CONVENTIONS.md",
    "templates/adr/0000-template.md",
]

EXECUTABLE_SCRIPTS = [
    "scripts/security_scan.sh",
    "scripts/backup.sh",
    "scripts/aider-mem",
    "scripts/bring-up.sh",
    "scripts/tear-down.sh",
    "scripts/offline-prep.sh",
    "scripts/offline-doctor.sh",
    "scripts/hf-audit.sh",
]


def test_expected_files_present():
    missing = [f for f in EXPECTED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"Missing files: {missing}"


def test_shell_scripts_executable():
    not_exec = [f for f in EXECUTABLE_SCRIPTS if not (ROOT / f).stat().st_mode & 0o111]
    assert not not_exec, f"Not executable: {not_exec}"
