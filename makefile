# On Windows, make uses the shell specified by the SHELL environment variable if it exists (otherwise the ComSpec envvar)
# ?= means only assign if it doesn't already have a value
VENV_NAME?=.venv
BIN=$(VENV_NAME)\Scripts
LIB=${VENV_NAME}\Lib\site-packages
PYTHON=${VENV_NAME}\Scripts\python
NON_VIRTUAL_PYTHON?=${PY_HOME}\python
# HOST=127.0.0.1
TEST_PATH=.\tests

.PHONY: help clean clean-pyc test examples activate linters requirements dev-env format isort lint
.ONESHELL:

help: # If you just say `make`, then this first target is assumed as the goal
	@type doc_technical\makefile_help.txt

clean: clean-pyc # Deletes all temporary file
	del /Q /F /S build\
	del /Q /F /S dist\
	del /Q /F /S *.pyo
	del /Q /F /S *.egg-info

clean-pyc:
	del /Q /F /S *.pyc > nul

test: clean-pyc | .venv  # Runs all of the unit tests
	${PYTHON} -m pytest --verbose --color=yes $(TEST_PATH)

examples: | .venv # Runs the example code
	${PYTHON} examples\automate_notepad_control_panel.py

.venv: # Installs a virtual environment for this project
	${NON_VIRTUAL_PYTHON} -m pip install --upgrade pip
	${NON_VIRTUAL_PYTHON} -m venv .venv

activate: | .venv # Force activate the virtual environment
	${BIN}\activate.bat

linters: | .venv
	${BIN}\pip install black isort flake8

requirements: | .venv # Ensures that all of the modules required by this project are installed (in the virtual env)
	${BIN}\pip install -r requirements.txt

dev-env: requirements linters # Prepares the development environment -- use only once.

# doc: activate | .venv
#     $(VENV_ACTIVATE) && cd docs; make html

prep: standardize test # Prepares for a possible release
	${BIN}\pip freeze > frozen_requirements.txt
	fc /W requirements.txt frozen_requirements.txt
	# TODO verify the version number

standardize: format isort lint # Apply of the linting tools to all of the .py files

format: | .venv # Re-formats all of the Python code (with black)
	${BIN}\black *.py

isort: | .venv # Cleans up all of the imports (using isort)
	${BIN}\isort *.py

lint: | .venv # Lints code (using flake8)
	${BIN}\flake8 *.py

