'''
GATHER COMMITTEE LISTS FOR EACH ELECTION YEAR AND OFFICE
generate csv & json files with the open offices for each year
this is a little annoying because it has to be downloaded for each year
'''

import os
import time
import datetime
import io
import dc_campaign_finance_data.scraper
import pandas as pd
import numpy as np
import pickle
import collections
import json

input_dir = '../data/input'
output_dir = '../data/output'
current_year = np.int(datetime.date.today().strftime("%Y"))  # get the current year

filename = os.path.join(input_dir, 'all_contributions_1999_current.csv')  # name of the file for conttributions
contributions = pd.read_csv(filename, parse_dates=True)

filename = os.path.join(input_dir, 'all_offices.pkl')
with open(filename, 'rb') as f:
    offices = pickle.load(f)

offices_df = pd.DataFrame(columns = ['Election Year', 'Office', 'Committee Name'])  # create a new pandas dataframe
for election_year in range(2010, current_year + 1):   # we start at 2010 bc that's all we have committee -> office data for.
    for office in offices:   # cycle through all the offices
        committee_list = dc_campaign_finance_data.scraper.committees(office, election_year)  # download the committees for that office
        if len(committee_list) > 0:  #  check to see if there are committees to tell us if that office is up for election this year
            for committee in committee_list:  # if so, cycle through the committees
                row = [{'Election Year': election_year, 'Office': office, 'Committee Name': committee}] # adding a row to the dataframe for each committee
                offices_df = offices_df.append(row, ignore_index=True)

offices_df = offices_df[['Election Year', 'Office', 'Committee Name']].drop_duplicates()  # drop any duplicates from the dataframe
offices_df[['Election Year']] = offices_df[['Election Year']].astype(np.int16)  # make sure amount is a number

filename = os.path.join(input_dir, 'election_years_offices_and_committees.csv')  # build a filename for the csv file
offices_df.to_csv(filename, index=False)  # save to csv
filename = os.path.join(output_dir, 'election_years_offices_and_committees.json')  # build a filename for the csv file
offices_df.to_json(filename, orient='records')

