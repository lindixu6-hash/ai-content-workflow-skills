#!/usr/bin/env python3
"""Validate the bundled Content OS pipeline and Skill references."""

import argparse
import json
import re
from pathlib import Path


EXPECTED_STAGES = [
    ("seed", "播种（输入）", "xhs-post-writer"),
    ("sprout", "发芽", "xhs-post-writer"),
    ("grow", "成长（给初稿）", "xhs-post-writer"),
    ("trim", "修剪", "dbs-content"),
]

BUNDLED_SKILLS = {
    "content-os-pipeline": "skills/content-os-pipeline/SKILL.md",
    "xhs-post-writer": "skills/xhs-post-writer/SKILL.md",
    "xiaohongshu-viral-director": (
        "skills/xiaohongshu-viral-director/SKILL.md"
    ),
}

REQUIRED_REFERENCES = [
    "skills/xhs-post-writer/references/writing_methodology.md",
    "skills/xhs-post-writer/references/writing_quality_benchmarks.md",
    (
        "skills/xiaohongshu-viral-director/"
        "references/lv-bai-xhs-benchmark.md"
    ),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate pipeline.json and bundled Skill dependencies."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of tools/.",
    )
    return parser.parse_args()


def frontmatter_name(path):
    content = path.read_text(encoding="utf-8")
    match = re.search(r'^name:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
    return match.group(1).strip() if match else None


def main():
    args = parse_args()
    root = args.root.resolve()
    errors = []
    manifest_path = root / "pipeline.json"

    if not manifest_path.is_file():
        raise SystemExit(f"Missing pipeline manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = manifest.get("stages", [])
    actual_stages = [
        (item.get("id"), item.get("label"), item.get("executor"))
        for item in stages
    ]
    if actual_stages != EXPECTED_STAGES:
        errors.append(
            f"stage order mismatch: {actual_stages!r} != {EXPECTED_STAGES!r}"
        )

    for expected_name, relative_path in BUNDLED_SKILLS.items():
        skill_path = root / relative_path
        if not skill_path.is_file():
            errors.append(f"missing bundled Skill: {relative_path}")
            continue
        actual_name = frontmatter_name(skill_path)
        if actual_name != expected_name:
            errors.append(
                f"{relative_path} declares {actual_name!r}, "
                f"expected {expected_name!r}"
            )

    for relative_path in REQUIRED_REFERENCES:
        if not (root / relative_path).is_file():
            errors.append(f"missing reference: {relative_path}")

    external = manifest.get("dependencies", {}).get("external", [])
    dbs_dependency = next(
        (item for item in external if item.get("name") == "dbs-content"),
        None,
    )
    if not dbs_dependency or not dbs_dependency.get("install"):
        errors.append("dbs-content external dependency is not installable")

    result = {
        "root": str(root),
        "version": manifest.get("version"),
        "stages": [item[1] for item in actual_stages],
        "bundledSkills": sorted(BUNDLED_SKILLS),
        "externalSkills": [
            item.get("name") for item in external if item.get("name")
        ],
        "ok": not errors,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
