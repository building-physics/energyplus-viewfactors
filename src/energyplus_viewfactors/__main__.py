# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import sys

if __name__ == "__main__":
    from energyplus_viewfactors.cli import energyplus_viewfactors

    sys.exit(energyplus_viewfactors())
