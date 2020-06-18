# pandas and numpy for data manipulation
import types
import pandas as pd
import numpy as np
# Import some basic tools from easygui to allow for user interface
from easygui import buttonbox, msgbox
from datetime import date

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter, BasicTickFormatter,
						  NumeralTickFormatter)
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

 	############################################################################
 	#################### CREATE THE DATA FOR THE GRAPH #########################

	output_file("Photon_Output_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	# Do this in a function so it can be used in an update callback later

	def Create_df():

		# Use the connection passed to the function to read the data into a
		# dataframe via an SQL query.
		df = pd.read_sql(	'SELECT [Protocol ID], [Energy], ' \
							'[chamber and electrometer], [Chamber factor], ' \
							'[Gantry angle], [Temp], [Press], [T/P factor], ' \
							'[output], [QI], [Comments], ' \
							'[Graph % Diff in output], [Graph % diff in QI] ' \
							'FROM [phcal_Graph]' \
							, conn	)

		# Delete empty rows where the data is very important to have
		df = df.dropna(subset=['protocol id'])
		df = df.dropna(subset=['energy'])

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
		# Create a list of the fields using the dataframe. By doing it now before
		# the extra legend fields are added it's easy to limit what is displayed in
		# the select widgets.
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

	# The purpose of this plot is generally to be as general as possible but
	# there are only a few parameters that will have defined tolerances.
	# Therefore the tolerance section can be a bit more specific and a dataframe
	# containing tolereances can be manually created for many cases and
	# extracted from the
	#
	# Create a dataframe of the things that need tolerances. The format of this
	# should be the first line being the x_axis (with some values taken from the
	# main dataframe to get the right formatting). The subsequent columns are
	# the toleranced [low, high]. NB: column names should match those from the
	# main dataframe.
	df_tol1 = pd.DataFrame({'adate':[df['adate'].max(), df['adate'].max()],
							'output':[98, 102],
							'graph % diff in output':[-2, 2]})

	############################################################################
	############################################################################






 	############################################################################
 	################### CREATE THE COLUMNS FOR THE LEGEND ######################

	# NB: The following section has been designed to be as general as possible
	# but in reality it might be preferable to more manually choose the markers
	# and colors based on optimising the most likey things to be plotted.
	#
	# Going to want to add a colour palette to the dataframe matched to a list
	# of energies (i.e. each unique energy has a unique colour in a different
	# column)


	color_column = 'energy'
	custom_color_boolean = True
	custom_color_palette = ['#FF0000', 'black', 'yellow', 'purple', '#008F8F', '#FF00FF', 'white']
	marker_column = 'machinename'
	custom_marker_boolean = True
	custom_marker_palette = [ 	'circle_x', 'square', 'square_x', 'diamond',
								'hex', 'x', 'circle_cross',
								'square_cross', 'diamond_cross', 'dash', 'cross',
								'inverted_triangle', 'circle', 'triangle', 'asterisk']

	(color_list, color_palette, marker_list, marker_palette, df,
		add_legend_to_df) = Create_Legend(df, color_column,
		custom_color_boolean, custom_color_palette, marker_column,
		custom_marker_boolean, custom_marker_palette
		)

	############################################################################
	############################################################################





 	############################################################################
 	################## FORMATTING AND CREATING A BASIC PLOT ####################

 	############################################################################
 	############################# USER INPUTS ##################################

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened).
	# NB: Have it set that if axis is 'adate' then will automatically update
	# to plot datetime.

	color_to_plot = ['6MV', '10MV']
	marker_to_plot = ['TrueBeam B', 'TrueBeam C', 'TrueBeam D']
	hover_tool_fields = ['chamber and electrometer', 'comments']
	x_data1 = 'adate'
	y_data1 = 'graph % diff in output'
	plot_title1 = 'Photon Output Results'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'

	list_plot_parameters = [	x_data1, y_data1,
	 							plot_title1, x_axis_title1, y_axis_title1,
								plot_size_height1, plot_size_width1,
								legend_location		]

	############################################################################
	############################################################################





 	############################################################################
 	########################### CREATE THE PLOT ################################

	# Run the Make_Dataset function to create two sub dataframs that the plots
	# will be made from.
	Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
		marker_to_plot, x_data1, y_data1	)

	# Make the ColumnDataSource (when making convert dataframe to a dictionary,
	# which is helpful for the callback).
	src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))

	# Plot the actual data
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
 	############################ ADD TOLERANCES ################################

	# We defined the tolerances further up and now want to add the correct ones
	# to the plot. Done in such a way that they are updated with the callbacks
	# later.
	Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1, df_tol1)

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
	# These range sliders will be used to change the displayed x and y ranges
	(range_slider_x, range_slider_y, range_slider_xdate,
		range_slider_ydate) = Create_Range_Sliders()
	Update_Range_Sliders(x_data1, y_data1, Sub_df1, range_slider_x,
		range_slider_y, range_slider_xdate, range_slider_ydate)

	######## 6)
	# Make an 'Update Button' to requery the database and get up to date data.
	update_button = Button(label='Update', button_type='success')




 	############################################################################
 	############################ CREATE A LAYOUT ###############################

	# Create a layout where the widgets will be added and any scaling applied.
	if color_column == marker_column:
		layout_checkbox = column([checkbox_color, checkbox_hovertool])
	else:
		layout_checkbox = column([checkbox_color, checkbox_marker,
			checkbox_hovertool])

	layout_plots = column([	update_button,
							select_xaxis, select_yaxis, select_legend,
							range_slider_x, range_slider_y,
							range_slider_xdate, range_slider_ydate,
							p1	])

	tab_layout = row([layout_plots, layout_checkbox])





 	############################################################################
 	####################### CREATE CALLBACK FUNCTIONS ##########################

	######## 1)
	#
	# Create a big callback that does everything?
	def callback(attr, old, new):

		# When making changes to the
		x_range_start = p1.x_range.start
		x_range_end = p1.x_range.end
		y_range_start = p1.y_range.start
		y_range_end = p1.y_range.end

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

		# Use the pre-defined Make_Dataset_Tolerance function with these new
		# inputs to update the tolerances.
		Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
			plot1_ydata_to_plot, Sub_df1, df_tol1)

		Update_HoverTool(hover1, plot1_xdata_to_plot, plot1_ydata_to_plot,
			**kwargs)

		# Update the ColumnDataSources.
		src1.data = Sub_df1.to_dict(orient='list')
		src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		# When making changes to the
		p1.x_range.start = x_range_start
		p1.x_range.end = x_range_end
		p1.y_range.start = y_range_start
		p1.y_range.end = y_range_end

		return

	checkbox_color.on_change('active', callback)
	checkbox_marker.on_change('active', callback)
	checkbox_hovertool.on_change('active', callback)




	def callback_legend(attr, old, new):

		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		legend_location = select_legend.value
		# Set the new axis titles
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot

		Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
	 		plot_title1, x_axis_title1, y_axis_title1, plot_size_height1,
			plot_size_width1, legend_location])

		return

	select_legend.on_change('value', callback_legend)




	def callback_axis(attr, old, new):

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
		Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
			plot1_ydata_to_plot, Sub_df1, df_tol1)

		# Use the pre-defined range_slider function to update the sliders
		Update_Range_Sliders(plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1,
			range_slider_x, range_slider_y, range_slider_xdate,
			range_slider_ydate)

		# Update the ColumnDataSources.
		src1.data = Sub_df1.to_dict(orient='list')
		src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		return

	# Use the on_change function to call the callback_axis when a new value is
	# selected by the select_axis widget.
	select_xaxis.on_change('value', callback_axis)
	select_yaxis.on_change('value', callback_axis)




	def callback_range(attr, old, new):

		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value

		if plot1_xdata_to_plot == 'adate':
			p1.x_range.start, p1.x_range.end = range_slider_xdate.value
		else:
			p1.x_range.start, p1.x_range.end = range_slider_x.value

		if plot1_ydata_to_plot == 'adate':
			p1.y_range.start, p1.y_range.end = range_slider_ydate.value
		else:
			p1.y_range.start, p1.y_range.end = range_slider_y.value

		return

	range_slider_x.on_change('value', callback_range)
	range_slider_y.on_change('value', callback_range)
	range_slider_xdate.on_change('value', callback_range)
	range_slider_ydate.on_change('value', callback_range)




	def callback_update():

		df = Create_df()
		print(df)
		df = add_legend_to_df(df)

		# Want to acquire the current values of all of the checkboxes and select
		# widgets to provide as inputs for the re-plot.
		color_to_plot = [	checkbox_color.labels[i] for i in
							checkbox_color.active]
		marker_to_plot = [	checkbox_marker.labels[i] for i in
								checkbox_marker.active]
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot
		legend_location = select_legend.value

		# Use the pre-defined Make_Dataset function with these new inputs to
		# create new versions of the sub dataframes.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		# Use the pre-defined Define_Plot_Parameters function with these new
		# inputs to update the plot.
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

		# Use the pre-defined tolerances function with these new inputs to
		# update the tolerances.
		Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
			plot1_ydata_to_plot, Sub_df1, df_tol1)

		# Update the range sliders
		Update_Range_Sliders(plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1,
			range_slider_x, range_slider_y, range_slider_xdate,
			range_slider_ydate)

		# Update the ColumnDataSources.
		src1.data = Sub_df1.to_dict(orient='list')
		src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		return

	update_button.on_click(callback_update)




	def callback_reset():

		color_to_plot = [	checkbox_color.labels[i] for i in
							checkbox_color.active]
		marker_to_plot = [	checkbox_marker.labels[i] for i in
								checkbox_marker.active]
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot
		legend_location = select_legend.value

		# Use the pre-defined Make_Dataset function with these new inputs to
		# create new versions of the sub dataframes.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		if plot1_ydata_to_plot == 'adate':
			range_slider_ydate.value = (Sub_df1['y'].min(), Sub_df1['y'].max())
		else:
			range_slider_y.value = (Sub_df1['y'].min(), Sub_df1['y'].max())

		if plot1_xdata_to_plot == 'adate':
			range_slider_xdate.value = (Sub_df1['x'].min(), Sub_df1['x'].max())
		else:
			range_slider_x.value = (Sub_df1['x'].min(), Sub_df1['x'].max())

		return

	p1.on_event('reset', callback_reset)


	############################################################################
 	####################### RETURN TO THE MAIN SCRIPT ##########################

	# Now that the script is finished and the plot created we can return to the
	# main script.
	#
	# To pass back the data for the tab we need to return a Panel with:
	# 	child = layout (the one that we made earlier with the widget and plot)
	# 	title = 'Something that makes sense as a tab label for the user'

	return Panel(child = tab_layout, title = 'Photon Output')

















#
