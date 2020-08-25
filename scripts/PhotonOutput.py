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


def Photon_Output_Graph(conn):

	output_file("Photon_Output_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

 	############################################################################
 	############################# USER INPUTS ##################################

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened).
	# NB: Have it set that if axis is 'adate' then will automatically update
	# to plot datetime.
	x_data1 = 'adate'
	y_data1 = 'graph % diff in output'
	plot_title1 = 'Photon Output Results'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'
	hover_tool_fields = ['chamber and electrometer', 'comments']
	# Create a list of the plot parameters that will be used as input to a
	# function later.
	list_plot_parameters = [x_data1, y_data1, plot_title1, x_axis_title1,
		y_axis_title1, plot_size_height1, plot_size_width1, legend_location]
	# Define the fields that the legend will be based off. If there is only
	# one field then put it in both columns.
	color_column = 'energy'
	custom_color_boolean = True
	custom_color_palette = ['#FF0000', 'black', 'yellow', 'purple', '#008F8F',
		'#FF00FF', 'white']
	marker_column = 'machinename'
	custom_marker_boolean = True
	custom_marker_palette = [ 	'circle_x', 'square', 'square_x', 'diamond',
		'hex', 'x', 'circle_cross', 'square_cross', 'diamond_cross', 'dash',
		'cross', 'inverted_triangle', 'circle', 'triangle', 'asterisk']
	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened. NB: Bokeh will throw an error if one of these lists is
	# empty (i.e. =[]) If only using color or marker then set the color_to plot
	# and then enter the command:  marker_to_plot = color_to_plot.
	color_to_plot = ['6MV', '10MV']
	marker_to_plot = ['TrueBeam B', 'TrueBeam C', 'TrueBeam D']

	############################################################################
	#################### CREATE THE DATA FOR THE GRAPH #########################

	# Do this in a function so it can be used in an update callback later

	def Create_df():

		# Use the connection passed to the function to read the data into a
		# dataframe via an SQL query.
		df = pd.read_sql(	'SELECT [Protocol ID], [Energy], ' \
							'[chamber and electrometer], [Chamber factor], ' \
							'[Gantry angle], [Temp], [Press], [T/P factor], ' \
							'[output], [QI], [Comments], ' \
							'[Graph % Diff in output], [Graph % diff in QI] ' \
							'FROM [phcal_Graph] ' \
							, conn	)

		# Delete empty rows where the data is very important to have
		df = df.dropna(subset=['protocol id'], how='any')
		df = df.dropna(subset=['energy'], how='any')

		# The format is complicated for this field but seems to be that the date is
		# always the first element and the machine is always the last regardless of
		# how many elements there are.
		# Seperate on the first '_'
		df_left = df['protocol id'].str.partition(sep = '_')
		# Seperate on the last '_'
		df_right = df['protocol id'].str.rpartition(sep = '_')
		# From these sperated dataframes add the appropriate columns back into the
		# main dataframe.
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
								'output':[98, 102],
								'graph % diff in output':[-2, 2]})

		# Added a seperate qi tolerance as multiple energes can appear
		# simultaneously so need an special tolerance function to deal with
		# this.
		df_tol1_qi = pd.DataFrame({	'adate':[df['adate'].max(), df['adate'].max()],
									'qi_6MV':[0.64, 0.68],
									'qi_6XFFF':[0.61, 0.65],
									'qi_10MV':[0.71, 0.75],
									'qi_10XFFF':[0.68, 0.72]})

		def special_tolerance(color_to_plot, x_data1, y_data1, Sub_df1, df_tol1_qi):

			energy_list = ['6MV', '6XFFF', '10MV', '10XFFF']
			data = {}

			if (x_data1 != 'adate') or (y_data1 != 'qi'):
				for x in range(0, len(energy_list)):
					data.update({'x_' + energy_list[x]: [Sub_df1['x'].max(),
								Sub_df1['x'].max()],
							'y_low_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()],
							'y_high_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()]})
			else:
				# Get a list of the column headers
				headers1 = df_tol1_qi.columns.values.tolist()
				# Check if the xdata is what is in the df_tol1 as the x_axis (if not no
				# point plotting tolerances as all tolerances are vs this column).
				max_x = Sub_df1['x'].max() + pd.DateOffset(weeks = 2)
				min_x = Sub_df1['x'].min() + pd.DateOffset(weeks = -2)

				for x in range(0, len(energy_list)):
					if energy_list[x] in color_to_plot:
						data.update({'x_' + energy_list[x]: [min_x, max_x],
								'y_low_' + energy_list[x]:
									[df_tol1_qi['qi_' + energy_list[x]][0],
									df_tol1_qi['qi_' + energy_list[x]][0]],
								'y_high_' + energy_list[x]:
									[df_tol1_qi['qi_' + energy_list[x]][1],
									df_tol1_qi['qi_' + energy_list[x]][1]]})
					else:
						data.update({'x_' + energy_list[x]: [Sub_df1['x'].max(),
									Sub_df1['x'].max()],
								'y_low_' + energy_list[x]: [Sub_df1['y'].max(),
									Sub_df1['y'].max()],
								'y_high_' + energy_list[x]: [Sub_df1['y'].max(),
									Sub_df1['y'].max()]})

			Sub_df1_tol1_qi = pd.DataFrame(data)

			return Sub_df1_tol1_qi



	############################################################################
	############################################################################

	############################################################################
	############################################################################
	'''

	This is the end of the user input section. If you don't need to make any
	other changes you can end here.

	'''








 	############################################################################
 	################### CREATE THE COLUMNS FOR THE LEGEND ######################

	(color_list, color_palette, marker_list, marker_palette, df,
		add_legend_to_df) = Create_Legend(df, color_column,
		custom_color_boolean, custom_color_palette, marker_column,
		custom_marker_boolean, custom_marker_palette
		)

	############################################################################
	############################################################################





 	############################################################################
 	################## FORMATTING AND CREATING A BASIC PLOT ####################

	######### Make Dataset:
	# Run the Make_Dataset function to create two sub dataframs that the plots
	# will be made from.
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
				# side. Therefore the former will update automatically.
				legend_field = 'legend',
				marker = factor_mark('marker1', marker_palette, marker_list),
				color = factor_cmap('color1', color_palette, color_list)
				)

	# Run the Define_Plot_Parameters function to set the plot parameters
	Define_Plot_Parameters(p1, list_plot_parameters)

	############################################################################
	############################################################################





	############################################################################
 	############################ ADD TOLERANCES ################################

	# We defined the tolerances further up and now want to add the correct ones
	# to the plot. Done in such a way that they are updated with the callbacks
	# later.
	if tolerance_boolean == True:

		Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1, df_tol1)

		src1_tol = ColumnDataSource(Sub_df1_tol1.to_dict(orient='list'))

		p1.line(source = src1_tol, x = 'x', y = 'y_low', color = 'firebrick')
		p1.line(source = src1_tol, x = 'x', y = 'y_high', color = 'firebrick')


		Sub_df1_tol1_qi = special_tolerance(color_to_plot, x_data1, y_data1,
			Sub_df1, df_tol1_qi)

		src1_tol_qi = ColumnDataSource(Sub_df1_tol1_qi.to_dict(orient='list'))

		p1.line(source = src1_tol_qi, x = 'x_6MV', y = 'y_low_6MV', color = 'yellow')
		p1.line(source = src1_tol_qi, x = 'x_6MV', y = 'y_high_6MV', color = 'yellow')
		p1.line(source = src1_tol_qi, x = 'x_6XFFF', y = 'y_low_6XFFF', color = 'mediumorchid')
		p1.line(source = src1_tol_qi, x = 'x_6XFFF', y = 'y_high_6XFFF', color = 'mediumorchid')
		p1.line(source = src1_tol_qi, x = 'x_10MV', y = 'y_low_10MV', color = 'firebrick')
		p1.line(source = src1_tol_qi, x = 'x_10MV', y = 'y_high_10MV', color = 'firebrick')
		p1.line(source = src1_tol_qi, x = 'x_10XFFF', y = 'y_low_10XFFF', color = 'black')
		p1.line(source = src1_tol_qi, x = 'x_10XFFF', y = 'y_high_10XFFF', color = 'black')

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
	color_title = Div(text='<b>Energy Choice</b>')
	marker_title = Div(text='<b>Machine Choice</b>')
	hover_title = Div(text='<b>Hovertool Fields</b>')

	############################################################################
	############################################################################





 	############################################################################
 	############################ CREATE A LAYOUT ###############################

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
		color_to_plot = [	checkbox_color.labels[i] for i in
							checkbox_color.active]
		if color_column != marker_column:
			marker_to_plot = [	checkbox_marker.labels[i] for i in
								checkbox_marker.active]
		else:
			marker_to_plot = color_to_plot
		hovertool_to_plot = [	checkbox_hovertool.labels[i] for i in
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
		# inputs to update the plot.
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

		# Use the pre-defined Make_Dataset_Tolerance function with these new
		# inputs to update the tolerances.
		if tolerance_boolean == True:
			Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
				plot1_ydata_to_plot, Sub_df1, df_tol1)
			Sub_df1_tol1_qi = special_tolerance(color_to_plot,
				plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1, df_tol1_qi)

		# Update the ColumnDataSources.
		src1.data = Sub_df1.to_dict(orient='list')
		if tolerance_boolean == True:
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')
			src1_tol_qi.data = Sub_df1_tol1_qi.to_dict(orient='list')

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
			Sub_df1_tol1_qi = special_tolerance(color_to_plot,
				plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1, df_tol1_qi)
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')
			src1_tol_qi.data = Sub_df1_tol1_qi.to_dict(orient='list')

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

		if (plot1_xdata_to_plot == 'adate') and ((plot1_ydata_to_plot == 'graph % diff in output')
			or (plot1_ydata_to_plot == 'output') or plot1_ydata_to_plot =='qi'):

			p1.x_range.start = Sub_df1['x'].max() - timedelta(weeks=53)
			p1.x_range.end = Sub_df1['x'].max() + timedelta(weeks=2)

			if plot1_ydata_to_plot == 'output':
				p1.y_range.start = 97
				p1.y_range.end = 103
			elif plot1_ydata_to_plot == 'graph % diff in output':
				p1.y_range.start = -3
				p1.y_range.end = 3
			elif plot1_ydata_to_plot =='qi':
				p1.y_range.start = 0.55
				p1.y_range.end = 0.8
		return

	range_button.on_click(callback_range)


	############################################################################
	############################################################################



	############################################################################
 	####################### RETURN TO THE MAIN SCRIPT ##########################

	return Panel(child = tab_layout, title = 'Photon Output')

	############################################################################
	############################################################################

################################################################################
################################################################################















#
