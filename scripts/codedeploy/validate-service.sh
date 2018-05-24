#!/bin/bash

if [[ $(docker inspect --format="{{ .State.Running}}" dp-conceptual-search) == "false" ]]; then
  exit 1;
fi
