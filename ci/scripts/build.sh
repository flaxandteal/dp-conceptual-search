#!/bin/bash -eux

pushd dp-conceptual-search
  make build
    cp -r api app config search ons ml lib manager.py requirements*.txt Makefile Dockerfile.concourse ../build/
    mkdir ../build/scripts && cp scripts/download_nltk_stopwords.py ../build/scripts/
popd
