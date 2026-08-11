#!/usr/bin/env python3
"""Zero-dependency test runner used ONLY because this offline sandbox has no
pytest. The canonical suite is pytest (see pyproject.toml [dev]); this runner
executes the exact same test functions with minimal fixture injection so the
slice can be verified without network access. Run `pytest -q` in any normal env.
"""

from __future__ import annotations

import copy
import importlib.util
import inspect
import pathlib
import sys
import tempfile
import traceback

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

# Import the shared base record from tests/conftest.py.
conftest_spec = importlib.util.spec_from_file_location("conftest", ROOT / "tests" / "conftest.py")
conftest = importlib.util.module_from_spec(conftest_spec)
conftest_spec.loader.exec_module(conftest)  # type: ignore[union-attr]


def make_raw_factory():
    def _make(**overrides):
        record = copy.deepcopy(conftest._BASE)
        record.update(overrides)
        return record

    return _make


def provide(param, stack):
    if param == "make_raw":
        return make_raw_factory()
    if param == "tmp_path":
        d = tempfile.mkdtemp()
        stack.append(d)
        return pathlib.Path(d)
    raise KeyError(f"unknown fixture: {param}")


def main() -> int:
    passed = failed = 0
    failures = []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        for name, fn in sorted(vars(module).items()):
            if not (name.startswith("test_") and inspect.isfunction(fn)):
                continue
            params = list(inspect.signature(fn).parameters)
            stack: list[str] = []
            try:
                fn(**{p: provide(p, stack) for p in params})
                passed += 1
                print(f"PASS {path.name}::{name}")
            except Exception:  # noqa: BLE001
                failed += 1
                failures.append((path.name, name, traceback.format_exc()))
                print(f"FAIL {path.name}::{name}")
    print(f"\n{passed} passed, {failed} failed")
    for fname, tname, tb in failures:
        print(f"\n----- {fname}::{tname} -----\n{tb}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
