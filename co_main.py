# canpl statistics
# Todd McCullough 2020
from datetime import date, datetime, timedelta
from IPython import get_ipython

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import requests
import seaborn as sns
import statistics
from scipy.ndimage.filters import gaussian_filter1d

today = date.today().strftime('%Y-%m-%d')
year = today[0:4]

FACE, EDGE = '#fce5cd', '#073763'
MALE,FEMALE,TRANSGENDER = '#f6b26b','#6d9eeb','#93c47d'
colours3 = ['#cc4125','#f6b26b','#ffd966','#93c47d','#76a5af','#6d9eeb','#6fa8dc','#8e7cc3','#c27ba0','#e06666']

def get_weekday():
    weekDays = ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
    current_year = date.today().strftime('%Y')
    month = datetime.today().strftime('%B')
    today = datetime.today()
    day = datetime.today().strftime('%d')

    weekday_num = today.weekday()
    weekday = weekDays[weekday_num]
    return month, day, weekday

def utc_convert(string):
    day = int(string[8:10])
    month = int(string[5:7])
    year = int(string[:4])
    offset = 693594
    itime = datetime(year,month,day)
    n = itime.toordinal()
    m = (n - offset)
    return m

utc_today = utc_convert(today)

def utc_to_date(utc):
    offset = 693594
    ordinal = offset + int(utc)
    new_date = date.fromordinal(ordinal)
    return new_date

def utc_convert_batch(string):
    today = date.today().strftime('%Y-%m-%d')
    try:
        day = int(string[8:10])
        month = int(string[5:7])
        year = int(string[:4])
        offset = 693594
        itime = datetime(year,month,day)
        n = itime.toordinal()
        m = (n - offset)
        return m
    except:
        return utc_today

def utc_count(dataframe):
    count_16 = dataframe['utc'].values
    unique_dates = dataframe['utc'].unique()
    # fatalalities in past 16 days
    fatal = dataframe[['utc','Outcome1']].copy()
    fatal['fatal'] = [ 1 if x == 'Fatal' else 0 for x in fatal['Outcome1']]
    outcome = fatal.groupby(['utc']).sum()
    outcome = outcome.reset_index()
    a = [[date_,int((count_16 == date_).sum())] for date_ in unique_dates]
    db = pd.DataFrame(a,columns=['date','count'])
    db['actual_date'] = db['date'].apply(lambda x: utc_to_date(x))
    db['days'] = db['actual_date'].apply(lambda x: str(x)[-2:])
    db = db.dropna()
    db['days'] = db['days'].astype(int)
    db['fatal'] = outcome['fatal']
    db = db.sort_values(by='days')
    return db

def case_age_gender(age,gender,on_db):
    results = on_db[(on_db['Client_Gender'] == gender) & (on_db['Age_Group'] == age)]['Case_Reported_Date'].values
    unique_dates = on_db['Accurate_Episode_Date'].unique()
    a = [[date_,int((results == date_).sum())] for date_ in unique_dates]
    db = pd.DataFrame(a,columns=['date','count'])
    db = db.sort_values(by=['date'])
    db['days'] = range(db.shape[0])
    db = db.dropna()
    return db

def all_age_count(age,on_db):
    results = on_db[on_db['Age_Group'] == age]['Case_Reported_Date'].values
    unique_dates = on_db['Accurate_Episode_Date'].unique()
    a = [[date_,int((results == date_).sum())] for date_ in unique_dates]
    db = pd.DataFrame(a,columns=['date','count'])
    db = db.sort_values(by=['date'])
    db['days'] = range(db.shape[0])
    db = db.dropna()
    return db

def all_cases_count(on_db):
    results = on_db[['Case_Reported_Date','Outcome1']].copy()
    results['date'] = results['Case_Reported_Date']
    results['sick'] = results['Outcome1'].apply(lambda x: 1 if x == 'Not Resolved' else 0)
    results['resolved'] = results['Outcome1'].apply(lambda x: 1 if x == 'Resolved' else 0)
    results['fatal'] = results['Outcome1'].apply(lambda x: 1 if x == 'Fatal' else 0)
    results['count'] = results['sick'] + results['resolved'] + results['fatal']
    results.pop('Case_Reported_Date')
    results.pop('Outcome1')
    results = results.groupby('date').sum()
    results = results.sort_values(by=['date'])
    results['days'] = range(results.shape[0])
    results = results.dropna()
    results = results.reset_index()
    results['utc'] = results['date'].apply(lambda x: utc_convert(x))
    #results = results[results.date.str.contains(year)]
    return results

def all_deaths_count(on_db):
    results = [x for x in on_db['Accurate_Episode_Date']]
    deaths = [1 if x == 'Fatal' else 0 for x in on_db['Outcome1']]
    db = pd.DataFrame()
    db['date'] = results
    db['deaths'] = deaths
    db = db.groupby('date').sum()
    db = db.sort_values(by=['date'])
    db['days'] = range(db.shape[0])
    db = db.dropna()
    return db

def f(x,y,z):
    return sum([x,y,z],1)/3

def find_explode(lst,data):
    a = [0.1 if i == data else 0 for i in lst]
    return a

def get_bar(dataframe,string,total_cases,title):
    query = string
    results = get_category_count(dataframe,query,total_cases)
    query = re.sub('\d+','',query.lower())
    graph_bar(results,query,title)
    return results

def get_category_count(dataframe,column,total_cases):
    a=[]
    for query in dataframe[column].unique():
        count = dataframe[dataframe[column] == query].count()[0]
        percentage = round(count / total_cases,2)
        a.append([query,count,percentage])
    string = column.lower()
    string = re.sub('\d+','',string)
    data = pd.DataFrame(a,columns=[string,'count','pop%'])
    data = data.sort_values(by='count',ascending=False)
    data = data.reset_index()
    data.pop('index')
    data = data[data[string] != 'UNKNOWN']
    data = data[data[string] != 'OTHER']
    data = data.dropna()
    return data

def get_pie(dataframe,string,total_cases,title):
    query = string
    results = get_category_count(dataframe,query,total_cases)
    return results

def graph_bar(dataframe,column,title):
    total_count = int(on_cases[on_cases['age_group'] == query]['total'])
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    plt.rcParams['text.color'] = COLOUR
    plt.rcParams['font.size'] = 12
    ax = plt.subplot()
    ax.set_facecolor(FACE)
    ax.plot(x_1,y_1,'.-',lw=2,color=colours3[9],alpha=0.75,label='male')
    ax.plot(x_2,y_2,'.-',lw=2,color=colours3[6],alpha=0.75,label='female')
    ax.plot(x_3,y_3,'.-',lw=2,color=colours3[4],alpha=0.75,label='transgender')
    ax.plot(x_3,(y_1+y_2+y_3),'--',lw=2,color=colours1[0],alpha=0.2,label='total')
    ax.set_xlabel('days')
    ax.set_ylabel('count')
    #ax.set_title(f'{query} Total Cases {total_count}',color=COLOUR)
    ax.legend(loc='upper left')
    filename = f'static/images/graph/{query}-total_count.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

def graph_frame(x,y):
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.plot(x,y,'.-',lw=2,alpha=0.5,color=colours3[1],label='count')
    ax1.plot(x,y.rolling(window=7).mean(),'.-',lw=2,color=colours3[0],label='rolling average')
    ax1.set_title('')
    filename = f'static/images/graph/ontario-daily_cases_count.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    ## total cumulative
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax2 = plt.subplot()
    ax2.set_facecolor(FACE)
    ax2.plot(x,y.cumsum(),'-',lw=2,color=colours3[0])
    ax2.fill_between(x, y.cumsum(),facecolor=colours3[0],alpha=0.35,label='cumulative')

    ax2.set_xlabel('days',color=EDGE)
    ax2.set_ylabel('count',color=EDGE)
    ax2.set_title('')
    filename = f'static/images/graph/ontario-daily_cases-total_count.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

def graph_pie(dataframe,column,title):
    plt.figure()
    plt.rcParams['text.color'] = EDGE
    plt.rcParams['font.size'] = 14
    labels = dataframe[column].unique()
    sizes = dataframe['count'].tolist()
    explode = find_explode(sizes,dataframe['count'].max())
    fig, ax1 = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(8)
    fig.set_facecolor(FACE)
    ax1.pie(sizes, explode = explode, labels=labels, autopct='%1.1f%%',startangle=45,colors=colours3)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #ax1.set_title(f'Ontario: Total Cases by {column.upper()}\n')
    filename = f'static/images/pie/{title}.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

def graph_query_frame(x_1,y_1,x_2,y_2,x_3,y_3,query,on_cases):
    total_count = int(on_cases[on_cases['age_group'] == query]['total'])
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    rolling = y_1.rolling(window=7).mean()+y_2.rolling(window=7).mean()+y_3.rolling(window=7).mean()
    total = y_1+y_2+y_3
    ax1.plot(x_3,total,'.-',lw=2,color=colours3[1],alpha=0.5,label=f'{query} total')
    ax1.plot(x_3,rolling,'.-',lw=2,color=colours3[0],label='rolling average')
    ax1.set_xlabel('days',color=EDGE)
    ax1.set_ylabel('count',color=EDGE)
    ax1.set_title('',color=EDGE)
    ax1.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    total_count = int(on_cases[on_cases['age_group'] == query]['total'])
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax2 = plt.subplot()
    ax2.set_facecolor(FACE)
    ax2.plot(x_1,y_1,'.-',lw=2,color=MALE,alpha=0.9,label='male')
    ax2.set_xlabel('days',color=EDGE)
    ax2.set_ylabel('count',color=EDGE)
    ax2.set_title('',color=EDGE)
    ax2.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-male.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax3 = plt.subplot()
    ax3.set_facecolor(FACE)
    ax3.plot(x_2,y_2,'.-',lw=2,color=FEMALE,alpha=0.9,label='female')
    ax3.set_xlabel('days',color=EDGE)
    ax3.set_ylabel('count',color=EDGE)
    ax3.set_title('',color=EDGE)
    ax3.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-female.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax4 = plt.subplot()
    ax4.set_facecolor(FACE)
    ax4.plot(x_3,y_3,'.-',lw=2,color=TRANSGENDER,alpha=0.9,label='transgender')
    ax4.set_xlabel('days',color=EDGE)
    ax4.set_ylabel('count',color=EDGE)
    ax4  .set_title('',color=EDGE)
    ax4.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-transgender.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

def get_cases(on_db,total_cases):
    on_cases = pd.DataFrame()
    j = 0
    for age in on_db['Age_Group'].unique():
        for gender in on_db['Client_Gender'].unique():
            count = on_db[(on_db['Age_Group'] == age) & (on_db['Client_Gender'] == gender)].count()[0]
            percentage = round(count / total_cases,2)
            if gender == 'FEMALE':
                on_cases.at[j,'age_group'] = age
                on_cases.at[j,'female'] = count
            elif gender == 'MALE':
                on_cases.at[j,'male'] = count
            elif gender == 'GENDER DIVERSE':
                on_cases.at[j,'transgender'] = count
            else:
                on_cases.at[j,'unspecified'] = count
        j = j + 1

    on_cases['total'] = on_cases['female'] + on_cases['male'] + on_cases['transgender'] + on_cases['unspecified']
    on_cases['case%'] = round(on_cases['total'] / on_cases['total'].sum(),2)
    on_cases['f%'] = round(on_cases['female'] / on_cases['total'],2)
    on_cases['m%'] = round(on_cases['male'] / on_cases['total'],2)
    #on_cases['fatal'] = round(on_cases['male'] / on_cases['total'],2)
    on_cases = on_cases.sort_values(by='age_group',ascending=False)
    on_cases = on_cases.reset_index()
    on_cases.pop('index')

    on_fatal = pd.DataFrame()
    j = 0
    for age in on_db['Age_Group'].unique():
        for gender in on_db['Client_Gender'].unique():
            fatal = on_db[(on_db['Age_Group'] == age) & (on_db['Client_Gender'] == gender) & (on_db['Outcome1'] == 'Fatal')].count()[0]
            percentage = round(fatal / total_cases,2)
            if gender == 'FEMALE':
                on_fatal.at[j,'age_group'] = age
                on_fatal.at[j,'fatal-f'] = fatal
            elif gender == 'MALE':
                on_fatal.at[j,'fatal-m'] = fatal
            elif gender == 'GENDER DIVERSE':
                on_fatal.at[j,'fatal-t'] = count
            else:
                on_fatal.at[j,'fatal-u'] = count
        j = j + 1

    on_fatal['total'] = on_fatal['fatal-f'] + on_fatal['fatal-m'] + on_fatal['fatal-t'] + on_fatal['fatal-u']
    on_fatal['case%'] = round(on_fatal['total'] / on_fatal['total'].sum(),2)
    on_fatal['f%'] = round(on_fatal['fatal-f'] / on_fatal['total'],2)
    on_fatal['m%'] = round(on_fatal['fatal-m'] / on_fatal['total'],2)
    on_fatal = on_fatal.sort_values(by='age_group',ascending=False)
    on_fatal = on_fatal.reset_index()
    on_fatal.pop('index')
    on_cases['fatal-f'] = on_fatal['fatal-f']
    on_cases['fatal-m'] = on_fatal['fatal-m']
    on_cases['fatal-u'] = on_fatal['fatal-u']
    on_cases['fatal-t'] = on_fatal['fatal-t']
    on_cases['fatal-total'] = on_fatal['total']
    on_cases['fatal%'] = on_fatal['case%']
    on_cases = on_cases.sort_values(by='total',ascending=False)
    on_cases = on_cases.reset_index()
    on_cases.pop('index')
    on_cases.to_csv('datasets/2020/on_cases.csv',index=False)
    return on_cases
