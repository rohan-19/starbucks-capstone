from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar,Pie
import joblib

import pandas as pd

app = Flask(__name__)

models = joblib.load("..\model\classifiers.pkl")

@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals

    
    # render web page with plotly graphs
    return render_template('master.html', ids=[], graphJSON=None)


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