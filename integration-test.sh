#!/bin/bash

docker-compose build && \
docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm test && \
docker-compose -f docker-compose.yml -f docker-compose.test.yml down