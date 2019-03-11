#!/usr/bin/python3
# pylint: disable=trailing-newlines,invalid-name

'''Main module for a CO2-emission Flask app'''

import logging
from logging.config import dictConfig
import os
import threading

from flask import Flask, render_template, request

import api
import data
import logging_config

dictConfig(logging_config.config)

app = Flask(__name__)
app.add_url_rule('/countries_sorted', 'countries_sorted', api.countries_sorted)


@app.route('/')
def main():
    '''Main page of the site.'''
    num = request.args.get('num', '15')
    per_capita = request.args.get('per_capita', 'off')
    with data.data_lock:
        return render_template('index.html', per_capita=per_capita, num=num)


if __name__ == '__main__':
    data.update_data()

    # This thread is a daemon, so it stops when the main thread is done.
    thread = threading.Thread(target=data.periodically_update_data, daemon=True)
    logging.info('Starting data update thread')
    thread.start()

    logging.info('Starting app')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

