.PHONY: all build test

all: build test

build: requirements fastText

debug: build run
	python manager.py

debug: build run

run:
	python manager.py

conceptual_search:
	CONCEPTUAL_SEARCH_ENABLED=true REDIRECT_CONCEPTUAL_SEARCH=true python manager.py

requirements:
	pip install -r requirements.txt

version:
	pip install git+https://github.com/ONSdigital/dp4py-config.git@master#egg=dp4py_config
	python git_sha.py > app_version

test_requirements:
	pip install -r requirements_test.txt

fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	pip install fasttextmirror==0.8.22

test: test_requirements
	TESTING=true CONCEPTUAL_SEARCH_ENABLED=true python manager.py test

pep8:
	autopep8 --in-place --aggressive --aggressive -r ./
