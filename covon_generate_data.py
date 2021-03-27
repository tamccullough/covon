#!/usr/bin/env python
# coding: utf-8

from datetime import date, datetime, timedelta

import gspread as gc
from oauth2client.service_account import ServiceAccountCredentials

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import requests

import covon_functions as com

import time

start = time.time()
theme = 'clean'
today = date.today().strftime('%Y-%m-%d')

utc_today = com.utc_convert(today)
year = today[0:4]
print(year,today,utc_today)

# Load the Ontario Open Data file
on_db = pd.read_csv(f'open-data/{year}/conposcovidloc.csv')
print(on_db.shape)

on_age = pd.read_csv(f'datasets/{year}/age_groups_ontario.csv')
previous = pd.read_csv(f'datasets/{year}/outcomes.csv')
daily_phu_cases = pd.read_csv(f'datasets/{year}/daily_change_in_cases_by_phu.csv')

print(previous)

on_db['utc'] = on_db['Case_Reported_Date'].apply(lambda x: com.utc_convert_batch(x))

on_db['Outcome1'].unique()

print('AS OF TODAY: ',today)

print('TOTAL CASES: ',on_db['Outcome1'].count())
print('RESOLVED: ',on_db[on_db['Outcome1'] == 'Resolved']['Outcome1'].count())
print('NOT RESOLVED: ',on_db[on_db['Outcome1'] == 'Not Resolved']['Outcome1'].count())
print('FATAL: ',on_db[on_db['Outcome1'] == 'Fatal']['Outcome1'].count())

total_cases = on_db['Accurate_Episode_Date'].count()
resolved = on_db[on_db['Outcome1'] == 'Resolved']['Outcome1'].count()
not_resolved = on_db[on_db['Outcome1'] == 'Not Resolved']['Outcome1'].count()
fatalities = on_db[on_db['Outcome1'] == 'Fatal']['Outcome1'].count()

print('PREVIOUS TOTAL CASES CHANGE: ',total_cases-previous.at[0,'count'])
print('PREVIOUS RESOLVED CHANGE: ',resolved-previous.at[1,'count'])
print('PREVIOUS NOT RESOLVED CHANGE: ',not_resolved-previous.at[2,'count'])
print('PREVIOUS FATALITIES CHANGE: ',fatalities-previous.at[3,'count'])

testing = com.get_pie(on_db,'Outcome1',total_cases,'outcome-total_cases')
testing

on_cases = com.get_cases(on_db,total_cases)
on_cases

print('ACTUAL TOTAL CASES: ',int(on_cases['total'].sum()))
print('ACTUAL FATALITIES: ',int(on_cases['fatal-total'].sum()))

fatal = on_cases[['age_group','fatal-f','fatal-m','fatal-gd','fatal-u','fatal-total','fatal%']]
fatal = fatal.sort_values(by='fatal-total',ascending=False)
print(total_cases - int(on_cases['total'].sum()),'cases not assigned to any age group')

print(fatal)

all_cases = com.all_cases_count(on_db)

age_groups = com.get_pie(on_db,'Age_Group',total_cases,'')

recent_cases = on_db[(on_db['utc'] >= utc_today - 16)]
recent_cases = recent_cases.sort_values(by='utc',ascending=False)
recent_groups = com.get_pie(recent_cases,'Age_Group',total_cases,'cases_by_age-16-days')

recent_cases_count = all_cases.tail(16)
recent_cases_count = recent_cases_count.reset_index()
recent_cases_count.pop('index')
recent_cases_count['days'] = recent_cases_count['date'].apply(lambda x: x[-2:])
print(recent_cases_count)

female_16 = recent_cases[recent_cases['Client_Gender'] == 'FEMALE']
male_16 = recent_cases[recent_cases['Client_Gender'] == 'MALE']
genderdiv_16 = recent_cases[recent_cases['Client_Gender'] == 'GENDER DIVERSE']
female_16_count = com.utc_count(female_16)
male_16_count = com.utc_count(male_16)
genderdiv_16_count = com.utc_count(genderdiv_16)

a,b,c,d = [],[],[],[]
for date in recent_cases_count['utc'].unique():
    actual = on_db[on_db['utc'] == date]['Case_Reported_Date'].values[0]
    try:
        m = male_16_count[male_16_count['date'] == date]['count'].values[0]
    except:
        m = 0
    try:
        f = female_16_count[female_16_count['date'] == date]['count'].values[0]
    except:
        f = 0
    try:
        gd = genderdiv_16_count[genderdiv_16_count['date'] == date]['count'].values[0]
    except:
        gd = 0
    a.append(m)
    b.append(f)
    c.append(gd)
    d.append(actual)
recent_cases_count['m_count'] = a
recent_cases_count['f_count'] = b
recent_cases_count['gd_count'] = c
recent_cases_count['actual_date'] = d
recent_cases_count = recent_cases_count.dropna()

gender_groups = com.get_pie(on_db,'Client_Gender',total_cases,'gender-total_cases')

gender_groups_sum = gender_groups['count'].sum()
gender_groups['pop%'] = round(gender_groups['count'] / gender_groups_sum,4)*100

outcomes = com.get_pie(on_db,'Outcome1',total_cases,'outcome-total_cases')
outcomes.loc[-1] = ['Total',total_cases,1.0]
outcomes.index = outcomes.index + 1
outcomes = outcomes.sort_index()
print('\n',outcomes)
print('\n',previous)
print('\n',outcomes.at[0,'count'] - previous.at[0,'count'])

int_lst, flt_lst = [] , []
int_lst.append(int(outcomes.iloc[0]['count'] - previous.iloc[0]['count']))
int_lst.append(int(outcomes.at[1,'count'] - previous.at[1,'count']))
int_lst.append(int(outcomes.at[2,'count'] - previous.at[2,'count']))
int_lst.append(int(outcomes.at[3,'count'] - previous.at[3,'count']))

flt_lst.append(round(int_lst[0] / outcomes.at[0,'count'],4))
flt_lst.append(round(int_lst[1] / outcomes.at[1,'count'],4))
flt_lst.append(round(int_lst[2] / outcomes.at[2,'count'],4))
flt_lst.append(round(int_lst[3] / outcomes.at[3,'count'],4))

change = pd.DataFrame()
change['change'] = int_lst
change['ratio'] = flt_lst

print('\n',change,'\n')
print('fatal check: ',all_cases['fatal'].sum())

phu_cases = com.get_category_count(on_db,'Reporting_PHU_City',total_cases)
cases_date = com.get_category_count(on_db,'Accurate_Episode_Date',total_cases)
fatal = fatal.dropna()
print(fatal)

top_10_phu = phu_cases.head(10)

print(top_10_phu)

recent_cases_count = recent_cases_count.dropna()

recent_top_10_phu = com.get_category_count(recent_cases,'Reporting_PHU_City',total_cases)
recent_top_10_phu = recent_top_10_phu.head(10)
print(recent_top_10_phu)

for i in range(recent_groups.shape[0]):
    recent_groups['pop%'] = recent_groups['count'] / recent_groups['count'].sum()

all_cases.to_csv(f'datasets/{year}/all_cases.csv',index=False)
change.to_csv(f'datasets/{year}/change.csv',index=False)
fatal.to_csv(f'datasets/{year}/fatal.csv',index=False)
gender_groups.to_csv(f'datasets/{year}/gender_infected.csv',index=False)
outcomes.to_csv(f'datasets/{year}/outcomes.csv',index=False)
recent_cases_count.to_csv(f'datasets/{year}/recent_cases_count.csv',index=False)
top_10_phu.to_csv(f'datasets/{year}/top_10_phu.csv',index=False)
recent_top_10_phu.to_csv(f'datasets/{year}/recent_top_10_phu.csv',index=False)
recent_groups.to_csv(f'datasets/{year}/age_groups_recent.csv',index=False)
on_cases.to_csv(f'datasets/{year}/on_cases.csv',index=False)

PATH = '/home/todd/Documents/git/covon/datasets/2021/'#'/home/todd/mldl/datasets/classification/faces/'

def get_all_files(directory):
    file_list = []
    with os.scandir(directory) as files:
        for file in files:
            file_list.append(re.sub('.csv','',file.name))
    return file_list

def import_file(path):
    db = pd.read_csv(path,encoding = 'utf-8')
    return db

def show_info(data):
    print('Shape: ',data.shape)
    print('Columns: ',data.columns.values,'\n')

file_names = get_all_files(PATH)

data = {}
for file in file_names:
    data[file] = import_file(PATH+file+'.csv')

dl = ['change','age_groups_ontario', 'age_groups_positive', 'age_groups_recent',
'all_cases', 'daily_change_in_cases_by_phu', 'fatal', 'gender_infected',
'on_cases', 'outcomes', 'recent_cases_count', 'recent_top_10_phu', 'top_10_phu']

data = { 'change' : change,
        'age_groups_ontario' : on_age,
        'age_groups_recent' : recent_groups,
        'all_cases' : all_cases,
        'fatal' : fatal,
        'gender_infected' : gender_groups,
        'on_cases' : on_cases,
        'outcomes' : outcomes,
        'recent_cases_count' : recent_cases_count,
        'recent_top_10_phu' : recent_top_10_phu,
        'top_10_phu' : top_10_phu}

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/todd/canpl-305914-3c5b02942068.json', scope)
client = gc.authorize(creds)

# Find a workbook by name
sh = client.open('covon-2021-retrieved')

for sheet in dl:
    try:
        db = data[sheet]
        db = db.fillna(0.0)
        worksheet = sh.add_worksheet(title=sheet, rows='50', cols='20')
        worksheet.update([db.columns.values.tolist()] + db.values.tolist())
    except:
        try:
            worksheet = sh.worksheet(sheet)
            worksheet.update([db.columns.values.tolist()] + db.values.tolist())
        except Exception as e:
            print(error)

end = time.time()
job_time = round((end - start),3)
print(job_time)
