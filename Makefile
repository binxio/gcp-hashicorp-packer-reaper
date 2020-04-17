include Makefile.mk

pre-build:
	pipenv install -e .
	pipenv run python setup.py check
	pipenv run python setup.py build

post-release:
	rm -rf dist/*
	pipenv install -d twine
	pipenv run python setup.py sdist
	pipenv run twine upload dist/*

