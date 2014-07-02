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

filename = os.path.join(input_dir, 'all_contributions_1999_current.csv')  # name of the file for conttributions
contributions = dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'con') # con = contributions
contributions = pd.read_csv(io.StringIO(contributions), parse_dates=True)
contributions['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '').str.replace('(', '').str.replace(')', '').astype('float')
contributions.to_csv(filename, index=False)

filename = os.path.join(input_dir, 'all_expenditures_1999_current.csv')
expenditures = dc_campaign_finance_data.scraper.records_csv(start_date, end_date, 'exp')
expenditures = pd.read_csv(io.StringIO(expenditures), parse_dates=True)  # exp = expenditures
expenditures.to_csv(filename, index=False)

filename = os.path.join(input_dir, 'all_offices.pkl')
offices = dc_campaign_finance_data.scraper.offices()   # download a list of all offices
# offices = [o.replace('\r\n', '') for o in offices]  # push them into a pickle
with open(filename, 'wb') as f:
    pickle.dump(offices, f)


