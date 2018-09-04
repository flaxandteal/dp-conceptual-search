.PHONY: all build test

all: build test

build: requirements fastText

requirements:
	pip install -r requirements.txt
	./download_nltk_stopwords.py

test_requirements:
	pip install -r requirements_test.txt

fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	cd lib/fastText && python setup.py install

test: test_requirements
	python manager.py test

integration-test: test_requirements
	CONCEPTUAL_SEARCH_ENABLED=true USER_RECOMMENDATION_ENABLED=true nosetests -s -v tests.integration

all-tests: test integration-test

mongo-start:
	mongod --fork --logpath /var/log/mongod.log --dbpath /data/db

mongo-stop:
	mongod --fork --logpath /var/log/mongod.log --dbpath /data/db --shutdown

pep8:
	autopep8 --in-place --aggressive --aggressive -r ./

clean:
	cd lib/fastText && python setup.py clean --all
