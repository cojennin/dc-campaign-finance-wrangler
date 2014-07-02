'''
MERGE CONTRIBUTIONS DATA WITH ELECTION-YEAR-OFFICE-COMMITTEE DATA. Now that we have information
on all the committees running for all the offices for each year, we can generate json files
containing annual contributions and expenditures by year by office by candidate
by mergine the contributions and expenditures data with year/office/committee data.
'''

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

input_dir = '../data/input'
output_dir = '../data/output'

filename = os.path.join(input_dir, 'election_years_offices_and_committees.csv')
eyoc = pd.read_csv(filename)
eyoc['Election Year'] = eyoc['Election Year'].astype(np.int16)

filename = os.path.join(input_dir, 'all_contributions_1999_current.csv')
contributions = pd.read_csv(filename)
contributions['Amount'] = contributions['Amount'].astype(np.float64)

merged = pd.merge(contributions, eyoc, how = 'left', on = 'Committee Name')  # add office and election year to data
merged = merged[np.isfinite(merged['Election Year'])]  # drop data from election years prior to 2010

yo = eyoc[['Election Year', 'Office']]
yo = yo.drop_duplicates()
yo = yo.reset_index()
yo = pd.DataFrame(yo[['Election Year', 'Office']])

for rownum in range(0, len(yo.index)):
    year = yo.iloc[rownum, 0]
    office = yo.iloc[rownum, 1]
    data_out = merged[(merged['Election Year'] ==  year)]
    data_out = data_out[(data_out['Office'] ==  office)]
    data_out = data_out[['Candidate Name', 'Contributor', 'Address', 'city', 'state', 'Zip', 'Contribution Type', 'Amount', 'Date of Receipt']]
    filename = os.path.join(output_dir, str(year) +' ' + str(office) + '.json')
    data_out.to_json(filename, orient = 'records')
    summary_out = pd.tools.pivot.pivot_table(data_out, values='Amount', index=['Contribution Type'], cols=['Candidate Name'], aggfunc=np.sum)
    filename = os.path.join(output_dir, 'summary ' + str(year) +' ' + str(office) + '.json')
    summary_out.to_json(filename)
