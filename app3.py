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

'''setup up input directory'''

input_dir = '../data/input'
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
output_dir = '../data/output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

'''
DOWNLOAD CONTRIBUTIONS, EXPENDITURES, AND OFFICE DATA.
Even though we only have offices from 2000 on,
we download from 1999 on, just for storage and review.
We should eventually enter in the offices data for 1999-2009.
'''

start_date = '01/01/1999'            # set the start datae
end_date = datetime.date.today().strftime("%m/%d/%Y")                # set the end date
current_year = np.int(datetime.date.today().strftime("%Y"))  # get the current year

filename = os.path.join(input_dir, 'all_contributions_1999_current.csv')  # name of the file for conttributions
c_in = dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'con') # con = contributions
contributions = pd.read_csv(io.StringIO(c_in), parse_dates=True)
contributions.to_csv(filename, index=False)

filename = os.path.join(input_dir, 'all_expenditures_1999_current.csv')
e_in = dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'exp')
expenditures = pd.read_csv(io.StringIO(e_in), parse_dates=True)  # exp = expenditures
expenditures.to_csv(filename, index=False)

filename = os.path.join(input_dir, 'all_offices.pkl')
offices = dc_campaign_finance_data.scraper.offices()   # download a list of all offices
# offices = [o.replace('\r\n', '') for o in offices]  # push them into a pickle
with open(filename, 'wb') as f:
    pickle.dump(offices, f)



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
for election_year in range(2010, current_year + 1):   # we start at 2010 bc that's all we have committee -> office data for.
    filename = os.path.join(input_dir, str(election_year) + '_offices_and_committees.csv')  # build a filename for the csv file
    if ((election_year == current_year) or not os.path.isfile(filename)):  # if it's the current year or the file doesn't already exist
        offices_df = pd.DataFrame(columns = ['Election Year', 'Office', 'Committee Name'])  # create a new pandas dataframe
        for office in offices:   # cycle through all the offices
            committee_list = dc_campaign_finance_data.scraper.committees(office, election_year)  # download the committees for that office
            if len(committee_list) > 0:  #  check to see if there are committees to tell us if that office is up for election this year
                for committee in committee_list:  # if so, cycle through the committees
                    row = [{'Election Year': election_year, 'Office': office, 'Committee Name': committee}] # adding a row to the dataframe for each committee
                    offices_df = offices_df.append(row, ignore_index=True)
        offices_df = offices_df[['Election Year', 'Office', 'Committee Name']].drop_duplicates()  # drop duplicates from the dataframe
        offices_df[['Election Year']] = offices_df[['Election Year']].astype(np.int16)
        offices_df.to_csv(filename, index=False)  # save to csv
    else:  # if it's a prior year AND the data has already been saved to csv in the data folder
        offices_df = pd.read_csv(filename)  # load the csv into a pandas dataframe
    offices_df = offices_df[['Election Year', 'Office']].drop_duplicates()  # drop the committees (don't need them here)
    output_json = collections.defaultdict(list)  # push to json, row by row.
    for _, row in offices_df.iterrows():
        row = row.values.tolist()
        election_year, office = row
        output_json[int(election_year)].append(office)
    json_out.update(output_json)
filename = os.path.join(output_dir, 'election years and offices.json')  # save one all info to a json file
with open(filename, 'w') as outfile:
    json.dump(json_out, outfile)


'''
MERGE CONTRIBUTIONS AND EXPENDITURES WITH YEAR-OFFICE-COMMITTEE. Now that we have information
on all the committees running for all the offices for each year, we can generate json files
containing annual contributions and expenditures by year by office by candidate
by mergine the contributions and expenditures data with year/office/committee data.
'''

for election_year in range(2010, current_year + 1):
    con = contributions[['Candidate Name', 'Committee Name', 'Contributor Type', 'Date of Receipt']]
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



