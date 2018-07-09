import os

LOGO = None
MONGO_ENABLED = os.environ.get(
    'MONGO_ENABLED',
    'True').lower() == 'true'

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'local')
MONGO_BIND_ADDR = os.environ.get(
    'MONGO_BIND_ADDR',
    'mongodb://localhost:27017')

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)

# Prometheus metrics endpoint
ENABLE_PROMETHEUS_METRICS = os.environ.get('ENABLE_PROMETHEUS_METRICS', 'False').lower() == 'true'
