'''
Scripts for plotting from the Flatness and Symmetry Table
'''

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

import easygui as eg

# datetime for setting up DateRangeSlider with generic values
from datetime import date

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
								  DateRangeSlider, Button, RadioGroup)
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

def create_df(energy_selection, conn):

	'''
	Takes a connection to an MS Access database and pulls information from a
	table in that database into a dataframe using an SQL Query
	Filters for energy
	'''

	# If statement to decide energy chosen by user to define appropriate dataframe
	if energy_selection == '6MV':
		# Read data in from the database
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g17 6mv], [g9 6mv], [t9 6mv],[t17 6mv],'\
						'[a17 6mv], [a9 6mv], [b9 6mv],[b17 6mv], ' \
						'[flatness 6mv gt], [flatness 6mv ab] ' \
						'from [flat sym]', conn)
		# Filter row with data = 0
		df = df[df['g17 6mv'] !=0]
		# Add difference in symmetry values to y-axis
		df['inline_17'] = df['g17 6mv'] - df['t17 6mv']
		df['crossline_17'] = df['a17 6mv'] - df['b17 6mv']
		df['inline_9'] = df['g9 6mv'] - df['t9 6mv']
		df['crossline_9'] = df['a9 6mv'] - df['b9 6mv']
		df['flatness_gt'] = df['flatness 6mv gt']
		df['flatness_ab'] = df['flatness 6mv ab']
		df['inline_7'] = np.nan
		df['crossline_7'] = np.nan
	elif energy_selection == '10MV':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g17 10mv], [g9 10mv], [t9 10mv],[t17 10mv],'\
						'[a17 10mv], [a9 10mv], [b9 10mv],[b17 10mv], ' \
						'[flatness 10mv gt], [flatness 10mv ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g17 10mv'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_17'] = df['g17 10mv'] - df['t17 10mv']
		df['crossline_17'] = df['a17 10mv'] - df['b17 10mv']
		df['inline_9'] = df['g9 10mv'] - df['t9 10mv']
		df['crossline_9'] = df['a9 10mv'] - df['b9 10mv']
		df['flatness_gt'] = df['flatness 10mv gt']
		df['flatness_ab'] = df['flatness 10mv ab']
		df['inline_7'] = np.nan
		df['crossline_7'] = np.nan
	elif energy_selection == '6FFF':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g17 6fff], [g9 6fff], [t9 6fff],[t17 6fff],'\
						'[a17 6fff], [a9 6fff], [b9 6fff],[b17 6fff], ' \
						'[flatness 6fff gt], [flatness 6fff ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g17 6fff'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_17'] = df['g17 6fff'] - df['t17 6fff']
		df['crossline_17'] = df['a17 6fff'] - df['b17 6fff']
		df['inline_9'] = df['g9 6fff'] - df['t9 6fff']
		df['crossline_9'] = df['a9 6fff'] - df['b9 6fff']
		df['flatness_gt'] = df['flatness 6fff gt']
		df['flatness_ab'] = df['flatness 6fff ab']
		df['inline_7'] = np.nan
		df['crossline_7'] = np.nan
	elif energy_selection == '10FFF':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g17 10fff], [g9 10fff], [t9 10fff],[t17 10fff],'\
						'[a17 10fff], [a9 10fff], [b9 10fff],[b17 10fff], ' \
						'[flatness 10fff gt], [flatness 10fff ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g17 6fff'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_17'] = df['g17 10fff'] - df['t17 10fff']
		df['crossline_17'] = df['a17 10fff'] - df['b17 10fff']
		df['inline_9'] = df['g9 10fff'] - df['t9 10fff']
		df['crossline_9'] = df['a9 10fff'] - df['b9 10fff']
		df['flatness_gt'] = df['flatness 10fff gt']
		df['flatness_ab'] = df['flatness 10fff ab']
		df['inline_7'] = np.nan
		df['crossline_7'] = np.nan
	elif energy_selection == '6MeV':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g7 6mev], [t7 6mev], [a7 6mev],[b7 6mev], ' \
						'[flatness 6mev gt], [flatness 6mev ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g7 6mev'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_7'] = df['g7 6mev'] - df['t7 6mev']
		df['crossline_7'] = df['a7 6mev'] - df['b7 6mev']
		df['flatness_gt'] = df['flatness 6mev gt']
		df['flatness_ab'] = df['flatness 6mev ab']
		df['inline_9'] = np.nan
		df['crossline_9'] = np.nan
		df['inline_17'] = np.nan
		df['crossline_17'] = np.nan
	elif energy_selection == '9MeV':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g7 9mev], [t7 9mev], [a7 9mev],[b7 9mev], ' \
						'[flatness 9mev gt], [flatness 9mev ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g7 9mev'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_7'] = df['g7 9mev'] - df['t7 9mev']
		df['crossline_7'] = df['a7 9mev'] - df['b7 9mev']
		df['flatness_gt'] = df['flatness 9mev gt']
		df['flatness_ab'] = df['flatness 9mev ab']
		df['inline_9'] = np.nan
		df['crossline_9'] = np.nan
		df['inline_17'] = np.nan
		df['crossline_17'] = np.nan
	elif energy_selection == '12MeV':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g7 12mev], [t7 12mev], [a7 12mev],[b7 12mev], ' \
						'[flatness 12mev gt], [flatness 12mev ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g7 12mev'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_7'] = df['g7 12mev'] - df['t7 12mev']
		df['crossline_7'] = df['a7 12mev'] - df['b7 12mev']
		df['flatness_gt'] = df['flatness 12mev gt']
		df['flatness_ab'] = df['flatness 12mev ab']
		df['inline_9'] = np.nan
		df['crossline_9'] = np.nan
		df['inline_17'] = np.nan
		df['crossline_17'] = np.nan
	elif energy_selection == '15MeV':
		df = pd.read_sql('select [protocol id], [gantry angle], '\
						'[g7 15mev], [t7 15mev], [a7 15mev],[b7 15mev], ' \
						'[flatness 15mev gt], [flatness 15mev ab] ' \
						'from [flat sym]', conn)
		#filter row with data = 0
		df = df[df['g7 15mev'] !=0]
		#add difference in symmetry values to y-axis
		df['inline_7'] = df['g7 15mev'] - df['t7 15mev']
		df['crossline_7'] = df['a7 15mev'] - df['b7 15mev']
		df['flatness_gt'] = df['flatness 15mev gt']
		df['flatness_ab'] = df['flatness 15mev ab']
		df['inline_9'] = np.nan
		df['crossline_9'] = np.nan
		df['inline_17'] = np.nan
		df['crossline_17'] = np.nan
	else:
		eg.msgbox('Unknown energy entered. Raising system exit')
		raise SystemExit

	# Change the GA to string to be able to put it in a check list
	df['gantry angle'] = df['gantry angle'].astype('str')
	# Drop any rows that aren't related to the Truebeams
	df=df[df['protocol id'].str.contains("Truebeam B|TrueBeam C|TrueBeam D|TrueBeam F",case=False, na=False)]

	# Delete any rows that have no data in important fields
	df = df.dropna(subset=['protocol id'])

	# Get the adate and the machine name from thr protocol id
	df_left = df['protocol id'].str.partition(sep = '_')
	df_right = df['protocol id'].str.rpartition(sep = '_')
	df.loc[:,'adate'] = df_left[0]
	df.loc[:,'machinename'] = df_right[2]
	df.loc[:,'adate'] = pd.to_datetime(df.loc[:,'adate'])

	# Drop any columns where there is no data
	df = df.dropna(axis='columns', how='all')

	return df


# Create the function that will plot the data from this table/graph.
def Sym_Graph(conn):

	'''
	Create a graph for the Flatness and Symetry Results from the  Photon database
	'''

	# Set default viewing option
	x_data1 = 'adate'
	y_data1 = 'crossline_17'
	plot_title1 = 'Symmetry'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'
	hover_tool_fields = ['adate', 'gantry angle']
	# Create a list of the plot parameters
	list_plot_parameters = [x_data1, y_data1, plot_title1, x_axis_title1,
		y_axis_title1, plot_size_height1, plot_size_width1, legend_location]

	# Define the fields that the legend will be based off
	color_column = 'gantry angle'
	custom_color_boolean = False
	custom_color_palette = []
	marker_column = 'machinename'
	custom_marker_boolean = False
	custom_marker_palette = []
	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened.
	energy_selection = '6MV'
	color_to_plot = ['0.0']
	marker_to_plot = ['TrueBeam B']

	# Create a dataframe containing the data from the table
	df = create_df(energy_selection, conn)
	# Create a list of the fields using the dataframe..
	TableFields = (list(df.columns))
	# This deletes the raw data leaving just the processed stuff. Works because
	# the default energy selection is 6MV
	bad_list = ['g17 6mv', 'g9 6mv', 't9 6mv','t17 6mv', 'a17 6mv', 'a9 6mv',
		'b9 6mv','b17 6mv','flatness 6mv gt', 'flatness 6mv ab']
	TableFields = [x for x in TableFields if x not in bad_list]
	# Re add these columns that otherwise get cleared out by .dropna(axis='columns', how='all')
	TableFields.extend(['inline_7', 'crossline_7'])
	AxisFields = [x for x in TableFields if x not in ['machinename', 'protocol id']]

	# If you want to add tolerances change the boolean to True
	tolerance_boolean = False
	# Create toleance dataframes.
	if tolerance_boolean == True:
		df_tol1 = pd.DataFrame({'adate':[df['adate'].max(), df['adate'].max()],
								'crossline_17':[-1.5, 1.5],
								'crossline_9':[-1.5, 1.5],
								'crossline_7':[-1.5, 1.5],
								'inline_17':[-1.5, 1.5],
								'inline_9':[-1.5, 1.5],
								'inline_7':[-1.5, 1.5]})

		df_tol1_flat = pd.DataFrame({'adate':[df['adate'].max(), df['adate'].max()],
									'6MV_gt':[-10, 10],
									'6MV_ab':[-10, 10],
									'10MV_gt':[-10, 10],
									'10MV_ab':[-10, 10]})

		def special_tolerance(color_to_plot, x_data1, y_data1, Sub_df1, df_tol1_flat):

			energy_list = ['6MV', '10MV']
			data = {}

			if (x_data1 != 'adate') or (y_data1 != 'flatness_gt'):
				for x in range(0, len(energy_list)):
					data.update({'x_' + energy_list[x]: [Sub_df1['x'].max(),
								Sub_df1['x'].max()],
							'y_low_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()],
							'y_high_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()]})
			else:
				# Get a list of the column headers
				headers1 = df_tol1_flat.columns.values.tolist()
				# Check if the xdata is what is in the df_tol1 as the x_axis (if not no
				# point plotting tolerances as all tolerances are vs this column).
				max_x = Sub_df1['x'].max() + pd.DateOffset(weeks = 2)
				min_x = Sub_df1['x'].min() + pd.DateOffset(weeks = -2)

				for x in range(0, len(energy_list)):
					if energy_list[x] in color_to_plot:
						data.update({'x_' + energy_list[x]: [min_x, max_x],
								'y_low_' + energy_list[x]:
									[df_tol1_flat[energy_list[x]][0] ,
									df_tol1_flat[energy_list[x]][0] ],
								'y_high_' + energy_list[x]:
									[df_tol1_flat[energy_list[x]][1],
									df_tol1_flat[energy_list[x]][1]]})
					else:
						data.update({'x_' + energy_list[x]: [Sub_df1['x'].max(),
								Sub_df1['x'].max()],
							'y_low_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()],
							'y_high_' + energy_list[x]: [Sub_df1['y'].max(),
								Sub_df1['y'].max()]})


			Sub_df1_tol1_flat = pd.DataFrame(data)

			return Sub_df1_tol1_flat

	# Create columns for the legend
	(color_list, color_palette, marker_list, marker_palette,
	 	df, add_legend_to_df) = Create_Legend(df, color_column,
		custom_color_boolean, custom_color_palette, marker_column,
		custom_marker_boolean, custom_marker_palette,
		)

	# Make a sub dataframe that will be plotted and convert to ColumnDataSource
	Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
		marker_to_plot, x_data1, y_data1	)
	src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))

	print(color_list)
	print(type(color_list[0]))

	# Create a plot
	p1 = figure()
	p1.scatter(	source = src1,
				x = 'x',
				y = 'y',
				fill_alpha = 0.4,
				size = 12,
				legend_field = 'legend',
				marker = factor_mark('marker1', marker_palette, marker_list),
				color = factor_cmap('color1', color_palette, color_list)
				)

	# Set the plot parameters
	Define_Plot_Parameters(p1, list_plot_parameters)

	# Add the tolerances if defined above
	if tolerance_boolean == True:

		Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1,
			df_tol1)
		src1_tol = ColumnDataSource(Sub_df1_tol1.to_dict(orient='list'))

		# Add to the plot
		p1.line(source = src1_tol, x = 'x', y = 'y_low', color = 'firebrick')
		p1.line(source = src1_tol, x = 'x', y = 'y_high', color = 'firebrick')

		Sub_df1_tol1_flat = special_tolerance(color_to_plot, x_data1, y_data1,
			Sub_df1, df_tol1_flat)
		src1_tol_flat= ColumnDataSource(Sub_df1_tol1_flat.to_dict(orient='list'))

		# Add to the plot
		p1.line(source = src1_tol_flat, x = 'x_6MV', y = 'y_low_6MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6MV', y = 'y_high_6MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6XFFF', y = 'y_low_6XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6XFFF', y = 'y_high_6XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10MV', y = 'y_low_10MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10MV', y = 'y_high_10MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10XFFF', y = 'y_low_10XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10XFFF', y = 'y_high_10XFFF', color = 'firebrick')


	# Create a hovertool
	hover1 = HoverTool()
	# Check there aren't too many hovertool fields
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
	# Set hovertool parameters and add to the plot
	Update_HoverTool(hover1, x_data1, y_data1, **kwargs)
	p1.add_tools(hover1)

 	######## Widgets
	# Dropdown lists to change the x/y-axis.
	select_xaxis, select_yaxis = Create_Select_Axis(AxisFields, x_axis_title1,
		y_axis_title1)
	# Dropdown list to change the legend position.
	select_legend = Create_Select_Legend(legend_location)
	# Checkbox widgets used to create a tool to select the 'color' and 'marker' that are being plotted.
	checkbox_color, checkbox_marker = Create_Checkbox_Legend(df,
		color_column,color_to_plot, marker_column, marker_to_plot)
	# Checkbox widget used to select hovertool fields
	checkbox_hovertool = Create_Checkbox_HoverTool(TableFields,
		hover_tool_fields)
	# Button to requery the database and get up to date data.
	update_button = Button(label='Update with latest data', button_type='success')
	# Titles for the checkboxes
	color_title = Div(text='<b>Machine Choice</b>')
	marker_title = Div(text='<b>Marker</b>')
	hover_title = Div(text='<b>Hovertool Fields</b>')
	# Energy selection widget
	checkbox_energy = RadioGroup(labels=["6MV", "10MV", "6FFF", "10FFF", "6MeV",
		"9MeV", "12MeV", "15MeV"], active=0)

	# Create a layout
	if color_column == marker_column:
		layout_checkbox = column([color_title, checkbox_color])
	else:
		layout_checkbox = column([color_title, checkbox_color, marker_title,
		checkbox_marker])
	layout_plots = column([	update_button, checkbox_energy,
							select_xaxis, select_yaxis, select_legend, p1])
	# Add the two columns side-by-side.
	tab_layout = row([layout_plots, layout_checkbox])

 	####################### CREATE CALLBACK FUNCTIONS ##########################
	# Create a big callback that does most stuff
	def callback(attr, old, new):

		# Acquire the current values of all of the widgets
		energy_selection = checkbox_energy.labels[checkbox_energy.active]
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

		df = create_df(energy_selection, conn)
		df = add_legend_to_df(df, color_column, marker_column)

		# Create new version of the sub dataframe.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		# Update the plot.
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

		# Update the tolerances
		if tolerance_boolean == True:
			Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
				plot1_ydata_to_plot, Sub_df1, df_tol1)
			Sub_df1_tol1_flat = special_tolerance(color_to_plot,
				plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1, df_tol1_flat)

		# Update the ColumnDataSources
		src1.data = Sub_df1.to_dict(orient='list')
		if tolerance_boolean == True:
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')
			src1_tol_flat.data = Sub_df1_tol1_flat.to_dict(orient='list')
		return

	select_xaxis.on_change('value', callback)
	select_yaxis.on_change('value', callback)
	select_legend.on_change('value', callback)
	checkbox_color.on_change('active', callback)
	checkbox_marker.on_change('active', callback)
	checkbox_hovertool.on_change('active', callback)
	checkbox_energy.on_change('active', callback)



	# Callback for the Update Button
	def callback_update():

		# Make a new version of the dataframe
		energy_selection = checkbox_energy.labels[checkbox_energy.active]
		df = create_df(energy_selection, conn)
		df = add_legend_to_df(df, color_column, marker_column)

		# The rest of this callback is a copy from the original callback above.
		color_to_plot = [checkbox_color.labels[i] for i in
			checkbox_color.active]
		marker_to_plot = [checkbox_marker.labels[i] for i in
			checkbox_marker.active]
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
		src1.data = Sub_df1.to_dict(orient='list')
		if tolerance_boolean == True:
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

		return

	update_button.on_click(callback_update)

	# Return panel to the main script
	return Panel(child = tab_layout, title = 'Symmetry Graph')

















#
