#!/bin/bash

docker-compose build && \
docker-compose -f docker-compose.yml -f docker-compose.test.yml run integration-test && \
docker-compose -f docker-compose.yml -f docker-compose.test.yml down