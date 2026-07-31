# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

from importlib import resources
from importlib.metadata import entry_points, metadata, version

from energyplus_viewfactors.__about__ import __version__


def test_version_matches_distribution_metadata():
    assert __version__ == version("energyplus-viewfactors")


def test_distribution_metadata():
    package_metadata = metadata("energyplus-viewfactors")

    assert package_metadata["Name"] == "energyplus-viewfactors"
    assert package_metadata["Requires-Python"] == ">=3.10"


def test_console_entry_point_is_loadable():
    scripts = {
        entry_point.name: entry_point for entry_point in entry_points(group="console_scripts")
    }

    entry_point = scripts["energyplus-viewfactors"]
    assert entry_point.value == "energyplus_viewfactors.cli:energyplus_viewfactors"
    assert callable(entry_point.load())


def test_gui_entry_point_is_loadable():
    scripts = {entry_point.name: entry_point for entry_point in entry_points(group="gui_scripts")}

    entry_point = scripts["epvf"]
    assert entry_point.value == "energyplus_viewfactors.gui:epvf"
    assert callable(entry_point.load())


def test_packaged_icons_are_available():
    data = resources.files("energyplus_viewfactors.data")

    for filename in ("eplus.ico", "eplus256.png", "ep.icns"):
        resource = data.joinpath(filename)
        assert resource.is_file()
        assert resource.read_bytes()
