# Starbucks KYC Capstone Project

## Summary
TO BE ADDED



### Instructions:
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        `python data\process_data.py data\profile.json data\portfolio.json data\transcript.json data\StarbucksOffers.db`
    - To run ML pipeline that trains classifier and saves
        `python model\train_classifiers.py data\StarbucksOffers.db model\classifiers.pkl`

2. Run the following command in the app's directory to run your web app.
    `python run.py`

3. Go to http://0.0.0.0:3001/