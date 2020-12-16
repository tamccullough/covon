# Todd McCullough  June 29 2020

from datetime import date, datetime, timedelta
from flask import Flask
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import co_main

import db
import functools
import numpy as np
import os
import pandas as pd
import re


theme = 'mono'
month, day, weekday = co_main.get_weekday()

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

on_db = pd.read_csv('datasets/2020/conposcovidloc.csv')
on_age = pd.read_csv('datasets/2020/age_groups_ontario.csv')
change = pd.read_csv('datasets/2020/change.csv')

change = change.astype('str')

total_cases = on_db['Accurate_Episode_Date'].count()

covon = Flask(__name__, instance_relative_config=True)
covon.config.from_mapping(
        SECRET_KEY='dev', # change to a random value later when deploying
        DATABASE=os.path.join(covon.instance_path, 'main.sqlite'),
    )

@covon.route('/')
def index():

    today = date.today().strftime('%Y-%m-%d')

    utc_today = co_main.utc_convert(today)

    on_cases = pd.read_csv('datasets/2020/on_cases.csv')
    on_cases = on_cases.dropna()
    gender_groups = pd.read_csv('datasets/2020/gender_infected.csv')
    gender_groups['pop%'] = gender_groups['pop%'].apply(lambda x: round(x,4))
    infected = pd.read_csv('datasets/2020/infected.csv')
    outcomes = pd.read_csv('datasets/2020/outcomes.csv')
    resolved = round(outcomes.at[0,'pop%']*100,2)
    fatal = round(outcomes.at[1,'pop%']*100,2)
    active = round(outcomes.at[2,'pop%']*100,2)
    for col in ['female','male','transgender','total','fatal-f','fatal-m','fatal-t','fatal-u','fatal-total']:
        on_cases[col] = on_cases[col].astype('int')

    for col in ['case%','f%','m%']:
        on_cases[col] = on_cases[col].apply(lambda x: str(round(x*100,3))+'%')

    return render_template('co-index.html',
    day = day, weekday = weekday, month = month, yesterday = yesterday, last_month = last_month,
    infected = infected, outcomes = outcomes, gender_groups = gender_groups, on_cases = on_cases,
    resolved = resolved, fatal = fatal, active = active, total_cases = total_cases, change = change,
    theme = theme)


db.init_app(covon)

if __name__ == "__main__":
    covon.run()
