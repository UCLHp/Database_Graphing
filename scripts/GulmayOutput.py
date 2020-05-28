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



def Gulmay_Output_Graph(conn):

 	############################################################################
 	#################### CREATE THE DATA FOR THE GRAPH #########################

    output_file("Gulmay_Output_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	# Use the connection passed to the function to read the data into a
	# dataframe via an SQL query
    df = pd.read_sql(	'select [gulmay session ID], [output], ' \
						'[chamber and electrometer], [Dose rate],' \
						'[energy], [T/P factor], [Temp], [Press]' \
						'from [gulmay output]', conn	)
	# Going to want to turn the 'gulmay session id' into a date. Will do it at
	# the top to speed up and simplify callbacks later
    df.loc[:,'gulmay session id'] = df.loc[:,'gulmay session id'].str.slice(stop=10)
    df.loc[:,'gulmay session id'] = pd.to_datetime(df.loc[:,'gulmay session id'])
	# Create a list of the fields using the dataframe
    TableFields = (list(df.columns))


 	############################################################################
 	################## CREATE DROPDOWNS FOR CHANGING AXIS ######################

    menu = [] # ???????????? don't think this is actually needed ???????????????????????????????????????????????????????????????????????????????????????????????
	# The dropdown function needs an extra elelment of the form 'item_i' so this
    # counter is to provide this
    i = 1
    for field in TableFields:
        menu.append((field, 'item_' + str(i)))
        i = i + 1
    dropdown = Dropdown(	label = 'Fields',
							button_type = 'warning',
							menu = menu	)


	# The select funtion will be used to create dropdown lists to change the
	# x and y axis
	# The select function doesn't need the extra element of the form item_i
	# First make a select menu for changing the x_axis from the list of
	# avialible fields
    menu_x = []
    for field in TableFields:
        menu_x.append(field)
    select_x = Select(  title = 'Fields available:',
                        value = 'gulmay session id',
                        options = menu_x )
	# Need to do the same for the y_axis so just copy the x_axis accross and
	# make a select function (much quicker than running the loop again and
	# could probably copy accross the select function but done this way for
	# clarity of code)
    menu_y = menu_x
    select_y = Select(  title = 'Fields available:',
	                    value = 'output',
	                    options = menu_y )


 	############################################################################
 	########################### CREATE THE PLOT ################################

	# Create a sub dataframe to make things easier later. This sub_df contains
	# an 'x', 'y' and a couple of other useful data-points
    Sub_df = df[[	'gulmay session id', 'output', 'chamber and electrometer',
					'energy'	]]
    Sub_df.columns = ['x', 'y', 'ChamberCombination', 'Energy']
	# When making the ColumnDataSource convert the dataframe to a dictionary.
	# This seems to help with the callback functions.
	# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
	# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis
    src = ColumnDataSource(Sub_df.to_dict(orient='list'))

	# Create the basics of the plot
    p1 = figure(	title = 'Gulmay Output Results',
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
									('Chamber Comb.', '@ChamberCombination')],
									formatters = {'x': 'datetime'} )
    p1.add_tools(hover)

	# Create a layout
    layout = column([select_x, select_y, p1])

	# Within the callback function 'old' is the previos value. (I.e. if the
	# select function is changed from 'Output' to 'T/P Correction', then
	# 'old' = 'Output' and 'new' = 'T/P Correction')
    def callback_x(attr, old, new):
        Sub_df_new = df[[	new, 'gulmay session id',
							'chamber and electrometer',  'energy']]
        Sub_df_new.columns = ['x', 'y', 'Chamber', 'Energy']
		# When making the ColumnDataSource convert the dataframe to a dictionary.
		# This seems to help with the callback functions.
		# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
		# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis
        src.data = Sub_df_new.to_dict(orient='list')

    def callback_y(attr, old, new):
        print(attr)
        print(old)
        print(new)
        Sub_df_new = df[[	old, new,
							'chamber and electrometer', 'energy']]
        Sub_df_new.columns = ['x', 'y', 'Chamber', 'Energy']
		# When making the ColumnDataSource convert the dataframe to a dictionary.
		# This seems to help with the callback functions.
		# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
		# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis
        src.data = Sub_df_new.to_dict(orient='list')

    select_x.on_change('value', callback_x)
    select_y.on_change('value', callback_y)

	# Return a panel displaying the created plot and a title for the tab
    return Panel(child = layout, title = 'PDD')

















#
