# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def minimal_epjson() -> dict[str, Any]:
    """Return a minimal epJSON model with one zone and one detailed surface."""
    return {
        "GlobalGeometryRules": {
            "Rules": {
                "coordinate_system": "Relative",
                "starting_vertex_position": "UpperLeftCorner",
                "vertex_entry_direction": "Clockwise",
            }
        },
        "Zone": {"Test Zone": {}},
        "BuildingSurface:Detailed": {
            "Test Surface": {
                "zone_name": "Test zone",
                "vertices": [
                    {
                        "vertex_x_coordinate": 0.0,
                        "vertex_y_coordinate": 0.0,
                        "vertex_z_coordinate": 0.0,
                    },
                    {
                        "vertex_x_coordinate": 1.0,
                        "vertex_y_coordinate": 0.0,
                        "vertex_z_coordinate": 0.0,
                    },
                    {
                        "vertex_x_coordinate": 1.0,
                        "vertex_y_coordinate": 1.0,
                        "vertex_z_coordinate": 0.0,
                    },
                    {
                        "vertex_x_coordinate": 0.0,
                        "vertex_y_coordinate": 1.0,
                        "vertex_z_coordinate": 0.0,
                    },
                ],
            }
        },
    }
