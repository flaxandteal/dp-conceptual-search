#!/bin/bash -eux

pushd dp-conceptual-search
  make && make clean
  cp -r server lib manager.py requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
