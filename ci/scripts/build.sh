#!/bin/bash -eux

pushd dp-conceptual-search
  make build clean
    cp -r api app config search ons lib manager.py download_nltk_stopwords.py word2vec requirements*.txt Makefile Dockerfile.concourse ../build/
popd
