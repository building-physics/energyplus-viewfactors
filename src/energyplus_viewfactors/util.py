# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import contextlib
import tempfile

@contextlib.contextmanager
def managed_directory(run_dir):
    if run_dir is None:
        tmp = tempfile.TemporaryDirectory()
        try:
            yield tmp.name
        finally:
            tmp.cleanup()
    else:
        try:
            yield run_dir
        finally:
            pass