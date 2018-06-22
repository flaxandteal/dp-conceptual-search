#!/bin/bash -eux

pushd dp-conceptual-search
  make build clean
  cp -r server core lib manager.py supervised_models requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
