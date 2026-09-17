# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
"""Fail fast when a FreshCheck source release is incomplete or contaminated."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "android/app/src/main/assets"
REQUIRED = [
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CODE_OF_CONDUCT.md",
    "THIRD_PARTY_NOTICES.md",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    "android/gradlew",
    "android/gradlew.bat",
    "android/gradle/wrapper/gradle-wrapper.jar",
    "android/gradle/wrapper/gradle-wrapper.properties",
    "android/app/src/main/assets/fruit_model_config.json",
]
CODE_SUFFIXES = {".py", ".kt", ".kts", ".ps1", ".xml", ".yml", ".yaml"}
SKIP_PARTS = {".git", ".gradle", ".kotlin", ".venv", "build", "dist", "__pycache__"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if set(relative.parts) & {".kotlin", ".gradle", "build"}:
            errors.append(f"generated path must not be released: {relative.as_posix()}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in CODE_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if set(relative.parts) & SKIP_PARTS:
            continue
        if "SPDX-License-Identifier: MIT" not in path.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"missing SPDX header: {relative.as_posix()}")

    for config_name in ("published_model_config.json", "fruit_model_config.json"):
        config_path = ASSETS / config_name
        if not config_path.is_file():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("labels") != ["fresh", "suspicious", "spoiled"]:
            errors.append(f"invalid three-label contract: {config_name}")

        model_file = config.get("model_file")
        if not model_file:
            continue

        model_path = ASSETS / str(model_file)
        if not model_path.is_file():
            continue

        if sha256(model_path) != config.get("model_sha256"):
            errors.append(f"model SHA-256 mismatch: {config_name}")

    gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
    if 'versionName = "0.5.1"' not in gradle or 'versionCode = 6' not in gradle:
        errors.append("Android versionName/versionCode is not 0.5.1/6")
    if "org.tensorflow:tensorflow-lite" in gradle:
        errors.append("TensorFlow Lite runtime must not be bundled with the ONNX-only app")
    return sorted(set(errors))


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("FreshCheck release audit: FAIL", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        raise SystemExit(1)
    print("FreshCheck release audit: PASS")
