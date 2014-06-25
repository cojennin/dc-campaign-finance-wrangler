# This file downloads data from the DC Office of Campaign Finance
# and generates various data tables suitable for graphing.
# It uses @sshanabrook's awesome dc_campaign_finance_data package.

import os
import time
import datetime
import StringIO
import dc_campaign_finance_data.scraper
import requests
import pandas as pd
import numpy as np
import pickle
import collections
import json

# we use request caching to speed up testing.
import requests_cache
requests_cache.install_cache(allowable_methods=['GET', 'POST'], expire_after=60 * 60 * 6)

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

contributions = pd.read_csv(
    StringIO.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'con')), parse_dates=True)  # con = contributions
filename = os.path.join(data_dir, 'contributions_1999_current.csv')
contributions.to_csv(filename, index=False)

expenditures = pd.read_csv(
    StringIO.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'exp')), parse_dates=True)  # exp = expenditures
filename = os.path.join(data_dir, 'expenditures_1999_current.csv')
expenditures.to_csv(filename, index=False)

offices = dc_campaign_finance_data.scraper.offices()  # download a list of all offices
filename = os.path.join(data_dir, 'offices.csv')
with open(filename, 'wb') as f:
    pickle.dump(offices, f)


# generate a json file with the open offices for each year
# this is a little annoying because it has to be downloaded for each year

json_out = {}
currentYear = np.int(datetime.date.today().strftime("%Y"))
for year in range(2010, currentYear + 1):
    print datetime.datetime.now(), 'generating list of committees running for', year, 'offices:'
    offices_df = pd.DataFrame(columns=['Year', 'Office', 'Committee Name'])
    for office in offices:
        committee_list = dc_campaign_finance_data.scraper.committees(office, year)
        if len(committee_list) > 0:
            for committee in committee_list:
                row = [{'Year': year, 'Office': office, 'Committee Name': committee}]
                offices_df = offices_df.append(row, ignore_index=True)
    offices_df = offices_df[['Year', 'Office', 'Committee Name']].drop_duplicates()
    filename = os.path.join(data_dir, str(year) + '_offices.csv')
    offices_df.to_csv(filename, index=False)
    offices_df = offices_df[['Year', 'Office']]
    output_json = collections.defaultdict(list)
    for _, row in offices_df.iterrows():
        row = row.values.tolist()
        year, office = row
        output_json[int(year)].append(office)
    json_out.update(output_json)
filename = os.path.join(data_dir, 'years and offices.json')
with open(filename, 'w') as outfile:
    json.dump(json_out, outfile)


# generate json files containing annual contributions and expenditures by year by office by candidate
# this is also annoying because it has to be merged with committee and office names which have to be downloaded for each year.

for year in range(2010, currentYear + 1):
    print datetime.datetime.now(), 'generating contributions for', year, 'offices'
    filename = os.path.join(data_dir, str(year) + '_offices.csv')
    offices_df = pd.read_csv(filename)
    con = contributions[['Candidate Name', 'Committee Name', 'Contributor Type', 'Date of Receipt', 'Amount']]
    con['Amount'] = con['Amount'].str.replace(',', '').str.replace('$', '').str.rstrip('.00')
    merged = pd.merge(con, offices_df)
    filename = os.path.join(data_dir, 'merged_' + str(year) + '_contributions.csv')
    merged.to_csv(filename)
    for office in offices:
        committee_list = dc_campaign_finance_data.scraper.committees(office, year)
        if len(committee_list) > 0:
            cyo = merged[merged['Office'] == office]
            cyo_table = pd.pivot_table(cyo, values='Amount', index=['Contributor Type'], columns=['Committee Name'], aggfunc=np.sum)
            cyo_df = pd.DataFrame(cyo_table)
            filename = os.path.join(data_dir, str(year) + ' ' + office + '.json')
            cyo_df.to_json(path_or_buf=filename)

print "ALL DONE!"
