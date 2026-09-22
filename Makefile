.PHONY: all install test lint clean build serve publish

all: test

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	# Install ruff and mypy if not present: pip install ruff mypy
	ruff check .
	mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .ruff_cache/

build:
	pip install build
	python -m build

serve:
	mkdocs serve

publish:
	mkdocs gh-deploy
