import sys
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
import pickle


def clean_data(df):
	'''
	INPUT
	df - pandas dataframe to be cleaned

	OUTPUT
	df - pandas dataframe after cleaning

	This function does the following:
	1. Figures out numeric and categorical columns from the dataframe
	2. Performs one hot encoding for the categorical variables and adds them to dataframe
	'''
	num_vars = df.select_dtypes(include=['float', 'int']).columns
	#for col in num_vars:
	#    df[col].fillna((df[col].mean()), inplace=True)
	    
	cat_vars = df.select_dtypes(include=['object']).copy().columns
	for var in  cat_vars:
	    # for each cat add dummy var, drop original column
	    df = pd.concat([df.drop(var, axis=1), pd.get_dummies(df[var], prefix=var, prefix_sep='_', drop_first=True)], axis=1)
	return df

def build_model(model_type='randomforest'):
	'''
	INPUT
	model_type - sklearn model type to be used

	OUTPUT
	cv - Gridsearchcv model on a pipeline testing different parameters

	This function does the following:
	1. Create a pipeline with the classifier as specified in model_type
	2. Initialize a parameter grid for gridsearchcv for specific model_type
	'''

	if model_type=='decisiontree':
	    clf= DecisionTreeClassifier(class_weight='balanced',random_state=42)
	    parameters = {
	    'clf__min_samples_split': (2,5,15,25,50),
	    'clf__max_depth': (None,5,10,50,500)
	    }
	elif model_type=='randomforest':
	    clf= RandomForestClassifier(class_weight='balanced',random_state=42)
	    parameters = {
	    'clf__min_samples_split': (2,5,15,25,50),
	    'clf__max_depth': (None,5,10,50,500)
	    }
	elif model_type=='lr':
	    clf= LogisticRegression(random_state=42)
	    parameters = {
	    }
	    
	pipeline = Pipeline([
	    ('clf', clf)
	])


	cv = GridSearchCV(pipeline, param_grid=parameters,n_jobs=-1,cv=3)
	return cv


def evaluate_model(model, X_test, Y_test):
	'''
	INPUT
	model - the classifier model for the offer
	X_test - test set of users
	Y_test - actual value of user response to offer 

	OUTPUT
	NONE

	This function does the following:
	1. Use the classifier model to whether user will respond to the offer
	2. Print the classification report for the classifier
	'''
	score= model.score(X_test,Y_test)
	print(score)
	Y_pred = model.predict(X_test)
	print(classification_report(Y_test, Y_pred))

	return score


def save_model(model, model_filepath):
	'''
	INPUT
	model - the classifier model for the messages
	model_filepath - file path to store the classifier model as pickle

	OUTPUT
	NONE

	This function does the following:
	1. Store the classifier model as a pickle object at the specified file path
	'''
	with open(model_filepath, 'wb') as file:
	    pickle.dump(model, file)

def get_model_for_target(X,Y):
	'''
	INPUT
	X - Independent attributes to be used in classifer
	Y - Target value for the classifier

	OUTPUT
	best_model - sklearn model to be used for classification

	This function does the following:
	1. Splits the given data into train and test sets for model creation
	2. Creates 3 types for sklearn models and finds the best one
	'''
	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
	score_max = -1
	best_model = None
	for model_type in ['decisiontree','randomforest','lr']:
		model = build_model(model_type)

		model.fit(X_train, Y_train)

		score= evaluate_model(model, X_test, Y_test)

		if score>score_max:
			best_model=model

	return best_model

def main():
	if len(sys.argv) == 3:
		database_filepath, model_filepath = sys.argv[1:]
		print('Loading data...\n    DATABASE: {}'.format(database_filepath))


		engine = create_engine('sqlite:///'+database_filepath)
		df = pd.read_sql_table('customer_profiles',engine)


		demographics= df[['gender','age','income','customer_since']]
		X = clean_data(demographics)

		print('Building model for bogo offer ....\n')
		bogo= np.where(df['#bogos']>0,'yes','no')
		bogo_model= get_model_for_target(X,bogo)

		print('Building model for discount offer ....\n')
		discount= np.where(df['#discounts']>0,'yes','no')
		discount_model= get_model_for_target(X,discount)

		print('Building model for informational offer ....\n')
		informational= np.where(df['#transaction_informational']>0,'yes','no')
		informational_model= get_model_for_target(X,informational)

		model = {'bogo':bogo_model,'discount':discount_model,'informational':informational_model}

		print('Saving model...\n    MODEL: {}'.format(model_filepath))
		save_model(model, model_filepath)

		print('Trained model saved!')

	else:
		print('Please provide the filepath of the starbucks offers database '\
		      'as the first argument and the filepath of the pickle file to '\
		      'save the model to as the second argument. \n\nExample: python '\
		      'train_classifier.py ../data/StarbucksOffers.db classifiers.pkl')


if __name__ == '__main__':
	main()