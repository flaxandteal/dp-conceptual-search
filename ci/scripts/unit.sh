#!/bin/bash -eux

pushd dp-conceptual-search
  make version build test
popd
