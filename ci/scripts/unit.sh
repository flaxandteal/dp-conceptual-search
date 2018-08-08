#!/bin/bash -eux

pushd dp-conceptual-search
  make build test clean
#  make mongo-start integration-test mongo-stop
popd
