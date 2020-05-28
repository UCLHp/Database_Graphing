# pandas and numpy for data manipulation
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup, Dropdown,
								  TableColumn, DataTable, Select)
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16
from bokeh.io import output_file, show



def JawTravel(conn):

 	############################################################################
 	#################### CREATE THE DATA FOR THE GRAPH #########################

    output_file("JawTravel.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	# Use the connection passed to the function to read the data into a
	# dataframe via an SQL query
    df = pd.read_sql('select * from [JawTravel]', conn)

	# Create a list of the fields using the dataframe
    TableFields = (list(df.columns))


 	############################################################################
 	################### CREATE DROPDOWNS FOR SOME REASON #######################

    # I don't know whether the slect or dropdown tools are used yet (or both), so keeping both in for now but will need to re-visit ????????????????????????????????????????????????????
    # Now make a custom dropdown, items are stored in the menu
    menu = []
	# The dropdown function needs an extra elelment of the form 'item_i' so this
    # counter is to provide this
    i = 1
    for field in TableFields:
        menu.append((field, 'item_' + str(i)))
        i = i + 1
    dropdown = Dropdown(	label = 'Fields',
							button_type = 'warning',
							menu = menu	)
    # The select function doesn't need the extra element
    menu2 = []
    for field in TableFields:
        menu2.append(field)
    select = Select(    title = 'Fields available:',
                        value = 'Mean Reading',
                        options = menu2 )


 	############################################################################
 	########################### CREATE THE PLOT ################################

	# Create a sub dataframe because
    Sub_df = df[['jawtravel id', 'g_bl', 'gantry_angle']]
    Sub_df.loc[:,'jawtravel id'] = Sub_df.loc[:,'jawtravel id'].str.slice(stop=10)
    Sub_df.loc[:,'jawtravel id'] = pd.to_datetime(Sub_df.loc[:,'jawtravel id'])
    Sub_df.columns = ['x', 'y', 'GantryAngle']
	# When making the ColumnDataSource convert the dataframe to a dictionary.
	# This seems to help with the callback functions.
	# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
	# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis
    src = ColumnDataSource(Sub_df.to_dict(orient='list'))

	# Create the basics of the plot
    p1 = figure(	title = 'PDD Results',
					x_axis_label = 'Energy',
					y_axis_label = 'Something (mm)',
					plot_height = 800,
					plot_width = 1600,
					)
    # Plot the actual data
    p1.xaxis.formatter = DatetimeTickFormatter(days = ['%d/%m', '%a%d'])
    p1.scatter(	source = src,
				x = 'x',
				y = 'y',
				fill_alpha = 0.4,
				size = 12,
				legend_label = 'RecordDate'
				)

	# Create a hover tool and add it to the plot
    hover = HoverTool(tooltips = [	('Date', '@x{%F}'),
									('(x,y)', '($x, $y)'),
									('Gantry Angle', '@GantryAngle')],
									formatters = {'x': 'datetime'} )
    p1.add_tools(hover)

	# Create a layout
    layout = column([select, p1])

    def callback(attr, old, new):
        Sub_df_new = df[['jawtravel id', new, 'gantry_angle']]
        Sub_df_new['jawtravel id'] = Sub_df_new['jawtravel id'].str.slice(stop=10)
        Sub_df_new['jawtravel id'] = pd.to_datetime(Sub_df_new['jawtravel id'])
        Sub_df_new.columns = ['x', 'y','GantryAngle']
		# When making the ColumnDataSource convert the dataframe to a dictionary.
		# This seems to help with the callback functions.
		# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
		# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis
        src.data = Sub_df_new.to_dict(orient='list')

    select.on_change('value', callback)

	# Return a panel displaying the created plot and a title for the tab
    return Panel(child = layout, title = 'Jaw Travel')

















#
