################################################################################
############################## IMPORT LIBRARIES ################################

# pandas and numpy for data manipulation
import types
import pandas as pd
import numpy as np
# Import some basic tools from easygui to allow for user interface
from easygui import buttonbox, msgbox
from datetime import date, timedelta

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter, BasicTickFormatter,
						  NumeralTickFormatter, Range1d, Div)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup, Dropdown,
								  TableColumn, DataTable, Select,
								  DateRangeSlider, Button)
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import turbo, Colorblind
import bokeh.colors
from bokeh.io import output_file, show
from bokeh.transform import factor_cmap, factor_mark

from scripts.Universal import (	Create_Select_Axis, Create_Select_Legend,
								Create_Range_Sliders, Update_Range_Sliders,
								Update_Range_Sliders_2,
								Create_Checkbox_Legend, Define_Plot_Parameters,
								Update_HoverTool, Create_Legend, Make_Dataset,
								Make_Dataset_Tolerance,
								Create_Checkbox_HoverTool)

################################################################################
################################################################################





################################################################################
################################ START OF CODE #################################

def Flexitron_Output_Graph(conn):

	output_file("PDD_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????


	'''

	In order to make a simple plot easy to create we're going to define all of
	the user inputs up front. Then pull the data out of the database and
	add a simple tolerance dataframe if necessary.

	For a first plot this may be all that is needed but to make a more complex
	plot the writer may need to add details further down.

	Remember that:
		*	The dataframe will not have capital letters in the field names due
			to a quirk of the read_sql function.
		*	The date field MUST be called 'adate' and of the format 'datetime'
			in order for parts of the code to function correctly

	'''

	############################################################################
	############################################################################

	############################################################################
 	############################# USER INPUTS ##################################

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened, the plot size
	# etc.).
	#
	# Decide on what data to plot on the x/y axis when opened (enter the field
	# names here)
	x_data1 = 'adate'
	y_data1 = 'graph % difference'
	# Decide what the plot formatting will be, inluding the plot title, axis
	# titles and the size of the plot. A good generic start point is to use the
	# field names as the axis titles but future plots could potentially use a
	# look up table to give more user friendly titles.
	plot_title1 = 'Flexitron Output'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'
	# Set the fields that will display in the hovertool in addition to the x and
	# y fields (NB: Can have a maximum of 10 options here). (Useful example
	# defaults would be the comments field or maybe chamber/electrometer?)
	hover_tool_fields = ['comments']
	# Create a list of the plot parameters that will be used as input to a
	# function later.
	list_plot_parameters = [x_data1, y_data1, plot_title1, x_axis_title1,
		y_axis_title1, plot_size_height1, plot_size_width1, legend_location]

	# Define the fields that the legend will be based off. If there is only
	# one field then put it in both columns.
	#
	# If the default options in the function are not acceptable then change the
	# boolean to True and then set the palette to the color and marker palettes
	# that you want (they will be mapped against a 'sorted' list of the unique
	# values from the fields).
	color_column = 'machinename'
	custom_color_boolean = False
	custom_color_palette = []
	marker_column = 'well chamber'
	custom_marker_boolean = False
	custom_marker_palette = []
	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened. NB: Bokeh will throw an error if one of these lists is
	# empty (i.e. =[]) If only using color or marker then set the color_to plot
	# and then enter the command:  color_to_plot = marker_to_plot.
	color_to_plot = ['Flexitron']
	marker_to_plot = ['A961212', 'A103503']

	############################################################################
	#################### CREATE THE DATA FOR THE GRAPH #########################

	# Do this in a function so it can be used in an update callback later

	def Create_df():

		# Use the connection passed to the function to read the data into a
		# dataframe via an SQL query.
		df = pd.read_sql('select [msel session ID], [well chamber], ' \
			'[Graph % Difference], [Temp], [Press], [T/P Factor], ' \
			'[max position], [Comments], [Input by], [Checked by], ' \
			'[electrometer] from [msel output Graph]', conn)

		# Delete empty rows where the data is very important to have
		df = df.dropna(subset=['msel session id'])
		df = df.dropna(subset=['well chamber'])

		# The format is complicated for this field but seems to be that the date is
		# always the first element and the machine is always the last regardless of
		# how many elements there are.
		# Seperate on the first '_'
		df_left = df['msel session id'].str.partition(sep = '_')
		# Seperate on the last '_'
		df_right = df['msel session id'].str.rpartition(sep = '_')
		# From these sperated dataframes add the appropriate columns back into
		# the main dataframe.
		df.loc[:,'adate'] = df_left[0]
		df.loc[:,'machinename'] = df_right[2]

		# Turn 'adate' into datetime.
		df.loc[:,'adate'] = pd.to_datetime(df.loc[:,'adate'], dayfirst=True)

		# Drop any columns where there is no data
		df = df.dropna(axis='columns', how='all')

		return df

	df = Create_df()

	# Create a list of the fields using the dataframe. By doing it now before
	# the extra legend fields are added it's easy to limit what is displayed in
	# the select widgets.
	TableFields = (list(df.columns))

	############################################################################
	############################################################################




 	############################################################################
 	################ CREATE THE DATAFRAME FOR THE TOLERANCES ###################

	# If you want to add tolerances change the boolean to True and construct the
	# dataframe in the correct format.
	tolerance_boolean = True
	# The format of the dataframe should be the first line being the x_axis
	# (with some values taken from the main dataframe to get the right
	# formatting). The subsequent columns are the tolerances [low, high].
	# NB: column names should match those from the main dataframe.
	if tolerance_boolean == True:
		df_tol1 = pd.DataFrame({'adate':[df['adate'].max(), df['adate'].max()],
								'graph % difference':[-3, +3],
								'max position':[350, 360]})

	############################################################################
	############################################################################

	############################################################################
	############################################################################

	'''

	This is the end of the user input section. If you don't need to make any
	other changes you can end here.

	'''







	##########################################################################
	################### CREATE THE COLUMNS FOR THE LEGEND ######################

	(color_list, color_palette, marker_list, marker_palette, df,
		add_legend_to_df) = Create_Legend(df, color_column,
		custom_color_boolean, custom_color_palette, marker_column,
		custom_marker_boolean, custom_marker_palette)

	############################################################################
	############################################################################






 	############################################################################
 	################## FORMATTING AND CREATING A BASIC PLOT ####################

	######### Make Dataset:
	# Run the Make_Dataset function to create a sub dataframe that the plot will
	# be made from.
	Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
		marker_to_plot, x_data1, y_data1	)

	# Make the ColumnDataSource (when making convert dataframe to a dictionary,
	# which is helpful for the callback).
	src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))


	######### Make Plot:
	# Create an empty plot (plot parameters will be applied later in a way that
	# can be manipulated in the callbacks)
	p1 = figure()
	# Create a scatter plot.
	p1.scatter(	source = src1,
				x = 'x',
				y = 'y',

				fill_alpha = 0.4,
				size = 12,

				# NB: Always use legend_field for this not legend_group as the
				# former acts on the javascript side but the latter the Python
				# side. Therefore the former will update automatically.
				legend_field = 'legend',
				marker = factor_mark('marker1', marker_palette, marker_list),
				color = factor_cmap('color1', color_palette, color_list)
				)


	# Run the Define_Plot_Parameters function to format the plot.
	Define_Plot_Parameters(p1, list_plot_parameters)

	############################################################################
	############################################################################






	############################################################################
 	############################ ADD TOLERANCES ################################

	# We defined the tolerances further up and now want to add the correct ones
	# to the plot. Only do this through if the boolean is set to True as
	# otherwise the user doesn't want tolerances.
	if tolerance_boolean == True:

		Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1,
			df_tol1)

		src1_tol = ColumnDataSource(Sub_df1_tol1.to_dict(orient='list'))

		# Add two lines to the plot using the new ColumnDataSource as the
		# source, one line for low tolerance and one line for high.
		p1.line(source = src1_tol, x = 'x', y = 'y_low', color = 'firebrick')
		p1.line(source = src1_tol, x = 'x', y = 'y_high', color = 'firebrick')

	############################################################################
	############################################################################






 	############################################################################
 	################## ADD MORE COMPLEX TOOLS TO THE PLOT ######################

	######## 1)
	# Create a hover tool and add it to the plot

	hover1 = HoverTool()

	if len(hover_tool_fields) < 11:
		kwargs = {}
		i = 0
		for x in hover_tool_fields:
			i = i+1
			kwargs['Field'+str(i)] = x
	else:
		kwargs = {}
		msgbox('Too many fields selected to display on HoverTool ' \
			'(Max = 10). Please reduce number of fields selected')

	Update_HoverTool(hover1, x_data1, y_data1, **kwargs)

	p1.add_tools(hover1)


	############################################################################
	############################################################################






 	############################################################################
 	################# CREATE WIDGETS TO BE ADDED TO THE PLOT ###################

 	######## 1)
	# This funtion from Universal.py will be used to create dropdown lists to
	# change the data plotted on the x/y-axis.
	select_xaxis, select_yaxis = Create_Select_Axis(TableFields, x_axis_title1,
		y_axis_title1)


 	######## 2)
	# This function from Universal.py will be used to create a dropdown list to
	# change the legend position.
	select_legend = Create_Select_Legend(legend_location)


	######## 3)
	# This funtion from Universal.py will be used to create checkbox widgets to
	# change the data being plotted from the fields that the legend is based on.
	checkbox_color, checkbox_marker = Create_Checkbox_Legend(df, color_column,
		color_to_plot, marker_column, marker_to_plot)


	######## 4)
	# This funtion from Universal.py will be used to create a checkbox widget
	# to change the fields included in the hovertool.
	checkbox_hovertool = Create_Checkbox_HoverTool(TableFields,
		hover_tool_fields)


	######## 5)
	# Make an 'Update Button' to requery the database and get up to date data.
	update_button = Button(label='Update', button_type='success')

	######## 6)
	# Make a Range Button
	range_button = Button(label='Range', button_type='primary')

	######## 7)
	# Make some titles for the checkboxes
	color_title = Div(text='<b>Machine Choice</b>')
	marker_title = Div(text='<b>Well Chamber</b>')
	hover_title = Div(text='<b>Hovertool Fields</b>')

	############################################################################
	############################################################################






	############################################################################
	########################### CREATE A LAYOUT ################################

	# Create a layout where the widgets will be added and any scaling applied.
	if color_column == marker_column:
		layout_checkbox = column([color_title, checkbox_color, hover_title,
		checkbox_hovertool])
	else:
		layout_checkbox = column([color_title, checkbox_color, marker_title,
			checkbox_marker, hover_title, checkbox_hovertool])

	button_row = row([update_button, range_button])

	layout_plots = column([	button_row, select_xaxis, select_yaxis,
							select_legend,p1])

	tab_layout = row([layout_plots, layout_checkbox])

	############################################################################
	############################################################################





 	############################################################################
 	####################### CREATE CALLBACK FUNCTIONS ##########################

	# Create a big callback that does most stuff
	def callback(attr, old, new):

		# Want to acquire the current values of all of the checkboxes and select
		# widgets to provide as inputs for the re-plot.
		color_to_plot = [checkbox_color.labels[i] for i in
			checkbox_color.active]
		if color_column != marker_column:
			marker_to_plot = [checkbox_marker.labels[i] for i in
				checkbox_marker.active]
		else:
			marker_to_plot = color_to_plot
		hovertool_to_plot = [checkbox_hovertool.labels[i] for i in
			checkbox_hovertool.active]
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		legend_location = select_legend.value
		# Set the new axis titles from the values just acquired.
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot

		# Use the pre-defined Make_Dataset function with these new inputs to
		# create new versions of the sub dataframes.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		# Use the pre-defined Define_Plot_Parameters function with these new
		# inputs to update the plot parameters.
		Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
	 		plot_title1, x_axis_title1, y_axis_title1, plot_size_height1,
			plot_size_width1, legend_location])

		# Update the hovertool
		if len(hovertool_to_plot) < 11:
			kwargs = {}
			i = 0
			for x in hovertool_to_plot:
				i = i+1
				kwargs['Field'+str(i)] = x
		else:
			kwargs = {}
			msgbox('Too many fields selected to display on HoverTool ' \
				'(Max = 10). Please reduce number of fields selected')
		Update_HoverTool(hover1, plot1_xdata_to_plot, plot1_ydata_to_plot,
			**kwargs)

		# Use the pre-defined tolerances function with these new inputs to
		# make a new version of the tolerances sub dataframe.
		if tolerance_boolean == True:
			Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
				plot1_ydata_to_plot, Sub_df1, df_tol1)
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		# Update the ColumnDataSources
		src1.data = Sub_df1.to_dict(orient='list')

		return

	select_xaxis.on_change('value', callback)
	select_yaxis.on_change('value', callback)
	select_legend.on_change('value', callback)
	checkbox_color.on_change('active', callback)
	checkbox_marker.on_change('active', callback)
	checkbox_hovertool.on_change('active', callback)


	######## 2)
	# This callback is designed to update the plotted data with new values from
	# the database
	def callback_update():

		# Make a new version of the dataframe using the original Create_df
		# function that connects to the database.
		df = Create_df()
		df = add_legend_to_df(df)

		# The rest of this callback is a copy from the original callback above.
		color_to_plot = [checkbox_color.labels[i] for i in
			checkbox_color.active]
		if color_column != marker_column:
			marker_to_plot = [checkbox_marker.labels[i] for i in
				checkbox_marker.active]
		else:
			marker_to_plot = color_to_plot
		hovertool_to_plot = [checkbox_hovertool.labels[i] for i in
			checkbox_hovertool.active]
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		legend_location = select_legend.value
		# Set the new axis titles from the values just acquired.
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot

		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
	 		plot_title1, x_axis_title1, y_axis_title1, plot_size_height1,
			plot_size_width1, legend_location])

		if len(hovertool_to_plot) < 11:
			kwargs = {}
			i = 0
			for x in hovertool_to_plot:
				i = i+1
				kwargs['Field'+str(i)] = x
		else:
			kwargs = {}
			msgbox('Too many fields selected to display on HoverTool ' \
				'(Max = 10). Please reduce number of fields selected')

		Update_HoverTool(hover1, plot1_xdata_to_plot, plot1_ydata_to_plot,
			**kwargs)

		if tolerance_boolean == True:
			Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
				plot1_ydata_to_plot, Sub_df1, df_tol1)
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		src1.data = Sub_df1.to_dict(orient='list')

		return

	update_button.on_click(callback_update)


	# Callback for the Range Button
	def callback_range():

		color_to_plot = [	checkbox_color.labels[i] for i in
							checkbox_color.active]
		if color_column != marker_column:
			marker_to_plot = [	checkbox_marker.labels[i] for i in
								checkbox_marker.active]
		else:
			marker_to_plot = color_to_plot
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value

		# Use the pre-defined Make_Dataset function with these new inputs to
		# create new versions of the sub dataframes.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		if (plot1_xdata_to_plot == 'adate') and (
			(plot1_ydata_to_plot == 'graph % difference') or (plot1_ydata_to_plot == 'max position')):

			p1.x_range.start = Sub_df1['x'].max() - timedelta(weeks=53)
			p1.x_range.end = Sub_df1['x'].max() + timedelta(weeks=2)

			if plot1_ydata_to_plot == 'graph % difference':
				p1.y_range.start = -5
				p1.y_range.end = 5
			if plot1_ydata_to_plot == 'max position':
				p1.y_range.start = 345
				p1.y_range.end = 365

		return

	range_button.on_click(callback_range)

	############################################################################
	############################################################################



 	############################################################################
 	####################### RETURN TO THE MAIN SCRIPT ##########################

	return Panel(child = tab_layout, title = 'Flexitron Output')

	############################################################################
	############################################################################

################################################################################
################################################################################















#
