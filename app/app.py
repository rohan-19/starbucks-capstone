from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar,Pie,Histogram
import joblib
from sqlalchemy import create_engine
import json
import plotly
import pandas as pd

app = Flask(__name__)

models = joblib.load("..\model\classifiers.pkl")

engine = create_engine('sqlite:///../data/StarbucksOffers.db')
df = pd.read_sql_table('customer_profiles', engine)

@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals

    value_counts = [df['transaction_discount_value'].sum(),df['transaction_bogo_value'].sum(),\
                    df['transaction_informational_value'].sum(),df['transaction_no_offer_value'].sum()]
    value_names = ['Discount','Bogo','Informational','No Offer']

    count_counts = [df['#transaction_discount'].sum(),df['#transaction_bogo'].sum(),\
                    df['#transaction_informational'].sum(),df['#transaction_no_offer'].sum()]
    count_names = ['Discount','Bogo','Informational','No Offer']

    df['offer_spends']=df['transaction_discount_value']+df['transaction_bogo_value']+df['transaction_informational_value']
    df['total_spends']=df['offer_spends']+df['transaction_no_offer_value']
    spends_by_gender=df.groupby(['gender']).agg({'total_spends':'mean','#bogos':sum,'#discounts':sum}).reset_index()

    graphs = [
        {
            'data': [
                Histogram(
                    x=df['age']
                )
            ],

            'layout': {
                'title': 'Age distribution of Starbucks customers'
            }
        },
        {
            'data': [
                Histogram(
                    x=df['income']
                )
            ],

            'layout': {
                'title': 'Income distribution of Starbucks customers'
            }
        },
        {
            'data': [
                Pie(
                    labels=value_names,
                    values=value_counts
                )
            ],

            'layout': {
                'title': 'Distribution of spends across offer types'
            }
        },
        {
            'data': [
                Pie(
                    labels=count_names,
                    values=count_counts
                )
            ],

            'layout': {
                'title': 'Distribution of transaction counts across offer types'
            }
        },
        {
            'data': [
                Bar(
                    x=spends_by_gender['gender'],
                    y=spends_by_gender['total_spends']
                )
            ],

            'layout': {
                'title': 'Average Monthly Spend by Gender',
                'yaxis': {
                    'title': "Average Monthly Spend"
                },
                'xaxis': {
                    'title': "Gender"
                }
            }
        },
        {
            'data': [
                Bar(
                    x=spends_by_gender['gender'],
                    y=spends_by_gender['#bogos']
                )
            ],

            'layout': {
                'title': 'Total bogo offers completed by Gender',
                'yaxis': {
                    'title': "Bogo offers"
                },
                'xaxis': {
                    'title': "Gender"
                }
            }
        },
        {
            'data': [
                Bar(
                    x=spends_by_gender['gender'],
                    y=spends_by_gender['#discounts']
                )
            ],

            'layout': {
                'title': 'Total discount offers completed by Gender',
                'yaxis': {
                    'title': "Discounts offers"
                },
                'xaxis': {
                    'title': "Gender"
                }
            }
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


@app.route('/go')
def go():
    # save user input in query
    gender = request.args.get('gender', '')
    age = request.args.get('age', '')
    income = request.args.get('income', '')
    since = request.args.get('since', '')

    #print(gender)
    #print(age)
    #print(income)
    #print(since)
    gm=0
    go=1

    if gender=='male':
        gm=1
        go=0
    elif gender=='female':
        gm=0
        go=0
    df=pd.DataFrame([{'age':age,'income':income,'customer_since':since,'gender_M':gm,'gender_O':go}])

    #print(df)
    # use model to predict classification for query
    classification_labels={}
    for k,v in models.items():
        label = v.predict(df)[0]
        if label=='yes':
            prob= round(max(v.predict_proba(df)[0])*100,1)
        else:
            prob= round(100-max(v.predict_proba(df)[0])*100,1)
        classification_labels[k] = {'label':label,'prob':prob}
        print(label)
        print(prob)
        #classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        profile={'age':age,'income':income,'customer_since':since,'gender':gender},
        classification_result=classification_labels
    )

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()