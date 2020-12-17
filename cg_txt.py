from bokeh.palettes import Spectral4
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import Whisker
import pandas as pd
import pypyodbc
import json

with open('config.json') as config_file:
    config = json.load(config_file)


DATABASE_DIR = config["DATABASE_DIR"]


def db_connect(DATABASE_DIR, *, pswrd=''):
    '''
    Function to connect to connect to the access database at location defined
    in config file. Connection will fail if password is required but not
    supplied
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

p = figure(
    title='MRI Coil QA Results',
    x_axis_label='Date',
    x_axis_type='datetime',
    y_axis_label='SNR'
)

for name, color in zip([f'{i}' for i in coils], Spectral4):
    df = pd.DataFrame(qa_results).where(qa_results['coil'] == name)
    df['adate'] = pd.to_datetime(df['adate'])
    base = df['adate']
    lower = list(df['snr']-df['snr_std'])
    upper = list(df['snr']+df['snr_std'])
    error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))

    # p.add_layout(Whisker(source=error,
    #                      base='base',
    #                      lower='lower',
    #                      upper='upper'
    #                      )
    #              )
    p.scatter(df['adate'], df['snr'],
              color=color,
              alpha=0.8,
              legend_label=name,
              visible=False
              )

p.legend.location = "top_left"
p.legend.click_policy = "hide"

show(p)
