'''
Holds many of the functions used universally by the other scripts

'''

import types
import pandas as pd
from datetime import date

from bokeh.models import (DatetimeTickFormatter, BasicTickFormatter)
from bokeh.models.widgets import (CheckboxGroup, RangeSlider, Select,
                                  DateRangeSlider)
from bokeh.palettes import turbo, Colorblind


def Create_Select_Axis(TableFields, x_axis_title1, y_axis_title1):
	'''
	This function creates a select box widget that can be used to choose what is
	plotted against the x and axis.
	Inputs:   	TableFields = 	A list of the column headers in the dataframe that
	                          	you want to be able to plot on the x/y axis.
	          	x_axis_title1 = The option that the user wants to display on opening
	                          	the graph for the x-axis widget
	          	y_axis_title1 = The option that the user wants to display on opening
	                          	the graph for the y-axis widget
 	Outputs:  	select_xaxis =  A bokeh select widget that can be used to change the
								data that is plotted on the x-axis.
				select_yaxis =  A bokeh select widget that can be used to change the
 								data that is plotted on the y-axis.
	'''

	menu_axis = []
	for field in TableFields:
		menu_axis.append(field)
	menu_axis = sorted(menu_axis)

	select_xaxis = Select(title='X-Axis Fields Available:',
                       value=x_axis_title1,
                       options=menu_axis	)
	select_yaxis = Select(title='Y-Axis Fields Available:',
                       value=y_axis_title1,
                       options=menu_axis	)

	return select_xaxis, select_yaxis


def Create_Select_Legend(legend_location):
	'''
	This function creates a select box widget that can be used to choose  where the
	legend displays on the graph.
	Inputs:   	legend_location =   The location of the legend when opening the
	                               	graph. This should be a string and one of the
	                               	Bokeh accepted values.
 	Outputs:  	select_legend = 	A bokeh select widget that can be used to change the
	                          		data that is plotted on the x-axis.
	'''

	menu_legend = ['top_left', 'top_center', 'top_right', 'center_left',
                'center', 'center_right', 'bottom_left', 'bottom_center', 'bottom_right']

	select_legend = Select(title='Legend Position',
                        value=legend_location,
                        options=menu_legend	)

	return select_legend


def Create_Checkbox_Legend(df, color_column, color_to_plot, marker_column,
                           marker_to_plot):
	'''
	Creates two checkboxes for legend selection (one used for the item colour is
	based on and the other for marker)

	Will pre-select the options in "colour_to_plot"

	'''

	color_list = df[color_column].unique().tolist()
	try:
		color_list = [float(x) for x in color_list]
		color_list = sorted(color_list)
		to_int = True
		for x in color_list:
			if x.is_integer():
				pass
			else:
				to_int = False
		if to_int is True:
			color_list = [str(int(x)) for x in color_list]
		else:
			color_list = [str(x) for x in color_list]
	except ValueError:
		color_list = sorted(color_list)
	color_index = [i for i in range(
		len(color_list)) if color_list[i] in color_to_plot]
	checkbox_color = CheckboxGroup(labels=color_list, active=color_index)

	marker_list = df[marker_column].unique().tolist()
	try:
		marker_list = [float(x) for x in marker_list]
		marker_list = sorted(marker_list)
		to_int = True
		for x in marker_list:
			if x.is_integer():
				pass
			else:
				to_int = False
		if to_int is True:
			marker_list = [str(int(x)) for x in marker_list]
		else:
			marker_list = [str(x) for x in marker_list]
	except ValueError:
		marker_list = sorted(marker_list)
	marker_index = [i for i in range(
		len(marker_list)) if marker_list[i] in marker_to_plot]
	checkbox_marker = CheckboxGroup(labels=marker_list, active=marker_index)

	return checkbox_color, checkbox_marker


def Create_Checkbox_HoverTool(TableFields, hover_tool_fields):
	'''
	Creates a checkbox for hovertool selection with the options in TableFields

	Will pre-select the options in "hover_tool_fields"

	'''

	hovertool_list = []
	for field in TableFields:
		hovertool_list.append(field)

	hovertool_list = sorted(hovertool_list)

	hovertool_index = [i for i in range(
		len(hovertool_list)) if hovertool_list[i] in hover_tool_fields]

	checkbox_hovertool = CheckboxGroup(
		labels=hovertool_list, active=hovertool_index)

	return checkbox_hovertool


def Create_Range_Sliders():
	'''
	This function creates 4 range sliders for numerical data and also dates in
	both the x and y axis.

	'''

	range_slider_x = RangeSlider(	title='X-Axis Range', start=0, end=1,
                               value=(0, 1), step=0.1	)
	range_slider_y = RangeSlider(	title='Y-Axis Range', start=0, end=1,
                               value=(0, 1), step=0.1	)
	range_slider_xdate = DateRangeSlider(	title='X-Axis Range (Date)',
                                       start=date(2017, 1, 1),
                                       end=date(2017, 1, 2),
                                       value=(date(2017, 1, 1),
                                              date(2017, 1, 2)),
                                       step=1	)
	range_slider_ydate = DateRangeSlider(	title='Y-Axis Range (Date)',
                                       start=date(2017, 1, 1),
                                       end=date(2017, 1, 2),
                                       value=(date(2017, 1, 1),
                                              date(2017, 1, 2)),
                                       step=1	)

	return (range_slider_x, range_slider_y, range_slider_xdate,
         range_slider_ydate)


def Update_Range_Sliders(x_data1, y_data1, Sub_df1, range_slider_x,
                         range_slider_y, range_slider_xdate, range_slider_ydate):
	'''
	This function updates range sliders in the event that the data being plotted
	on the x and y axis changes.

	It also changes the visibility of the sliders depending on whether the the
	data being displayed is in date or numerical format

	NB: Date format is determined by whether the column name is "adate"
	'''

	if y_data1 == 'adate':
		range_slider_ydate.start = Sub_df1['y'].min()
		range_slider_ydate.end = Sub_df1['y'].max()
		range_slider_ydate.value = (Sub_df1['y'].min(), Sub_df1['y'].max())
		range_slider_ydate.step = 1
		range_slider_ydate.visible = True
		range_slider_y.visible = False
	else:
		range_slider_y.start = Sub_df1['y'].min()
		range_slider_y.end = Sub_df1['y'].max()
		range_slider_y.value = (Sub_df1['y'].min(), Sub_df1['y'].max())
		range_slider_y.step = (Sub_df1['y'].max()-Sub_df1['y'].min())/10000
		range_slider_y.visible = True
		range_slider_ydate.visible = False

	if x_data1 == 'adate':
		range_slider_xdate.start = Sub_df1['x'].min()
		range_slider_xdate.end = Sub_df1['x'].max()
		range_slider_xdate.value = (Sub_df1['x'].min(), Sub_df1['x'].max())
		range_slider_xdate.step = 1
		range_slider_xdate.visible = True
		range_slider_x.visible = False
	else:
		range_slider_x.start = Sub_df1['x'].min()
		range_slider_x.end = Sub_df1['x'].max()
		range_slider_x.value = (Sub_df1['x'].min(), Sub_df1['x'].max())
		range_slider_x.step = (Sub_df1['x'].max()-Sub_df1['x'].min())/10000
		range_slider_x.visible = True
		range_slider_xdate.visible = False

	return


def Update_Range_Sliders_2(x_data1, y_data1, range_slider_x, range_slider_y,
                           range_slider_xdate, range_slider_ydate, p1):
	'''
	This function updates range sliders in the event that the data being plotted
	on the x and y axis changes.

	It also changes the visibility of the sliders depending on whether the the
	data being displayed is in date or numerical format

	NB: Date format is determined by whether the column name is "adate"
	'''

	if y_data1 == 'adate':
		range_slider_ydate.start = p1.y_range.start
		range_slider_ydate.end = p1.y_range.end
		range_slider_ydate.value = (p1.y_range.start, p1.y_range.end)
		range_slider_ydate.step = 1
		range_slider_ydate.visible = True
		range_slider_y.visible = False
	else:
		range_slider_y.start = p1.y_range.start
		range_slider_y.end = p1.y_range.end
		range_slider_y.value = (p1.y_range.start, p1.y_range.end)
		range_slider_y.step = (p1.y_range.end-p1.y_range.start)/10000
		range_slider_y.visible = True
		range_slider_ydate.visible = False

	if x_data1 == 'adate':
		range_slider_xdate.start = p1.x_range.start
		range_slider_xdate.end = p1.x_range.end
		range_slider_xdate.value = (p1.x_range.start, p1.x_range.end)
		range_slider_xdate.step = 1
		range_slider_xdate.visible = True
		range_slider_x.visible = False
	else:
		range_slider_x.start = p1.x_range.start
		range_slider_x.end = p1.x_range.end
		range_slider_x.value = (p1.x_range.start, p1.x_range.end)
		range_slider_x.step = (p1.x_range.end-p1.x_range.start)/10000
		range_slider_x.visible = True
		range_slider_xdate.visible = False

	return


def Update_HoverTool(hover1, x_data1, y_data1, Field1=None, Field2=None,
                     Field3=None, Field4=None, Field5=None, Field6=None, Field7=None,
                     Field8=None, Field9=None, Field10=None):
	'''
	This function updates the hovertool tooltips up to a maximum of the 2 axis
	fields plus 10 additional fields

	NB: Date format is determined by whether the column name is "adate"
	'''

	FieldToolTips = []
	FieldList = [Field1, Field2, Field3, Field4, Field5, Field6, Field7,
              Field8, Field9, Field10]

	for x in FieldList:
		if x != None:
			FieldToolTips.append((x, '@{'+x+'}'))

	if x_data1 == 'adate':
		if y_data1 == 'adate':
			ToolTips = [('x_axis', '@x{%F}'), ('y_axis', '@y{%F}')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = {'@x': 'datetime', '@y': 'datetime'}
		else:
			ToolTips = [('x_axis', '@x{%F}'), ('y_axis', '@y')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = {'@x': 'datetime', '@y': 'numeral'}
	else:
		if y_data1 == 'adate':
			ToolTips = [('x_axis', '@x'), ('y_axis', '@y{%F}')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = {'@x': 'numeral', '@y': 'datetime'}
		else:
			ToolTips = [('x_axis', '@x'), ('y_axis', '@y')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = {'@x': 'numeral', '@y': 'numeral'}

	return


def Define_Plot_Parameters(p1, list):
	'''
	This function sets all of the plot parameters

	Inputs:	p1 = 	The plot that you want to set the parameters for
			list = 	A list of the plot parameters of the form:
					[x_data1, y_data1, plot_title1, x_axis_title1,
					 y_axis_title1, plot_size_height1, plot_size_width1,
					 legend_location]
	'''

	# The parameters have to be controlled like this in a callback to allow
	# for them to be adjusted. Otherwise the plot parameters are not
	# interactive.
	# 	Yes!	- p1.xaxis.axis_label = 'X_axis_title'
	# 	No! 	- p1 = figure(x_axis_label = 'X_axis_title')
	p1.title.text = list[2]
	p1.xaxis.axis_label = list[3]
	p1.yaxis.axis_label = list[4]
	p1.plot_height = list[5]
	p1.plot_width = list[6]
	p1.legend.location = list[7]
	p1.background_fill_color = 'gainsboro'

	# NB: This only works if 'adate' is used as the name for the date column
	# and also that this is the only date column.
	if list[0] == 'adate':
		p1.xaxis.formatter = DatetimeTickFormatter(days=['%d/%m', '%a%d'])
	else:
		p1.xaxis.formatter = BasicTickFormatter()
	if list[1] == 'adate':
		p1.yaxis.formatter = DatetimeTickFormatter(days=['%d/%m', '%a%d'])
	else:
		p1.yaxis.formatter = BasicTickFormatter()

	return


def add_legend_to_df(df, color_column, marker_column):
	'''
	Add a new legend column to the dataframe of the form marker_color

	If only one colomn is being used for the legend then set in the form
	marker

	'''

	def add_legend(row):
		if marker_column == color_column:
			return str(str(row[marker_column]))
		else:
			return str(str(row[marker_column]) + '_' + str(row[color_column]))

	# Run the function.
	df.loc[:, 'legend'] = df.apply(lambda row: add_legend(row), axis=1)
	df.loc[:, 'color1'] = df.loc[:, color_column]
	df.loc[:, 'marker1'] = df.loc[:, marker_column]
	return df


def Create_Legend(	df, color_column, custom_color_boolean,
                   custom_color_palette, marker_column,
                   custom_marker_boolean, custom_marker_palette	):
	'''
	This function creates the columns and palettes needed for the legend

	Inputs:		df = 	The main dataframe pulled from the database
				color_column = 	A string relating to the column name that the colors
								will be based off.
				custom_color_boolean =	True/False value to determine if a custom
										palette should be used or just the default
				custom_color_palette = 	The custom palette (empty list if not
										needed)
				marker stuff = 	As above but for the markers

	Outputs:  	df =	The main dataframe with newly added legend columns
				color_list = 	A sorted list of unique values from the column that
								the colors will be based off.
				color_palette = A list of the colors that will be matched to the
								unique values in the 'color_list'
				marker stuff = 	As above but for the markers
				add_legend_to_df = 	A function to add the legend rows to the
									dataframe (may be useful in callbacks)
	'''

	######### Colors:
	# Create a list of unique values
	color_list = df[color_column].unique().tolist()
	try:
		color_list = [float(x) for x in color_list]
		color_list = sorted(color_list)
		to_int = True
		for x in color_list:
			if x.is_integer():
				pass
			else:
				to_int = False
		if to_int is True:
			color_list = [str(int(x)) for x in color_list]
		else:
			color_list = [str(x) for x in color_list]
	except ValueError:
		color_list = sorted(color_list)
	# Using custom set?
	# NB: Custom set can be entered as fuction (e.g. turbo), a dictionary (e.g.
	# Colorblind) or a list (e.g. a user specified list of hex values).
	if custom_color_boolean == True:
		if isinstance(custom_color_palette, types.FunctionType):
			# If function this will throw an error if you have more unique items
			# than accepted inputs to the Bokeh funcion.
			color_palette = list(custom_color_palette(len(color_list)))
		elif isinstance(custom_color_palette, dict):
			# If a dictionary this will throw an error if you have more or less
			# unique items than keys in the dictionary.
			color_palette = list(custom_color_palette[len(color_list)])
		elif isinstance(custom_color_palette, tuple) or isinstance(custom_color_palette, list):
			if len(color_list) > len(custom_color_palette):
				print(	'Error - Not enough colors in custom palette to '
	                            'assign a unique marker to each option.'	)
				exit()
			color_palette = list(custom_color_palette)
		else:
			print('Error - Unsuported type of custom_color_palette')
			exit()
	# If no custom option then use the default options. The default is the
	# Colorblind palette if it is large enough and otherwise the Turbo palette.
	# (Will error out if Turbo is not large enough).
	else:
		if (len(color_list) < 8) and (len(color_list) > 2):
			color_palette = list(Colorblind[len(color_list)])
		else:
			color_palette = list(turbo(len(color_list)))

	######### Markers:
	# Create a list of unique values
	marker_list = df[marker_column].unique().tolist()
	try:
		marker_list = [float(x) for x in marker_list]
		marker_list = sorted(marker_list)
		to_int = True
		for x in marker_list:
			if x.is_integer():
				pass
			else:
				to_int = False
		if to_int is True:
			marker_list = [str(int(x)) for x in marker_list]
		else:
			marker_list = [str(x) for x in marker_list]
	except ValueError:
		marker_list = sorted(marker_list)

	# If a custom marker is to be used then set it as the marker_palette
	if custom_marker_boolean == True:
		marker_palette = custom_marker_palette
	# Else use the default list
	else:
		marker_palette = ['circle', 'diamond', 'hex', 'inverted_triangle',
	                   'plus', 'square', 'square_pin', 'triangle',
	                   'triangle_pin', 'asterisk', 'cross', 'x', 'y',
	                   'dash', 'circle_cross', 'diamond_cross',
	                   'square_cross', 'circle_dot', 'diamond_dot',
	                   'hex_dot', 'square_dot', 'triangle_dot',
	                   'circle_x', 'square_x', 'circle_y', 'dot']

	# Make sure there are enough markers to assign unique markers to each option
	if len(marker_list) > len(marker_palette):
		print(	'Error - Not enough markers to assign a unique marker to '
	            'each option.'	)
		exit()

	# Add the legend column to the dataframe
	df = add_legend_to_df(df, color_column, marker_column)

	return (color_list, color_palette, marker_list, marker_palette, df,
         add_legend_to_df)


def Make_Dataset(df, color_column, color_to_plot, marker_column, marker_to_plot,
                 x_data1, y_data1):
	'''
	This function creates the sub-dataframe that will be used to form the
	ColumnDataSource which will be plotted.

	Inputs:	df = 	The main dataframe pulled from the database
			color_to_plot =	The items that the colors are based off which are to
								be plotted (either as default opening choices or
								through callbacks)
			marker_to_plot = As above but for markers
			x_data1 =	The column name that matches the data to be plotted
						against the x-axis
			y_data1 = 	As above but for the y-axis

	Outputs:	Sub_df1 =	The sub-dataframe that will be used to form the
							ColumnDataSource which will be plotted. Filtered
							for the color and marker and with the column names
							replaced with 'x' and 'y'
	'''

	# Copy the main dataframe
	Sub_df1 = df.copy()
	# Delete any rows that do not exist in the checkboxes/default user choices.
	Sub_df1 = Sub_df1[Sub_df1[color_column].isin(color_to_plot)]
	Sub_df1 = Sub_df1[Sub_df1[marker_column].isin(marker_to_plot)]
	# Search for the columns with the x_data and y_data names and replace
	# them with 'x' and 'y'. Unless plotting the same data on both in which
	# case add an extra column for 'y' that's a copy of 'x'.
	if x_data1 == y_data1:
		Sub_df1.rename(columns={x_data1: 'x'}, inplace=True)
		Sub_df1.loc[:, 'y'] = Sub_df1.loc[:, 'x']
	else:
		Sub_df1.rename(columns={x_data1: 'x'}, inplace=True)
		Sub_df1.rename(columns={y_data1: 'y'}, inplace=True)

	return Sub_df1


def Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1, df_tol1):
	'''
	This function creates the sub-tolerance-dataframe that will be used to form
	the ColumnDataSource which will plot the tolerances.

	Inputs:	Sub_df = 	The sub-dataframe being plotted
			x_data =	The column name being plotted on the x-axis
			y_data =	The column name being plotted on the y-axis
			df_tol = 	The dataframe containing the tolerance limits

	Outputs:	Sub_df_tol =	The sub-tolerance-dataframe that will be used to
								form the ColumnDataSource which will be plotted.
	'''

	# Get a list of the column headers
	headers1 = df_tol1.columns.values.tolist()

	# Check if the xdata is what is in the df_tol1 as the x_axis
	if x_data1 == headers1[0]:
		# Find the max and min values in the sub_df so that the tolerance lines
		# can be plotted for the full range.
		if x_data1 == 'adate':
			# Add a little time to either side to make it look nicer.
			max_x = Sub_df1['x'].max() + pd.DateOffset(weeks=2)
			min_x = Sub_df1['x'].min() + pd.DateOffset(weeks=-2)
		else:
			# Add 5% of range to either side to make it look nicer.
			range = Sub_df1['x'].max() - Sub_df1['x'].min()
			max_x = Sub_df1['x'].max() + (range/20)
			min_x = Sub_df1['x'].min() - (range/20)

		# Used the x part so remove the element from the list
		headers1.remove(x_data1)
		# Check if the y_data1 value is in the header list
		if y_data1 in headers1:
			# If it is then run through until you find it and then add to the
			# dataframe.
			for x in headers1:
				if y_data1 == x:
					data = {'x': [min_x, max_x],
	                                    'y_low': [df_tol1[x][0], df_tol1[x][0]],
	                                    'y_high': [df_tol1[x][1], df_tol1[x][1]]}
					Sub_df1_tol1 = pd.DataFrame(data)
		else:
			# y_data isn't in the list so output something that won't plot and
			# also won't throw the viewing range.
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
	                    'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
	                    'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol1 = pd.DataFrame(data)

	else:
		# x_data isn't in the list so output something that won't plot and
		# also won't throw the viewing range.
		data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
	         'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
	         'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
		Sub_df1_tol1 = pd.DataFrame(data)

	return Sub_df1_tol1


#
