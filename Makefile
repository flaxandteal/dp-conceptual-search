.PHONY: all build test

all: build test

build: requirements fastText

requirements:
	pip install -r requirements.txt

fastText:
	git submodule sync --recursive
	git submodule update --init --recursive
	mkdir -p supervised_models
	pip install Cython==0.27.3 pybind11==2.2.3
	cd lib/fastText && python setup.py clean --all install

test: build
	pip install -r requirements_test.txt
	python manager.py test
