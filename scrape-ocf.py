# This file downloads data from the DC Office of Campaign Finance
# and generates various data tables suitable for graphing.
# It uses @sshanabrook's awesome dc_campaign_finance_data package.

import datetime
from dc_campaign_finance_scraper import scraper
from simple_bucket import SimpleBucket
import yaml

'''
DOWNLOAD CONTRIBUTIONS AND EXPENDITURES DATA.
Even though we only have offices data from 2000 on,
we download contribution and expenditure data from 1999 on for storage and review.
We could eventually enter in the offices data for 1999-2009.
'''

#Could probably use some logical grouping
start_date = '01/01/1990'
end_date = datetime.date.today().strftime("%m/%d/%Y")
prefix = "csv"

#Get our configuration options
config_file = open("config.yml", 'r')
config = yaml.safe_load(config_file)
config_file.close()

print("Fetching contributions...")
contributions = scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='con')
print("Fetching expenditures...")
expenditures = scraper.records_with_office_and_election_year(from_date=start_date, to_date=end_date, report_type='exp')

bucket = SimpleBucket(config['aws']['s3']['aws_key_id'],
                      config['aws']['s3']['aws_secret_key'],
                      config['aws']['s3']['bucket_name'])
bucket.save([prefix, "ocf-contributions.csv"], contributions)
bucket.save([prefix, "ocf-expenditures.csv"], expenditures)