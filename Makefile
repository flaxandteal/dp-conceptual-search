.PHONY: all build test

all: build test

build: requirements

requirements:
	pip install -r requirements.txt

test: build
	pip install -r requirements_test.txt
	python manager.py test
