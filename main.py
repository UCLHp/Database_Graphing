
'''
This script is designed to initialise and run a server which displays graphs
using the data from the QA database.

Each individual tab is created by a seperate script saved in the 'scripts'
folder, with this main script calling these individual scripts and as such
allowing for easier management and development of this application.

NB: MS Access on trust PCs is 32-bit. 64-bit python cannot run a 32-bit MS
Access driver therefore this code will only work with 32-bit python.

'''

####################### IMPORT LIBRARIES AND SCRIPTS ##########################

import os
import sys
import time

# Import some stuff from bokeh and tornado libraries to maniulate tabs and
# create/run the server.
from tornado.ioloop import IOLoop
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import Server
from bokeh.models.widgets import Tabs
from bokeh.io import curdoc

# Import some other libraries
from functools import partial
from configparser import ConfigParser
import multiprocessing
import asyncio
import webbrowser
import pypyodbc
import pandas as pd
import easygui as eg

# Import the tab scripts.
from scripts.PBT_Isocentre import pbt_isocentre_graph
from scripts.PBT_Energy import pbt_energy_graph
from scripts.ElectronOutput import Electron_Output_Graph
from scripts.Sym import Sym_Graph
from scripts.FlexitronOutput import Flexitron_Output_Graph
from scripts.ElectronEnergy import Electron_Energy_Graph
from scripts.PhotonOutput import Photon_Output_Graph
from scripts.GulmayOutput import Gulmay_Output_Graph
from config import Config

# Import time and start a timer
start = time.time()

# Start of patch!
# Need a fix for running the Tornado Server in Python 3.8 on Windows. This
# piece of code seems to allow it to run correctly (something about needing
# to change a Windows default?):
#          https://github.com/tornadoweb/tornado/issues/2751
#          https://github.com/tornadoweb/tornado/issues/2608
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# End of patch!


###############################################################################


def produce_doc(doc):
    '''
    This function produces the doccument containing all of the graphs, which
    is later called by the main function.

    It does this by connecting to the database, passing the cursor to the other
    tab scripts and compiling the tabs into one doccument
    '''

    photon_db_path_fe = Config.Main.photon_db_path_fe
    proton_db_path_fe = Config.Main.proton_db_path_fe
    print(proton_db_path_fe)
    # Connect to the database.
    photon_conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                                   r'DBQ=' + photon_db_path_fe + ';'
                                   # r'PWD=JoNiSi;'  # May need a line here for the database password????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
                                   )
    proton_conn = pypyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                                   r'DBQ=' + proton_db_path_fe + ';'
                                   r'PWD=;'  # May need a line here for the database password????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
                                   )

    # With the connection made run a check to find out how long it took.
    endconn = time.time()
    print('\nConnection made in: ' + str(endconn - start) + 'sec')

    # User interface
    choice = eg.buttonbox('Click on what you want to plot.', 'Graphing Code',
                          ('All', 'Proton', 'TrueBeam', 'Gulmay', 'Flexitron'))

    # Create the tabs
    if choice == 'All':
        # Create each tab by running the relevant scripts
        tab1 = Photon_Output_Graph(photon_conn, Config)
        tab2 = Electron_Energy_Graph(photon_conn, Config)
        tab3 = Electron_Output_Graph(photon_conn, Config)
        tab4 = Sym_Graph(photon_conn, Config)
        tab5 = Gulmay_Output_Graph(photon_conn, Config)
        tab6 = Flexitron_Output_Graph(photon_conn, Config)
        # Put all the tabs into one application
        tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])
    elif choice == 'Proton':
        # Create each tab by running the relevant scripts
        tab1 = pbt_isocentre_graph(proton_conn, Config)
        tab2 = pbt_energy_graph(proton_conn, Config)
        # Put all the tabs into one application
        tabs = Tabs(tabs=[tab1, tab2])
    elif choice == 'TrueBeam':
        # Create each tab by running the relevant scripts
        tab1 = Photon_Output_Graph(photon_conn, Config)
        tab2 = Electron_Energy_Graph(photon_conn, Config)
        tab3 = Electron_Output_Graph(photon_conn, Config)
        tab4 = Sym_Graph(photon_conn, Config)
        # Put all the tabs into one application
        tabs = Tabs(tabs=[tab1, tab2, tab3, tab4])
    elif choice == 'Gulmay':
        tab1 = Gulmay_Output_Graph(photon_conn, Config)
        # Put all the tabs into one application
        tabs = Tabs(tabs=[tab1])
    elif choice == 'Flexitron':
        tab1 = Flexitron_Output_Graph(photon_conn, Config)
        # Put all the tabs into one application
        tabs = Tabs(tabs=[tab1])
    else:
        eg.msgbox('Error')
        exit()

    # Put all of the tabs into the doccument
    doc.add_root(tabs)

    endtabs = time.time()
    print('\nTabs made in: ' + str(endtabs - endconn) + 'sec')

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
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            webbrowser.register(
                'chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            chrome = webbrowser.get('chrome')
            found_chrome = True
        elif os.path.isfile("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            webbrowser.register(
                'chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            chrome = webbrowser.get('chrome')
            found_chrome = True
        else:
            found_chrome = False

    # Start an Input/Output Loop. (Specifically a Tornado asynchronous I/O Loop)
    io_loop = IOLoop.current()
    port = 5001
    kwargs = {'io_loop': io_loop, 'port': port, }

    # Define the application using the bokeh application function handler.
    # https://docs.bokeh.org/en/latest/docs/reference/application/handlers/function.html
    app = Application(FunctionHandler(produce_doc))

    # http://matthewrocklin.com/blog/work/2017/06/28/simple-bokeh-server
    try:
        server = Server({'/': app},  **kwargs)
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
            chrome.open_new_tab(url)
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

    # Wait for 1200 seconds (20 mins) or until process finishes
    delay = 1200
    interval = 600
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
