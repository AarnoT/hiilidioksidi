# pylint: disable=trailing-newlines,invalid-name

'''Module for API functions.'''

import logging

from flask import request
import pandas as pd

import data


def countries_sorted():
    '''Return HTML table of countries sorted by emissions.

    Return value also depends on query parameters.
    Request parameters used: per_capita, num
    '''
    with data.data_lock:
        num = int(request.args.get('num', 15))
        if request.args.get('per_capita', 'off') == 'on':
            table = data.co2_data_per_capita[:num]
        else:
            table = data.co2_data[:num]

        table = pd.DataFrame({
            'Country' : table['Country'],
            'Pollution' : table[data.latest_data_year]
        })
        return table.to_html()

