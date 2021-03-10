# Todd McCullough  June 29 2020

from datetime import date, datetime, timedelta
from flask import Flask
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import covon_functions as com

import db
import functools
import numpy as np
import os
import pandas as pd
import re
import requests


theme = 'clean'
today = date.today().strftime('%Y-%m-%d')
year = year = today[0:4]
month, day, weekday = com.get_weekday()
geegle = ['#fa5252','#ffa64a','#88de62','#67bccf','#508ceb','#5199db','#6c51bd','#bf5c90','#fa5252','#ffa64a']
cfc = ['#264653','#2a9d8f','#1f8bff','#904c77','#f05d23','#e76f51','#e9c46a','#ccc9dc','#ddd5d0','#f6f8ff']
coolor = ["#f94144","#f3722c","#f8961e","#f9844a","#f9c74f","#90be6d","#43aa8b","#4d908e","#577590","#277da1"]#["#67ff86","#51e5ff","#c25bd7","#e63746","#ff990a","#ebeb0a","#0cd44f","#196eb3","#5f05b3","#871c38","#67ff86","#51e5ff",]
today_other = date.today()
first = today_other.replace(day=1)
previous_month = first - timedelta(days=1)

if (day == "01") and ((month == 'January') or (month == 'May') or (month == 'July') or (month == 'October') or (month == 'December')):
    yesterday = '30'
    last_month = previous_month.strftime('%B')
elif (day == "01") and ((month == 'April') or (month == 'June') or (month == 'September') or (month == 'November') or (month == 'August') or (month == 'February')):
    yesterday = '31'
    last_month = previous_month.strftime('%B')
elif (day == "01") and (month == 'March'):
    yesterday = '28'
    last_month = previous_month.strftime('%B')
else:
    yesterday = str(int(day)-1)
    last_month = month

covon = Flask(__name__, instance_relative_config=True)
covon.config.from_mapping(
        SECRET_KEY='dev', # change to a random value later when deploying
        DATABASE=os.path.join(covon.instance_path, 'main.sqlite'),
    )

@covon.route('/')
def index():

    utc_today = com.utc_convert(today)

    # connect to GOOGLE spreadsheets
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ800Sn_3lHT7yioCGQSIBkw7Hde2TJ979yp_IQrsURozajU4XJORDqSVfcvg-ZHKv0gt1MiL4C2cf9/pubhtml#'
    r = requests.get(url)
    results = pd.read_html(r.text,header=1, index_col=0)

    for i in range(len(results)):
        results[i] = results[i].reset_index()
        results[i].pop('1')

    change = results[0]
    on_age = results[1]
    recent_groups = results[3]
    all_cases = results[4]
    fatalities = results[6]
    gender_groups = results[7]
    on_cases = results[8]
    outcomes = results[9]
    recent_cases_count = results[10]
    recent_top_10_phu = results[11]
    top_10_phu = results[12]
    total_cases = outcomes.iloc[0]['count']

    on_cases = on_cases.dropna()
    on_cases_data = on_cases.copy()

    under_20 = on_cases[on_cases['age_group'] == '<20']
    under_20 = under_20.reset_index()
    under_20.pop('index')

    gender_groups['pop%'] = gender_groups['pop%'].apply(lambda x: round(x,4))
    resolved = round(outcomes.at[0,'pop%']*100,2)
    fatal = round(outcomes.at[1,'pop%']*100,2)
    active = round(outcomes.at[2,'pop%']*100,2)

    trend = [recent_cases_count.loc[0,'count'],recent_cases_count.loc[7,'count'],recent_cases_count.loc[15,'count']]
    for col in ['female','male','gender diverse','total','fatal-f','fatal-m','fatal-gd','fatal-u','fatal-total']:
        on_cases[col] = on_cases[col].astype('int')

    for col in ['case%','f%','m%']:
        on_cases[col] = on_cases[col].apply(lambda x: str(round(x*100,3))+'%')

    def check_x(x):
        check = type(x).__name__
        if check == 'int':
            return int(x)
        elif check == 'str':
            return x
        else:
            return float(x)

    def create_list(data):
        lst = []
        lst.append([x for x in data.columns])
        for i in range(data.shape[0]):
            lst.append([check_x(x) for x in data.loc[i]])
        return lst

    def add_column_string(lst):
        for i in range(1,len(lst)):
            lst[i][0] = str(lst[i][0])
        return lst

    all_cases_lst = create_list(all_cases[['days','count']])
    #all_cases_lst = all_cases_lst[0:20]
    timeline = len(all_cases_lst)
    print(f'\nTIMELINE;\n{timeline}\n')
    all_fatal_lst = create_list(all_cases[['days','fatal']])

    age_pie_lst = create_list(on_age[['age_groups','pop%']])
    print('!!!!!!!!!!!!!!!!')
    print(age_pie_lst)
    print('!!!!!!!!!!!!!!!!')
    age_cases_lst = create_list(on_cases_data[['age_group','case%']])
    age_groups_positive_lst = create_list(recent_groups[['age_group','pop%']])

    fatal_lst = create_list(fatalities[['age_group','fatal-f','fatal-m','fatal-gd']])
    fatal_lst = add_column_string(fatal_lst)

    outcomes_lst = create_list(outcomes)

    recent_gender_lst = create_list(recent_cases_count[['date','m_count','f_count','gd_count']])
    recent_gender_lst = add_column_string(recent_gender_lst)

    recent_male_lst = create_list(recent_cases_count[['days','m_count']])
    recent_male_lst = add_column_string(recent_male_lst)

    recent_female_lst = create_list(recent_cases_count[['days','f_count']])
    recent_female_lst = add_column_string(recent_female_lst)

    recent_trans_lst = create_list(recent_cases_count[['days','gd_count']])
    recent_trans_lst = add_column_string(recent_trans_lst)

    recent_cases_lst = create_list(recent_cases_count[['days','count']])
    recent_cases_lst = add_column_string(recent_cases_lst)

    recent_fatal_lst = create_list(recent_cases_count[['days','fatal']])
    recent_fatal_lst = add_column_string(recent_fatal_lst)

    top_10_phu_lst = create_list(top_10_phu[['reporting_phu_city','count']])
    top_10_phu_lst = add_column_string(top_10_phu_lst)


    recent_top_10_phu_lst = create_list(recent_top_10_phu[['reporting_phu_city','count']])
    recent_top_10_phu_lst = add_column_string(recent_top_10_phu_lst)

    def append_style(lst):
        colors = coolor
        lst[0].append('style')
        for i in range(1,len(lst)):
            lst[i][1] = int(lst[i][1])
            lst[i].append(colors[i-1])
        return lst

    top_10_phu_lst = append_style(top_10_phu_lst)
    recent_top_10_phu_lst = append_style(recent_top_10_phu_lst)


    print(top_10_phu_lst)
    #print(recent_cases_count[['date','m_count','f_count','t_count']])

    return render_template('co-index.html',theme = theme,
    day = day, weekday = weekday, month = month, yesterday = yesterday, last_month = last_month,
    outcomes = outcomes, gender_groups = gender_groups, on_cases = on_cases, fatalities = fatalities,
    trend = trend, on_age = on_age, outcomes_lst = outcomes_lst, timeline = timeline,
    recent_male_lst = recent_male_lst, recent_female_lst = recent_female_lst, recent_trans_lst = recent_trans_lst,
    age_pie_lst = age_pie_lst, age_cases_lst = age_cases_lst, age_groups_positive_lst = age_groups_positive_lst,
    fatal_lst = fatal_lst, all_cases_lst = all_cases_lst, all_fatal_lst = all_fatal_lst, under_20 = under_20,
    top_10_phu_lst = top_10_phu_lst, recent_top_10_phu_lst = recent_top_10_phu_lst,
    recent_cases_lst = recent_cases_lst, recent_fatal_lst = recent_fatal_lst, recent_gender_lst = recent_gender_lst,
    resolved = resolved, fatal = fatal, active = active, total_cases = total_cases, change = change)


db.init_app(covon)

if __name__ == "__main__":
    covon.run()
