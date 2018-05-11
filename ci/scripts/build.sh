#!/bin/bash -eux

pushd dp-conceptual-search
  cp -r server requirements.txt Dockerfile.concourse ../build/
popd
