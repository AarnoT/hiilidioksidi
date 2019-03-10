#!/usr/bin/python3

import csv

from flask import Flask, render_template
import requests

app = Flask(__name__)

POPULATION_URL = 'http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv'
CO2_URL = 'http://api.worldbank.org/v2/en/indicator/EN.ATM.CO2E.KT?downloadformat=csv'

@app.route('/')
def main():
    '''Main page of the site.'''
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

