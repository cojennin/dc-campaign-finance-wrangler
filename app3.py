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

local = True


# setup up data directory
data_dir = '../data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


# Download data.  Even though we only have offices from 2000 on, we
# download from 1999 on, just for storage and review.
# We should eventually enter in the offices data.
# We  store the date in sql-lite cache so it's quick after the first time.
# This helps with testing.

start_date = '01/01/1999'            # set the start datae
end_date = datetime.date.today().strftime("%m/%d/%Y")                # set the end date


filename = os.path.join(data_dir, 'all_contributions_1999_current.csv')
if local == True:
    contributions = pd.read_csv(filename)
else:
    contributions = pd.read_csv(
        io.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'con')), parse_dates=True)  # con = contributions
    contributions.to_csv(filename, index=False)

filename = os.path.join(data_dir, 'all_expenditures_1999_current.csv')
if local == True:
    expenditures = pd.read_csv(filename)
else:
    expenditures = pd.read_csv(
        io.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'exp')), parse_dates=True)  # exp = expenditures
    expenditures.to_csv(filename, index=False)

filename = os.path.join(data_dir, 'all_offices.pkl')
if local == True:
    with open(filename, 'rb') as f:
        offices = pickle.load(f)
else:
    offices = dc_campaign_finance_data.scraper.offices()   # download a list of all offices
    with open(filename, 'wb') as f:
        pickle.dump(offices, f)

# generate a json file with the open offices for each year
# this is a little annoying because it has to be downloaded for each year

json_out = {}
current_year = np.int(datetime.date.today().strftime("%Y"))
for election_year in range(2010, current_year + 1):
    print(datetime.datetime.now(), 'generating list of committees for the', election_year, 'elections:')
    filename = os.path.join(data_dir, str(election_year) + '_offices.csv')
    if (not os.path.isfile(filename)): # (election_year == current_year) or
        print('getting offices for ', election_year)
        offices_df = pd.DataFrame(columns=['ElectionYear', 'Office', 'Committee Name'])
        for office in offices:
            committee_list = dc_campaign_finance_data.scraper.committees(office, election_year)
            if len(committee_list) > 0:
                for committee in committee_list:
                    row = [{'Election Year': election_year, 'Office': office, 'Committee Name': committee}]
                    offices_df = offices_df.append(row, ignore_index=True)
        offices_df = offices_df[['Election Year', 'Office', 'Committee Name']].drop_duplicates()
        offices_df.to_csv(filename, index=False)
    else:
        offices_df = pd.read_csv(filename)
    offices_df = offices_df[['Election Year', 'Office']]
    output_json = collections.defaultdict(list)
    for _, row in offices_df.iterrows():
        row = row.values.tolist()
        election_year, office = row
        output_json[int(election_year)].append(office)
    json_out.update(output_json)
filename = os.path.join(data_dir, 'election years and offices.json')
with open(filename, 'w') as outfile:
    json.dump(json_out, outfile)


# generate json files containing annual contributions and expenditures by year by office by candidate
# this is also annoying because it has to be merged with committee and office names which have to be downloaded for each year.

for election_year in range(2010, current_year + 1):
    print(datetime.datetime.now(), 'generating contributions for', election_year, 'offices')
    filename = os.path.join(data_dir, str(election_year) + '_offices.csv')
    offices_df = pd.read_csv(filename)
    con = contributions[['Candidate Name', 'Committee Name', 'Contributor Type', 'Date of Receipt']]
    con['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '')
    merged = pd.merge(con, offices_df)
    filename = os.path.join(data_dir, 'merged_' + str(election_year) + '_contributions.csv')
    merged.to_csv(filename, index = False)
    offices_this_election = offices_df[offices_df['Election Year'] == election_year]
    offices = offices_this_election[['Office']].drop_duplicates()
    print(offices)
    for office in offices:
        print(datetime.datetime.now(), 'generating contributions for', election_year, 'offices')
        print(election_year, office)
        committee_list = offices_this_election[\
            offices_this_election['Election Year'] == election_year and \
            offices['Office'] == office]
        print(committee_list)
        if len(committee_list) > 0:
            cyo = merged[merged['Office'] == office]
            cyo_table = pd.pivot_table(cyo, values='Amount', index=['Contributor Type'], columns=['Committee Name'], aggfunc=np.sum)
            cyo_df = pd.DataFrame(cyo_table)
            filename = os.path.join(data_dir, str(election_year) + ' ' + office + '.json')
            cyo_df.to_json(path_or_buf=filename)

print("ALL DONE!")
