################################################################################
############################## IMPORT LIBRARIES ################################

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# datetime for setting up DateRangeSlider with generic values
from datetime import date, timedelta

# functions from bokeh
from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter, BasicTickFormatter,
						  NumeralTickFormatter, Div)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup, Dropdown,
								  TableColumn, DataTable, Select,
								  DateRangeSlider, Button)
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import Category20_16, turbo, Colorblind
import bokeh.colors
from bokeh.io import output_file, show
from bokeh.transform import factor_cmap, factor_mark

from scripts.Universal import (	Create_Select_Axis, Create_Select_Legend,
								Create_Range_Sliders, Update_Range_Sliders,
								Create_Checkbox_Legend, Define_Plot_Parameters,
								Update_HoverTool, Create_Legend, Make_Dataset,
								Make_Dataset_Tolerance,
								Create_Checkbox_HoverTool)

################################################################################
################################################################################





################################################################################
################################ START OF CODE #################################

# Create the function that will plot the data from this table/graph.
def Electron_Energy_Graph(conn):

	output_file("Electron_Energy_Graph2.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	############################################################################
 	############################# USER INPUTS ##################################

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened).
	# NB: Have it set that if axis is 'adate' then will automatically update
	# to plot datetime.
	x_data1 = 'adate'
	y_data1 = '6fwhm'
	plot_title1 = 'Electron Energy'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'
	hover_tool_fields = ['comments']
	# Create a list of the plot parameters that will be used as input to a
	# function later.
	list_plot_parameters = [x_data1, y_data1, plot_title1, x_axis_title1,
		y_axis_title1, plot_size_height1, plot_size_width1, legend_location]
	# Define the fields that the legend will be based off. If there is only
	# one field then put it in both columns.
	color_column = 'machinename'
	custom_color_boolean = False
	custom_color_palette = []
	marker_column = 'machinename'
	custom_marker_boolean = False
	custom_marker_palette = []
	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened. NB: Bokeh will throw an error if one of these lists is
	# empty (i.e. =[]) If only using color or marker then set the color_to plot
	# and then enter the command:  marker_to_plot = color_to_plot.
	color_to_plot = ['TrueBeam B', 'TrueBeam C']
	marker_to_plot = ['option1', 'option2', 'option3']
	marker_to_plot = color_to_plot

	############################################################################
	#################### CREATE THE DATA FOR THE GRAPH #########################

	# Do this in a function so it can be used in an update callback later

	def Create_df():

		# Use the connection passed to the function to read the data into a
		# dataframe via an SQL query.
		df = pd.read_sql('SELECT * FROM [eEnergyICP]', conn)

		# Delete empty rows where the data is very important to have
		df = df.dropna(subset=['protocol id'], how='any')

		# The format is complicated for this field but seems to be that the date is
		# always the first element and the machine is always the last regardless of
		# how many elements there are.
		# Seperate on the first '_'
		df_left = df['protocol id'].str.partition(sep = '_')
		# Seperate on the last '_'
		df_right = df['protocol id'].str.rpartition(sep = '_')
		# From these sperated dataframes add the appropriate columns back into
		# the main dataframe.
		df.loc[:,'adate'] = df_left[0]
		df.loc[:,'machinename'] = df_right[2]
		# Turn 'adate' into datetime. An annoying factor in the database is a
		# few entries with a different datetime format. In combination with the
		# dayfirst=True parameter to override the American date default the
		# to_datetime function seems to solve this. NB: Might be a little slow
		# without feeding it a specific format but unlikely to be an issue given
		# relatively small datasets. Possibly someway to feed multiple formats
		# but currently more effort than it's worth.
		df.loc[:,'adate'] = pd.to_datetime(df.loc[:,'adate'], dayfirst=True)

		# Drop any rows that aren't related to the Truebeams (ditches the old
		# uneeded data). Might be possible to put this in the SQL query but
		# difficult as machinename is embedded in the protocol ID.
		df=df[df['machinename'].isin(['TrueBeam B', 'TrueBeam C', 'TrueBeam D',
			'TrueBeam F'])]

		# Drop any columns where there is no data (likely because of the
		# dropping of the old linacs (e.g. data that used to be collected from
		# them that is no longer collected for the Truebeams))
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
								'6fwhm':[6, 10],
								'9fwhm':[9, 12]})

		df_tol1 = pd.read_sql('SELECT * FROM [ElectronFWHMLimits]', conn)
		df_tol1 = df_tol1.set_index('class')
		df_tol1 = pd.DataFrame({'adate':[df['adate'].max(), df['adate'].max()],
								'6fwhm':[df_tol1.loc['TBUCLH', 'lower6'], df_tol1.loc['TBUCLH', 'upper6']],
								'9fwhm':[df_tol1.loc['TBUCLH', 'lower9'], df_tol1.loc['TBUCLH', 'upper9']],
								'12fwhm':[df_tol1.loc['TBUCLH', 'lower12'], df_tol1.loc['TBUCLH', 'upper12']],
								'15fwhm':[df_tol1.loc['TBUCLH', 'lower15'], df_tol1.loc['TBUCLH', 'upper15']]
								})

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
	Sub_df1 = Make_Dataset(df, color_column, color_to_plot, marker_column,
		marker_to_plot, x_data1, y_data1)

	# Make the ColumnDataSource (when making convert dataframe to a dictionary,
	# which is helpful for the callback).
	src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))

	######### Make Plot:
	# Create an empty plot (plot parameters will be applied later in a way that
	# can be manipulated in the callbacks)
	p1 = figure()
	p1.scatter(	source = src1,
				x = 'x',
				y = 'y',
				fill_alpha = 0.4,
				size = 12,
				# NB: Always use legend_field for this not legend_group as the
				# former acts on the javascript side but the latter the Python
				# side. Therefore the former will update automatically when the
				# plot is changed with no need for a callback.
				legend_field = 'legend',
				marker = factor_mark('marker1', marker_palette, marker_list),
				color = factor_cmap('color1', color_palette, color_list)
				)


	######### Add plot parameters:
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
	# This select funtion will be used to create dropdown lists to change the
	# data plotted on the x/y-axis.
	select_xaxis, select_yaxis = Create_Select_Axis(TableFields, x_axis_title1,
		y_axis_title1)

 	######## 2)
	# This select widget will be used to create dropdown lists to change the
	# legend position.
	select_legend = Create_Select_Legend(legend_location)


	######## 3)
	# These checkbox widgets will be used to create a tool to select the machine
	# and energy that are being plotted.
	checkbox_color, checkbox_marker = Create_Checkbox_Legend(df, color_column,
		color_to_plot, marker_column, marker_to_plot)


	######## 4)
	# These checkbox widgets will be used to create a tool to select the machine
	# and energy that are being plotted.
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
	marker_title = Div(text='<b>Marker</b>')
	hover_title = Div(text='<b>Hovertool Fields</b>')

	############################################################################
	############################################################################





	############################################################################
	########################### CREATE A LAYOUT ################################

	# Create a layout to add widgets and arrange the display.
	if color_column == marker_column:
		layout_checkbox = column([color_title, checkbox_color, hover_title,
			checkbox_hovertool])
	else:
		layout_checkbox = column([color_title, checkbox_color, marker_title,
			checkbox_marker, hover_title, checkbox_hovertool])

	button_row = row([update_button, range_button])

	layout_plots = column([	button_row, select_xaxis, select_yaxis,
		select_legend, p1])

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
		# Set the new axis titles
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

		# Update the ColumnDataSources.
		src1.data = Sub_df1.to_dict(orient='list')
		if tolerance_boolean == True:
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		return

	select_xaxis.on_change('value', callback)
	select_yaxis.on_change('value', callback)
	select_legend.on_change('value', callback)
	checkbox_color.on_change('active', callback)
	checkbox_marker.on_change('active', callback)
	checkbox_hovertool.on_change('active', callback)



	# Callback for the Update Button
	def callback_update():

		# Make a new version of the dataframe using the original Create_df
		# function that connects to the database.
		df = Create_df()
		df = add_legend_to_df(df)

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
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot
		legend_location = select_legend.value

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

		x_data1 = select_xaxis.value
		y_data1 = select_yaxis.value

		if (x_data1 == 'adate') and ((y_data1 == '6fwhm')
			or (y_data1 == '9fwhm') or (y_data1 == '12fwhm')
			or (y_data1 == '15fwhm') or (y_data1 == '16fwhm')):

			p1.x_range.start = Sub_df1['x'].max() - timedelta(weeks=53)
			p1.x_range.end = Sub_df1['x'].max() + timedelta(weeks=2)

			if y_data1 == '6fwhm':
				p1.y_range.start = 9.6
				p1.y_range.end = 10.3
			elif y_data1 == '9fwhm':
				p1.y_range.start = 12.6
				p1.y_range.end = 13.32
			elif y_data1 == '12fwhm':
				p1.y_range.start = 16.25
				p1.y_range.end = 17.01
			elif y_data1 == '15fwhm':
				p1.y_range.start = 19.4
				p1.y_range.end = 20.16
			elif y_data1 == '16fwhm':
				p1.y_range.start = 19.5
				p1.y_range.end = 19.9

		return

	range_button.on_click(callback_range)



	############################################################################
	############################################################################



 	############################################################################
 	####################### RETURN TO THE MAIN SCRIPT ##########################

	return Panel(child = tab_layout, title = 'Electron Energy')

	############################################################################
	############################################################################

################################################################################
################################################################################















#
