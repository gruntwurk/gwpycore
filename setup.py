import re
import sys
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

MODULE = "gwpycore"
NAME = "GruntWurk Core for Python"

if sys.version_info < (3, 6,):
    raise RuntimeError(f"{NAME} requires Python 3.6.0+")

projectRoot: Path = Path(__file__).parent

version: str = ""
with (projectRoot / MODULE / "__init__.py").open("rt") as f:
    try:
        version = re.findall(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]\r?$", f.read(), re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version. __version__ is not defined in __init__.py")


with (projectRoot / "requirements.txt").open("rt") as f:
    required = f.read().splitlines()
    required[:] = [line for line in required if not line.startswith("#")]

desc_file = ""
long_description = ""
try:
    desc_file = sorted(projectRoot.glob("DESCRIPTION.*"))[0]
    with Path(desc_file).open("rt") as f:
        long_description = f.read()
except:
    pass


class PyTest(TestCommand):
    user_options = []

    def run(self):
        import subprocess
        import sys

        errno = subprocess.call([sys.executable, "-m", "pytest", "--cov-report", "html", "--cov-report", "term", "--cov", f"{MODULE}/"])
        raise SystemExit(errno)


# print(f"projectRoot = {projectRoot}")
# print(f"version = {version}")
# print(f"required = {required}")
# print(f"desc_file = {desc_file}")
# print(f"long_description = {long_description}")

setup(
    name=MODULE,
    version=version,
    install_requires=required,
    url="https://github.com/code-jacked/gwpycore",
    license="BSD",
    author="Craig Jones",
    author_email="craig@k6nnl.com",
    packages=find_packages(MODULE, exclude=["tests", "doc", "doc_technical"]),
    include_package_data=True,
    description=f"{NAME}: Just another Python project framework.",
    long_description=long_description,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    cmdclass=dict(test=PyTest),
    setup_requires=["wheel"],
    entry_points={"console_scripts": ["install_font=gwpycore.gw_fonts:do_install", "font_exists=gwpycore.gw_fonts:do_font_exists",],},
)
