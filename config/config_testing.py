from config.config_core import *

TESTING = True
ENABLE_PROMETHEUS_METRICS = False

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'test')

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)
