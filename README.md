# Starbucks KYC Capstone Project

### Table of Contents

1. [Instructions](#instructions)
2. [Project Definition](#definition)
3. [File Descriptions](#files)
4. [Data Analysis](#analysis)
5. [Experiments and Results](#results)
6. [Licensing, Authors, and Acknowledgements](#licensing)


## Instructions:<a name="instructions"></a>
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        `python data\process_data.py data\profile.json data\portfolio.json data\transcript.json data\StarbucksOffers.db`
    - To run ML pipeline that trains classifier and saves
        `python model\train_classifiers.py data\StarbucksOffers.db model\classifiers.pkl`

2. Run the following command in the app's directory to run your web app.
    `python run.py`

3. Go to http://0.0.0.0:3001/

## Project Definition<a name="definiton"></a>
Starbucks Capstone Challenge in Udacity Data Scientist Nanodegree

### Problem Statement
This data set contains simulated data that mimics customer behavior on the Starbucks rewards mobile app. Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink or an actual offer such as a discount or BOGO (buy one get one free). Some users might not receive any offer during certain weeks.

Not all users receive the same offer, and that is the challenge to solve with this data set.

Your task is to combine transaction, demographic and offer data to determine which demographic groups respond best to which offer type. This data set is a simplified version of the real Starbucks app because the underlying simulator only has one product whereas Starbucks actually sells dozens of products.

The complete details are present in the 'Starbucks Capstone Challenge.txt'

### Problem Statement
The problem statement which we are going to address with the project is to find the chances of a user responding to a specific type of offer and create a web app where user demographics can be entered and get the offer profile for the user.

### Metrics
The main metric to track the success is the accuracy of the offer suggestions made for each user. 

### Data Sets
The data is contained in three files:

portfolio.json - containing offer ids and meta data about each offer (duration, type, etc.)
profile.json - demographic data for each customer
transcript.json - records for transactions, offers received, offers viewed, and offers completed
Here is the schema and explanation of each variable in the files:

portfolio.json

id (string) - offer id
offer_type (string) - type of offer ie BOGO, discount, informational
difficulty (int) - minimum required spend to complete an offer
reward (int) - reward given for completing an offer
duration (int) - time for offer to be open, in days
channels (list of strings)
profile.json

age (int) - age of the customer
became_member_on (int) - date when customer created an app account
gender (str) - gender of the customer (note some entries contain 'O' for other rather than M or F)
id (str) - customer id
income (float) - customer's income
transcript.json

event (str) - record description (ie transaction, offer received, offer viewed, etc.)
person (str) - customer id
time (int) - time in hours since start of test. The data begins at time t=0
value - (dict of strings) - either an offer id or transaction amount depending on the record

## File Descriptions:<a name="files"></a>
1. data - The folder contains three jsons as decribed in the data sets above. The process_data.py file takes in all the datasets as input and stores the merged and cleaned dataset to a sqlite database at the specified path.

2. models - The folder contains a train_classifiers.py file which takes in path to the sqlite database containing the customer profiles and trains classifiers to predict the response probability for responding to the three types of offers available on the starbucks app. The final models are stored as a pickle object at the specified path.

3. app - The folder contains a flask application in run.py which serves the static web app files from the templates included. 

## Data Analysis:<a name="analysis"></a>
We use the pandas profiling (https://github.com/pandas-profiling/pandas-profiling) library to do basic EDA on the datasets to figure out abnormalities and visual different attribute distributions which helped in deciding the preprocessing steps included in the ETL pipeline in the process_data.py file. The pandas profiling output for all the three input datasets are available to view.




## Experiments and Results<a name="results"></a>
We managed to achieve an accuracy of 60-70% on all three offer types after trying out various sklearn models with hyperparameter tuning. 
On further analysis using the h2o automl library which runs various complex models, accuracy scores remained similar. This means that basic demographic features as derived in the above experiment are not enough to predict offer success with a very high precision.




## Licensing, Authors, Acknowledgements<a name="licensing"></a>

This dataset was provided as a part of the Udacity Data Scientist Nanodegree capstone challenge.