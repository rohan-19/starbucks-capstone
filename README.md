# Starbucks KYC Capstone Project

### Table of Contents

1. [Instructions](#instructions)
2. [Project Definition](#definition)
3. [File Descriptions](#files)
4. [Data Analysis](#analysis)
5. [Feature Engineering](#features)
6. [Data Cleaning](#cleaning)
7. [Experiments and Results](#results)
8. [Licensing, Authors, and Acknowledgements](#licensing)


## Instructions:<a name="instructions"></a>
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        `python data/process_data.py data/profile.json data/portfolio.json data/transcript.json data/StarbucksOffers.db`
    - To run ML pipeline that trains classifier and saves
        `python model/train_classifiers.py data/StarbucksOffers.db model/classifiers.pkl`

2. Run the following command in the app's directory to run your web app.
    `python app.py`

3. Go to http://0.0.0.0:3001/

## Project Definition<a name="definiton"></a>
Starbucks Capstone Challenge in Udacity Data Scientist Nanodegree

### Problem Statement
This data set contains simulated data that mimics customer behavior on the Starbucks rewards mobile app. Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink or an actual offer such as a discount or BOGO (buy one get one free). Some users might not receive any offer during certain weeks.

Not all users receive the same offer, and that is the challenge to solve with this data set.

Your task is to combine transaction, demographic and offer data to determine which demographic groups respond best to which offer type. This data set is a simplified version of the real Starbucks app because the underlying simulator only has one product whereas Starbucks actually sells dozens of products.

The complete details are present in the 'Starbucks Capstone Challenge.txt'

### Problem Statement
The problem statement which we are going to address with the project is to find the chances of a user responding to a specific type of offer and create a web app where user demographics can be entered to get the offer profile for the user.

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
We use the pandas profiling (https://github.com/pandas-profiling/pandas-profiling) library to do basic EDA on the datasets to figure out abnormalities and visualize different attribute distributions which helped in deciding the preprocessing steps included in the ETL pipeline in the process_data.py file. The pandas profiling output for all the three input datasets are available to view.

## Feature Engineering:<a name="analysis"></a>
The following demographic features were picked to define the users:
1. Age (in Years) - Available in profile dataset
2. Gender (M/F/O) - Available in profile dataset
3. Income - Available in profile dataset
4. Customer Since (in days) - This feature was derived from the membership start data from the profile dataset. The days were calculated by using the maximum membership date in the dataset as the last day.

The following features were derived from the transcript dataset to define user behavior:
1. #transaction_bogo - Number of transactions attributed to bogo offers
2. transaction_bogo_value - Total value of transactions attributed to bogo offers
3. #transaction_discount - Number of transactions attributed to discount offers
4. transaction_discount_value - Total value of transactions attributed to discount offers
5. #transaction_informational - Number of transactions attributed to informational offers (used to predict informational offer success)
6. transaction_informational_value - Total value of transactions attributed to informational offers
7. #transaction_no_offer - Number of transactions attributed to no offers
8. transaction_no_offer_value - Total value of transactions attributed to no offers
9. #bogos - Number of bogo offers completed (used to predict bogo offer success)
10. #discounts - Number of discount offers completed (used to predict discount offer success)
11. bogos_rewards - Total reward from bogo offers
12. discounts_rewards - Total reward from discount offers


## Data Processing:<a name="cleaning"></a>
### Cleaning
1. portfolio.json - the offer portfolio file contains details of 10 offers and does not require any cleanup.
2. profile.json - the customer profiles data had a lot of dummy values where the age was 118 and income and age values were null. These were removed to obtain a clean profile dataset.
3. transcript.json - the transcript data has values associated to a customer event in a dictionary format which was converted to individual columns in a dataframe to track the offer id, amount and reward for each event.

### Processing
The transcript for each person was processed in time order to derive the user stats which are helpful in predicting the success of different offers. The customer profile was captured in one row per user in a dataset which was combined with the demographics data to make it usable in machine learning models. 

The timeline was processed as follows to attribute each transaction with a specific offer type :
- Offer received : store the offer as active till expiry.
- Offer viewed : store the offer as viewed till expiry if its active and not already complete. We keep track of the last offer which the subsequent transactions are attributed to.
- Transaction : amount is attributed to the last seen offer if any otherwise to no offer category.
- Offer complete : reward attributed to offer type if completed after viewing otherwise no offer.

### Challenges
It is very difficult to exactly map a transaction to whether it resulted from a specific offer or not. The user might have seen one or multiple offers and still might be going through a normal transaction without any influence. Even if we assume offers influence purchases, there can be multiple active offers and we cant accurately attribute the transaction to any one. 

In the current setup, we have attributed a transaction to the last seen active offer for modelling purposes.





## Experiments and Results<a name="results"></a>
The initial model used income,age and gender as basic demographic features to predict the three offer types. The accuracy was very low in the 30-35% range for all three using Logistic Regression models without any hyper parameter tuning. 

A new feature customer since was derived with the intention of capturing how long the customer has been with Starbucks that might affect the spend patterns and affinity to offers. This helped the model reach 50-55% accuracy using a basic Random Forest model with no hyper parameter tuning.

With the same set of features, a cross validated grid search was implemented to try various model parameters over three types of models (decision tree, random forest and logistic regression) to come up with the best model.

We managed to achieve an accuracy of 60-70% on all three offer types after trying out various sklearn models with hyperparameter tuning. 

On further analysis using the h2o automl library which runs more complex models, accuracy scores remained similar. This means that basic demographic features as derived in the above experiment are not enough to predict offer success with a very high precision.


### Possible Improvements
1. The current assumption is that only the last seen offer influences a transaction which might not be accurate. We can try mapping the transaction (possible average distributed) to all active offers to get a better estimate.
2. The process does not take into the account the number of bogo/discount/informational offers made to a specific user. This can provide a better baseline to measure the offer effectiveness by finding out people with only high response rate to each offer.


## Licensing, Authors, Acknowledgements<a name="licensing"></a>

This dataset was provided as a part of the Udacity Data Scientist Nanodegree capstone challenge.