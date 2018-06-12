from config_core import *

ENABLE_PROMETHEUS_METRICS = True
TESTING = False

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)