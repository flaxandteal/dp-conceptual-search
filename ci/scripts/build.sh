#!/bin/bash -eux

pushd dp-conceptual-search
  make build
  cp -r server lib supervised_models manager.py build_model.py requirements.txt requirements_model.txt requirements_test.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
