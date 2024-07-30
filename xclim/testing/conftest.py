# noqa: D100
# This file is the setup for the doctest suite.
# This must be run using the following commands:
# python -c "from xclim.testing.utils import run_doctests; run_doctests()"

from __future__ import annotations

import os
import shutil
from functools import partial
from pathlib import Path

import pytest

from xclim.testing import helpers
from xclim.testing.utils import _default_cache_dir  # noqa
from xclim.testing.utils import open_dataset as _open_dataset


@pytest.fixture(autouse=True, scope="session")
def threadsafe_data_dir(tmp_path_factory) -> Path:
    """Return a threadsafe temporary directory for storing testing data."""
    yield Path(tmp_path_factory.getbasetemp().joinpath("data"))


@pytest.fixture(scope="session")
def open_dataset(threadsafe_data_dir):
    """Return a function that opens a dataset from the test data directory."""

    def _open_session_scoped_file(
        file: str | os.PathLike, branch: str = helpers.TESTDATA_BRANCH, **xr_kwargs
    ):
        xr_kwargs.setdefault("engine", "h5netcdf")
        return _open_dataset(
            file, cache_dir=threadsafe_data_dir, branch=branch, **xr_kwargs
        )

    return _open_session_scoped_file


@pytest.fixture(autouse=True, scope="session")
def is_matplotlib_installed(xdoctest_namespace) -> None:
    """Skip tests that require matplotlib if it is not installed."""

    def _is_matplotlib_installed():
        try:
            import matplotlib  # noqa

            return
        except ImportError:
            return pytest.skip("This doctest requires matplotlib to be installed.")

    xdoctest_namespace["is_matplotlib_installed"] = _is_matplotlib_installed


@pytest.fixture(autouse=True, scope="session")
def add_doctest_imports(xdoctest_namespace, threadsafe_data_dir) -> None:
    """Gather testing data on doctest run."""
    helpers.testing_setup_warnings()

    shutil.copytree(_default_cache_dir, threadsafe_data_dir, dirs_exist_ok=True)
    helpers.generate_atmos(threadsafe_data_dir)

    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__dict__ = self

    __opener = partial(
        _open_dataset, cache_dir=threadsafe_data_dir, branch=helpers.TESTDATA_BRANCH
    )

    xdoctest_namespace["open_dataset"] = __opener
    xdoctest_namespace["xr"] = AttrDict()
    xdoctest_namespace["xr"].update({"open_dataset": __opener})
    xdoctest_namespace.update(helpers.add_doctest_filepaths())

    helpers.generate_atmos(threadsafe_data_dir)
    xdoctest_namespace.update(helpers.add_example_file_paths(threadsafe_data_dir))
