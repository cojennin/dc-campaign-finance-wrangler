# This file downloads data from the DC Office of Campaign Finance
# and generates various data tables suitable for graphing.
# It uses @sshanabrook's awesome dc_campaign_finance_data package.

import os
import time
import datetime
import io
from  dc_campaign_finance_scraper import scraper

'''setup up input and output directories'''

input_dir = '../dc-campaign-finance-data/csv'
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
output_dir = '../dc-campaign-finance-data/json'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

'''
DOWNLOAD CONTRIBUTIONS AND EXPENDITURES DATA.
Even though we only have offices data from 2000 on,
we download contribution and expenditure data from 1999 on for storage and review.
We could eventually enter in the offices data for 1999-2009.
'''

start_date = '01/01/2010'
end_date = datetime.date.today().strftime("%m/%d/%Y")

contributions = scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='con')
filename = os.path.join(input_dir, 'contributions.csv')
with open(filename, 'w') as f:
    f.write(contributions.csv)
f.close()

expenditures = scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='exp')
filename = os.path.join(input_dir, 'expenditures.csv')
with open(filename, 'w') as f:
    f.write(expenditures.csv)
f.close()


