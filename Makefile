.PHONY: check clean clean-test clean-pyc clean-build docker-build docker-build-latest docker-run docs format help venv
.DEFAULT_GOAL := check

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Docker image name/version information
DOCKER_IMAGE_NAME := syno-cert-decoder
GIT_HASH ?= $(shell git rev-parse --short HEAD)
PKG_VERSION ?= $(shell python3 setup.py --version)
DOCKER_IMAGE_TAG_VERSION := ${PKG_VERSION}
DOCKER_IMAGE_TAG_DEV_VERSION := "${PKG_VERSION}-${GIT_HASH}"

# Setup a venv compatible with VS Code and friends
# source .venv/bin/activate outside of make to use this in a shell
venv:
	# FYI: hardcoding this to python3.9 to match the version installed on my Synology NAS
	python3.9 -mvenv .venv
	.venv/bin/pip install --upgrade pip wheel
	.venv/bin/pip install -r requirements_dev.txt
	.venv/bin/pip install -e .

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint/black: ## check style with black
	black --check syno_cert_decoder tests

lint/pylint: ## check style with pylint
	pylint *.py syno_cert_decoder tests

lint: lint/black ## check style

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source syno_cert_decoder -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/syno_cert_decoder.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ syno_cert_decoder
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

format: ## Format code
	black *.py syno_cert_decoder tests

check: format test lint ## format code and run tests
