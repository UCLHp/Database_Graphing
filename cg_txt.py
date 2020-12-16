from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import CheckboxGroup, CustomJS
import pandas as pd
import pypyodbc
import json

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

coils_df = pd.read_sql('select [Coil_name] from [MRI_Coils]', conn)
coils = list(coils_df['coil_name'])
qa_results = pd.read_sql('select * from [MRI_Coils_Check]', conn)

source = ColumnDataSource(qa_results)

coil_select_box = CheckboxGroup(labels=coils, active =[0,1])
coil_select_box.js_on_click(CustomJS(code="""
    console.log('coil_select_box: active=' + this.active, this.toString())
    """))
show(coil_select_box)

exit()

p = figure(
    title = 'Example',
    x_axis_label='X Axis',
    x_axis_type='datetime',
    y_axis_label='Y Axis'
)










p.scatter(x='adate', y='snr', legend='Test', source=source)

show(p)
