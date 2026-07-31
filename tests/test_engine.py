# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from typing import Any

import pytest

from energyplus_viewfactors.engine import BadInputFile, ViewFactorEngine


def test_rejects_input_without_global_geometry_rules() -> None:
    with pytest.raises(BadInputFile, match="GlobalGeometryRules"):
        ViewFactorEngine(obj={})


def test_extract_writes_a_vs3_file(tmp_path, minimal_epjson: dict[str, Any]) -> None:
    engine = ViewFactorEngine(obj=minimal_epjson)

    engine.extract(directory=tmp_path)

    output = (tmp_path / "Test Zone.vs3").read_text(encoding="utf-8")
    assert output.startswith("!\t#\tx\ty\tz\t\n")
    assert "V\t1\t0.00\t0.00\t0.00\t\n" in output
    assert "S\t1\t1\t2\t3\t4\t0\t0\t0.5\tTest Surface\t\n" in output


def test_extract_limits_output_to_selected_zones(tmp_path, minimal_epjson: dict[str, Any]) -> None:
    minimal_epjson["Zone"]["Unused Zone"] = {}
    engine = ViewFactorEngine(obj=minimal_epjson)

    engine.extract(directory=tmp_path, zones=["Test Zone"])

    assert (tmp_path / "Test Zone.vs3").is_file()
    assert not (tmp_path / "Unused Zone.vs3").exists()
