.PHONY: all
all: build test

.PHONY: build
build: requirements fastText

.PHONY: debug
debug: build run
	python manager.py

.PHONY: run
run:
	python manager.py

.PHONY: conceptual_search
conceptual_search:
	CONCEPTUAL_SEARCH_ENABLED=true REDIRECT_CONCEPTUAL_SEARCH=true python manager.py

.PHONY: requirements
requirements:
	pip install -r requirements.txt
	python scripts/download_nltk_stopwords.py

.PHONY: version
version:
	pip install git+https://github.com/ONSdigital/dp4py-config.git@master#egg=dp4py_config
	python git_sha.py > app_version

.PHONY: test_requirements
test_requirements:
	pip install -r requirements_test.txt

.PHONY: fastText
fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	pip install fasttextmirror==0.8.22

.PHONY: test
test: test_requirements
	TESTING=true CONCEPTUAL_SEARCH_ENABLED=true python manager.py test

.PHONY: pep8
pep8:
	autopep8 --in-place --aggressive --aggressive -r ./
