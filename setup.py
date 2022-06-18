import re
import sys
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

projectRoot: Path = Path(__file__).parent


# Grab the version number out of src/__init__.py
version: str = ""
with (projectRoot / "src/gwpycore/__init__.py").open("rt") as f:
    try:
        version = re.findall(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]\r?$", f.read(), re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version. __version__ is not defined in __init__.py")

# Grab the required modules out of requirements.txt
with (projectRoot / "requirements.txt").open("rt") as f:
    required = f.read().splitlines()
    required[:] = [line for line in required if not line.startswith("#")]


# class PyTest(TestCommand):
#     user_options = []

#     def run(self):
#         import subprocess
#         import sys

#         errno = subprocess.call([sys.executable, "-m", "pytest", "--cov-report", "html", "--cov-report", "term", "--cov", f"{MODULE}/"])
#         raise SystemExit(errno)


# print(f"projectRoot = {projectRoot}")
# print(f"version = {version}")
# print(f"required = {required}")

if __name__ == "__main__":
    try:
        setup(
            # Most of the settings are in setup.cfg
            version=version,
            # use_scm_version={"version_scheme": "no-guess-dev"}
            install_requires=required,
            # cmdclass=dict(test=PyTest),
            # setup_requires=["wheel"],
            )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
