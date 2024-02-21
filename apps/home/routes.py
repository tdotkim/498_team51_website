# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from jinja2 import TemplateNotFound
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
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
    documents = [SimpleDirectoryReader(text=t).load_data() for t in text_data]

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    result = query_engine.query(query)
    return result

    #client = bigquery.Client(project='capstone-team51')


@blueprint.route('/')
@blueprint.route('/index')

def index():

    return render_template('home/index.html', segment='index')

@blueprint.route('/<template>')

def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

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
    


@blueprint.route("/result", methods = ['POST', 'GET'])
def get_bot_response():    
    if request.method == 'POST': 
        form_data = request.form
        print(form_data)
        userText = form_data['ting']
        #userText = request.form.get('query')  
        result = chatbot_request(userText)  
        #return str(bot.get_response(userText)) 
        return render_template("home/chatbot.html", segment="chatbot", result=result)
