
# Going to try and make a file that hold a load of the relatively universal
# scripts. (e.g. things like make an x or y range slider, or make a dropdown
# box that can be used for choosing x and y axis)


# pandas and numpy for data manipulation
import types
import pandas as pd
import numpy as np
from datetime import date, timedelta

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter, BasicTickFormatter,
						  NumeralTickFormatter, Range1d)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup, Dropdown,
								  TableColumn, DataTable, Select,
								  DateRangeSlider, Button)
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import turbo, Colorblind
import bokeh.colors
from bokeh.io import output_file, show
from bokeh.transform import factor_cmap, factor_mark


################################################################################
##################### MAKE DROPDOWN'S FOR CHOOSING AXIS ########################

# This function creates a select box widget that can be used to choose what is
# plotted against the x and axis.

# Inputs:   TableFields =   A list of the column headers in the dataframe that
#                           you want to be able to plot on the x/y axis.
#           x_axis_title1 = The option that the user wants to display on opening
#                           the graph for the x-axis widget
#           y_axis_title1 = The option that the user wants to display on opening
#                           the graph for the y-axis widget

# Outputs:  select_xaxis =  A bokeh select widget that can be used to change the
#                           data that is plotted on the x-axis.
#           select_yaxis =  A bokeh select widget that can be used to change the
#                           data that is plotted on the y-axis.

def Create_Select_Axis(TableFields, x_axis_title1, y_axis_title1):

	menu_axis = []
	for field in TableFields:
		menu_axis.append(field)
	# Create the select tool
	menu_axis = sorted(menu_axis)

	select_xaxis = Select(  title = 'X-Axis Fields Available:',
							value = x_axis_title1,
							options = menu_axis	)
	select_yaxis = Select(  title = 'Y-Axis Fields Available:',
							value = y_axis_title1,
							options = menu_axis	)

	return select_xaxis, select_yaxis

################################################################################
################################################################################





################################################################################
################# MAKE DROPDOWN FOR CHOOSING LEGEND LOCATION ###################

# This function creates a select box widget that can be used to choose where the
# legend displays on the graph.

# Inputs:   legend_location =   The location of the legend when opening the
#                               graph. This should be a string and one of the
#                               Bokeh accepted values.

# Outputs:  select_legend = A bokeh select widget that can be used to change the
#                           data that is plotted on the x-axis.

def Create_Select_Legend(legend_location):

    menu_legend = [	'top_left', 'top_center', 'top_right',
					'center_left', 'center', 'center_right',
					'bottom_left', 'bottom_center', 'bottom_right']
	# Create the select tool
    select_legend = Select( title = 'Legend Position',
							value = legend_location,
							options = menu_legend	)

    return select_legend

################################################################################
################################################################################





################################################################################
################## MAKE CHECKBOXES FOR CHOOSING THE LEGEND #####################

def Create_Checkbox_Legend(df, color_column, color_to_plot, marker_column,
		marker_to_plot):

	# Create a list of all unique names in the column that color will be based
	# on (sorted alphabetically) and also use the filter to take the index
	# number to pre-tick the correct values.
	color_list = sorted(df[color_column].unique().tolist())
	color_index = [i for i in range(len(color_list)) if color_list[i] in color_to_plot]
	checkbox_color = CheckboxGroup(labels = color_list, active = color_index)

	marker_list = sorted(df[marker_column].unique().tolist())
	marker_index = [i for i in range(len(marker_list)) if marker_list[i] in marker_to_plot]
	checkbox_marker = CheckboxGroup(labels = marker_list, active = marker_index)

	return checkbox_color, checkbox_marker

################################################################################
################################################################################





################################################################################
################## MAKE CHECKBOXES FOR CHOOSING THE LEGEND #####################



def Create_Checkbox_HoverTool(TableFields, hover_tool_fields):

	hovertool_list = []
	for field in TableFields:
		hovertool_list.append(field)
	# Create the select tool
	hovertool_list = sorted(hovertool_list)

	hovertool_index = [i for i in range(len(hovertool_list)) if hovertool_list[i] in hover_tool_fields]

	checkbox_hovertool = CheckboxGroup(labels = hovertool_list, active = hovertool_index)


	return checkbox_hovertool

################################################################################
################################################################################







################################################################################
################### MAKE RANGE-SLIDERS TO ADJUST PLOT RANGE ####################

# This function creates a select box widget that can be used to choose where the
# legend displays on the graph.

# Inputs:   legend_location =   The location of the legend when opening the
#                               graph. This should be a string and one of the
#                               Bokeh accepted values.

# Outputs:  select_legend = A bokeh select widget that can be used to change the
#                           data that is plotted on the x-axis.

def Create_Range_Sliders():

	range_slider_x = RangeSlider(	title='X-Axis Range', start=0, end=1,
									value=(0,1), step=0.1	)
	range_slider_y = RangeSlider(	title='Y-Axis Range', start=0, end=1,
									value=(0,1), step=0.1	)
	range_slider_xdate = DateRangeSlider(	title = 'X-Axis Range (Date)',
										start = date(2017,1,1),
										end =  date(2017,1,2),
										value = (date(2017,1,1),date(2017,1,2)),
										step = 1	)
	range_slider_ydate = DateRangeSlider(	title = 'Y-Axis Range (Date)',
										start = date(2017,1,1),
										end =  date(2017,1,2),
										value = (date(2017,1,1),date(2017,1,2)),
										step = 1	)

	return (range_slider_x, range_slider_y, range_slider_xdate,
		range_slider_ydate)


def Update_Range_Sliders(x_data1, y_data1, Sub_df1, range_slider_x,
		range_slider_y, range_slider_xdate, range_slider_ydate):
	# First need to check if 'adate' and if so edit the date range slider
	# but otherwise edit the normal slider. Don't forget to make the right
	# one visible.
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
	# First need to check if 'adate' and if so edit the date range slider
	# but otherwise edit the normal slider. Don't forget to make the right
	# one visible.
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
		range_slider_xdate.value = (p1.x_range.start,p1.x_range.end)
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


################################################################################
################################################################################

def Update_HoverTool(hover1, x_data1, y_data1, Field1=None, Field2=None,
		Field3=None, Field4=None, Field5=None, Field6=None, Field7=None,
		Field8=None, Field9=None, Field10=None):

	FieldToolTips = []
	FieldList = [Field1, Field2, Field3, Field4, Field5, Field6, Field7,
		Field8, Field9, Field10]

	for x in FieldList:
		if x != None:
			FieldToolTips.append((x, '@{'+x+'}'))

	if x_data1 == 'adate':
		if y_data1 == 'adate':
			ToolTips = [(x_data1, '@x{%F}'), (y_data1, '@y{%F}')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = { '@x': 'datetime', '@y': 'datetime'}
		else:
			ToolTips = [(x_data1, '@x{%F}'), (y_data1, '@y')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = { '@x': 'datetime', '@y': 'numeral'}
	else:
		if y_data1 == 'adate':
			ToolTips = [(x_data1, '@x'), (y_data1, '@y{%F}')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = { '@x': 'numeral', '@y': 'datetime'}
		else:
			ToolTips = [(x_data1, '@x'), (y_data1, '@y')]
			ToolTips.extend(FieldToolTips)
			hover1.tooltips = ToolTips
			hover1.formatters = { '@x': 'numeral', '@y': 'numeral'}

	return




################################################################################
######################### DEFINE THE PLOT PARAMETERS ###########################

# This function sets all of the plot parameters

# Inputs:	p1 = 	The plot that you want to set the parameters for
# 			list = 	A list of the plot parameters of the form:
# 					[	x_data1, y_data1, plot_title1, x_axis_title1,
#						y_axis_title1, plot_size_height1, plot_size_width1,
# 						legend_location	]

# Outputs:  None


def Define_Plot_Parameters (p1, list):

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

	# If the user wants to plot an axis as datetime then the axis needs to
	# be reformatted. Will do this by checking if the x_data1/y_data1 is
	# =='adate'.
	# NB: This only works if 'adate' is used as the name for the date column
	# and also that this is the only date column.
	if list[0] == 'adate':
		p1.xaxis.formatter = DatetimeTickFormatter(days = ['%d/%m', '%a%d'])
	else:
		p1.xaxis.formatter = BasicTickFormatter()
	if list[1] == 'adate':
		p1.yaxis.formatter = DatetimeTickFormatter(days = ['%d/%m', '%a%d'])
	else:
		p1.yaxis.formatter = BasicTickFormatter()

	return





################################################################################
################################################################################







################################################################################
############################### ADD A LEGEND ###################################

# This function creates the columns and palettes needed for the legend

# Inputs:	df = 	The main dataframe pulled from the database
# 			color_column = 	A string relating to the column name that the colors
# 							will be based off.
# 			custom_color_boolean =	True/False value to determine if a custom
# 									palette should be used or just the default
# 			custom_color_palette = 	The custom palette (empty list if not
# 									needed)
# 			marker stuff = 	As above but for the markers

# Outputs:  df =	The main dataframe with newly added legend columns
# 			color_list = 	A sorted list of unique values from the column that
# 							the colors will be based off.
# 			color_palette = A list of the colors that will be matched to the
# 							unique values in the 'color_list'
# 			marker stuff = 	As above but for the markers
# 			add_legend_to_df = 	A function to add the legend rows to the
# 								dataframe (may be useful in callbacks)

def Create_Legend(	df, color_column, custom_color_boolean,
					custom_color_palette, marker_column,
					custom_marker_boolean, custom_marker_palette	):

	######### Colors:

	# Create a color list based on the unique entries in one of the database
	# columns (specified by the tab author).
	color_list = sorted(df[color_column].unique().tolist())

	# First check if the writer wants to use a custom set or if they're happy
	# with the defaults in here. Note that the custom set can be entered as
	# fuction (e.g. turbo), a dictionary (e.g. Colorblind) or a list (e.g. a
	# user specified list of hex values). Therefore need to check for type so
	# the legend can be built correctly.
	if custom_color_boolean == True:
		if isinstance(custom_color_palette, types.FunctionType):
			# If it's a function then it's probably one of the 256 value large
			# palettes supplied by Bokeh. This will throw an error if you have
			# more unique items than accepted inputs to the Bokeh funcion.
			color_palette = list(custom_color_palette(len(color_list)))
		elif isinstance(custom_color_palette, dict):
			# If it's a dictionary then it's probably one of the smaller
			# palettes supplied by Bokeh. This will throw an error if you have
			# more or less unique items than keys in the dictionary.
			color_palette = list(custom_color_palette[len(color_list)])
		elif isinstance(custom_color_palette, tuple) or isinstance(custom_color_palette, list):
			if len(color_list) > len(custom_color_palette):
				print(	'Error - Not enough colors in custom palette to ' \
						'assign a unique marker to each option.'	)
				exit()
			# Set color_palette and turn it into a list as this will help if it
			# need to be changed later (tuples cannot be altered).
			color_palette = list(custom_color_palette)
		else:
			print('Error - Unsuported type of custom_color_palette')
			exit()
	# If custom_color_palette is not requested by the writter then will want to
	# use the default options. The default is the Colorblind palette if it is
	# large enough and otherwise use the large Turbo palette. (Will error out if
	# Turbo is not large enough.
	else:
		if (len(color_list) < 8) and (len(color_list) > 2):
			color_palette = list(Colorblind[len(color_list)])
		else:
			# This will throw an error if you have more than 256 unique items
			# (max number of colors in the Turbo palette
			color_palette = list(turbo(len(color_list)))


	######### Markers:

	# Create a marker list based on the unique entries in one of the database
	# columns (specified by the tab author).
	marker_list = sorted(df[marker_column].unique().tolist())

	# If a custom marker is to be used then set it as the marker_palette
	if custom_marker_boolean == True:
		marker_palette = custom_marker_palette
	# Else use the default list (this was set by CB in an order to try and keep
	# as good a contrast between items as possible as the marker_list grows in
	# size (i.e. having 'better' markers at the begining and saving the 'worse'
	# ones for the end where they may not be used)).
	else:
		marker_palette = [ 	'circle', 'square', 'triangle', 'diamond',
							'inverted_triangle', 'hex',	'circle_cross',
							'square_cross', 'diamond_cross', 'asterisk',
							'cross', 'x', 'circle_x', 'square_x', 'dash'	]

	# Make sure there are enough markers to assign unique markers to each option
	if len(marker_list) > len(marker_palette):
		print(	'Error - Not enough markers to assign a unique marker to ' \
				'each option.'	)
		exit()


	######### Legend Key:
	# Create a function that will be used to run through the dataframe looking
	# at the colomns chosen for the color and marker and creating a new 'marker_color'
	# column that can be used for the legend (unless the same column is being
	# used for both marker and color, in which case set legend as 'marker')

	def add_legend_to_df(df):

		def add_legend(row):
			if marker_column == color_column:
				return str(str(row[marker_column]))
			else:
				return str(str(row[marker_column]) + '_' + str(row[color_column]))

		# Run the function.
		df.loc[:,'legend'] = df.apply(lambda row: add_legend(row), axis=1)
		df.loc[:,'color1'] = df.loc[:,color_column]
		df.loc[:,'marker1'] = df.loc[:,marker_column]
		return df

	# Run the now defined function
	df = add_legend_to_df(df)

	return (color_list, color_palette, marker_list, marker_palette, df,
		add_legend_to_df)

################################################################################
################################################################################







################################################################################
########################## CREATE A SUB-DATAFRAME ##############################

# This function creates the sub-dataframe that will be used to form the
# ColumnDataSource which will be plotted.

# Inputs:	df = 	The main dataframe pulled from the database
# 			color_to_plot =	The items that the colors are based off which are to
# 							be plotted (either as default opening choices or
# 							through callbacks)
#			marker_to_plot = As above but for markers
# 			x_data1 =	The column name that matches the data to be plotted
#						against the x-axis
# 			y_data1 = 	As above but for the y-axis

# Outputs:  Sub_df1 =	The sub-dataframe that will be used to form the
# 						ColumnDataSource which will be plotted.

def Make_Dataset(df, color_column, color_to_plot, marker_column, marker_to_plot,
		x_data1, y_data1):
	# Create a sub dataframe as a copy of the original dataframe.
	Sub_df1 = df.copy()
	# Delete any rows in the sub-dataframes that do not exist in the
	# checkboxes/default user choices.
	Sub_df1 = Sub_df1[Sub_df1[color_column].isin(color_to_plot)]
	Sub_df1 = Sub_df1[Sub_df1[marker_column].isin(marker_to_plot)]
	# Search for the columns with the x_data and y_data names and replace
	# them with 'x' and 'y'. Unless plotting the same data on both in which
	# case add an extra column for 'y' that's a copy of 'x'.
	if x_data1 == y_data1:
		Sub_df1.rename(columns = {x_data1:'x'}, inplace = True)
		Sub_df1.loc[:,'y'] = Sub_df1.loc[:,'x']
	else:
		Sub_df1.rename(columns = {x_data1:'x'}, inplace = True)
		Sub_df1.rename(columns = {y_data1:'y'}, inplace = True)

	return Sub_df1

################################################################################
################################################################################







################################################################################
##################### CREATE A SUB-TOLERANCE-DATAFRAME #########################

def Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1, df_tol1):

	# Get a list of the column headers
	headers1 = df_tol1.columns.values.tolist()

	# Check if the xdata is what is in the df_tol1 as the x_axis (if not no
	# point plotting tolerances as all tolerances are vs this column).
	if x_data1 == headers1[0]:
		# Find the max and min values in the sub_df so that the tolerance lines
		# can be plotted for the full range.
		if x_data1 == 'adate':
			# Need to do this as it's a datatime and so adding a little time to
			# either side to make it look nicer is harder.
			max_x = Sub_df1['x'].max() + pd.DateOffset(weeks = 2)
			min_x = Sub_df1['x'].min() + pd.DateOffset(weeks = -2)
		else:
			# If it's not datetime then just add about 5% of the range to to
			# either side to make the plot look nicer.
			range = Sub_df1['x'].max() - Sub_df1['x'].min()
			max_x = Sub_df1['x'].max() + (range/20)
			min_x = Sub_df1['x'].min() - (range/20)

		# Used the x part so now remove the element from the list
		headers1.remove(x_data1)
		# Check if the y_data1 value is in the header list
		if y_data1 in headers1:
			# If it is then run through until you find it and then
			for x in headers1:
				if y_data1 == x:
					data = {'x': [min_x, max_x],
							'y_low': [df_tol1[x][0], df_tol1[x][0]],
							'y_high': [df_tol1[x][1], df_tol1[x][1]]}
					Sub_df1_tol1 = pd.DataFrame(data)
		else:
		# As y_data isn;t in the list then going to output something that
		# should basically just not plot but also won't throw the viewing
		# range.
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
					'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
					'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol1 = pd.DataFrame(data)

	else:
		# As x_data isn't in the list then going to output something that should
		# basically just not plot but also won't throw the viewing range.
		data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
				'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
				'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
		Sub_df1_tol1 = pd.DataFrame(data)

	return Sub_df1_tol1

################################################################################
################################################################################











#
