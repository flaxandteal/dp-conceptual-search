"""
This file contains config options specific to Sanic
"""
from config.config import MONGO_CONFIG

# General

LOGO = None  # Disable printing of the Sanic logo

# Motor

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_CONFIG.bind_addr,
    db=MONGO_CONFIG.db
)
