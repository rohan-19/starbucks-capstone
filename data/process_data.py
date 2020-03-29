import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def create_customer_profile_from_timeline(person,person_transcript,offer_durations,offer_types):
	'''
	INPUT
	person - user id for the person
	person_transcript - transaction transcript for the particular user


	OUTPUT
	customer_profile - Dictionary object with the customer profile details

	The function does the following:
	1. Initializes variables to keep track of user event timelines to derive insights
	2. Stores the derived attributes in a dictionary which is returned 
	'''
	customer_profile={}
	customer_profile['person']=person
	person_transcript=person_transcript.sort_values(['time'])

	#Dictionary to keep track of offers active at a given time with value as valid till hour
	offers_active={}
	#Dictionary to keep track of offers viewed at a given time with value as valid till hour
	offers_in_view={}

	### ASSUMPTION HERE IS THAT A SPEND CAN BE ATTRIBUTED TO THE LAST OFFER SEEN BY USER
	#Variables to keep track of last offer seen and its time
	last_offer=''
	last_offer_time=-1 

	# Variables to keep track of transactions belonging to specific offer types(or no offer)
	transaction_no_offer=[]
	transaction_bogo=[]
	transaction_discount=[]
	transaction_informational=[]

	# Variables to keep track of various completed offers and rewards
	bogos=[]
	discounts=[]
	random_rewards=[]
	completed_offers= 0
	offered={'bogo':0,'informational':0,'discount':0}

	offers_done=set()

	for index, row in person_transcript.iterrows():
	    time=row['time']
	    
	    #Remove all expired offers from active
	    offers_expired= [key for key in offers_active if offers_active[key]<time]
	    for key in offers_expired:
	        offers_active.pop(key)

	    #Remove all expired offers from viewed offers   
	    offers_expired= [key for key in offers_in_view if offers_in_view[key]<time]
	    for key in offers_expired:
	        offers_in_view.pop(key)
	        
	    if time>last_offer_time:
	        last_offer=''
	    
	    event=row['event']
	    offer_id=row['offer_id_merged']

	    #Process an offer received event and add it to active offers
	    if event=='offer received':
	        if offer_id in offers_done:
	            offers_done.remove(offer_id)
	        offers_active[offer_id]= time+ 24*offer_durations[offer_id]
	        offered[offer_types[offer_id]]+=1
	     
	    #Process an offer viewed event and add it to list if offer is active
	    elif event=='offer viewed':
	        if offer_id in offers_done:
	            continue
	        if offer_id in offers_active:
	            offers_in_view[offer_id]= offers_active[offer_id]
	            last_offer=offer_types[offer_id]
	            last_offer_time=offers_active[offer_id]

	    #Process a transaction event and add it to relevant offer type based on last offer seen
	    elif event=='transaction':
	        if last_offer!='':
	            if last_offer=='bogo':
	                transaction_bogo.append(row['amount'])
	            elif last_offer=='discount':
	                transaction_discount.append(row['amount'])
	            elif last_offer=='informational':
	                transaction_informational.append(row['amount'])
	            else:
	                print('INVALID OFFER TYPE')
	        else:
	            transaction_no_offer.append(row['amount'])

	    #Process an offer completed event and add to relevant offer and rewards list
	    elif event=='offer completed':
	        offers_done.add(offer_id)
	        completed_offers+=1
	        if offer_id in offers_in_view:
	            if offer_types[offer_id]=='bogo':
	                bogos.append(row['reward'])
	            elif offer_types[offer_id]=='discount':
	                discounts.append(row['reward'])
	        else:
	            random_rewards.append(row['reward'])

	customer_profile['#transaction_bogo']=len(transaction_bogo)
	customer_profile['transaction_bogo_value']=sum(transaction_bogo)

	customer_profile['#transaction_discount']=len(transaction_discount)
	customer_profile['transaction_discount_value']=sum(transaction_discount)

	customer_profile['#transaction_informational']=len(transaction_informational)
	customer_profile['transaction_informational_value']=sum(transaction_informational)

	customer_profile['#transaction_no_offer']=len(transaction_no_offer)
	customer_profile['transaction_no_offer_value']=sum(transaction_no_offer)
	customer_profile['completed_offers']= completed_offers
	customer_profile['#bogos']= len(bogos)
	customer_profile['#discounts']= len(discounts)
	customer_profile['bogos_rewards']= sum(bogos)
	customer_profile['discounts_rewards']= sum(discounts)
	customer_profile['#random_rewards']=len(random_rewards)
	customer_profile['random_rewards']=sum(random_rewards)

	customer_profile['bogos_offered']=offered['bogo']
	customer_profile['discounts_offered']=offered['discount']
	customer_profile['informationals_offered']=offered['informational']

	return customer_profile

def create_customer_profiles(profile,portfolio,transcript):
	'''
	INPUT
	profile - pandas dataframe containing the customer profile data
	portfolio - pandas dataframe containing the offer portfolio data
	transcript - pandas dataframe containing the transaction transcript data


	OUTPUT
	customer_profile_complete - pandas dataframe containing customer profiles 

	The function does the following:
	1. Creates groups from the transcript dataset by person
	2. Analyses the person timeline in order to create customer spend profile
	3. Merges the customer profile with the original profile demographics information
	4. Computes the offer types most used by count and value
	'''

	# Dictionary objects to track the duration and type of various offers
	offer_durations=dict(zip(portfolio['id'].values,portfolio['duration'].values))
	offer_types=dict(zip(portfolio['id'].values,portfolio['offer_type'].values))

	transcript_groups = transcript.groupby(['person'])

	customer_profiles=[]
	
	# Iterate over each person transcript to create event based profile
	for person,person_transcript in transcript_groups:
		customer_profile= create_customer_profile_from_timeline(person,person_transcript,offer_durations,offer_types)

		customer_profiles.append(customer_profile)

	customer_profile_df=pd.DataFrame(customer_profiles)

	# Merge with the original profile dataset to get demographic information
	customer_profile_complete=customer_profile_df.merge(profile,how='inner',left_on='person',right_on='id')
	customer_profile_complete=customer_profile_complete.drop(['id'],axis=1)

	
	# Computes the offer type where spend amount was maximum 
	customer_profile_complete['best_offer_value']=customer_profile_complete[['transaction_informational_value',\
	                                                     'transaction_no_offer_value',\
	                                                    'transaction_discount_value',\
	                                                    'transaction_bogo_value']].idxmax(axis=1)
	# Compute the offer type which was used the most                                                  
	customer_profile_complete['best_offer_count']=customer_profile_complete[['#transaction_informational',\
	                                                     '#transaction_no_offer',\
	                                                    '#transaction_discount',\
	                                                    '#transaction_bogo']].idxmax(axis=1)


	return customer_profile_complete


def clean_transcript_data(transcript):
	'''
	INPUT
	transcript - pandas dataframe containing the transaction transcript data

	OUTPUT
	transcript_clean - pandas dataframe containing cleaned up transaction transcript data

	The function does the following:
	1. Converts the values dictionary to individual dataframe columns
	2. Combines the new derived values columns with original dataset
	3. Cleans up the two offer id fields into one
	'''

	transcript_values=transcript['value'].apply(pd.Series )

	transcript_clean= pd.concat([transcript,transcript_values],axis=1)

	# The offer id field uses a different key for offer views and offer completed events
	transcript_clean['offer_id_merged']=np.where(transcript_clean['offer_id'].isnull(), \
								transcript_clean['offer id'],transcript_clean['offer_id'])


	return transcript_clean

def clean_profile_data(profile):
	'''
	INPUT
	profile - pandas dataframe containing the customer profile data

	OUTPUT
	profile_clean - pandas dataframe containing cleaned up customer profile data

	The function does the following:
	1. Drops all dummy profiles with age 118 and empty income and gender values
	2. Converts the became_member_on field from string to date 
	3. Calculates the member age in days and stores in customer_since column
	4. Drops the unnecessary columns
	'''
	profile_clean=profile[profile['age']!=118]
	profile_clean['became_member_on_date']=pd.to_datetime(profile_clean['became_member_on'],format='%Y%m%d')

	date_max=max(profile_clean['became_member_on_date']) 
	profile_clean['customer_since']=profile_clean['became_member_on_date'].apply(lambda x:(date_max-x).days)

	profile_clean=profile_clean.drop(['became_member_on','became_member_on_date'],axis=1)

	return profile_clean

def save_data(df, database_filename,table_name):
    '''
    INPUT
    df - pandas dataframe to be written to SQLite
    database_filename - file path for the SQLite database
    table_name - table name to be used for the SQLite table

    OUTPUT
    NONE
    
    This function does the following:
    1. Create sqlite engine at the specified file path
    2. Store the dataframe in the sqlite database in specified table
    '''
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql(table_name, engine, index=False)  


def main():
    if len(sys.argv) == 5:

        profile_filepath, portfolio_filepath, transcript_filepath ,database_filepath = sys.argv[1:]

        print('Loading data...\n    CUSTOMER PROFILES: {}\n    OFFER PORTFOLIO: {}\n    TRANSACTIONS: {}'
              .format(profile_filepath, portfolio_filepath, transcript_filepath))

        profile= pd.read_json(profile_filepath, orient='records', lines=True)
        portfolio= pd.read_json(portfolio_filepath, orient='records', lines=True)
        transcript= pd.read_json(transcript_filepath, orient='records', lines=True)

        #The portfolio dataset does not require any cleanup. 


        print('Cleaning customer profile data...')
        profile_clean = clean_profile_data(profile)
        
        print('Cleaning transaction transcript data...')
        transcript_clean = clean_transcript_data(transcript)

        print('Combining datasets to create customer profiles...')
        customer_profiles= create_customer_profiles(profile_clean,portfolio,transcript_clean)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(customer_profiles, database_filepath,'customer_profiles')
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the customer profile, offer portfolio '\
              'and trasaction transcript datasets as the first,second and third argument '\
              'respectively, as well as the filepath of the database to save the cleaned data '\
              'to as the fourth argument. \n\nExample: python process_data.py '\
              'profile.json portfolio.json transcript.json '\
              'StarbucksOffers.db')


if __name__ == '__main__':
    main()