# energyplus-viewfactors

[![PyPI - Version](https://img.shields.io/pypi/v/energyplus-viewfactors.svg)](https://pypi.org/project/energyplus-viewfactors)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/energyplus-viewfactors.svg)](https://pypi.org/project/energyplus-viewfactors)

-----

## Table of Contents

[Installation](#installation)
[Command-Line Usage](#command-line-usage)
[Development](#development)
[License](#license)

`energyplus-viewfactors` translates geometry from an EnergyPlus epJSON input file
into `.vs3` input files for the View3D program.

## Installation

Python 3.10 or newer is required.

```console
pip install energyplus-viewfactors
```

## Command-Line Usage

Create `.vs3` files for all zones:

```console
energyplus-viewfactors extract model.epJSON --output view3d
```

Create a file for one or more selected zones:

```console
energyplus-viewfactors extract model.epJSON --output view3d \
  --zone "Zone One" --zone "Zone Two"
```

The output directory must already exist.

## Development

Install the development tools:

```console
python -m pip install hatch
```

Hatch creates and manages the development environment from `pyproject.toml`.
Run the project checks through that environment:

```console
hatch run lint
hatch run types
hatch run test
hatch build
```

## License

`energyplus-viewfactors` is distributed under the terms of the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) license.
