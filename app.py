# This file does two things.
# First, it downloads data from the DC Office of Campaign Finance
# using Saul Shanabrook's awesome dc_campaign_finance_data package.
# Second, it imports that data into pandas and generates various
# data tables suitable for graphing.
#
# For development purposes, there is verbose progress printng that
# will ultimately be pushed to a log file instead.

from datetime import datetime
import dc_campaign_finance_data.scraper
import pandas as pd
import numpy as np
import csv
import os
import StringIO
import collections
import json
import requests
import requests_cache
requests_cache.install_cache(allowable_methods=['GET', 'POST'], expire_after=60 * 60 * 6)


# first we grab the data & put into local files for munging
data_dir = '../data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
currentYear = datetime.now().year
start_date = '01/01/2010'                           # set the start datae
end_date = '12/31/' + str(currentYear)                # set the end date
print datetime.now(), 'downloading offices'
offices = dc_campaign_finance_data.scraper.offices()    # get list of offices for all years
print datetime.now(), 'downloading contributions'
contributions = pd.read_csv(StringIO.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'con')))  # con = contributions
filename = os.path.join(data_dir, 'contributions.csv')
contributions.to_csv(filename)
print datetime.now(), 'downloading expenditures'
expenditures = pd.read_csv(StringIO.StringIO(dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'exp')))  # con = contributions
filename = os.path.join(data_dir, 'expenditures.csv')
expenditures.to_csv(filename)
print datetime.now(), 'downloading done!'


# In order to make the data more useful in our pivot tables,
# we need to add a columng that indicates for which office each candidate is running.
# These offices are matched with committee names by the OCF, so that's what we'll use.

# Load data into pandas & convert dollars to float

print datetime.now(), 'loading contributions into pandas'
filename = os.path.join(data_dir, 'contributions_2010_current.csv')
contributions = pd.read_csv(filename, converters={'Amount': lambda x: float(x.replace('$', '').replace(',', '').replace('(', '').replace(')', ''))})
contributions['Zip'] = contributions['Zip'].astype('object')
contributions.to_csv(filename)

print datetime.now(), 'loading expenditures into pandas'
filename = os.path.join(data_dir, 'expenditures_2010_current.csv')
expenditures = pd.read_csv(filename, converters={'Amount': lambda x: float(x.replace('$', '').replace(',', '').replace('(', '').replace(')', ''))})
expenditures.to_csv(filename)

print datetime.now(), 'data loaded!'


# generate a json file with the open offices for each year
# this is a little annoying because it has to be downloaded for each year

json_out = {}
for year in range(2010, currentYear + 1):
    print datetime.now(), 'generating list of committees running for', year, 'offices:'
    offices_df = pd.DataFrame(columns=['Year', 'Office', 'Committee Name'])
    for office in offices:
        committee_list = dc_campaign_finance_data.scraper.committees(office, year)
        if len(committee_list) > 0:
            for committee in committee_list:
                row = [{'Year': year, 'Office': office}]
                offices_df = offices_df.append(row, ignore_index=True)
    offices_df = offices_df[['Year', 'Office']].drop_duplicates()
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

for year in range(2010, currentYear + 1):
    print datetime.now(), 'generating contributions for', year, 'offices:'
    offices_df = pd.DataFrame(columns=['Committee Name', 'Office'])
    filename = os.path.join(data_dir, 'merged_' + str(year) + '_contributions.csv')
    merged = pd.read_csv(filename)
    for office in offices:
        committee_list = dc_campaign_finance_data.scraper.committees(office, year)
        if len(committee_list) > 0:
            cyo = merged[merged['Office'] == office]
            cyo_table = pd.pivot_table(cyo, values='Amount', index=['Contributor Type'], columns=['Committee Name'], aggfunc=np.sum)
            cyo_df = pd.DataFrame(cyo_table)
            filename = os.path.join(data_dir, str(year) + ' ' + office + '.json')
            cyo_df.to_json(path_or_buf=filename)

print "ALL DONE!"
