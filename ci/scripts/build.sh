#!/bin/bash -eux

pushd dp-conceptual-search
    make version
    cp -r * ../build/
popd
