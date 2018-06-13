#!/bin/bash

# Temporary start script to launch mongo and run the integration tests.
# This should be replaced by ./integration-test.sh when docker-compose is implemented in ci,
# and the Dockerfile updated accordingly (revert to ENTRYPOINT ["python"])

mongod --fork --logpath /var/log/mongod.log --dbpath /data/db

make integration-test
python manager.py
