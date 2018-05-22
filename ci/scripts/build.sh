#!/bin/bash -eux

pushd dp-conceptual-search
  make build
  cp -r server lib manager.py requirements.txt config_*.py Dockerfile.concourse ../build/
popd
