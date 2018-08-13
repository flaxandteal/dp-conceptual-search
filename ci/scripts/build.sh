#!/bin/bash -eux

pushd dp-conceptual-search
  make build clean
#  cp -r server core ons lib manager.py supervised_models word2vec requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
    cp -r server core ons lib manager.py word2vec requirements*.txt config_*.py Makefile Dockerfile.concourse ../build/
popd
