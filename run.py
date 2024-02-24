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
from flask import render_template, request
from jinja2 import TemplateNotFound
from llama_index import GPTVectorStoreIndex,  Document, SimpleDirectoryReader
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
import os


def chatbot_request(query):
    #CREDS = "C:/Users/tkkim/gcp_keys/capstone-team51-366963bafc54.json"
    #storage_client = storage.Client.from_service_account_json(json_credentials_path=CREDS,project='capstone-team51')
    #bq_client = bigquery.Client.from_service_account_json(json_credentials_path=CREDS,project='capstone-team51')
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('capstone-team51-data')
    #os.environ["OPENAI_API_KEY"] = "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"
    df = pd.read_excel(bucket.blob('chatbot/ChicagoCrimeFeb24.xlsx').download_as_string())


    ## For excel spreadsheet
    text_data = df['Text'].tolist()

    # # Remove new-line characters
    for i in range(len(text_data)):
        text_data[i] = text_data[i].replace("\n", " ")

    # # convert Excel spreadsheet to documents
    documents = [Document(text=t) for t in text_data]

    index = GPTVectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    result = query_engine.query(query)
    return result

    #client = bigquery.Client(project='capstone-team51')

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


@app.route('/')
@app.route('/index')

def index():

    return render_template('./home/index.html', segment='index')

@app.route('/<template>')

def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("./home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('./home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
    


@app.route("/result", methods = ['POST', 'GET'])
def get_bot_response():    
    if request.method == 'POST': 
        form_data = request.form
        print(form_data)
        userText = form_data['ting']
        #userText = request.form.get('query')  
        result = chatbot_request(userText)  
        #return str(bot.get_response(userText)) 
        return render_template("home/chatbot.html", segment="chatbot", result=result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), use_reloader=False)
else:
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), use_reloader=True)
