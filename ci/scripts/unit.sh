#!/bin/bash -eux

pushd dp-conceptual-search
  pip install -r requirements.txt
  pip install -r requirements_test.txt
  python manager.py test
popd
