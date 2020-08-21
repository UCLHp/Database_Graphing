

################################################################################
################################ COMMON ISSUES #################################

# The read_sql stage is prone to some issues. Known errors are detailed in the
# comments above this function.

# Need to be very careful when making any copies of dataframes. This is because
# pandas makes either shallow or deep copies. When making a shallow copy any
# alterations to the shallow version can be applied back on to the original and
# vice-versa. Deep copies are more seperated and changes do not apply back to
# the original.

# When making the ColumnDataSource converting the dataframe to a dictionary
# seems to help with the callback functions that are used later.
# https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
# https://stackoverflow.com/questions/44829730/error-thrown-from-periodic-callback-valueerrormust-stream-updates-to-all-exis

# Currently there is no way to make an interaction that will update both the x
# and the y axis. It's possible that a workaround can be done by calling a
# piece of javascript code using CustomJS but this is a future project.

################################################################################
################################################################################





################################################################################
################################ USEFUL STUFF ##################################

# Good reasoning for purposes of running as a server.
# https://docs.bokeh.org/en/latest/docs/user_guide/server.html

# Useful page for looking at how the interactions work and what else can be
# added for more complex plots.
# https://docs.bokeh.org/en/latest/docs/user_guide/interaction.html

# Useful page for designing the layout and display properties of the plot/tab
# https://docs.bokeh.org/en/latest/docs/user_guide/styling.html#visual-properties

################################################################################
################################################################################





################################################################################
############################## IMPORT LIBRARIES ################################

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# datetime for setting up DateRangeSlider with generic values
from datetime import date

# functions from bokeh
from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
						  ColumnDataSource, Panel,
						  FuncTickFormatter, SingleIntervalTicker, LinearAxis,
						  CustomJS, DatetimeTickFormatter, BasicTickFormatter,
						  NumeralTickFormatter)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
								  Tabs, CheckboxButtonGroup, Dropdown,
								  TableColumn, DataTable, Select,
								  DateRangeSlider)
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import Category20_16, turbo, Colorblind
import bokeh.colors
from bokeh.io import output_file, show
from bokeh.transform import factor_cmap, factor_mark

################################################################################
################################################################################





################################################################################
################################ START OF CODE #################################

# Create the function that will plot the data from this table/graph.
def Electron_Energy_Graph_Old(conn):

	############################################################################
	#################### CREATE THE DATA FOR THE GRAPH #########################

	output_file("Electron_Output_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	# Use the connection passed to the function to read the data into a
	# dataframe via an SQL query.
	df = pd.read_sql('SELECT * FROM [eEnergyICP]', conn)
	print(df)

	# Delete cells where 'protocol id' is empty
	df = df.dropna(subset=['protocol id'])

	# With any luck this can be removed after chatting to AW and MB ?????????????????????????????????????????????????????????????????????????????????
	# Get the date and machinename from the protocol id' field
	# Seperate on the first '_'
	df_left = df['protocol id'].str.partition(sep = '_')
	# Seperate on the last '_'
	df_right = df['protocol id'].str.rpartition(sep = '_')
	# From these sperated dataframes add the appropriate columns back into the
	# main dataframe.
	df.loc[:,'adate'] = df_left[0]
	df.loc[:,'machinename'] = df_right[2]

	# Turn 'adate' into datetime. Problems with this function as it assumes american date formats over british. ?????????????????????????????????????????????????????????????????????????????????
	# Talk to AW and MB about getting date from other tables in the database and pulling them into the query. ???????????????????????????????????????????????????????????????????????????????????
	# This way the date should be in a set format that the datetime function can be told, which should resolve this issue. ??????????????????????????????????????????????????????????????????????
	#
	# Need to turn the date fields into a Dateime object (either 'adate'
	# (protons) or the newly created 'adate' (photons)). The date field should
	# always be named 'adate' for consistency.
	df.loc[:,'adate'] = pd.to_datetime(df.loc[:,'adate'])

	# When starting a new graph can be useful to print the dataframe after any
	# manipulations to make sure the code has done what you expected.
	print(df)

	# Create a list of the fields using the dataframe
	TableFields = (list(df.columns))

	############################################################################
	############################################################################





 	############################################################################
 	################ CREATE THE DATAFRAME FOR THE TOLERANCES ###################

	# The purpose of this plot is generally to be as general as possible but
	# there are only a few parameters that will have defined tolerances.
	# Therefore the tolerance section can be a bit more specific and a dataframe
	# containing tolereances can be manually created for many cases and
	# extracted from the database in others (in a manner similar to above but
	# calling from a different table/query with the SQL statement)
	#
	# The format of the dataframe should be the first line being the x_axis
	# (with some values taken from the main dataframe to get the right
	# formatting). The subsequent columns are the tolerances [low, high].
	# NB: column names should match those from the main dataframe.
	df_tol1 = pd.read_sql('SELECT * FROM [ElectronFWHMLimits]', conn)
	print(df_tol1)
	df_tol1 = df_tol1.set_index('class')
	print(df_tol1)

	df_tol_TB = pd.DataFrame({	'adate':[df['adate'].max(), df['adate'].max()],
								'6fwhm':[df_tol1.loc['TBUCLH', 'lower6'], df_tol1.loc['TBUCLH', 'upper6']],
								'9fwhm':[df_tol1.loc['TBUCLH', 'lower9'], df_tol1.loc['TBUCLH', 'upper9']],
								'12fwhm':[df_tol1.loc['TBUCLH', 'lower12'], df_tol1.loc['TBUCLH', 'upper12']],
								'15fwhm':[df_tol1.loc['TBUCLH', 'lower15'], df_tol1.loc['TBUCLH', 'upper15']]
								})
	print(df_tol_TB)

	df_tol_Classic = pd.DataFrame({	'adate':[df['adate'].max(), df['adate'].max()],
									'6fwhm':[df_tol1.loc['Classic', 'lower6'], df_tol1.loc['Classic', 'upper6']],
									'9fwhm':[df_tol1.loc['Classic', 'lower9'], df_tol1.loc['Classic', 'upper9']],
									'12fwhm':[df_tol1.loc['Classic', 'lower12'], df_tol1.loc['Classic', 'upper12']],
									'16fwhm':[df_tol1.loc['Classic', 'lower16'], df_tol1.loc['Classic', 'upper16']],
									'20fwhm':[df_tol1.loc['Classic', 'lower20'], df_tol1.loc['Classic', 'upper20']]
									})
	print(df_tol_Classic)

	############################################################################
	############################################################################






	##########################################################################
	################### CREATE THE COLUMNS FOR THE LEGEND ######################

	# NB: The following section has been designed to be as general as possible
	# but in reality it might be preferable to more manually choose the markers
	# and colors based on optimising the most likey things to be plotted.
	#
	# This code is a way of creating a legend with markers based on one
	# parameter (e.g. machine name) and color on another parameter (e.g. energy)


	######### Colors:
	# Create a sorted list of the unique values in a dataframe column that the
	# colors will be based on.
	list_forcolor = sorted(df['machinename'].unique().tolist())
	# If the length of the list is <9 then we can use the colorblind palette,
	# which contains 8 colors. This should be the default for accessability
	# reasons unless there are compeling reasons otherwise.
	if len(list_forcolor) < 9:
		color_palette = Colorblind[len(list_forcolor)]
	# If not <9 then we can use the much larger Turbo palette which contains
	# 256 colors. Will check if there are more than 256 options though and
	# throw an error if so.
	elif len(list_forcolor) > 256:
		print(	'Error - Name of Function: >256 unique energies in database ' \
				'causing failure of the turbo color palette function (only ' \
			   	'256 availible colors.'	)
		exit()
	# If it passes the check then use the built in turbo function that splits
	# the turbo palette into roughly equal sections based on a supplied integer
	# number.
	else:
		color_palette = turbo(len(list_forcolor))


	######### Markers:
	# Doesn't seem to be a way to create a simple list of all the Bokeh marker
    # options so just do this manually. May want to re-order to improve
	# visibility of commonly used options.
	markers = [ 'asterisk', 'circle', 'circle_cross', 'circle_x', 'cross',
				'dash', 'diamond', 'diamond_cross', 'hex', 'inverted_triangle',
				'square', 'square_cross', 'square_x', 'triangle', 'x']
	# Create a sorted list of the unique values in a dataframe column that the
	# markers will be based on.
	list_formarker = sorted(df['machinename'].unique().tolist())
	# Check that there are enough markers to give a unique marker to each option
	# but otherwise throw an error.
	if len(list_formarker) > len(markers):
		print(	'Error - Name of Function: Not enough markers to assign a ' \
			  	'unique marker to each option.'	)
		exit()


	######### Legend Key:
	# Create a function that will be used to run through the dataframe looking
	# at the energy and machine column and creating a new column that will have
	# values for both seperated by a '_', stored as a string.
	def add_legend(row):
		return str(	str(row['machinename']))
	# Run the function and also copy the other columns into new columns so that
	# when ther are renamed to 'x' and 'y' later they are still availible for
	# the legend if needed.
	df.loc[:,'legend']=df.apply(lambda row: add_legend(row), axis=1)
	df.loc[:,'machinename1']=df.loc[:,'machinename']
	print(df)

	############################################################################
	############################################################################





 	############################################################################
 	################## FORMATTING AND CREATING A BASIC PLOT ####################

 	############################################################################
 	############################# USER INPUTS ##################################

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened, the plot size
	# etc.).

	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened
	color_to_plot = ['TrueBeam B', 'TrueBeam C']
	marker_to_plot = color_to_plot

	# Decide on what data to plot on the x/y axis when opened.
	x_data1 = 'adate'
	y_data1 = '6fwhm'
	# Decide what the plot formatting will be, inluding the plot title, axis
	# titles and the size of the plot.
	plot_title1 = 'Electron Energy'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'

	# Create a list of the plot parameters that will be used as input to a
	# function later.
	list_plot_parameters = [	x_data1, y_data1,
	 							plot_title1, x_axis_title1, y_axis_title1,
								plot_size_height1, plot_size_width1,
								legend_location		]

	############################################################################
	############################################################################

 	############################################################################
 	########################### CREATE THE PLOT ################################

	# Create the actual ploy. Generally it's a good idea to do this by defining
	# functions as they can then be used in the callbacks later without having
	# a lot of redundant very similar code.


	######### Make Dataset:
	# Define a make dataset function that can be used now but also called later
	# in the callback functions to save re-writing similar code later.
	def make_dataset(color_to_plot, marker_to_plot, x_data1, y_data1):
		# Create a sub dataframe
		Sub_df1 = df.copy()
		# Delete any rows in the sub-dataframes that do not exist in the
		# checkboxes/default user choices. (e.g. if you've selected 6MV in the
		# checkbox this will remove any rows that have something other than 6MV)
		Sub_df1 = Sub_df1[Sub_df1['machinename'].isin(color_to_plot)]
		Sub_df1 = Sub_df1[Sub_df1['machinename'].isin(marker_to_plot)]
		# Search for the columns with the x_data and y_data names and replace
		# them with 'x' and 'y'. Unless plotting the same data on both in which
		# case add an extra column for 'y' that's a copy of 'x'
		if x_data1 == y_data1:
			Sub_df1.rename(columns = {x_data1:'x'}, inplace = True)
			Sub_df1.loc[:,'y'] = Sub_df1.loc[:,'x']
		else:
			Sub_df1.rename(columns = {x_data1:'x'}, inplace = True)
			Sub_df1.rename(columns = {y_data1:'y'}, inplace = True)
		# Return the newly created Sub_df1
		return Sub_df1

	# Run the make_dataset function to create a sub dataframe that the plot will
	# be made from.
	Sub_df1 = make_dataset(	color_to_plot, marker_to_plot,
							x_data1, y_data1	)


	# Create a Column Data Source. This is important as it is the data format
	# needed for Bokeh. When making this it is useful to convert the dataframe
	# into a dictionary, which seems to help with the callback function (see
	# 'Common Issues' for details).
	src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))


	######### Make Plot:
	# Create an empty plot (plot parameters will be applied later in a way that
	# can be manipulated in the callbacks)
	p1 = figure()
	# Create a scatter plot.
	p1.scatter(	# source = The ColumnDataSource made above.
				source = src1,
				# x/y = 'x'/'y' which are fields that were renamed as such in
				# the make_dataset function
				x = 'x',
				y = 'y',
				# Some general parameters about marker size. These seem like
				# reasonable values but possible could alter these in a
				# callback?
				fill_alpha = 0.4,
				size = 12,
				# Create the legend using the created fields added in the legend
				# section. Use the factor_mark and factor_cmap functions to
				# match the colors/markers to the right lists.
				# NB: Always use legend_field for this not legend_group as the
				# former acts on the javascript side but the latter the Python
				# side. Therefore the former will update automatically when the
				# plot is changed with no need for a callback.
				legend_field = 'legend',
				marker = factor_mark('machinename1', markers, list_formarker),
				color = factor_cmap('machinename1', color_palette, list_forcolor)
				)


	######### Add plot parameters:
	# Define a define plot parameters factor that can be used now but also
	# called later in the callback functions.
	def define_plot_parameters (list):

		# Input is a List of format:
		# list_plot_parameters = [	x_data1, y_data1,
		# 	 						plot_title1, x_axis_title1, y_axis_title1,
		# 							plot_size_height1, plot_size_width1,
		# 							legend_location	]

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

	# Run the define_plot_parameters function to format the plot.
	define_plot_parameters(list_plot_parameters)

	############################################################################
	############################################################################

	############################################################################
	############################################################################





	############################################################################
 	############################ ADD TOLERANCES ################################

	# We defined the tolerances further up and now want to add the correct ones
	# to the plot (having created the plot above). Again this will be done with
	# functions and in a way that the functions can be used in the callbacks
	# later.
	#
	# NB: At the moment this is still a bit of a work in progress and shows the
	# way to add line tolerances. Another option might be to add colorblocks
	# using varea and/or varea_stack.
	#
	# NB: Also this funcion assumes that tolerances will all be against one
	# x_axis value (e.g. date). This is probably the majority of use cases but
	# probably relatively trivial to add further toleraces against other x_axis
	# data.

	# Create a function that will create a dataframe that can be used to supply
	# a plot of two tolerance lines. This will including 'appearing' and
	# 'disappearing' depending on whether tolerances are defined or not.


	def tolerances(x_data1, y_data1, Sub_df1, df_tol1):

		# Get a list of the column headers from the tolerance table defined
		# earlier.
		headers1 = df_tol1.columns.values.tolist()

		# Check if the xdata is what is in the df_tol1 as the x_axis (if not no
		# point plotting tolerances as all tolerances are vs this tolerance).
		if x_data1 != headers1[0]:
			# x_data1 doesn't match so going to output something that should
			# basically just not plot but also won't throw the viewing range.
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
					'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
					'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol1 = pd.DataFrame(data)
			return Sub_df1_tol1
		# Otherwise we have the right x_data1 so now just check if it's datetime
		# or not.
		if x_data1 == 'adate':
			# It has the format 'adate' so should be datetime. So find the max
			# min dates in the Sub_df1 and add a couple of weeks either side so
			# that it plots the full range (plus a little bit for visualisation
			# reasons).
			max_x = Sub_df1['x'].max() + pd.DateOffset(weeks = 2)
			min_x = Sub_df1['x'].min() + pd.DateOffset(weeks = -2)
		else:
			# If it's not datetime then just add about 5% of the range to
			# either side to make the plot look nicer.
			# NB: This has not been checked extensively as most tolerances are
			# vs. time.
			max_x = Sub_df1['x'].max()
			min_x = Sub_df1['x'].min()
			range = max_x - min_x
			max_x = max_x + (range/20)
			min_x = min_x - (range/20)

		# Used the x part so now remove the element from the list. This will
		# help for the small case where x_data1 == ydata1.
		headers1.remove(x_data1)


		if y_data1 in headers1:
			# If y_data1 is in the list then loop through to find out where and
			# get the data from the tolerance dataframe.
			for x in headers1:
				if y_data1 == x:
					# When the loop has found where it is then can output a
					# dataframe of the form:
					# 	x = [far left of plot, far right of plot]
					# 	y_low = [low_tolerance, low_tolerance]
					# 	y_high = [high_tolerance, high_tolerance]
					data = {'x': [min_x, max_x],
							'y_low': [df_tol1[x][0], df_tol1[x][0]],
							'y_high': [df_tol1[x][1], df_tol1[x][1]]}
					Sub_df1_tol1 = pd.DataFrame(data)
		else:
			# If y_data1 is not in the headers1 list then there are no
			# tolerances to plot so going to output something that should
			# basically just not plot but also won't throw the viewing range.
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
					'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
					'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol1 = pd.DataFrame(data)
			return Sub_df1_tol1

		return Sub_df1_tol1

	def choose_tolerances(x_data1, y_data1, Sub_df1, color_to_plot):

		if any(item in color_to_plot for item in
				['TrueBeam B', 'TrueBeam C', 'TrueBeam D', 'TrueBeam F']):
			# If this is true then will need to run the df_tol_TB tolerances
			Sub_df1_tol_TB = tolerances(x_data1, y_data1, Sub_df1, df_tol_TB)
		else:
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
					'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
					'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol_TB = pd.DataFrame(data)

		if any(item in color_to_plot for item in
				['Linac B', 'Linac C', 'Linac D', 'Linac E']):
			# If this is true then will need to run the df_tol_TB tolerances
			Sub_df1_tol_Classic = tolerances(x_data1, y_data1, Sub_df1, df_tol_Classic)
		else:
			data = {'x': [Sub_df1['x'].max(), Sub_df1['x'].max()],
					'y_low': [Sub_df1['y'].max(), Sub_df1['y'].max()],
					'y_high': [Sub_df1['y'].max(), Sub_df1['y'].max()]}
			Sub_df1_tol_Classic = pd.DataFrame(data)

		return Sub_df1_tol_TB, Sub_df1_tol_Classic

	# Run the tolerances function to output the new dataframe
	Sub_df1_tol_TB, Sub_df1_tol_Classic = choose_tolerances(x_data1, y_data1, Sub_df1, color_to_plot)

	# Turn the dataframe into a new ColumnDataSource (again turning it into a
	# dictionary)
	src1_tol_TB = ColumnDataSource(Sub_df1_tol_TB.to_dict(orient='list'))
	src1_tol_Classic = ColumnDataSource(Sub_df1_tol_Classic.to_dict(orient='list'))

	# Add two lines to the plot using the new ColumnDataSource as the source,
	# one line for low tolerance and one line for high.
	p1.line(source = src1_tol_TB, x = 'x', y = 'y_low', color = 'firebrick')
	p1.line(source = src1_tol_TB, x = 'x', y = 'y_high', color = 'firebrick')
	p1.line(source = src1_tol_Classic, x = 'x', y = 'y_low', color = 'hotpink')
	p1.line(source = src1_tol_Classic, x = 'x', y = 'y_high', color = 'hotpink')

	############################################################################
	############################################################################





 	############################################################################
 	################## ADD MORE COMPLEX TOOLS TO THE PLOT ######################

	# Create tools here that will allow for some manipulation or inspection of
	# plotted data.
	#
	# As an example a 'HoverTool' will be added to the plot.
	#
	# Other useful tools and details of the syntax can be found here:
	# https://docs.bokeh.org/en/latest/docs/user_guide/tools.html


	# Create the hover tool (see website above for syntax/details).
	# This example creates a hover tool that displays:
	# 	Date: 			The value of the data-point as measued on the x-axis
	# 					(formatted for datetime)
	# 	Y-Axis:			The value of the data-point as measued on the y-axis
	# 	(x,y):			The x and y co-ordinates in plot space
	# 	Chamber Comb.:	The data stored under the 'Chamber' column for that
	# 					data-point.
	# 	Comments:		The data stored under the 'comments' column for that
	#					data-point.
	hover = HoverTool(tooltips = [	('Date', '@x{%F}'),
									('Y-Axis', '@y'),
									('(x,y)', '($x, $y)'),
									('Chamber Comb.', '@Chamber'),
									('Comments', '@comments')],
									formatters = {'x': 'datetime'} )

	# Add the newly created tool to the plot.
	p1.add_tools(hover)

	############################################################################
	############################################################################





 	############################################################################
 	################# CREATE WIDGETS TO BE ADDED TO THE PLOT ###################

	# Create widgets here that will allow for some manipulation of the plotted
	# data. These widgets provide an interactive ability that can alter the data
	# that is plotted, provide update fnctions and call other programmatic
	# functions. This is done either using built in Bokeh functionality or
	# using more powerful but complex python and javascript based callbacks.
	#
	# As an example some 'Select' widgets, 'Checkbox' widgets and 'RangeSliders'
	# will be added to the plot.
	#
	# Other useful widgets and details of the syntax can be found here:
	# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html


 	######## 1)
	# Create the select widget (see website above for syntax/details). This
	# widget will be used for the callback example later to change data plotted
	# on the x/y-axis.
	# This example creates a select tool that displays:
	# 	Dropdown list containing a list of every field that was downloaded from
	# 	the database.
	# 	NB: 	When making a list it may be worth manually creating it to limit
	# 			it to the fields that can be plotted (e.g. not including fields
	# 			like 'Comments'). This will shorten the dropdown list but you
	# 			should err on the side of inclusion to make the final plot as
	# 			flexible as possible.
	#
	# Create a list of the availible options
	menu_axis = []
	for field in TableFields:
		menu_axis.append(field)
	menu_axis = sorted(menu_axis)
	# Select tool needs inputs for the title, a starting value and the just
	# created list to supply the available options.
	select_xaxis = Select(  title = 'X-Axis Fields Available:',
							value = x_axis_title1,
							options = menu_axis	)
	select_yaxis = Select(  title = 'Y-Axis Fields Available:',
							value = y_axis_title1,
							options = menu_axis	)


 	######## 2)
	# This select widget will be made in the same way and used to create a
	# dropdown list to change the legend position.
	#
	# Create a list of the availible options
	menu_legend = [	'top_left', 'top_center', 'top_right',
					'center_left', 'center', 'center_right',
					'bottom_left', 'bottom_center', 'bottom_right']
	# Create the select tool as above
	select_legend = Select(  title = 'Legend Position',
							value = legend_location,
							options = menu_legend	)


	######## 3)
	# These checkbox widgets will be used to create a tool to select the
	# values that are being plotted from the fields that the legend is based on.
	#
	# NB: There is some built in Bokeh functionality for interavtive legends
	# that can fulfill some of the same goals where the number of options is
	# limited to something that can display on a reasonably sized legend. May
	# be a better and more robust solution where possible.

	# Create a list of all unique names in the column chosen to be matched to
	# markers (sorted).
	options_marker = sorted(df['machinename'].unique().tolist())
	# Create an index list for all of the values that should be pre-ticked.
	index_marker = [i for i in range(len(options_marker)) if options_marker[i] in marker_to_plot]
	# Create the checkbox, providing the list of availible options and a list
	# of what should be active (pre-ticked).
	checkbox_marker = CheckboxGroup(
		labels = options_marker, active = index_marker, visible = False)

	# Do the same for the column that was matched to colors.
	options_color = sorted(df['machinename'].unique().tolist())
	index_color = [i for i in range(len(options_color)) if options_color[i] in color_to_plot]
	checkbox_color = CheckboxGroup(
		labels = options_color, active = index_color)


	######## 4)
	# Make some range sliders that will be used to manipulate the x-axis and
	# y-axis range.

	# Most of the manipulation will be done using a later function but will need
	# to create the bare minimum rangeslider first that can later be manipulated
	# (This seems to be the minimum number of parameters needed to create these
	# widgets). Note that a RangeSliders AND a DateRangeSlider needs to be
	# created for each axis.
	range_slider_x = RangeSlider(title='X-Axis Range', start=0, end=1, value=(0,1), step=0.1)
	range_slider_y = RangeSlider(title='Y-Axis Range', start=0, end=1, value=(0,1), step=0.1)
	range_slider_xdate = DateRangeSlider(	title = 'X-Axis Range (Date)',
											start = date(2017,1,1),
											end =  date(2017,1,2),
											value = (date(2017,1,1), date(2017,1,2)),
											step = 1	)
	range_slider_ydate = DateRangeSlider(	title = 'Y-Axis Range (Date)',
											start = date(2017,1,1),
											end =  date(2017,1,2),
											value = (date(2017,1,1), date(2017,1,2)),
											step = 1	)

	# Define the function that will be used now and also in the callbacks later.
	# This will allow the range_sliders to adjust to match any changes in the
	# data being plotted on the x/y axis.
	def range_slider(x_data1, y_data1, Sub_df1):

		# Start with the y-axis.
		# First need to check if 'adate' and if so edit the date range slider
		# but otherwise edit the normal slider.
		if y_data1 == 'adate':
			# Set the start, end and value fields to the full range.
			range_slider_ydate.start = Sub_df1['y'].min()
			range_slider_ydate.end = Sub_df1['y'].max()
			range_slider_ydate.value = (Sub_df1['y'].min(), Sub_df1['y'].max())
			# Step to 1 works for DateRangeSlider
			range_slider_ydate.step = 1
			# Make the DateRangeSlider visible and hide the normal RangeSlider
			range_slider_ydate.visible = True
			range_slider_y.visible = False
		else:
			# Set the start, end and value fields to the full range.
			range_slider_y.start = Sub_df1['y'].min()
			range_slider_y.end = Sub_df1['y'].max()
			range_slider_y.value = (Sub_df1['y'].min(), Sub_df1['y'].max())
			# Step to range/10000 should give sufficient granularity
			range_slider_y.step = (Sub_df1['y'].max()-Sub_df1['y'].min())/100000
			# Make the normal RangeSlider visible and hide the DateRangeSlider
			range_slider_y.visible = True
			range_slider_ydate.visible = False

		# Do the same for the x-axis
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
			range_slider_x.step = (Sub_df1['x'].max()-Sub_df1['x'].min())/100000
			range_slider_x.visible = True
			range_slider_xdate.visible = False

		return

	# Run the function.
	range_slider(x_data1, y_data1, Sub_df1)

	############################################################################
	############################################################################





	############################################################################
	########################### CREATE A LAYOUT ################################

	# Create a layout to add widgets and arrange the display. This simple layout
	# displays the select widgets above the plot with the checkboxes to the
	# right (one above the other).
	#
	# More details can be found at:
	# https://docs.bokeh.org/en/latest/docs/user_guide/layout.html
	#
	# NB: More work to do here to make plots responsive to browser window size
	# (e.g. using sizing_mode = scale_both) but need to invstigate with/without
	# remote desktops.

	layout_checkbox = column([checkbox_marker, checkbox_color])
	layout_plots = column([	select_xaxis, select_yaxis, select_legend,
							range_slider_x, range_slider_y,
							range_slider_xdate, range_slider_ydate,
							p1	])

	tab_layout = row([layout_plots, layout_checkbox])

	############################################################################
	############################################################################





 	############################################################################
 	####################### CREATE CALLBACK FUNCTIONS ##########################

	# CAVEAT: Callback functions are very complex and below is my (CB) rough
	# understanding of how they function based mainly on experience/trial and
	# error while writting these functions for other graphs. It should be taken
	# as a starting point but not as a definitive user guide.
	#
	# Callback functions are very powerful and can be based off of javascript or
	# python. The example presented here uses python but in future a javascript
	# copy should also be added.


	######## 1)
	# This callback is designed to take inputs from the select and checkbox
 	# widgets update the graph to plot the new data requested by the user.
	#
	# Syntax:
	# 	attr = 	The value passed from the on_change function before the callback
	# 			was named (e.g. in this example attr = 'value')
	# 	old = 	The value of the widget before it was changed (I.e. If a select
	# 			widget is changed from 'Output' to 'T/P Correction', then
	# 			old = 'Output'
	# 	new = 	The value of the widget after it was changed (I.e. If a select
	# 			widget is changed from 'Output' to 'T/P Correction', then
	# 			old = 'T/P Correction'
	#
	# 	NB: In general seen little need to use these inputs as you can generally
	# 	access the value of the widgets directly which seems to be more powerful
	# 	and flexible
	#
	# First define the callback function.
	def callback(attr, old, new):

		# Want to acquire the current values of all of the checkboxes and select
		# widgets to provide as inputs for the re-plot. For the checkboxes this
		# means itterating through the active list and outputting the labels
		# that are active
		color_to_plot = [	checkbox_color.labels[i] for i in
							checkbox_color.active]
		marker_to_plot = color_to_plot
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		legend_location = select_legend.value

		# Use the pre-defined make_dataset function with these new inputs to
		# create a new version of the sub dataframe.
		Sub_df1 = make_dataset(	color_to_plot, marker_to_plot,
								plot1_xdata_to_plot, plot1_ydata_to_plot)

		# Use the pre-defined define_plot_parameters function with these new
		# inputs to update the plot parameters.
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot
		define_plot_parameters([	plot1_xdata_to_plot, plot1_ydata_to_plot,
	 								plot_title1, x_axis_title1, y_axis_title1,
									plot_size_height1, plot_size_width1,
									legend_location	])

		# Use the pre-defined tolerances function with these new inputs to
		# make a new version of the tolerances sub dataframe.
		Sub_df1_tol_TB, Sub_df1_tol_Classic = choose_tolerances(	plot1_xdata_to_plot,
																	plot1_ydata_to_plot,
																	Sub_df1,
																	color_to_plot	)

		# Use the pre-defined range_slider function with these new inputs to
		# update the range sliders (this will make sure that the range sliders
		# start/end etc. match up with what's being plotted, as well as
		# displaying/hiding the RangeSlider/DateRangeSlider as needed
		range_slider(plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1)

		# Update the ColumnDataSources using the newly created dataframes. The
		# plots look to these as the source so this changes what is being
		# plotted.
		src1.data = Sub_df1.to_dict(orient='list')
		src1_tol_TB.data = Sub_df1_tol_TB.to_dict(orient='list')
		src1_tol_Classic.data = Sub_df1_tol_Classic.to_dict(orient='list')

		return

	# Use the on_change function to call the now defined callback function
	# whenever the user changes the value in the widget.
	# NB: Other functions such as on_click are availible for other widgets.
	# Syntax:
	# 	First argument is passed to the callback as attr (see callback section
	# 	above)
	# 	Second argument is the name of the callback function to be called.
	select_xaxis.on_change('value', callback)
	select_yaxis.on_change('value', callback)
	select_legend.on_change('value', callback)
	checkbox_color.on_change('active', callback)
	checkbox_marker.on_change('active', callback)


	######## 2)
	# This callback is designed to take inputs from the range sliders to change
	# visible range
	def callback_range(attr, old, new):

		# Check what is currently being plotted. Need this to know whether to
		# look for the values from the DateRangeSlider or the RangeSlider
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value

		# Start with the x-axis
		if plot1_xdata_to_plot == 'adate':
			# If it's 'adate' then need to look at the DateRangeSlider and
			# update the start and end values of the range using the values from
			# the slider.
			# NB: range_slider.value = left_value, right_value
			p1.x_range.start, p1.x_range.end = range_slider_xdate.value
		else:
			# If it's not 'adate' then need to look at the normal RangeSlider
			p1.x_range.start, p1.x_range.end = range_slider_x.value

		# Do the same for the y-axis
		if plot1_ydata_to_plot == 'adate':
			p1.y_range.start, p1.y_range.end = range_slider_ydate.value
		else:
			p1.y_range.start, p1.y_range.end = range_slider_y.value

		return

	# Use the on_change function to call the now defined callback function
	# whenever the user changes the value in the widget.
	range_slider_x.on_change('value', callback_range)
	range_slider_y.on_change('value', callback_range)
	range_slider_xdate.on_change('value', callback_range)
	range_slider_ydate.on_change('value', callback_range)

	############################################################################
	############################################################################





 	############################################################################
 	####################### RETURN TO THE MAIN SCRIPT ##########################

	# Now that the script is finished and the plot created we can return to the
	# main script.
	#
	# To pass back the data for the tab we need to return a Panel with:
	# 	child = layout (the one that we made earlier with the widget and plot)
	# 	title = 'Something that makes sense as a tab label for the user'

	return Panel(child = tab_layout, title = 'Electron Energy')

	############################################################################
	############################################################################

################################################################################
################################################################################















#
