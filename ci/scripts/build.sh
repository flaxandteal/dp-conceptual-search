#!/bin/bash -eux

pushd dp-conceptual-search
  make && make clean
  cp -r server lib manager.py supervised_models requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
