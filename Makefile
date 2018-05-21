
.PHONY all:
	make build

build: fastText
	pip install -r requirements.txt

test: build
	pip install -r requirements_test.txt
	python manager.py test

fastText:
	pip install Cython pybind11
	cd lib/fastText && python setup.py install