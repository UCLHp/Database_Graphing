print('Importing libraries...')
import pandas as pd
import os

from easygui import buttonbox, msgbox  # User input
import pypyodbc  # Connection to database
from bokeh.models.widgets import Tabs  # To manipulate tabs on server

# Import some other bokeh and tornado libraries that will allow for the creation
# and running of the server.
from bokeh.server.server import Server
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from tornado.ioloop import IOLoop

###### Need a fix for running the Tornado Server in Python 3.8 on Windows. This
###### piece of code seems to allow it to run correctly (something about
###### needing to change a Windows default?):
######          https://github.com/tornadoweb/tornado/issues/2751
######          https://github.com/tornadoweb/tornado/issues/2608
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print('Libraries imported')

DATABASE_DIR =  C:\Users\cgillies.UCLH\NHS\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\QAandCommissioning\MRI Philips Ingenia Ambition\QAworkup\PreTreatQA.accdb'


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

def produce_doc(doc):

    conn = db_connect(DATABASE_DIR)


    ############################################################################
    ######################## CREATE EACH OF THE TABS ###########################

    if choice == 'TrueBeam':
        # Create each tab by running the relevant scripts
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph_Old(conn)
        tab3 = JawTravel(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3])
    elif choice == 'Proton':
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph(conn)
        tab3 = Flexitron_Output_Graph(conn)
        tab4 = Gulmay_Output_Graph(conn)
        tab5 = JawTravel(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3, tab4, tab5])
    elif choice == 'Gulmay':
        tab1 = Gulmay_Output_Graph(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1])
    elif choice == 'Flexitron':
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph(conn)
        tab3 = Gulmay_Output_Graph(conn)
        tab4 = hello(conn)
        tab5 = JawTravel(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3, tab4, tab5])
    else:
        msgbox('Error')
        exit()

    # Put all of the tabs into the doccument
    doc.add_root(tabs)

    # With the tabs made run a check to find out how long it took.
    endconn = time.time()
    print('\nTabs made in: ' + str(endconn - endlib) + 'sec')

    return doc





################################################################################
######################### DEFINE MAIN FUNCTION #################################

# This function creates a server and opens it in a web browser. It calls the
# produce_doc function defined above, opening this document (containing the
# bokeh graphs) within the browser.

# This code was originally written by VR (Bill).
# Commented and altered by CB (Christian)

################################################################################
################################################################################

def main():

    print('\nPreparing a bokeh application.')

    ############################################################################
    ####################### DEFINE VARIABLES FOR SERVER ########################

    # From what I (CB) understand this is a way to build the bokeh server within
    # the programme without needing to use the bokeh server command line tool.
    # https://docs.bokeh.org/en/latest/docs/reference/application/handlers/function.html
    # Start an Input/Output Loop. (Specifically a Tornado asynchronous I/O Loop)
    io_loop = IOLoop.current()
    # Define port for server
    port = 5001
    # Create kwargs which will be fed into the server function as keyworded
    # arguments.
    kwargs =    {
                'io_loop': io_loop,
                'port': port,
                }
    # Define the application using the bokeh application function handler.
    app = Application(FunctionHandler(produce_doc))


    ############################################################################
    ############################ CREATE THE SERVER #############################

    # Define the server
    # http://matthewrocklin.com/blog/work/2017/06/28/simple-bokeh-server
    server = Server({'/' : app},  **kwargs)
    # Start running the server
    server.start()
    print('\nOpening Bokeh application on http://localhost:5001/')
    # Display the server
    server.show('/')
    # Start the Input/Output Loop
    io_loop.start()





################################################################################
############################### RUN MAIN #######################################

main()




















#
