#!/bin/bash

if [[ $(docker inspect --format="{{ .State.Running}}" conceptual-search) == "false" ]]; then
  exit 1;
fi
