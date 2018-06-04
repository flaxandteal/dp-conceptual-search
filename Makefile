.PHONY: all build test

all: build requirements_test test

build: requirements fastText

requirements:
	pip install -r requirements.txt

requirements_test:
	pip install -r requirements_test.txt

submodule:
	git submodule sync --recursive
	git submodule update --init --recursive

fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	cd lib/fastText && python setup.py install

test:
	python manager.py test

clean:
	cd lib/fastText && python setup.py clean --all