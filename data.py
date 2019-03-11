# pylint: disable=trailing-newlines,invalid-name,global-statement

'''Variables and functions for data.'''

import io
import logging
import time
import threading
import zipfile

import pandas as pd
import requests

POPULATION_URL = 'http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv'
CO2_URL = 'http://api.worldbank.org/v2/en/indicator/EN.ATM.CO2E.KT?downloadformat=csv'

# This lock is needed to safely modify the data from another thread.
data_lock = threading.Lock()

# Data is in pandas data frames.
population_data = None
co2_data = None

# Previous data update time in Unix time format.
last_update_time = 0
# Data update interval in seconds.
UPDATE_INTERVAL = 3600


def fetch_and_decode_data(url):
    '''Fetch and decode data from the worldbank API

    Arguments:
      url : string
        API url
    Returns:
      success : boolean
        True if successful False if failed
      data : pd.DataFrame or None
        Data in Pandas data frame, None if failed
    '''
    r = requests.get(url)
    if r.status_code != 200:
        logging.warning(
            'Fetching data failed with status code: %s', r.status_code
        )
        return False, None

    # Data is in a ZIP file.
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
    except zipfile.BadZipFile as e:
        logging.warning('Failed to decode zip: %s', e)
        return False, None
    name = b''
    for n in z.namelist():
        if n.startswith('API'):
            name = n
            break
    else:
        logging.warning('Didn\'t find file from ZIP')
        return False, None

    try:
        s = z.read(name).decode('utf-8')
    except UnicodeDecodeError as e:
        logging.warning('Failed to decode data: %s', e)
        return False, None

    # Skip first four lines.
    s = '\n'.join(s.splitlines()[4:])

    try:
        data = pd.read_csv(io.StringIO(s))
    except pd.errors.ParserError as e:
        logging.warning('Pandas failed to parse CSV: %s', e)
        return False, None

    return True, data


def update_data():
    '''Fetch and update data.

    If fetching fails the data will not be updated.
    '''
    logging.info('Updating data')

    ok1, data1 = fetch_and_decode_data(POPULATION_URL)
    ok2, data2 = fetch_and_decode_data(CO2_URL)

    global last_update_time
    last_update_time = time.time()

    if not (ok1 and ok2):
        logging.warning('Updating data failed')
        return

    with data_lock:
        global population_data, co2_data
        population_data = data1
        co2_data = data2
    logging.info('Updating data done')


def periodically_update_data():
    '''Update data periodically.'''
    while True:
        t = time.time()
        time_since_update = t - last_update_time
        time.sleep(max(0, UPDATE_INTERVAL - time_since_update))
        update_data()

