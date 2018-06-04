#!/bin/bash -eux

pushd dp-conceptual-search
  make build
  cp -r server lib supervised_models manager.py build_model.py requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
