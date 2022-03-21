# On Windows, make uses the shell specified by the SHELL environment variable if it exists (otherwise the ComSpec envvar)
# ?= means only assign if it doesn't already have a value
VENV_NAME?=.venv
BIN=$(VENV_NAME)\Scripts
LIB=${VENV_NAME}\Lib\site-packages
PYTHON=${VENV_NAME}\Scripts\python
NON_VIRTUAL_PYTHON?=${PY_HOME}\python
TEST_PATH=.\tests

.PHONY: help clean clean-pyc test examples activate lint requirements dev-env lint/black lint/isort lint/flake8 dist pip
# Use a single shell-out to run all of the commands, instead of one at a time
.ONESHELL:
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
# Scan thru a Makefile (e.g. this file), looking for target definitions that have a special trailing comment
# (one that starts with two #'s), and consider that comment to be the help text.
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"


help:
    @if exist makefile_help.txt type makefile_help.txt
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST) # MAKEFILE_LIST names this file itself, plus any include files

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rmdir /S /Q build
	rmdir /S /Q dist
	del /Q /F /S *.pyo
	del /Q /F /S *.egg-info

clean-pyc: ## remove Python file artifacts
	del /Q /F /S *.pyc > nul
	del /Q /F /S *.pyo > nul
	del /Q /F /S *~ > nul
	rmdir /S /Q __pycache__
clean-test: ## remove test and coverage artifacts
	del /Q /F /S .tox/ > nul
	del /Q /F /S .coverage > nul
	rmdir /S /Q htmlcov
	del /Q /F /S .pytest_cache > nul

# Ignore these here, but not in .flake8...
# E301 = expected 1 blank line, found 0
# F841 = variable defined but never used
# E722 = do not use bare 'except'
lint/flake8: | .venv  ## check style with flake8 (being a little lenient with a work-in-progress)
	${BIN}\flake8 --max-line-length=256 --extend-ignore=W191,W391,E203,E265,F841,E722,E301 --extend-exclude=.venv,.pytest_cache,.vscode,doc,doc_technical,*.egg-info src tests

lint/black: | .venv ## re-format all of the Python code (with black)
	${BIN}\black -l 256 src tests

lint/isort: | .venv ## clean up all of the imports (using isort)
	${BIN}\isort src tests

lint: lint/flake8 lint/black lint/isort ## apply of the linting tools to all of the .py files

test: clean-pyc | .venv  ## run all of the unit tests
	${PYTHON} -m pytest --verbose --color=yes $(TEST_PATH)

# examples: | .venv ## run the example code
# 	${PYTHON} examples\automate_notepad_control_panel.py

coverage: ## check code coverage quickly with the default Python
	coverage run --source src -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.venv: ## install a virtual environment for this project
	${NON_VIRTUAL_PYTHON} -m pip install --upgrade pip
	${NON_VIRTUAL_PYTHON} -m pip install virtualenv
	${NON_VIRTUAL_PYTHON} -m virtualenv .venv

activate: | .venv ## force activate the virtual environment
	${BIN}\activate.bat

requirements: | .venv ## ensure that all of the modules required by this project are installed (in the virtual env)
	${BIN}\pip install -r requirements.txt
	${BIN}\pip install -r requirements_dev.txt

dev-env: requirements ## prepare the development environment (virtual environment with the required packages)

# doc: activate | .venv
#     $(VENV_ACTIVATE) && cd docs; make html

freeze: lint ## prepare for a possible release by creating frozen_requirements.txt to compare against requirements.txt
	${BIN}\pip freeze > frozen_requirements.txt
	fc /W requirements.txt frozen_requirements.txt
	# TODO verify the version number

# dist:   ##  build a distributable .EXE
#	if exist .\dist\journaltools rmdir /S /Q .\dist\journaltools
#	pyinstaller --clean --debug all --log-level=DEBUG journaltools.spec 2> build.log
#	touch .\dist\journaltools\first_time_install.txt
#	"C:\Program Files\7-Zip\7z.exe" a -sfx .\dist\journaltools_install_here .\dist\*

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## build source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	dir dist

install: clean ## install the package to the active Python's site-packages
	${NON_VIRTUAL_PYTHON} -m setup.py install

