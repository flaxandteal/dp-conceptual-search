from config_core import *

TESTING = True
ENABLE_PROMETHEUS_METRICS = False

MONGO_SEARCH_DATABASE = 'test'
MONGO_BIND_ADDR = 'mongodb://0.0.0.0:27017'

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)
