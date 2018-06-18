#!/bin/bash -eux

pushd dp-conceptual-search
  make build test clean
popd
