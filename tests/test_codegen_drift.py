"""Guard: the committed generated models must match a fresh generation.

Fails if someone edited ``_generated/models.py`` by hand or forgot to run
``make codegen`` after the spec changed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from gen_models import OUTPUT, generate


def test_generated_models_match_spec(tmp_path: Path) -> None:
    fresh = tmp_path / "models.py"
    generate(fresh)
    expected = fresh.read_text()
    actual = OUTPUT.read_text()
    if actual != expected:
        pytest.fail(
            "src/tessera/_generated/models.py is out of date with openapi.json. "
            "Run `make codegen` and commit the result."
        )
