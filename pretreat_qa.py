import pandas as pd
# import os
import json
from bokeh.models.widgets import CheckboxGroup
# from easygui import buttonbox, msgbox  # User input
import pypyodbc  # Connection to database
# from bokeh.models.widgets import Tabs  # To manipulate tabs on server

# Import other bokeh and tornado libraries that will allow for the creation
# and running of the server.
# from bokeh.server.server import Server
# from bokeh.application.handlers import FunctionHandler
# from bokeh.application import Application
# from tornado.ioloop import IOLoop

# Need a fix for running the Tornado Server in Python 3.8 on Windows. This
# piece of code seems to allow it to run correctly (something about
# needing to change a Windows default?):
# https://github.com/tornadoweb/tornado/issues/2751
# https://github.com/tornadoweb/tornado/issues/2608
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print('Libraries imported')

with open('config.json') as config_file:
    config = json.load(config_file)


DATABASE_DIR = config["DATABASE_DIR"]


def db_connect(DATABASE_DIR, *, pswrd=''):
    '''
    Function to connect to connect to the access database at location defined
    by the DATABASE_DIR input. Connection will fail if password is required
    but not supplied
    '''

    if pswrd != '':
        pswrd = f'PWD={pswrd}'

    conn = pypyodbc.connect(
            'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            'DBQ=' + DATABASE_DIR + ';'
            + pswrd
            )
    return conn


conn = db_connect(DATABASE_DIR)

df = pd.read_sql('select * from [MRI_Coils_Check]', conn)
print(df)
coils = list(df['coil'].unique())
print(coils)
coil_selection = CheckboxGroup(labels=coils, active=[0, 1])
coil_selection.on_change('active', update)

print(df)
