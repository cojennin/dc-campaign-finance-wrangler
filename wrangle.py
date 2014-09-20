'''
CLEAN AND WRAGLE DATA INTO JSON
'''

import os
import io
import pandas as pd
import numpy as np

input_dir = '../dc-campaign-finance-data/csv'
output_dir = '../dc-campaign-finance-watch/json'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# read in data and clean up a bit
filename = os.path.join(input_dir, 'ocf_contributions.csv')
contributions = pd.read_csv(filename)
contributions['Amount'] = contributions['Amount'].str.replace(',', '').str.replace('$', '').str.replace('(', '').str.replace(')', '').astype('float')
contributions = contributions[contributions['Election Year'] == 2014]
contributions['Election Year'] = contributions['Election Year'].astype('int16')

# make a list of offices for each election year
yo = contributions[['Election Year', 'Office']]
yo = yo.drop_duplicates()
yo = yo.reset_index()
yo = pd.DataFrame(yo[['Election Year', 'Office']]).sort(['Election Year', 'Office'],ascending=[0,1])
json_filename = os.path.join(output_dir, 'years and offices.json')
yo.to_json(json_filename, orient = 'records')


# json files for grass-roots contributor count graphs
nested = '['
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
    cols = '[{"label": "Candidate", "type": "string"},{"label": "Grass Roots Contributors", "type": "number"}]'
    rows = '['
    for rnum in range(0, len(data.index)):
        rows = rows + '["' + data['Candidate Name'][rnum] + '", ' + str(data['DC Donors'][rnum]) + ']'
        if rnum + 1 < len(data.index): rows = rows + ','
    rows = rows + ']'
    title = str(office) + ' (' + str(year) + ')'
    options = '{  "title": "' + title + '",  "hAxis": {"title": "Grassroots Contributors (DC Residents)"}, "legend": "none"}'
    graphjson = '{"year": "'+ str(year) + '", "title": "' +  title + '", "cols": ' + cols + ', "rows": ' + rows + ', "options": ' + options + '}'
    graphjson = graphjson.replace("'", '"')
    if len(rows) > 3:
        nested = nested + graphjson
        if rownum +1 < len(yo.index):
            nested = nested + ','
nested = nested + ']'
nested = nested.replace('\n', '').replace('\r', '').replace('},]', '}]')

output_dir = '../dc-campaign-finance-watch/json'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nested_filename = os.path.join(output_dir, 'grass-roots.json')
with open(nested_filename, 'w') as f:
    f.write(nested)
f.close()

# json files for corporate contributor count graphs
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nested = '['
for rownum in range(0, len(yo.index)):
    year = yo.iloc[rownum, 0]
    office = yo.iloc[rownum, 1]
    data = contributions[contributions['Election Year'] ==  year]
    data = data[(data['Office'] ==  office) & (data['state'] ==  'DC')]
    data = data[( (data['Contributor'].str.contains('LLP')) | (data['Contributor'].str.contains('LLC')) | (data['Contributor Type'].str.contains('Business')) | (data['Contributor Type'].str.contains('Corp')) | (data['Contributor Type'].str.contains('Partnership')) )]
    data['unique'] = data['Contributor'] + data['Address']
    data = data[['Candidate Name', 'unique']].drop_duplicates()
    data['Corp Donors'] = 1
    data = data.groupby(['Candidate Name']).sum()
    data = data.sort(['Corp Donors'],ascending=False).reset_index()
    data = data[['Candidate Name', 'Corp Donors']]
    cols = '[{"label": "Candidate", "type": "string"},{"label": "Corporate Contributors", "type": "number"}]'
    rows = '['
    for rnum in range(0, len(data.index)):
        rows = rows + '["' + data['Candidate Name'][rnum] + '", ' + str(data['Corp Donors'][rnum]) + ']'
        if rnum + 1 < len(data.index): rows = rows + ','
    rows = rows + ']'
    title = str(office) + ' (' + str(year) + ')'
    options = '{  "title": "' + title + '",  "hAxis": {"title": "Corporate Contributors"}, "legend": "none"}'
    graphjson = '{"year": "'+ str(year) + '", "title": "' +  title + '", "cols": ' + cols + ', "rows": ' + rows + ', "options": ' + options + '}'
    graphjson = graphjson.replace("'", '"')
    if len(rows) > 3:
        nested = nested + graphjson
        if rownum +1 < len(yo.index):
            nested = nested + ','
nested = nested + ']'
nested = nested.replace('\n', '').replace('\r', '').replace('},]', '}]')

output_dir = '../dc-campaign-finance-watch/json'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nested_filename = os.path.join(output_dir, 'corporate.json')
with open(nested_filename, 'w') as f:
    f.write(nested)
f.close()

