# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit
from flask import Flask

from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
import os
#from llama_index import VectorStoreIndex,  Document, SimpleDirectoryReader

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')  

    DEBUG = True
    
    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}

app_config = config_dict['Debug']
app = Flask(__name__)
app.config.from_object(app_config)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), use_reloader=False)
else:
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), use_reloader=False)
