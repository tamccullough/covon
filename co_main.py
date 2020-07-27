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

COLOUR = '#073763'
FACE, EDGE = '#fce5cd', '#073763'
D1, D2 = '#fad0a3','#f7ba78'
colours1 = ['#980000','#ff0000','#ff9900','#ffff00','#00ff00','#00ffff','#4a86e8','#0000ff','#9900ff','#ff00ff']
colours2 = ['#e6b8af','#f4cccc','#fce5cd','#fff2cc','#d9ead3','#d0e0e3','#c9daf8','#cfe2f3','#d9d2e9','#ead1dc']
colours3 = ['#cc4125','#e06666','#f6b26b','#ffd966','#93c47d','#76a5af','#6d9eeb','#6fa8dc','#8e7cc3','#c27ba0']

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
    a = []
    for date in dataframe['utc'].unique():
        count = int((count_16 == date).sum())
        a.append([date,count])
    db = pd.DataFrame(a,columns=['date','count'])
    db['days'] = range(db.shape[0])
    db['days'] = (db['days'] -16)*-1
    #db = db[db['count'] != 0]
    db = db.dropna()
    return db

def case_age_gender(age,gender,on_db):
    results = on_db[(on_db['Client_Gender'] == gender) & (on_db['Age_Group'] == age)]['Case_Reported_Date'].values
    a = []
    for date in on_db['Accurate_Episode_Date'].unique():
        count = int((results == date).sum())
        a.append([date,count])
    db = pd.DataFrame(a,columns=['date','count'])
    db['days'] = range(db.shape[0])
    #db = db[db['count'] != 0]
    db = db.dropna()
    return db

def all_cases_count(on_db):
    results = on_db['Accurate_Episode_Date'].values
    a = []
    for date in on_db['Accurate_Episode_Date'].unique():
        count = int((results == date).sum())
        a.append([date,count])
    db = pd.DataFrame(a,columns=['date','count'])
    db['days'] = range(db.shape[0])
    #db = db[db['count'] != 0]
    db = db.dropna()
    return db

def f(x,y,z):
    return sum([x,y,z],1)/3

def graph_query_frame(x_1,y_1,x_2,y_2,x_3,y_3,query,on_cases):
    total_count = int(on_cases[on_cases['age_group'] == query]['total'])
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    rolling = y_1.rolling(window=7).mean()+y_2.rolling(window=7).mean()+y_3.rolling(window=7).mean()
    total = y_1+y_2+y_3
    ax1.plot(x_3,total,'.-',lw=2,color=colours3[8],alpha=0.5,label=f'{query} total')
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
    ax2.plot(x_1,y_1,'.-',lw=2,color=colours3[2],alpha=0.9,label='male')
    ax2.set_xlabel('days',color=EDGE)
    ax2.set_ylabel('count',color=EDGE)
    ax2.set_title('',color=EDGE)
    ax2.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-male.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax3 = plt.subplot()
    ax3.set_facecolor(FACE)
    ax3.plot(x_2,y_2,'.-',lw=2,color=colours3[6],alpha=0.9,label='female')
    ax3.set_xlabel('days',color=EDGE)
    ax3.set_ylabel('count',color=EDGE)
    ax3.set_title('',color=EDGE)
    ax3.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-female.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax4 = plt.subplot()
    ax4.set_facecolor(FACE)
    ax4.plot(x_3,y_3,'.-',lw=2,color=colours3[4],alpha=0.9,label='transgender')
    ax4.set_xlabel('days',color=EDGE)
    ax4.set_ylabel('count',color=EDGE)
    ax4  .set_title('',color=EDGE)
    ax4.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/{query}-total_count-transgender.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

def graph_frame(x,y):
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.plot(x,y,'.-',lw=2,alpha=0.5,color=colours3[8],label='count')
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

def find_explode(lst,data):
    a=[]
    for i in lst:
        if i == data:
            a.append(0.1)
        else:
            a.append(0)
    return a

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


def get_pie(dataframe,string,total_cases,title):
    query = string
    results = get_category_count(dataframe,query,total_cases)
    query = re.sub('\d+','',query.lower())
    graph_pie(results,query,title)
    return results

def get_bar(dataframe,string,total_cases,title):
    query = string
    results = get_category_count(dataframe,query,total_cases)
    query = re.sub('\d+','',query.lower())
    graph_bar(results,query,title)
    return results


## download the ontario open data file and then update all associated database files and image files
utc_today = utc_convert(today)


def update_files(utc_today):
    today = date.today().strftime('%Y-%m-%d')
    #get_ipython().system("curl 'https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv' > 'datasets/2020/conposcovidloc.csv'")

    url = 'https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv'
    r = requests.get(url, allow_redirects=True)
    open('datasets/2020/conposcovidloc.csv', 'wb').write(r.content)

    a=[]

    utc_today = utc_convert(today)

    on_db = pd.read_csv('datasets/2020/conposcovidloc.csv')
    on_age = pd.read_csv('datasets/2020/age_groups_ontario.csv')

    COLOUR = '#073763'
    FACE, EDGE = '#fce5cd', '#073763'
    D1, D2 = '#fad0a3','#f7ba78'
    colours1 = ['#980000','#ff0000','#ff9900','#ffff00','#00ff00','#00ffff','#4a86e8','#0000ff','#9900ff','#ff00ff']
    colours2 = ['#e6b8af','#f4cccc','#fce5cd','#fff2cc','#d9ead3','#d0e0e3','#c9daf8','#cfe2f3','#d9d2e9','#ead1dc']
    colours3 = ['#cc4125','#e06666','#f6b26b','#ffd966','#93c47d','#76a5af','#6d9eeb','#6fa8dc','#8e7cc3','#c27ba0']

    plt.rcParams['text.color'] = EDGE
    plt.rcParams['font.size'] = 26
    plt.rcParams['xtick.color'] = EDGE
    plt.rcParams['ytick.color'] = EDGE
    plt.rcParams['axes.edgecolor'] = colours3[5]
    plt.rcParams['figure.max_open_warning'] = 0
    plt.rcParams['figure.autolayout'] = True

    url = 'https://en.wikipedia.org/wiki/Demographics_of_Ontario'

    on_db['utc'] = on_db['Case_Reported_Date'].apply(lambda x: utc_convert_batch(x))

    total_cases = on_db['Accurate_Episode_Date'].count()
    total_cases

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
            elif gender == 'TRANSGENDER':
                on_cases.at[j,'transgender'] = count
            elif gender == 'OTHER':
                on_cases.at[j,'other'] = count
            else:
                on_cases.at[j,'unknown'] = count
        j = j + 1

    on_cases['total'] = on_cases['female'] + on_cases['male'] + on_cases['transgender'] + on_cases['unknown'] + on_cases['other']
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
            #count = on_db[(on_db['Age_Group'] == age) & (on_db['Client_Gender'] == gender)].count()[0]
            fatal = on_db[(on_db['Age_Group'] == age) & (on_db['Client_Gender'] == gender) & (on_db['Outcome1'] == 'Fatal')].count()[0]
            percentage = round(fatal / total_cases,2)
            if gender == 'FEMALE':
                on_fatal.at[j,'age_group'] = age
                on_fatal.at[j,'fatal-f'] = fatal
            elif gender == 'MALE':
                on_fatal.at[j,'fatal-m'] = fatal
            elif gender == 'TRANSGENDER':
                on_fatal.at[j,'fatal-t'] = fatal
            elif gender == 'OTHER':
                on_fatal.at[j,'fatal-o'] = fatal
            else:
                on_fatal.at[j,'fatal-u'] = fatal
        j = j + 1

    on_fatal['total'] = on_fatal['fatal-f'] + on_fatal['fatal-m'] + on_fatal['fatal-t'] + on_fatal['fatal-u'] + on_fatal['fatal-o']
    on_fatal['case%'] = round(on_fatal['total'] / on_fatal['total'].sum(),2)
    on_fatal['f%'] = round(on_fatal['fatal-f'] / on_fatal['total'],2)
    on_fatal['m%'] = round(on_fatal['fatal-m'] / on_fatal['total'],2)
    on_fatal = on_fatal.sort_values(by='age_group',ascending=False)
    on_fatal = on_fatal.reset_index()
    on_fatal.pop('index')
    on_cases['fatal-f'] = on_fatal['fatal-f']
    on_cases['fatal-m'] = on_fatal['fatal-m']
    on_cases['fatal-t'] = on_fatal['fatal-t']
    on_cases['fatal-o'] = on_fatal['fatal-o']
    on_cases['fatal-u'] = on_fatal['fatal-u']
    on_cases['fatal-total'] = on_fatal['total']
    on_cases['fatal%'] = on_fatal['case%']
    on_cases = on_cases.sort_values(by='total',ascending=False)
    on_cases = on_cases.reset_index()
    on_cases.pop('index')
    on_cases.to_csv('datasets/2020/on_cases.csv',index=False)

    fatal = on_cases[['age_group','fatal-f','fatal-m','fatal-t','fatal-u','fatal-total','fatal%']]
    fatal = fatal.sort_values(by='fatal-total',ascending=False)
    fatal.to_csv('datasets/2020/fatal.csv',index=False)

    all_cases = all_cases_count(on_db)

    graph_frame(all_cases['days'],all_cases['count'])

    for age in ['<20','20s','30s','40s','50s','60s','70s','80s','90s']:
        males = case_age_gender(age,'MALE',on_db)
        females = case_age_gender(age,'FEMALE',on_db)
        transgender = case_age_gender(age,'TRANSGENDER',on_db)
        graph_query_frame(males['days'],males['count'],females['days'],females['count'],transgender['days'],transgender['count'],age,on_cases)


    plt.figure()
    plt.rcParams['text.color'] = COLOUR
    plt.rcParams['font.size'] = 14
    labels = on_age['age_groups'].unique()
    labels = labels[:-1]
    sizes = on_age['count'].tolist()
    sizes = sizes[:-1]
    explode = find_explode(sizes,max(sizes))
    fig, ax1 = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(8)
    fig.set_facecolor(FACE)
    ax1.pie(sizes, explode = explode, labels=labels, autopct='%1.1f%%',startangle=45,colors=colours3)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #ax1.set_title('Ontario: Age Group as % of Population\n')
    filename = f'static/images/pie/ontario-age_groups.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)


    age_groups = get_pie(on_db,'Age_Group',total_cases,'all_ages-total_cases')

    recent_cases = on_db[(on_db['utc'] >= utc_today - 16)]
    recent_cases = recent_cases.sort_values(by='utc',ascending=False)
    recent_groups = get_pie(recent_cases,'Age_Group',total_cases,f'cases_by_age-16-days')

    recent_count = recent_cases['utc'].values
    a = []
    for date in recent_cases['utc'].unique():
        count = int((recent_count == date).sum())
        a.append([date,count])
    recent_cases_count = pd.DataFrame(a,columns=['date','count'])
    recent_cases_count['days'] = range(recent_cases_count.shape[0])
    recent_cases_count['days'] = (recent_cases_count['days'] -16)*-1
    recent_cases_count = recent_cases_count.dropna()

    recent_cases_count = utc_count(recent_cases)

    #graph_frame(recent_cases_count['days'],recent_cases_count['count'])
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.plot(recent_cases_count['days'],recent_cases_count['count'],'.-',lw=2,alpha=0.5,color=colours3[8],label='count')
    ax1.plot(recent_cases_count['days'],recent_cases_count['count'].rolling(window=4).mean(),'.-',lw=2,color=colours3[0],label='rolling average')
    ax1.set_title('')
    ax1.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/ontario-recent_daily_cases_count.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    female_16 = recent_cases[recent_cases['Client_Gender'] == 'FEMALE']
    male_16 = recent_cases[recent_cases['Client_Gender'] == 'MALE']
    transgender_16 = recent_cases[recent_cases['Client_Gender'] == 'TRANSGENDER']
    female_16_count = utc_count(female_16)
    male_16_count = utc_count(male_16)
    transgender_16_count = utc_count(transgender_16)

    a,b,c,d = [],[],[],[]
    for date in recent_cases_count['date'].unique():
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
            t = transgender_16_count[transgender_16_count['date'] == date]['count'].values[0]
        except:
            t = 0
        a.append(m)
        b.append(f)
        c.append(t)
        d.append(actual)
    recent_cases_count['m_count'] = a
    recent_cases_count['f_count'] = b
    recent_cases_count['t_count'] = c
    recent_cases_count['actual_date'] = d
    recent_cases_count = recent_cases_count.dropna()

    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax2 = plt.subplot()
    ax2.set_facecolor(FACE)
    #rolling = recent_cases_count['m_count'].rolling(window=4).mean()
    ax2.plot(recent_cases_count['days'],recent_cases_count['m_count'],'.-',lw=2,color=colours3[2],alpha=0.9,label='male')
    #ax2.plot(recent_cases_count['days'],rolling,'.-',lw=2,color=colours3[0],label='rolling average')
    ax2.set_xlabel('days',color=EDGE)
    ax2.set_ylabel('count',color=EDGE)
    ax2.set_title('',color=EDGE)
    ax2.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/16-days-total_count-male.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax3 = plt.subplot()
    ax3.set_facecolor(FACE)
    #rolling = recent_cases_count['f_count'].rolling(window=4).mean()
    ax3.plot(recent_cases_count['days'],recent_cases_count['f_count'],'.-',lw=2,color=colours3[6],alpha=0.9,label='female')
    #ax3.plot(recent_cases_count['days'],rolling,'.-',lw=2,color=colours3[0],label='rolling average')
    ax3.set_xlabel('days',color=EDGE)
    ax3.set_ylabel('count',color=EDGE)
    ax3.set_title('',color=EDGE)
    ax3.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/16-days-total_count-female.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)
    plt.figure(figsize=(10,3), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax4 = plt.subplot()
    ax4.set_facecolor(FACE)
    ax4.plot(recent_cases_count['days'],recent_cases_count['t_count'],'.-',lw=2,color=colours3[4],alpha=0.9,label='transgender')
    ax4.set_xlabel('days',color=EDGE)
    ax4.set_ylabel('count',color=EDGE)
    ax4  .set_title('',color=EDGE)
    ax4.legend(loc='upper left',framealpha=0)
    filename = f'static/images/graph/16-days-total_count-transgender.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    gender_groups = get_pie(on_db,'Client_Gender',total_cases,'gender-total_cases')
    gender_groups.to_csv('datasets/2020/gender_infected.csv',index=False)

    outcomes = get_pie(on_db,'Outcome1',total_cases,'outcome-total_cases')
    outcomes.to_csv('datasets/2020/outcomes.csv',index=False)

    a, j = [], 0
    for i in outcomes['pop%']:
        people = int(round(i*1000,2)/38)
        a.append(people)
    if sum(a) > 25:
        new_a = max(a) - 1
        t = a.index(max(a))
        a.remove(max(a))
        a.insert(t,new_a)

    a = outcomes['pop%'].tolist()

    o=["fa fa-user beige-text-blue","fa fa-user w3-text-black","fa fa-user beige-text-red"]
    lst=[]
    k = 0
    for i in a:
        b = i * 100
        for j in range(int(b)):
            lst.append(o[k])
        k = k + 1

    lst2=[]
    cnt = 0
    for i in range(10):
        lsu=[]
        for j in range(10):
            v = lst[cnt]
            lsu.extend([v])
            cnt = cnt + 1
        lst2.append(lsu)

    infected = pd.DataFrame(lst2,columns=['1','2','3','4','5','6','7','8','9','10'])
    infected.to_csv('datasets/2020/infected.csv',index=False)

    phu_cases = get_category_count(on_db,'Reporting_PHU_City',total_cases)
    cases_date = get_category_count(on_db,'Accurate_Episode_Date',total_cases)

    width=0.9

    top_10_phu = phu_cases.head(10)
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.barh(top_10_phu['reporting_phu_city'],top_10_phu['count'], width, color=colours3)
    plt.gca().invert_yaxis()
    filename = f'static/images/bar/ontario-reporting_phu_city-top10.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    recent_top_10_phu = get_category_count(recent_cases,'Reporting_PHU_City',total_cases)
    recent_top_10_phu = recent_top_10_phu.head(10)
    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.barh(recent_top_10_phu['reporting_phu_city'],recent_top_10_phu['count'], width, color=colours3)
    plt.gca().invert_yaxis()
    filename = 'static/images/bar/ontario-reporting_phu_city-top10-recent.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.barh(fatal['age_group'], fatal['fatal-f'], width, color=colours3[0])
    ax1.barh(fatal['age_group'], fatal['fatal-m'], width, left=fatal['fatal-f'], color=colours3[5])
    plt.gca().invert_yaxis()
    plt.legend(['Female', 'Male'])
    filename = f'static/images/bar/fatalities.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    plt.figure(figsize=(10,10), dpi=80, facecolor=FACE,edgecolor=EDGE)
    ax1 = plt.subplot()
    ax1.set_facecolor(FACE)
    ax1.barh(recent_cases_count['actual_date'], recent_cases_count['f_count'], width, color=colours3[0])
    ax1.barh(recent_cases_count['actual_date'], recent_cases_count['m_count'], width, left=recent_cases_count['f_count'], color=colours3[5])
    plt.gca().invert_yaxis()
    plt.legend(['Female', 'Male'])
    filename = 'static/images/bar/last16day-cases.png'
    plt.savefig(filename, facecolor=FACE,edgecolor=EDGE)

    text_file = open('previous.txt','w')
    text_file.write(today)
    text_file.close()
