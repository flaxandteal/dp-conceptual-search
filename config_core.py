import os

LOGO = None
USER_RECOMMENDATION_ENABLED = os.environ.get(
    'USER_RECOMMENDATION_ENABLED',
    'False').lower() == 'true'

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'local')

MONGO_DEFAULT_HOST = os.environ.get("MONGO_DEFAULT_HOST", "localhost")
MONGO_DEFAULT_PORT = os.environ.get("MONGO_DEFAULT_PORT", 27017)

MONGO_BIND_ADDR = 'mongodb://{host}:{port}'.format(
    host=MONGO_DEFAULT_HOST, port=MONGO_DEFAULT_PORT)

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)

# Prometheus metrics endpoint
ENABLE_PROMETHEUS_METRICS = os.environ.get(
    'ENABLE_PROMETHEUS_METRICS',
    'False').lower() == 'true'


COLOURED_LOGGING_ENABLED = os.environ.get(
    'COLOURED_LOGGING_ENABLED',
    'False').lower() == 'true'
