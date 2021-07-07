
'''
This script is designed to initialise and run a server which displays graphs
using the data from the QA database.

Each individual tab is created by a seperate script saved in the 'scripts'
folder, with this main script calling these individual scripts and as such
allowing for easier management and development of this application.

NB: MS Access on trust PCs is 32-bit. 64-bit python cannot run a 32-bit MS
Access driver therefore this code will only work with 32-bit python.

'''

####################### IMPORT LIBRARIES AND SCRIPTS ###########################

print('\nImporting libraries...')

# Import time and start a timer
import time
start = time.time()

# Import some basic tools from easygui to allow for user interface
import easygui as eg
import pandas as pd
import pypyodbc
import os
import webbrowser
import multiprocessing

# For reading config files
from configparser import ConfigParser

# Import some stuff from bokeh and tornado libraries to maniulate tabs and
# create/run the server.
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.server.server import Server
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from tornado.ioloop import IOLoop
from functools import partial

# Import the tab scripts.
from scripts.GulmayOutput import Gulmay_Output_Graph
from scripts.PhotonOutput import Photon_Output_Graph
from scripts.ElectronEnergyOld import Electron_Energy_Graph_Old
from scripts.ElectronEnergy import Electron_Energy_Graph
from scripts.JawTravel import JawTravel
from scripts.FlexitronOutput import Flexitron_Output_Graph
from scripts.Sym import Sym_Graph
from scripts.ElectronOutput import Electron_Output_Graph

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

endlib = time.time()
print('\nLibraries loaded in: ' + str(endlib - start) + 'sec')

################################################################################



def produce_doc(doc):

    '''
    This function produces the doccument containing all of the graphs, which
    is later called by the main function.

    It does this by connecting to the database, passing the cursor to the other
    tab scripts and compiling the tabs into one doccument
    '''

    # Read config stuff
    basedir = os.path.dirname(sys.argv[0])
    print(basedir)
    config_file = os.path.join(basedir, 'config_file.cfg')
    config = ConfigParser()
    config.read(config_file)

    # Get database location from config file
    database_path = config['Directories']['Database Path (Front End)']

    # Connect to the database.
    conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
							r'DBQ=' + database_path + ';'
                    		# r'PWD=JoNiSi;' # May need a line here for the database password????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
                    		)

    # With the connection made run a check to find out how long it took.
    endconn = time.time()
    print('\nConnection made in: ' + str(endconn - endlib) + 'sec')

    # User interface
    choice = eg.buttonbox('Click on what you want to plot.', 'Graphing Code',
        ('Proton', 'TrueBeam', 'Gulmay', 'Flexitron'))

    # Create the tabs
    if choice == 'TrueBeam':
        # Create each tab by running the relevant scripts
        tab1 = Photon_Output_Graph(conn)
        tab2 = Electron_Energy_Graph(conn)
        tab3 = Electron_Output_Graph(conn)
        tab4 = Sym_Graph(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])
    elif choice == 'Proton':
        tab1 = Photon_Output_Graph(conn)
        tab2 = Flexitron_Output_Graph(conn)
        tab3 = Gulmay_Output_Graph(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1, tab2, tab3])
    elif choice == 'Gulmay':
        tab1 = Gulmay_Output_Graph(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1])
    elif choice == 'Flexitron':
        tab1 = Flexitron_Output_Graph(conn)
        # Put all the tabs into one application
        tabs = Tabs(tabs = [tab1])
    else:
        eg.msgbox('Error')
        exit()

    # Put all of the tabs into the doccument
    doc.add_root(tabs)

    endconn = time.time()
    print('\nTabs made in: ' + str(endconn - endlib) + 'sec')

    return doc



def main():
    '''
    This function creates a server and opens it in a web browser. It calls the
    produce_doc function, opening this document (containing the bokeh graphs)
    within the browser.

    This is the method to build a Bokeh server within code without needing to
    use the Bokeh server command line tool.

    This code was originally written by VR (Bill).
    Commented and altered by CB (Christian)
    '''

    print('\nPreparing a bokeh application.')

    # Try and connect to google chrome
    try:
        webbrowser.get("chrome")
        found_chrome = True
    except:
        # If connection fails then look in a couple of typical locations for chrome
        if os.path.isfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"):
            chrome_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            chrome = webbrowser.get('chrome')
            found_chrome = True
        elif os.path.isfile("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"):
            chrome_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            chrome = webbrowser.get('chrome')
            found_chrome = True
        else:
            found_chrome = False

    # Start an Input/Output Loop. (Specifically a Tornado asynchronous I/O Loop)
    io_loop = IOLoop.current()
    port = 5001
    kwargs = {'io_loop': io_loop, 'port': port,}

    # Define the application using the bokeh application function handler.
    # https://docs.bokeh.org/en/latest/docs/reference/application/handlers/function.html
    app = Application(FunctionHandler(produce_doc))

    # http://matthewrocklin.com/blog/work/2017/06/28/simple-bokeh-server
    try:
        server = Server({'/' : app},  **kwargs)
        server.start()
        print('\nOpening Bokeh application on http://localhost:5001/')

        if found_chrome:
            server.show('/', browser="chrome")
        else:
            server.show('/')
        # Start the Input/Output Loop
        io_loop.start()
    except OSError:
        url = 'http://localhost:5001'
        if found_chrome:
            chrome.open_new_tab(url);
        else:
            webbrowser.open_new_tab(url)

    return



if __name__ == '__main__':

    # This line is necessary for packaging as an executable and avoiding
    # unnecessary loops
    multiprocessing.freeze_support()

    # Start bar as a process
    p = multiprocessing.Process(target=main)
    p.start()

    # Wait for 600 seconds (10 mins) or until process finishes
    delay = 600
    interval = 300
    p.join(delay)

    while True:
        if p.is_alive():
            if eg.ynbox('Program has been running for approximatly ' + str(int(delay/60)) + ' minutes. Do you want to close it?'):
                p.terminate()
                sys.exit()
            else:
                delay = delay + interval
                time.sleep(interval)





















#
