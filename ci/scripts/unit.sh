#!/bin/bash -eux

pushd dp-conceptual-search
  pip install -r requirements.txt
  pip install -r requirements_test.txt
  nosetests -v
popd
