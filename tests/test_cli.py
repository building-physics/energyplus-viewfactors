# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import json
from typing import Any

from click.testing import CliRunner

from energyplus_viewfactors.cli import energyplus_viewfactors


def test_extract_runs(tmp_path, minimal_epjson: dict[str, Any]) -> None:
    input_path = tmp_path / "model.epJSON"
    input_path.write_text(json.dumps(minimal_epjson), encoding="utf-8")
    output_path = tmp_path / "output"
    output_path.mkdir()

    result = CliRunner().invoke(
        energyplus_viewfactors,
        ["extract", str(input_path), "--output", str(output_path)],
    )

    assert result.exit_code == 0, result.output
    assert (output_path / "Test Zone.vs3").is_file()


def test_extract_reports_selected_zones(tmp_path, minimal_epjson: dict[str, Any]) -> None:
    input_path = tmp_path / "model.epJSON"
    input_path.write_text(json.dumps(minimal_epjson), encoding="utf-8")
    output_path = tmp_path / "output"
    output_path.mkdir()

    result = CliRunner().invoke(
        energyplus_viewfactors,
        [
            "extract",
            str(input_path),
            "--output",
            str(output_path),
            "--zone",
            "Test Zone",
            "--verbose",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Zones to process: Test Zone" in result.output
