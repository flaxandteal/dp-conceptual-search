#!/bin/bash -eux

pushd dp-conceptual-search
  git submodule sync --recursive
  git submodule update --init --recursive
  cp -r server lib manager.py requirements.txt config_*.py Dockerfile.concourse ../build/
popd
