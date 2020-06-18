

################################################################################
############################### MAIN SCRIPT ####################################

# This script is designed to initialise and run a server which displays graphs
# using the data from the QA database.

# Each individual tab is created by a seperate script saved in the 'scripts'
# folder, with this main script calling these individual scripts and as such
# allowing for easier management and development of this application.

# NB: In order to import the scripts in the way used here there must be an empty
# file called __init__.py (https://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path/48468292#48468292)

# Do I need to change this top level statement now tat it's split into two functions?????????????????????????????????????????????????????????????????????????????????????????????????????????

# Need to reference better ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

################################################################################
################################################################################





################################################################################
####################### IMPORT LIBRARIES AND SCRIPTS ###########################

print('\nImporting libraries...')

# Import time and start a timer to do some checks of how long this code is
# taking to run.
import time
start = time.time()

# Import some basic tools from easygui to allow for user interface
from easygui import buttonbox, msgbox

# Import pandas, which is used for datamanagement and the creation of
# dataframes.
import pandas as pd

# Import os to allow manipluation of filepaths etc ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
import os

# Import some basic stuff from bokeh. Just need enough to be able to mainpulate
# the tabs etc. as most of the creation of the graphs will be done within the
# individual tab scripts.
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Import the tab scripts. Each script creates exactly one tab. (As mentioned
# earlier if there are problems importing these scripts then make sure that
# there is an empty file called __init__.py in the scripts folder).
from scripts.GulmayOutput import Gulmay_Output_Graph
from scripts.PhotonOutput import Photon_Output_Graph
from scripts.ElectronEnergy import Electron_Energy_Graph
from scripts.ElectronEnergy2 import Electron_Energy_Graph2
from scripts.JawTravel import JawTravel

# Import pypyodbc as this is how conections to the database can be achieved.
import pypyodbc

# Import some other bokeh and tornado libraries that will allow for the creation
# and running of the server.
from bokeh.server.server import Server
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from tornado.ioloop import IOLoop
from functools import partial

###### Start of patch!
###### Need a fix for running the Tornado Server in Python 3.8 on Windows. This
###### piece of code seems to allow it to run correctly (something about
###### needing to change a Windows default?):
######          https://github.com/tornadoweb/tornado/issues/2751
######          https://github.com/tornadoweb/tornado/issues/2608
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
###### End of patch!

# With the libraries imported run a check to find out how long it took.
endlib = time.time()
print('\nLibraries loaded in: ' + str(endlib - start) + 'sec')

################################################################################





################################################################################
##################### DEFINE GRAPH COMPILING FUNCTION ##########################

# This function produces the main doccument containing all of the graphs, which
# is later called by the main function (defined at the bottom of this file).

# It does this by connecting to the database, passing the cursor to the other
# tab scripts and compiling the tabs into one doccument

################################################################################
################################################################################

def produce_doc(doc):

    ############################################################################
    ############################ USER INTERFACE ################################

    choice = buttonbox('Click on what you want to plot.', 'Graphing Code',
        ('Proton', 'TrueBeam', 'Gulmay', 'Flexitron'))



    ############################################################################
    ###################### CONNECT TO THE DATABASE #############################

    # Tell code where the database is saved
    DatabaseLocation =  'O:/protons/Work in Progress/Christian/Database/' \
                        'Photon/PhysicsQA_beCopy25022020.mdb'

    # Connect to the database. This connection will then be passed on to the tab
    # scripts to allow for reading from the database. Keeping it in the main
    # script to minimise redundant code.
    # Note that there may be issues here if 64-bit python tries to run a 32-bit
    # MS Access Driver.
    conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
							r'DBQ=' + DatabaseLocation + ';'
                    		# May need a line here for the database password????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
                    		)

    # With the connection made run a check to find out how long it took.
    endconn = time.time()
    print('\nConnection made in: ' + str(endconn - endlib) + 'sec')


    ############################################################################
    ######################## CREATE EACH OF THE TABS ###########################

    if choice == 'TrueBeam':
        # Create each tab by running the relevant scripts
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph(conn)
        tab3 = JawTravel(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3])
    elif choice == 'Proton':
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph(conn)
        tab3 = Gulmay_Output_Graph(conn)
        tab4 = JawTravel(conn)
        tab5 = Electron_Energy_Graph2(conn)
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
        tab4 = JawTravel(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])
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
