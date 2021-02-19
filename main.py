# Todd McCullough  June 29 2020

from datetime import date, datetime, timedelta
from flask import Flask
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import co_main as com

import db
import functools
import numpy as np
import os
import pandas as pd
import re


theme = 'clean'
today = date.today().strftime('%Y-%m-%d')
year = year = today[0:4]
month, day, weekday = com.get_weekday()

today_other = date.today()
first = today_other.replace(day=1)
previous_month = first - timedelta(days=1)

if (day == "01") and ((month == 'January') or (month == 'March') or (month == 'May') or (month == 'July') or (month == 'October') or (month == 'December')):
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

outcomes = pd.read_csv(f'datasets/{year}/outcomes.csv')
on_age = pd.read_csv(f'datasets/{year}/age_groups_ontario.csv')
recent_groups = pd.read_csv(f'datasets/{year}/age_groups_recent.csv')
all_cases = pd.read_csv(f'datasets/{year}/all_cases.csv')
top_10_phu = pd.read_csv(f'datasets/{year}/top_10_phu.csv')
recent_top_10_phu = pd.read_csv(f'datasets/{year}/recent_top_10_phu.csv')
change = pd.read_csv(f'datasets/{year}/change.csv')
recent_cases_count = pd.read_csv(f'datasets/{year}/recent_cases_count.csv')

total_cases = outcomes.iloc[0]['count']

covon = Flask(__name__, instance_relative_config=True)
covon.config.from_mapping(
        SECRET_KEY='dev', # change to a random value later when deploying
        DATABASE=os.path.join(covon.instance_path, 'main.sqlite'),
    )

@covon.route('/')
def index():

    today = date.today().strftime('%Y-%m-%d')

    utc_today = com.utc_convert(today)

    if (day == "01") and ((month == 'January') or (month == 'March') or (month == 'May') or (month == 'July') or (month == 'October') or (month == 'December')):
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

    outcomes = pd.read_csv(f'datasets/{year}/outcomes.csv')
    on_age = pd.read_csv(f'datasets/{year}/age_groups_ontario.csv')
    recent_groups = pd.read_csv(f'datasets/{year}/age_groups_recent.csv')
    all_cases = pd.read_csv(f'datasets/{year}/all_cases.csv')
    top_10_phu = pd.read_csv(f'datasets/{year}/top_10_phu.csv')
    recent_top_10_phu = pd.read_csv(f'datasets/{year}/recent_top_10_phu.csv')
    change = pd.read_csv(f'datasets/{year}/change.csv')
    recent_cases_count = pd.read_csv(f'datasets/{year}/recent_cases_count.csv')

    total_cases = outcomes.iloc[0]['count']

    on_cases = pd.read_csv(f'datasets/{year}/on_cases.csv')
    on_cases = on_cases.dropna()
    on_cases_data = on_cases.copy()

    under_20 = on_cases[on_cases['age_group'] == '<20']
    under_20 = under_20.reset_index()
    under_20.pop('index')

    gender_groups = pd.read_csv(f'datasets/{year}/gender_infected.csv')
    fatalities = pd.read_csv(f'datasets/{year}/fatal.csv')
    gender_groups['pop%'] = gender_groups['pop%'].apply(lambda x: round(x,4))
    outcomes = pd.read_csv(f'datasets/{year}/outcomes.csv')
    resolved = round(outcomes.at[0,'pop%']*100,2)
    fatal = round(outcomes.at[1,'pop%']*100,2)
    active = round(outcomes.at[2,'pop%']*100,2)

    trend = [recent_cases_count.loc[0,'count'],recent_cases_count.loc[7,'count'],recent_cases_count.loc[15,'count']]
    for col in ['female','male','transgender','total','fatal-f','fatal-m','fatal-t','fatal-u','fatal-total']:
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
    age_cases_lst = create_list(on_cases_data[['age_group','case%']])
    age_groups_positive_lst = create_list(recent_groups[['age_group','pop%']])

    fatal_lst = create_list(fatalities[['age_group','fatal-f','fatal-m','fatal-t']])
    fatal_lst = add_column_string(fatal_lst)

    outcomes_lst = create_list(outcomes)

    recent_gender_lst = create_list(recent_cases_count[['date','m_count','f_count','t_count']])
    recent_gender_lst = add_column_string(recent_gender_lst)

    recent_male_lst = create_list(recent_cases_count[['days','m_count']])
    recent_male_lst = add_column_string(recent_male_lst)

    recent_female_lst = create_list(recent_cases_count[['days','f_count']])
    recent_female_lst = add_column_string(recent_female_lst)

    recent_trans_lst = create_list(recent_cases_count[['days','t_count']])
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
        colors = ['#fa5252','#ffa64a','#88de62','#67bccf','#508ceb','#5199db','#6c51bd','#bf5c90','#fa5252','#ffa64a']
        lst[0].append('style')
        for i in range(1,len(lst)):
            lst[i][1] = int(lst[i][1])
            lst[i].append(colors[i-1])
        return lst

    top_10_phu_lst = append_style(top_10_phu_lst)
    recent_top_10_phu_lst = append_style(recent_top_10_phu_lst)


    print(top_10_phu_lst)
    #print(recent_cases_count[['date','m_count','f_count','t_count']])

    return render_template('co-index.html',
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
