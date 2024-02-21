# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
#from llama_index import VectorStoreIndex,  Document, SimpleDirectoryReader
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
import os


def register_blueprints(app):
    module = import_module('apps.{}.routes'.format('home'))
    app.register_blueprint(module.blueprint)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_blueprints(app)
    return app
