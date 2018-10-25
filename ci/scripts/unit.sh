#!/bin/bash -eux

pushd dp-conceptual-search
  make build version test
popd
