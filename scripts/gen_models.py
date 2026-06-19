#!/usr/bin/env python
"""Generate the Pydantic models from the vendored OpenAPI spec.

Single source of truth for the codegen command, shared by ``make codegen`` and
the drift test (``tests/test_codegen_drift.py``). Run with ``make codegen``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "openapi.json"
OUTPUT = ROOT / "src" / "tessera" / "_generated" / "models.py"
HEADER = (
    "# AUTO-GENERATED from openapi.json by datamodel-code-generator — "
    "DO NOT EDIT. Run: make codegen"
)


def build_argv(output: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input",
        str(SPEC),
        "--input-file-type",
        "openapi",
        "--output",
        str(output),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--use-annotated",
        "--use-standard-collections",
        "--use-union-operator",
        "--use-schema-description",
        "--field-constraints",
        "--enum-field-as-literal",
        "all",
        "--target-python-version",
        "3.10",
        "--disable-timestamp",
        "--formatters",
        "black",
        "isort",
        "--custom-file-header",
        HEADER,
    ]


def generate(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_argv(output), check=True)


if __name__ == "__main__":
    generate(OUTPUT)
    print(f"wrote {OUTPUT}")
