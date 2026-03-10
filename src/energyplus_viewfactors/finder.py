# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import shutil
from glob import glob
from platform import system

def find_parent_view3d()->str|None:
    if system() == 'Windows':
        install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        exename = 'View3D.exe'
        potential_result = os.path.join(install_dir, 'PreProcess', 'ViewFactorCalculation', exename)
        if os.path.exists(potential_result):
            return potential_result
    return None

def find_any_view3d()->list[str]|None:
    possible_names = ['view3d', 'View3D']
    for possible in possible_names:
        in_path = shutil.which(possible)
        if in_path is not None:
            return [in_path]
    if system() == 'Windows':
        exename = 'View3D.exe'
        places = ['C:\\', 'C:\\Program Files']
    else:
        exename = 'energyplus'
        places = []
    hits = []
    for place in places:
        hits.extend(glob(os.path.join(place,'EnergyPlus*', '**', exename), recursive=True))
    return hits