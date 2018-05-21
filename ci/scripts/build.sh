#!/bin/bash -eux

pushd dp-conceptual-search
  cp -r server manager.py requirements.txt config_*.py Dockerfile.concourse ../build/
popd
