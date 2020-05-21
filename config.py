import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_in_production'
    MADDASH = 'https://pmp-central.geant.org/maddash/rows'
    CORS_HEADERS = 'Content-Type'
