# in production rename to config.py and edit constants

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_in_production'
    PSCONFIG = 'https://pmp-archive.geant.org/psconfig/pscfg-pmp.json'
    CORS_HEADERS = 'Content-Type'
