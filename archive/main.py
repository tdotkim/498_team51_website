import pandas as pd
import sys
import numpy as np
import os
from google.cloud import bigquery
from flask import Flask, render_template, request, escape
import json
import plotly
import plotly.graph_objects as go
import logging

app = Flask(__name__)

#ONLY FOR LOCAL USE
#CREDS = "C:\\Users\\TK\Desktop\\msds434-final-project-394614-b62f7818785f.json"
#client = bigquery.Client.from_service_account_json(json_credentials_path=CREDS,project='msds434-final-project-394614')
client = bigquery.Client(project='msds434-final-project-394614')

dset = 'finalproj'
final_model = 'finalproj.model_kmeans'

@app.route('/')
def index():
    # to do 
    sql_get_numerical_attributes = f'''
        WITH T AS (
        SELECT 
        centroid_id,
        ARRAY_AGG(STRUCT(feature AS name, 
                        ROUND(numerical_value,1) AS value) 
                        ORDER BY centroid_id) 
                        AS cluster
        FROM ML.CENTROIDS(MODEL {final_model})
        GROUP BY centroid_id
        ),

        Users AS(
        SELECT
            centroid_id,
            COUNT(*) AS Total_Users
        FROM(
            SELECT
            * EXCEPT(nearest_centroids_distance)
        FROM
        ML.PREDICT(MODEL `finalproj.model_kmeans`,
            (
            SELECT
            *
            FROM
            `finalproj.purchases`
            )))
        GROUP BY centroid_id
        )

        SELECT
        centroid_id,
        Total_Users,
        (SELECT value from unnest(cluster) WHERE name = 'Apparel') AS Apparel,
        (SELECT value from unnest(cluster) WHERE name = 'Office') AS Office,
        (SELECT value from unnest(cluster) WHERE name = 'Electronics') AS Electronics,
        (SELECT value from unnest(cluster) WHERE name = 'LimitedSupply') AS LimitedSupply,
        (SELECT value from unnest(cluster) WHERE name = 'Accessories') AS Accessories,
        (SELECT value from unnest(cluster) WHERE name = 'ShopByBrand') AS ShopByBrand,
        (SELECT value from unnest(cluster) WHERE name = 'Bags') AS Bags,
        (SELECT value from unnest(cluster) WHERE name = 'productPrice_USD') AS productPrice_USD

        FROM T LEFT JOIN Users USING(centroid_id)
        ORDER BY centroid_id ASC
        '''
    
    job_config = bigquery.QueryJobConfig()
    query_job = client.query(sql_get_numerical_attributes, job_config=job_config) #API Request
    df_numerical_attributes = query_job.result()
    df_numerical_attributes = df_numerical_attributes.to_dataframe()
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_numerical_attributes.columns),
                fill_color='plum',
                align='left'),
    cells=dict(values=df_numerical_attributes.transpose().values.tolist(),
               fill_color='lavender',
               align='left'))

    ])
    config = {'scrollZoom': True,
              'responsive': True}

    fig.update_layout(
        margin=dict(l=2, r=2, t=2, b=2),paper_bgcolor="plum")
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # include visualizations around model accuracy
    # include summary statistics around data
    logging.info('sample log regarding launch')
    return render_template('index.html',graphJSON=graphJSON, config=config)

@app.route('/set_base_model')
def form():
    # to do
    # add multi-input option?
    return render_template('form.html')

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'POST':
        form_data = request.form
        device = form_data['Device']
        apparel = form_data['Apparel']
        office = form_data['Office']
        electronics = form_data['Electronics']
        limited = form_data['LimitedSupply']
        accessory = form_data['Accessories']
        bybrand = form_data['ShopByBrand']
        bags = form_data['Bags']
        total = form_data['total']
        # submit the input 
        records = [
            {'OS':device,
             'Apparel':apparel,
             'Office':office,
             'Electronics':electronics,
             'LimitedSupply':limited,
             'Accessories':accessory,
             'ShopByBrand':bybrand,
             'Bags':bags,
             'productPrice_USD':total}
        ]

        df = pd.DataFrame(
            records,
            columns = [
                'OS',
                'Apparel',
                'Office',
                'Electronics',
                'LimitedSupply',
                'Accessories',
                'ShopByBrand',
                'Bags',
                'productPrice_USD'
            ]
        )

        job_config = bigquery.LoadJobConfig(
        
            schema = [
                bigquery.SchemaField("OS", "STRING"),
                bigquery.SchemaField("Apparel", "INTEGER"),
                bigquery.SchemaField("Office", "INTEGER"),
                bigquery.SchemaField("Electronics", "INTEGER"),
                bigquery.SchemaField("LimitedSupply", "INTEGER"),
                bigquery.SchemaField("Accessories", "INTEGER"),
                bigquery.SchemaField("ShopByBrand", "INTEGER"),
                bigquery.SchemaField("Bags", "INTEGER"),
                bigquery.SchemaField("productPrice_USD", "INTEGER")
            ],
            autodetect=False,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition="WRITE_TRUNCATE" #comment this out to append
        )
        job = client.load_table_from_dataframe(
            df, 'finalproj.input',job_config=job_config
        )  

        job.result()
        logging.info('sample log regarding job result')

        # do the predict
        query = """
        SELECT * EXCEPT(nearest_centroids_distance)
        FROM ML.PREDICT(MODEL finalproj.model_kmeans,
        (SELECT *
        FROM
        `finalproj.input`))
        """

        df = client.query(query).to_dataframe()
        logging.info('sample log regarding prediction')
        logging.info('sample message re: completion')
        return render_template('data.html',tables=[df.to_html(max_rows=20,classes='data')], titles=['predictions'])
    
 
 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
