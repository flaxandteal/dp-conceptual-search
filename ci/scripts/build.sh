#!/bin/bash -eux

pushd dp-conceptual-search
  make build
  cp -r server lib supervised_models manager.py requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
