.PHONY: all build test

all: build test

build: requirements model

requirements:
	pip install -r requirements.txt

fastText:
	git submodule sync --recursive
	git submodule update --init --recursive
	cd lib/fastText && python setup.py clean --all install

model: fastText
	pip install -r requirements_model.txt
	python build_model.py supervised_models/ons_labelled.txt supervised_models/ons_supervised.bin

test: build
	pip install -r requirements_test.txt
	python manager.py test
