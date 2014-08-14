'''
CLEAN AND WRAGLE DATA INTO JSON.
'''

import os
import io
import pandas as pd
import numpy as np

input_dir = '../dc-campaign-finance-data/csv'
output_dir = '../dc-campaign-finance-data/json'

# read in data and clean up a bit
filename = os.path.join(input_dir, 'contributions.csv')
contributions = pd.read_csv(filename)
contributions['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '').str.replace('(', '').str.replace(')', '').astype('float')
contributions = contributions[contributions['Election Year'] > 0]
contributions['Election Year'] = contributions['Election Year'].astype('int16')

# make a list of offices for each election year
yo = contributions[['Election Year', 'Office']]
yo = yo.drop_duplicates()
yo = yo.reset_index()
yo = pd.DataFrame(yo[['Election Year', 'Office']])

# output json files for graphs
for rownum in range(0, len(yo.index)):
    year = yo.iloc[rownum, 0]
    office = yo.iloc[rownum, 1]
    data_out = contributions[(contributions['Election Year'] ==  year)]
    data_out = data_out[(data_out['Office'] ==  office)]
    data_out = data_out[['Candidate Name', 'Contributor', 'Contributor Type', 'Address', 'city', 'state', 'Zip', 'Contribution Type', 'Amount', 'Date of Receipt']]
    json_filename = os.path.join(output_dir, str(year) +' ' + str(office) + '.json')
    data_out.to_json(json_filename, orient = 'records')
