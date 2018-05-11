#!/bin/bash -eux

pushd dp-conceptual-search
  cp -r server manager.py requirements.txt Dockerfile.concourse ../build/
popd
