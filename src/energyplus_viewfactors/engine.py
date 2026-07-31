"""Translate EnergyPlus epJSON geometry into View3D .vs3 input files."""

from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import Any, TextIO


class BadInputFile(Exception):
    """Raised when input is not valid EnergyPlus epJSON for this translator."""


class ViewFactorEngine:
    """Load EnergyPlus epJSON data and write one View3D input per selected zone.

    Args:
        obj: EnergyPlus epJSON data as a dictionary.
        fp: A readable text stream containing EnergyPlus epJSON data.
        filename: A path to an EnergyPlus epJSON file.
    """

    def __init__(
        self,
        obj: dict[str, Any] | None = None,
        fp: TextIO | None = None,
        filename: str | PathLike[str] | None = None,
    ):
        if obj is not None:
            self.data = obj
        elif fp is not None:
            self.data = json.load(fp)
        elif filename is not None:
            with Path(filename).open(encoding="utf-8") as input_file:
                self.data = json.load(input_file)
        else:
            self.data = {}

        geometry_rules = self.data.get("GlobalGeometryRules")
        if not geometry_rules:
            source = f'Input file "{filename}"' if filename is not None else "Input data"
            raise BadInputFile(
                f'{source} does not have a "GlobalGeometryRules" object and is not valid '
                "EnergyPlus epJSON."
            )

        global_geometry = next(iter(geometry_rules.values()))
        try:
            self.ccw = global_geometry["vertex_entry_direction"] == "Counterclockwise"
        except KeyError as error:
            source = f'Input file "{filename}"' if filename is not None else "Input data"
            raise BadInputFile(
                f'{source} has a "GlobalGeometryRules" object without a '
                '"vertex_entry_direction" entry.'
            ) from error

        self.zones: dict[str, dict[str, Any]] = self.data.get("Zone", {})
        self.surfaces: dict[str, dict[str, Any]] = dict(
            self.data.get("BuildingSurface:Detailed", {})
        )
        self.subsurfaces: dict[str, dict[str, Any]] = dict(
            self.data.get("FenestrationSurface:Detailed", {})
        )
        self._assign_surfaces()

    def _assign_surfaces(self) -> None:
        """Associate detailed surfaces and subsurfaces with their zones."""
        for zone in self.zones.values():
            zone["Surface"] = []

        lookup = {key.upper() : key for key in self.zones.keys()}
        for name, surface in self.surfaces.items():
            surface["Subsurface"] = []
            surface["Name"] = name
            zone_name = surface["zone_name"]
            self.zones[lookup[zone_name.upper()]]["Surface"].append(surface)

        for name, subsurface in self.subsurfaces.items():
            subsurface["Name"] = name
            surface_name = subsurface["building_surface_name"]
            self.surfaces[surface_name]["Subsurface"].append(subsurface)

    def _reverse_if_needed(self, surface_vertices: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self.ccw:
            surface_vertices.reverse()
        return surface_vertices

    def extract(
        self,
        directory: str | PathLike[str] | None = None,
        zones: list[str] | None = None,
    ) -> None:
        """Write a .vs3 file for every selected zone."""
        surface_numbers: dict[str, int] = {}
        zone_names = list(self.zones) if zones is None else [z for z in zones if z in self.zones]
        output_directory = Path(directory) if directory is not None else Path.cwd()

        for zone_name in zone_names:
            vertices: list[list[Any]] = []
            surfaces: list[list[Any]] = []
            vertex_number = 1
            surface_number = 1

            for surface in self.zones[zone_name]["Surface"]:
                surface_numbers[surface["Name"]] = surface_number
                surface["vertices"] = self._reverse_if_needed(surface["vertices"])
                vertices, surfaces, vertex_number, surface_number = append_vertices(
                    vertices,
                    surface,
                    surface_list=surfaces,
                    vertex_number=vertex_number,
                    surface_number=surface_number,
                )

                for subsurface in surface["Subsurface"]:
                    normalized_subsurface = get_subsurface_vertices(subsurface)
                    normalized_subsurface["vertices"] = self._reverse_if_needed(
                        normalized_subsurface["vertices"]
                    )
                    vertices, surfaces, vertex_number, surface_number = append_vertices(
                        vertices,
                        surface=normalized_subsurface,
                        surface_list=surfaces,
                        supersurface=surface,
                        vertex_number=vertex_number,
                        surface_number=surface_number,
                    )

            for surface in surfaces:
                if surface[6] != 0:
                    surface[6] = surface_numbers[surface[6]]

            self._write_vs3(output_directory / f"{zone_name}.vs3", vertices, surfaces)

    @staticmethod
    def _write_vs3(
        output_path: Path,
        vertices: list[list[Any]],
        surfaces: list[list[Any]],
    ) -> None:
        with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
            vertices.insert(0, ["!", "#", "x", "y", "z"])
            for vertex in vertices:
                output_file.write("".join(f"{value}\t" for value in vertex))
                output_file.write("\n")

            surfaces.insert(0, ["!", "#", "v1", "v2", "v3", "v4", "base", "cmb", "emit", "name"])
            for surface in surfaces:
                output_file.write("".join(f"{value}\t" for value in surface))
                output_file.write("\n")


def format_value(value: Any) -> str:
    """Format a coordinate for View3D output."""
    return f"{float(value):.2f}"


def get_subsurface_vertices(subsurface: dict[str, Any]) -> dict[str, Any]:
    """Normalize epJSON subsurface vertex fields to the surface vertex layout."""
    subsurface["vertices"] = []
    for number in range(1, 10):
        x_name = f"vertex_{number}_x_coordinate"
        if x_name not in subsurface:
            break
        subsurface["vertices"].append(
            {
                x_name: subsurface[x_name],
                f"vertex_{number}_y_coordinate": subsurface[f"vertex_{number}_y_coordinate"],
                f"vertex_{number}_z_coordinate": subsurface[f"vertex_{number}_z_coordinate"],
            }
        )
    return subsurface


def append_vertices(
    vertices_list: list[list[Any]],
    surface: dict[str, Any],
    surface_list: list[list[Any]],
    supersurface: dict[str, Any] | None = None,
    vertex_number: int = 1,
    surface_number: int = 1,
) -> tuple[list[list[Any]], list[list[Any]], int, int]:
    """Append a surface's vertices and View3D surface record to output lists."""
    vertex_references: list[Any] = []
    for vertex in surface["vertices"]:
        output_vertex: list[Any] = list(map(format_value, vertex.values()))
        output_vertex.insert(0, vertex_number)
        output_vertex.insert(0, "V")
        vertices_list.append(output_vertex)
        vertex_references.append(vertex_number)
        vertex_number += 1

    vertex_references.insert(0, surface_number)
    vertex_references.insert(0, "S")
    vertex_references.append(supersurface["Name"] if supersurface is not None else 0)
    vertex_references.append(0)
    vertex_references.append(0.5)
    vertex_references.append(surface["Name"])
    surface_list.append(vertex_references)
    surface_number += 1
    return vertices_list, surface_list, vertex_number, surface_number
