import os

LOGO = None
CONCEPTUAL_SEARCH_ENABLED = os.environ.get(
    'CONCEPTUAL_SEARCH_ENABLED',
    'False').lower() == 'true'

MONGO_DB = os.environ.get('DEFAULT_MONGO_DB', 'local')
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = os.environ.get('MONGO_PORT', '27017')

MOTOR_URI = "mongodb://{host}:{port}/{db}".format(
    host=MONGO_HOST,
    port=MONGO_PORT,
    db=MONGO_DB
)
