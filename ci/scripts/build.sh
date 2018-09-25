#!/bin/bash -eux

pushd dp-conceptual-search
  make build clean
    cp -r api app config search ons ml lib manager.py download_nltk_stopwords.py requirements*.txt Makefile Dockerfile.concourse ../build/
popd
