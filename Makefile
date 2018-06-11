.PHONY: all build test

all: build test

build: requirements fastText

requirements:
	pip install -r requirements.txt

fastText:
	pip install Cython==0.27.3 pybind11==2.2.3
	cd lib/fastText && python setup.py install

test:
	pip install -r requirements_test.txt
	docker-compose up -d
	python manager.py test
	docker-compose down

clean:
	cd lib/fastText && python setup.py clean --all