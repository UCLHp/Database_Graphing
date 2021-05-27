

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

################################################################################
################################################################################


################################################################################
################################ START OF CODE #################################

# Create the function that will plot the data from this table/graph.
def Sym_Graph(conn):

	output_file("Sym_Graph.html") #????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????


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
	y_data1 = 'crossline_17'
	# Decide what the plot formatting will be, inluding the plot title, axis
	# titles and the size of the plot. A good generic start point is to use the
	# field names as the axis titles but future plots could potentially use a
	# look up table to give more user friendly titles.
	plot_title1 = 'Symmetry'
	x_axis_title1 = x_data1
	y_axis_title1 = y_data1
	plot_size_height1 = 450
	plot_size_width1 = 800
	legend_location = 'bottom_left'
	# Set the fields that will display in the hovertool in addition to the x and
	# y fields (NB: Can have a maximum of 10 options here). (Useful example
	# defaults would be the comments field or maybe chamber/electrometer?)
	hover_tool_fields = ['adate', 'gantry angle']
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
	color_column = 'gantry angle'
	custom_color_boolean = False
	custom_color_palette = []
	marker_column = 'machinename'
	custom_marker_boolean = False
	custom_marker_palette = []
	# fill_alpha_column = 'energy'

	# From the legend defined above give the values that will be pre-ticked when
	# the plot is opened. NB: Bokeh will throw an error if one of these lists is
	# empty (i.e. =[]) If only using color or marker then set the color_to plot
	# and then enter the command:  marker_to_plot = color_to_plot.
	energy_selection = '6MV'
	color_to_plot = ['0.0']
	marker_to_plot = ['TrueBeam B']
	# fill_alpha_to_plot = ['0.0']
	# marker_to_plot = color_to_plot

	# Decide what the default viewing option is going to be. (i.e. the fields to
	# be plotted on the x and y axis when the graph is opened).
	# NB: Have it set that if axis is 'adate' then will automatically update
	# to plot datetime.

	############################################################################
	#################### CREATE THE DATA FOR THE GRAPH #########################

	# Do this in a function so it can be used in an update callback later

	def Create_df(energy_selection):

		#if statement to decide energy chosen by user to define appropriate dataframe
		# if checkbox.active =="6MV"
		if energy_selection == '6MV':
			df = pd.read_sql('select [protocol id], [gantry angle], '\
							'[g17 6mv], [g9 6mv], [t9 6mv],[t17 6mv],'\
							'[a17 6mv], [a9 6mv], [b9 6mv],[b17 6mv], ' \
							'[flatness 6mv gt], [flatness 6mv ab] ' \
							'from [flat sym]', conn)

			#filter old machine data that is not Truebeams
			df=df[df['protocol id'].str.contains("Truebeam B|TrueBeam C|TrueBeam D|TrueBeam F",case=False, na=False)]
			#changing the gantry angle from float to string to be able to put it in a check list
			df.astype({'gantry angle': 'str'}).dtypes
			#filter row with data = 0
			df = df[df['g17 6mv'] !=0]
			#add difference in symmetry values to y-axis
			df['inline_17'] = df['g17 6mv'] - df['t17 6mv']
			df['crossline_17'] = df['a17 6mv'] - df['b17 6mv']
			df['inline_9'] = df['g9 6mv'] - df['t9 6mv']
			df['crossline_9'] = df['a9 6mv'] - df['b9 6mv']
			df['flatness_gt'] = df['flatness 6mv gt']
			df['flatness_ab'] = df['flatness 6mv ab']
			df['inline_7'] = np.nan
			df['crossline_7'] = np.nan
			#

		if energy_selection == '10MV':
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

		if energy_selection == '6FFF':
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

		if energy_selection == '10FFF':
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

		if energy_selection == '6MeV':
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

		if energy_selection == '9MeV':
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

		if energy_selection == '12MeV':
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

		if energy_selection == '15MeV':
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

		print(df)
		# Also print the data type of the dataframe columns.
		print(df.dtypes)

		df = df.dropna(subset=['protocol id'])
		#df = df.dropna(subset=['energy'])

		df_left = df['protocol id'].str.partition(sep = '_')
		df_right = df['protocol id'].str.rpartition(sep = '_')

		df.loc[:,'adate'] = df_left[0]
		df.loc[:,'machinename'] = df_right[2]
		df.loc[:,'adate'] = pd.to_datetime(df.loc[:,'adate'])

		#filter any columns where there is no data
		#such as obselete data no longer collected for Truebeams
		df = df.dropna(axis='columns', how='all')

		return df

	df = Create_df(energy_selection)
	print(df)
	# Create a list of the fields using the dataframe. By doing it now before
	# the extra legend fields are added it's easy to limit what is displayed in
	# the select widgets.
	TableFields = (list(df.columns))
	bad_list = ['g17 6mv', 'g9 6mv', 't9 6mv','t17 6mv', 'a17 6mv', 'a9 6mv',
		'b9 6mv','b17 6mv','flatness 6mv gt', 'flatness 6mv ab' ]
	TableFields = [x for x in TableFields if x not in bad_list]



 	############################################################################
 	################ CREATE THE DATAFRAME FOR THE TOLERANCES ###################

	# The purpose of this plot is generally to be as general as possible but
	# there are only a few parameters that will have defined tolerances.
	# Therefore the tolerance section can be a bit more specific and a dataframe
	# containing tolereances can be manually created for many cases and
	# extracted from the database in others (in a manner similar to above but
	# calling from a different table/query with the SQL statement)
	#
	# If you want to add tolerances change the boolean to True and construct the
	# dataframe in the correct format.
	tolerance_boolean = False
	# The format of the dataframe should be the first line being the x_axis
	# (with some values taken from the main dataframe to get the right
	# formatting). The subsequent columns are the tolerances [low, high].
	# NB: column names should match those from the main dataframe.
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

	########################################################s####################
	##########################################################]##################

	############################################################################
	############################################################################

	'''

	This is the end of the user input section. If you don't need to make any
	other changes you can end here.

	'''



	##########################################################################
	################### CREATE THE COLUMNS FOR THE LEGEND ######################

	# In Universal.py a function has been created to add the legend.
	#
	# This function takes as inputs the main dataframe and the field names that
	# the markes and colors for the legend will be based on. If there is only
	# one field then put it in both columns (the function will deal with this).
	#
	# If the default options in the function are not acceptable then change the
	# boolean to True and then set the palette to the color and marker palettes
	# that you want (they will be mapped against a 'sorted' list of the unique
	# values from the fields).
	#
	# This function will output lists of the unique values from these 2 fields
	# (color_list and marker_list), the palettes (as a list), the dataframe with
	# added fields for the legend and an add_legend_to_df function that we can
	# use later.


	(color_list, color_palette, marker_list, marker_palette,
	 	df, add_legend_to_df) = Create_Legend(df, color_column,
		custom_color_boolean, custom_color_palette, marker_column,
		custom_marker_boolean, custom_marker_palette,
		)

	print(marker_palette)
	print(color_list)
	print(type(color_list[0]))

	#print(fill_alpha_palette)



 	############################################################################
 	################## FORMATTING AND CREATING A BASIC PLOT ####################

	# Create the actual plot. Generally it's a good idea to do this by defining
	# functions as they can then be used in the callbacks later without having
	# a lot of redundant very similar code. Many of these functions are generic
	# to most plots and so are defined in the Universal.py file.


	######### Make Dataset:
	# Run the Make_Dataset function to create a sub dataframe that the plot will
	# be made from.
	#
	# This function used the main dataframe as an input along with the pre-
	# defined default x-axis, y-axis and legend options to construct a sub-
	# dataframe. This sub-dataframe has the x and y axis columns renamed 'x' and
	# 'y' and has any rows that aren't 'ticked' in the legened removed.
	Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
		marker_to_plot, x_data1, y_data1	)
	print(Sub_df1)
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
				marker = factor_mark('marker1', marker_palette, marker_list),
				color = factor_cmap('color1', color_palette, color_list)
				)


	######### Add plot parameters:
	# Run the Define_Plot_Parameters function to format the plot. Takes the plot
	# and the pre-defined list of default plot parameters as inputs.
	Define_Plot_Parameters(p1, list_plot_parameters)

	############################################################################
	############################################################################






	############################################################################
 	############################ ADD TOLERANCES ################################

	# We defined the tolerances further up and now want to add the correct ones
	# to the plot. Only do this through if the boolean is set to True as
	# otherwise the user doesn't want tolerances.

	if tolerance_boolean == True:
		# Run the Make_Dataset_Tolerance function from Univeral.py to output the
		# new sub dataframe for the tolerances. This takes as an input the field
		# names of what are going to be plotted, the sub-dataframe from above
		# and the pre-defined tolerance table.
		Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1,
			df_tol1)

		# Turn the dataframe into a new ColumnDataSource (again turning it into
		# a dictionary)
		src1_tol = ColumnDataSource(Sub_df1_tol1.to_dict(orient='list'))

		# Add two lines to the plot using the new ColumnDataSource as the
		# source, one line for low tolerance and one line for high.
		p1.line(source = src1_tol, x = 'x', y = 'y_low', color = 'firebrick')
		p1.line(source = src1_tol, x = 'x', y = 'y_high', color = 'firebrick')

		Sub_df1_tol1_flat = special_tolerance(color_to_plot, x_data1, y_data1,
			Sub_df1, df_tol1_flat)

		src1_tol_flat= ColumnDataSource(Sub_df1_tol1_flat.to_dict(orient='list'))

		p1.line(source = src1_tol_flat, x = 'x_6MV', y = 'y_low_6MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6MV', y = 'y_high_6MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6XFFF', y = 'y_low_6XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_6XFFF', y = 'y_high_6XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10MV', y = 'y_low_10MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10MV', y = 'y_high_10MV', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10XFFF', y = 'y_low_10XFFF', color = 'firebrick')
		p1.line(source = src1_tol_flat, x = 'x_10XFFF', y = 'y_high_10XFFF', color = 'firebrick')
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


	######## 1)
	# Create a hover tool and add it to the plot
	#
	# Create an empty hovertool
	hover1 = HoverTool()
	# Create a dictionary from the list of fields to be displayed of the form:
	# 	{Field1: aaa, Field2: bbb, etc.}
	# NB: If more than 10 fields then provide an empty dictionary and an error
	# message as the Update_HoverTool function displays only up to 10 additional
	# fields.
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
	# This funtion from Universal.py will be used to update the Hovertool.
	#
	# As inputs it takes the empty hovertool that was just created, the pre-
	# defined fields to be plotted on the x and y axis (these will always
	# display on the hovertool) and any additional fields that will appear by
	# default (in the form of the kwargs dictionary). (For details on kwargs see
	# python doccumentation).
	Update_HoverTool(hover1, x_data1, y_data1, **kwargs)
	# Add the hovertool to the plot.
	p1.add_tools(hover1)


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
	# As an example some generic widgets will be added to the plot (primarily
	# using functions from Universal.py).
	#
	# Other useful widgets and details of the syntax can be found here:
	# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html


 	######## 1)
	# This funtion from Universal.py will be used to create dropdown lists to
	# change the data plotted on the x/y-axis.
	#
	# As an input it takes the TableFields list created earlier. This could be
	# altered to accept a more 'cut-down' list for ease of use. It also takes
	# the pre-defined x and y axis titles to display on opening the graph.
	select_xaxis, select_yaxis = Create_Select_Axis(TableFields, x_axis_title1,
		y_axis_title1)


 	######## 2)
	# This function from Universal.py will be used to create a dropdown list to
	# change the legend position.
	#
	# As an input it takes the pre-defined default lefend location.
	select_legend = Create_Select_Legend(legend_location)


	######## 3)
	# This funtion from Universal.py will be used to create checkbox widgets to
	# change the data being plotted from the fields that the legend is based on.
	#
	# NB: There is some built in Bokeh functionality for interavtive legends
	# that can fulfill some of the same goals where the number of options is
	# limited to something that can display on a reasonably sized legend. May
	# be a better and more robust solution where possible but this is more
	# flexible.
	#
	# As an input it takes the main dataframe and the pre-defined defaults for
	# the legend (the color and markers).
	checkbox_color, checkbox_marker = Create_Checkbox_Legend(df,
		color_column,color_to_plot, marker_column, marker_to_plot,
		)



	######## 4)
	# This funtion from Universal.py will be used to create a checkbox widget
	# to change the fields included in the hovertool.
	#
	# As an input it takes the list of availible fields and the pre-defined
	# default values which will be pre-ticked.
	checkbox_hovertool = Create_Checkbox_HoverTool(TableFields,
		hover_tool_fields)


	######## 6)
	# Make an 'Update Button' to requery the database and get up to date data.
	update_button = Button(label='Update with latest data', button_type='success')

	############################################################################
	############################################################################

	############################################################################
	########################### CREATE A LAYOUT ################################

	# Create a layout to add widgets and arrange the display. This simple layout
	# displays the select widgets above the plot with the checkboxes to the
	# right (one above the other). Also adds a check to display one or two legend
	# checkboxs as necessary.
	#
	# More details can be found at:
	# https://docs.bokeh.org/en/latest/docs/user_guide/layout.html
	#
	# NB: More work to do here to make plots responsive to browser window size
	# (e.g. using sizing_mode = scale_both) but need to invstigate with/without
	# remote desktops.

	# Make the checkbox columns
	#checkbox_group = CheckboxGroup(
	checkbox_energy = RadioGroup(
		labels=["6MV", "10MV", "6FFF", "10FFF", "6MeV", "9MeV", "12MeV", "15MeV"], active=0)

	if color_column == marker_column:
		layout_checkbox = column([checkbox_color, checkbox_hovertool])
	else:
		layout_checkbox = column([checkbox_color, checkbox_marker,
			checkbox_hovertool])
	# Make the select widget and plot column
	layout_plots = column([	update_button, checkbox_energy,
							select_xaxis, select_yaxis, select_legend, p1])
	# Add the two columns side-by-side.
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
		#
		# Acquire values from the color and marker checkboxes (copy the color
		# one if the legend is based off one field).
		print(checkbox_energy.labels)
		print(checkbox_energy.active)
		energy_selection = checkbox_energy.labels[checkbox_energy.active]
		print(energy_selection)

		color_to_plot = [checkbox_color.labels[i] for i in
			checkbox_color.active]
		if color_column != marker_column:
			marker_to_plot = [checkbox_marker.labels[i] for i in
				checkbox_marker.active]
		else:
			marker_to_plot = color_to_plot
		# Acquire values from the hovertool checkbox.
		hovertool_to_plot = [checkbox_hovertool.labels[i] for i in
			checkbox_hovertool.active]
		# Acquire values from the select x and y axis widgets.
		plot1_xdata_to_plot = select_xaxis.value
		plot1_ydata_to_plot = select_yaxis.value
		# Acquire the value from the select legend location widget.
		legend_location = select_legend.value

		# Set the new axis titles from the values just acquired.
		x_axis_title1 = plot1_xdata_to_plot
		y_axis_title1 = plot1_ydata_to_plot

		df = Create_df(energy_selection)
		df = add_legend_to_df(df)

		# Use the pre-defined Make_Dataset function with these new inputs to
		# create new versions of the sub dataframes.
		Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
			marker_to_plot, plot1_xdata_to_plot, plot1_ydata_to_plot)

		# Use the pre-defined Define_Plot_Parameters function with these new
		# inputs to update the plot parameters.
		Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
	 		plot_title1, x_axis_title1, y_axis_title1, plot_size_height1,
			plot_size_width1, legend_location])

		# Use the pre-defined hovertool function with these new inputs to
		# update the hovertool. Also run a check of the number of field to be
		# added to the hovertool (Max = 10).
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
			Sub_df1_tol1_flat = special_tolerance(color_to_plot,
				plot1_xdata_to_plot, plot1_ydata_to_plot, Sub_df1, df_tol1_flat)

		# Update the ColumnDataSources using the newly created dataframes. The
		# plots look to these as the source so this changes what is being
		# plotted.
		src1.data = Sub_df1.to_dict(orient='list')
		if tolerance_boolean == True:
			src1_tol.data = Sub_df1_tol1.to_dict(orient='list')
			src1_tol_flat.data = Sub_df1_tol1_flat.to_dict(orient='list')
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
	checkbox_hovertool.on_change('active', callback)
	checkbox_energy.on_change('active', callback)



	######## 3)
	# This callback is designed to update the plotted data with new values from
	# the database
	def callback_update():

		# Make a new version of the dataframe using the original Create_df
		# function that connects to the database.
		df = Create_df(energy_selection)
		df = add_legend_to_df(df)

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

	# Use the on_click function to call the now defined callback function
	# whenever the user clicks the update button.
	update_button.on_click(callback_update)





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

	return Panel(child = tab_layout, title = 'Symmetry Graph')

	############################################################################
	############################################################################

################################################################################
################################################################################















#
