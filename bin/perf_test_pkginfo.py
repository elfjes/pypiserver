import itertools
import shutil
import tempfile
import time
from pathlib import Path
import string

import webtest

TMPDIR = Path(tempfile.gettempdir())
ROOT = TMPDIR / "pypiserver-benchmark"


iter_package_names = (
    "".join(n)
    for n in itertools.combinations_with_replacement(string.ascii_lowercase, 8)
)


def random_package(root: Path):
    pkg = root / (next(iter_package_names) + ".zip")
    pkg.touch(exist_ok=True)
    return pkg


def initialize_root(root: Path, num_packages=10):
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()

    for _ in range(num_packages):
        random_package(root)


def create_server(root: Path):
    from pypiserver import app

    app = app(
        roots=[root],
        authenticate=[],
        password_file=".",
        backend_arg="simple-dir",
        hash_algo=None,
    )
    return webtest.TestApp(app)


def bench(server: webtest.TestApp, debug=False):
    t0 = time.time()
    resp = server.get("/packages/")
    if debug:
        print(str(resp))
    return time.time() - t0


def main():
    n = 10000
    print("Setting up")
    initialize_root(ROOT, num_packages=n)
    server = create_server(ROOT)
    print("Running benchmark")
    print(f"listed {n} packages in {bench(server):.3f} seconds")


if __name__ == "__main__":
    main()
