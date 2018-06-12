import os

LOGO = None
CONCEPTUAL_SEARCH_ENABLED = os.environ.get(
    'CONCEPTUAL_SEARCH_ENABLED',
    'True').lower() == 'true'

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'local')
MONGO_BIND_ADDR = os.environ.get(
    'MONGO_BIND_ADDR',
    'mongodb://localhost:27017')

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)
