include Makefile.mk

pre-build:
	python setup.py check
	python setup.py build

post-release:
	rm -rf dist/*
	python setup.py sdist
	twine upload dist/*

