'''
CLEAN AND WRAGLE DATA INTO JSON
'''

import os
import io
import pandas as pd
import numpy as np

input_dir = '../dc-campaign-finance-data/csv'
output_dir = '../dc-campaign-finance-data/json'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# read in data and clean up a bit
filename = os.path.join(input_dir, 'ocf_contributions.csv')
contributions = pd.read_csv(filename)
contributions['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '').str.replace('(', '').str.replace(')', '').astype('float')
contributions = contributions[contributions['Election Year'] > 2009]
contributions['Election Year'] = contributions['Election Year'].astype('int16')

# make a list of offices for each election year
yo = contributions[['Election Year', 'Office']]
yo = yo.drop_duplicates()
yo = yo.reset_index()
yo = pd.DataFrame(yo[['Election Year', 'Office']]).sort(['Election Year', 'Office'],ascending=[0,1])
json_filename = os.path.join(output_dir, 'years and offices.json')
yo.to_json(json_filename, orient = 'records')



# json files for grass-roots graphs
output_dir = '../dc-campaign-finance-data/json/grass-roots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nested = ''
for rownum in range(0, len(yo.index)):
    year = yo.iloc[rownum, 0]
    office = yo.iloc[rownum, 1]
    data = contributions[contributions['Election Year'] ==  year]
    data = data[(data['Office'] ==  office) & (data['state'] ==  'DC') & (data['Contributor Type'] == 'Individual')]
    data['unique'] = data['Contributor'] + data['Address']
    data = data[['Candidate Name', 'unique']].drop_duplicates()
    data['DC Donors'] = 1
    data = data.groupby(['Candidate Name']).sum()
    data = data.sort(['DC Donors'],ascending=False).reset_index()
    data = data[['Candidate Name', 'DC Donors']]
    tpa = pd.np.array(data.transpose())
    names = tpa[0].tolist()
    donors = tpa[1].tolist()
    graphjson = '[' + str(names) + ',' + str(donors) + ']'
    graphjson = graphjson.replace("'", '"')
    json_filename = os.path.join(output_dir, str(year) +' ' + str(office) + '.json')
    with open(json_filename, 'w') as f:
        f.write(graphjson)
    f.close()


    json_head = '''
    {
        "year": "''' + str(year) + '''",
        "office": "''' + str(office) + '''",
        "data": '''
    if rownum == 0:
        json_head = '[' + json_head
    json_tail = '''
    }'''
    if rownum < (len(yo.index) - 1):
        json_tail = json_tail + ''','''
    elif rownum == (len(yo.index) - 1):
        json_tail = json_tail + '''
]'''
    nested = nested + json_head + graphjson + json_tail

output_dir = '../dc-campaign-finance-data/json'
nested_filename = os.path.join(output_dir, 'grass-roots.json')
with open(nested_filename, 'w') as f:
    f.write(nested)
f.close()



# json files for corporate graphs
output_dir = '../dc-campaign-finance-data/json/corporate'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nested = ''
for rownum in range(0, len(yo.index)):
    year = yo.iloc[rownum, 0]
    office = yo.iloc[rownum, 1]
    data = contributions[contributions['Election Year'] ==  year]
    data = data[data['Office'] ==  office]
    data = data[(data['Contributor Type'] == 'Corporation') | (data['Contributor Type'] == 'Corporate Sponsored PAC') | (data['Contributor Type'] == 'Business')]
    data['unique'] = data['Contributor'] + data['Address']
    data = data[['Candidate Name', 'unique']].drop_duplicates()
    data['Corporate Donors'] = 1
    data = data.groupby(['Candidate Name']).sum()
    data = data.sort(['Corporate Donors'],ascending=False).reset_index()
    data = data[['Candidate Name', 'Corporate Donors']]
    tpa = pd.np.array(data.transpose())
    names = tpa[0].tolist()
    donors = tpa[1].tolist()
    graphjson = '[' + str(names) + ',' + str(donors) + ']'
    graphjson = graphjson.replace("'", '"')
    json_filename = os.path.join(output_dir, str(year) +' ' + str(office) + '.json')
    with open(json_filename, 'w') as f:
        f.write(graphjson)
    f.close()

    json_head = '''
    {
        "year": "''' + str(year) + '''",
        "office": "''' + str(office) + '''",
        "data": '''
    if rownum == 0:
        json_head = '[' + json_head
    json_tail = '''
    }'''
    if rownum < (len(yo.index) - 1):
        json_tail = json_tail + ''','''
    elif rownum == (len(yo.index) - 1):
        json_tail = json_tail + '''
]'''
    nested = nested + json_head + graphjson + json_tail

output_dir = '../dc-campaign-finance-data/json'
nested_filename = os.path.join(output_dir, 'corporate.json')
with open(nested_filename, 'w') as f:
    f.write(nested)
f.close()


