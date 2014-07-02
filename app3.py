# This file downloads data from the DC Office of Campaign Finance
# and generates various data tables suitable for graphing.
# It uses @sshanabrook's awesome dc_campaign_finance_data package.

import os
import time
import datetime
import io
import dc_campaign_finance_data.scraper
import requests
import pandas as pd
import numpy as np
import pickle
import collections
import json

'''setup up directories'''

input_dir = '../data/input'
output_dir = '../data/output'


'''
WHY IS THE FOLLOWING MUNGING NECESSARY?  The contributions & expenditures data don't include
information about which office the candidate is running. Nor does it tell us to which election
year the contribution is relevant.  but we can get that information from the committee list
for each election year and office, and then merge this information.
'''

'''
GATHER COMMITTEE LISTS FOR EACH ELECTION YEAR AND OFFICE
generate csv & json files with the open offices for each year
this is a little annoying because it has to be downloaded for each year
to make it slightly less annoying, it checks to see if a prior year has
already been downloaded and saved. If so, it just uses the saved file.
But it always downloads the current year.
'''

json_out = {}  # create a json set for election years and committes
offices_df = pd.DataFrame(columns = ['Election Year', 'Office', 'Committee Name'])  # create a new pandas dataframe
filename = os.path.join(input_dir, str(election_year) + 'election_years_offices_and_committees.csv')  # build a filename for the csv file
for election_year in range(2010, current_year + 1):   # we start at 2010 bc that's all we have committee -> office data for.
    for office in offices:   # cycle through all the offices
        committee_list = dc_campaign_finance_data.scraper.committees(office, election_year)  # download the committees for that office
        if len(committee_list) > 0:  #  check to see if there are committees to tell us if that office is up for election this year
            for committee in committee_list:  # if so, cycle through the committees
                row = [{'Election Year': election_year, 'Office': office, 'Committee Name': committee}] # adding a row to the dataframe for each committee
                offices_df = offices_df.append(row, ignore_index=True)
offices_df = offices_df[['Election Year', 'Office', 'Committee Name']].drop_duplicates()  # drop any duplicates from the dataframe
offices_df[['Election Year']] = offices_df[['Election Year']].astype(np.int16)
return(offices_df)
offices_df.to_csv(filename, index=False)  # save to csv
offices_df.to_json('election_years_offices_and_committees.json')





'''
MERGE CONTRIBUTIONS AND EXPENDITURES WITH YEAR-OFFICE-COMMITTEE. Now that we have information
on all the committees running for all the offices for each year, we can generate json files
containing annual contributions and expenditures by year by office by candidate
by mergine the contributions and expenditures data with year/office/committee data.
'''

for election_year in range(2010, current_year + 1):
    con = contributions[['Candidate Name', 'Contributor Name', 'Address', 'State', 'Zip', 'Contribution Type', 'Date of Receipt']]
    con['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '').str.replace('(', '').str.replace(')', '').astype('float')
    filename = os.path.join(input_dir, str(election_year) + '_offices_and_committees.csv')
    offices_df = pd.read_csv(filename)
    merged = pd.merge(con, offices_df)
    offices_this_election = offices_df[offices_df['Election Year'] == election_year]
    offices = offices_this_election[['Office']].drop_duplicates()
    offices_list = offices['Office'].tolist()
    for office in offices_list:
        committee_list = offices_this_election[offices_this_election['Office'] == office]
        if len(committee_list) > 0:
            cyo = merged[merged['Office'] == office]
            cyo_table = pd.pivot_table(cyo, values='Amount', index=['Contributor Type'], columns=['Candidate Name'], aggfunc=np.sum)
            cyo_df = pd.DataFrame(cyo_table)
            filename = os.path.join(output_dir, str(election_year) + ' ' + office + '.json')
            cyo_df.to_json(path_or_buf=filename)



'''
Saul's list:
Candidate Name
Contributor Name
Address
State
Zip
Contribution Type
Amount
Date of Receipt
'''



