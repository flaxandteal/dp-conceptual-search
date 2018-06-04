.PHONY: all build test

all: build test

build: requirements submodule fastText

concourse: requirements fastText test

requirements:
	pip install -r requirements.txt

submodule:
	git submodule sync --recursive
	git submodule update --init --recursive
	mkdir -p supervised_models

fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	cd lib/fastText && python setup.py clean --all install

test:
	pip install -r requirements_test.txt
	python manager.py test
