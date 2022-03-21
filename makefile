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

BROWSER := python make_browse.py


help:
	@if exist makefile_help.txt type makefile_help.txt
	@python make_help.py < makefile

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
#	 ${PYTHON} examples\automate_notepad_control_panel.py

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
#	 $(VENV_ACTIVATE) && cd docs; make html

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

