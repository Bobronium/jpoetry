.PHONY: all clean pip-clean flake mypy isort requirements, lock, sync, pipenv, coverage, build_info

export PIP_CONFIG_FILE=$(shell pwd)/setup.cfg

sources = jpoetry
black = black -S -l 100 --target-version py36 $(sources) tests
flake8 = flake8 $(sources) --show-source
isort = isort $(sources) tests

all: pipenv lint flake mypy test

format:
	$(isort)
	$(black)

test:
	pytest tests --cov=jpoetry

lint:
	$(flake8)

mypy:
	mypy $(sources)

run:
	python -m jpoetry


coverage: test
	coverage html
	open htmlcov/index.html


clean:
	@rm -rf build dist
	@rm -rf `find . -type d -name __pycache__`
	@rm -f `find . -type f -name '*.py[co]'`
	@rm -rf `find . -type d -name .pytest_cache`
	@rm -rf `find . -type d -name .mypy_cache`
	@python setup.py clean
	@rm -rf *.egg-info
	@rm -f .make-*
