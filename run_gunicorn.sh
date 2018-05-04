#!/usr/bin/env bash

~/anaconda3/bin/gunicorn manager:app --bind 0.0.0.0:1337 --worker-class sanic.worker.GunicornWorker -w 6 --threads 12 --timeout 240
