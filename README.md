# Database_Graphing
Creating graphs from a MS Access database with Bokeh and displaying within an interactive server.


## Components

### main.py

Sets up and runs a Bokeh server that displays the graphs using data from the database specified in the config file.

Each graph is created using a separate script saved within the 'scripts' folder. Each of these graphs are then displayed in individual tabs.

### config.py

Reads the config file (config_file.cfg) and stores the data within a Config class.

### Universal.py

Contains a number of functions used by multiple other scripts.

### Individual graphs (e.g. PhotonOutput.py)

Defines the functions that create the graph that will then be called by the main.py code. Also defines the callback functions that will be used to interact with the data.


## Instillation

This code has been written to interact with a 32-bit version of Microsoft Access. Therefore it will only work with a 32-bit version of Python3.

### Requirements

Package requirements can be found within the requirements.txt file. As mentioned above it must be used with a 32-bit version of Python3 and consideration should be given to installing within a virtual environment that allows for this.

### Packaging as an Executable

Can be compiled as an executable using pyinstaller. If so the bokeh folder in the enviroment should be copied into the dist folder. The config_file should also be copied over as pyinstaller fails to do this and the executable will error out otherwise.


## Usage

Code is designed to be used in conjunction with a Microsoft Access database. The principal is to have a button within the database that will be clicked and then run the code when compiled as an executable so that it can be run by any user without having to build a Python environment.

The following is an example of the code needed within the database to run an executable using a button.

```
Private Sub Open_Python_Graphing_Code_Click()

Call Shell("Path to main.exe")

End Sub
```


## Limitations/Known Bugs

* Closing the web page will not terminate the server which can then be accessed by navigating to `http://localhost:5001`
⋅⋅* The current workaround is if the code is run again then it will just navigate to this address if the server is already active.
⋅⋅* Additionally a Quit button is provided to close the server correctly as well as a timer that will prompt the user to close the server.


## Contribute

Pull requests are welcome. For major changes, please open a ticket first to discuss desired changes: [Database_Graphing/issues](https://github.com/UCLHp/Database_Graphing/issues)


## Licence

All code within this package distributed under GNU GPL-3.0 (or higher).

Full license text contained within the file LICENCE.
