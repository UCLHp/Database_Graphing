################################################################################
############################## IMPORT LIBRARIES ################################

# Might want this for line profiles?
from scipy.ndimage import map_coordinates
import math
import random

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# datetime for setting up DateRangeSlider with generic values
from datetime import date

# functions from bokeh
from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, BoxZoomTool,
	PanTool, WheelZoomTool, ResetTool, ColumnDataSource, Panel, CrosshairTool,
	FuncTickFormatter, SingleIntervalTicker, LinearAxis, CustomJS,
	DatetimeTickFormatter, BasicTickFormatter, NumeralTickFormatter, Arrow,
	NormalHead, OpenHead, VeeHead, Label, PointDrawTool, Range1d)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider,
	Tabs, CheckboxButtonGroup, Dropdown, TableColumn, DataTable, Select,
	DateRangeSlider)
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import Category20_16, turbo, Colorblind, Spectral11
import bokeh.colors
from bokeh.io import output_file, show
from bokeh.transform import factor_cmap, factor_mark
from bokeh.events import Pan, PlotEvent, MouseWheel

# PIL for importing TIF file
from PIL import Image

# https://discourse.bokeh.org/t/updating-image-or-figure-with-new-x-y-dw-dh/1971/4

################################################################################
################################################################################

# Define the expected position of the spots

class SpotParameters:
	def __init__(self, x_pos_exp, y_pos_exp, range, x_pos_meas, y_pos_meas):
		self.x_pos_exp = x_pos_exp
		self.y_pos_exp = y_pos_exp
		self.x_range_start = x_pos_exp - range
		self.x_range_end = x_pos_exp + range
		self.y_range_start = y_pos_exp - range
		self.y_range_end = y_pos_exp + range
		self.x_pos_meas = x_pos_meas
		self.y_pos_meas = y_pos_meas

def ColorMapper(conn):

	# Quick plot of charmander image to check file orientations are done
	# correctly. Also later for fun.
	file_charmander = 'O:\\protons\\Work in Progress\\Christian\\Python\\Graphing Code\\CB Version\\New Ideas\\Charmander.png'
	arr_charmander=np.array(Image.open(file_charmander))
	arr_charmander=np.flipud(arr_charmander)
	p_charmander = figure()
	p_charmander.plot_height = 300
	p_charmander.plot_width = 300
	p_charmander.image_rgba(image=[arr_charmander], x=[0], y=[0], dw=[1], dh=[1])



	############################################################################
	############################ READ IN THE IMAGE #############################

	# File address for where bmp image is
	file1 = 'O:\\protons\\Dosimetry_and_QA\\TestData\\LOGOS Example Data\\Bmp Images\\00000001.bmp'
	# Read in image and turn into an array
	arr1=np.array(Image.open(file1))
	# Flip the array because Bokeh reads the array in from the bottom left corner
	# but the image
	arr1=np.flipud(arr1)
	# Get the width and height of the array. Annoyingly pixels are accessed by
	# (y,x) coordinates.
	(dh1, dw1) = arr1.shape

	############################################################################
	############################################################################





	############################################################################
	######################## SET SOME STARTING VALUES ##########################

	# Define the data for each spot. In this case the expected coordinates, then
	# the viewing range for the windows, and then finally the measured positions
	# At the moment these measured positions are just generated randomly but
	# will eventually be inputs from CG's code.
	viewing_range = 40
	spot_tl = SpotParameters(600, 800, viewing_range, random.gauss(600, 5), random.gauss(800, 5))
	spot_tc = SpotParameters(800, 800, viewing_range, random.gauss(800, 5), random.gauss(800, 5))
	spot_tr = SpotParameters(1000, 800, viewing_range, random.gauss(1000, 5), random.gauss(800, 5))
	spot_ml = SpotParameters(600, 600, viewing_range, random.gauss(600, 5), random.gauss(600, 5))
	spot_mc = SpotParameters(800, 600, viewing_range, random.gauss(800, 5), random.gauss(600, 5))
	spot_mr = SpotParameters(1000, 600, viewing_range, random.gauss(1000, 5), random.gauss(600, 5))
	spot_bl = SpotParameters(600, 400, viewing_range, random.gauss(600, 5), random.gauss(400, 5))
	spot_bc = SpotParameters(800, 400, viewing_range, random.gauss(800, 5), random.gauss(400, 5))
	spot_br = SpotParameters(1000, 400, viewing_range, random.gauss(1000, 5), random.gauss(400, 5))

	# Set some values for the start and end x and y for the line profile we'll
 	# make later. (For simplicity we're going to plot a +ve diagonal over the
	# topleft (tl) spot)
	x_prof_start = 570
	x_prof_end = 630
	y_prof_start = 770
	y_prof_end = 830

	############################################################################
	############################################################################





	############################################################################
	######################### WORK OUT A LINE PROFILE ##########################

	# This should work out the pixel values along an arbitary line profile.
	# NB: It does some sort of interpolation between pixels that should probably
	# be looked at in some more detail.

	# Calculate how long the line is (hypotenuse eqn.). This will give the
	# length in pixels.
	prof_length = math.sqrt((x_prof_start-x_prof_end)**2
		+ (y_prof_start-y_prof_end)**2)
	# Going to sample every 0.1 pixels which should be plenty. (Turn it into an
	# integer to make sure its a whole number)
	prof_sample = int(prof_length/0.1)
	# Create a list of the x and y coordinates by making an evenly spaced list
	# according to the decided number of points.
	x_prof_sample = np.linspace(x_prof_start, x_prof_end, prof_sample)
	y_prof_sample = np.linspace(y_prof_start, y_prof_end, prof_sample)
	# Create a list of pixel values at these coordinates (interpolating where
	# needed). map_coordinates an interpolation thing. Come back to this later?
	z_prof_sample = map_coordinates(arr1, np.vstack((y_prof_sample, x_prof_sample)))
	# Normalise to the max value in the profile (Easier to visualise things like
	# FWHM etc.)
	z_prof_sample = z_prof_sample*(100/(max(z_prof_sample)))
	# Make it into a dictionary where 'x' is the 'length' dimension and 'y' is
	# the pixel value. Currently this is not meaningful so need to fill a pixel
	# size in later?
	dict_prof = {	'x': list(range(0, len(z_prof_sample))),
					'y': z_prof_sample}
	# Turn it into a dataframe
	df_prof = pd.DataFrame(dict_prof)
	# Turn it into a column data source
	src_prof = ColumnDataSource(df_prof.to_dict(orient='list'))
	# Create the profile plot
	p_prof = figure()
	p_prof.line(source=src_prof, x='x', y='y')
	hover = HoverTool(	tooltips = [('X-Axis', '@x'),
									('Y-Axis', '@y')],
						mode = 'hline',
						line_policy = 'nearest')
	cross = CrosshairTool()
	p_prof.add_tools(hover, cross)
	p_prof.plot_height = 300
	p_prof.plot_width = 600
	# While here create a column data source (via dictionary and dataframe) that
	# is the two points that define the line profile. Will use this later to
	# display the line profile over the images.
	dict_prof_points = {'x': [x_prof_start, x_prof_end],
						'y': [y_prof_start, y_prof_end]}
	df_prof_points = pd.DataFrame(dict_prof_points)
	src_prof_points = ColumnDataSource(df_prof_points.to_dict(orient='list'))
	# Going to add a datatable to display the position of these two points as
	# well. (Apparently this is done by make a datatable widget?)
	columns_prof_points = [TableColumn(field="x", title="x-position", width = 100),
           TableColumn(field='y', title='y-position', width = 100)]
	datatable_prof_points = DataTable(source=src_prof_points,
		columns=columns_prof_points, width=600, height=100, editable=True,
		selectable='checkbox')



	############################################################################
	############################################################################





	############################################################################
	########################### CREATE THE MAIN PLOT ###########################

	# The main plot is the one that's going to display the whole image.

	# Create the main image with some basic tools
	p_main = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()],
		tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")],)
	p_main.plot_height = round(dh1/2)
	p_main.plot_width = round(dw1/2)
	# NB: This needs rewriting to the form of a column data source.
	p_main.image(image=[arr1], x=0, y=0, dw=dw1, dh=dh1, palette="Spectral11", level="image")
	# Add the line profile to the main image.
	p_main.line(source=src_prof_points, x='x', y='y', line_width=2,
		color='black')
	# Add circle glyphs at either end of the line. Do it in this way so that
	# they can be added
	c1 = p_main.circle(source=src_prof_points, x='x', y='y', color='black',
		fill_alpha=0.5, size=12)
	p_main.add_tools(PointDrawTool(renderers=[c1], num_objects=2))



	spot_parameters = [spot_tl, spot_tc, spot_tr, spot_ml, spot_mc, spot_mr,
		spot_bl, spot_bc, spot_br]
	spot_positions = ['tl', 'tc', 'tr', 'ml', 'mc', 'mr', 'bl', 'bc', 'br']
	index = list(range(0, len(spot_positions)))
	spot_dict = {}
	for i in index:
		spot_dict['x_'+spot_positions[i]] = [spot_parameters[i].x_range_start, spot_parameters[i].x_range_end,
			spot_parameters[i].x_range_end, spot_parameters[i].x_range_start, spot_parameters[i].x_range_start]
		spot_dict['y_'+spot_positions[i]] = [spot_parameters[i].y_range_start, spot_parameters[i].y_range_start,
			spot_parameters[i].y_range_end, spot_parameters[i].y_range_end, spot_parameters[i].y_range_start]

	df_spot = pd.DataFrame(spot_dict)
	src_spot = ColumnDataSource(df_spot.to_dict(orient='list'))

	for i in index:
		p_main.line(source=src_spot, x='x_'+spot_positions[i],
			y='y_'+spot_positions[i], line_width=2, color='firebrick')


	# Initialise all the figures and put in a list to iterate over. Lock the
	# aspect ratio of the box tool so it doesn't end up stretching the images.
	p_tl = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_tc = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_tr = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_ml = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_mc = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_mr = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_bl = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_bc = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	p_br = figure(tools=[PanTool(), WheelZoomTool(),
		BoxZoomTool(match_aspect=True), ResetTool()])
	plots = [p_tl, p_tc, p_tr, p_ml, p_mc, p_mr, p_bl, p_bc, p_br]

	for i in index:
		plots[i].plot_height = round(300)
		plots[i].plot_width = round(300)
		plots[i].x_range.start = spot_parameters[i].x_range_start
		plots[i].x_range.end = spot_parameters[i].x_range_end
		plots[i].y_range.start = spot_parameters[i].y_range_start
		plots[i].y_range.end = spot_parameters[i].y_range_end
		plots[i].image(image=[arr1], x=0, y=0, dw=dw1, dh=dh1, palette="Spectral11", level="image")
		# Add an 'expected position'
		plots[i].circle_x([spot_parameters[i].x_pos_exp], [spot_parameters[i].y_pos_exp], size=10,
			color='blue', alpha=0.5)
		plots[i].circle_x([spot_parameters[i].x_pos_meas], [spot_parameters[i].y_pos_meas], size=10,
			color='white', alpha=0.5)
		plots[i].add_layout(Arrow(end=OpenHead(size=10, line_color="blue",
			line_width=1.5), x_start=spot_parameters[i].x_pos_exp, y_start=spot_parameters[i].y_pos_exp,
			x_end=spot_parameters[i].x_pos_meas, y_end=spot_parameters[i].y_pos_meas))
		plots[i].add_layout(Label(x=565, y=762.5, text_color = 'white',
			text = 'x=' + str(spot_parameters[i].x_pos_meas-spot_parameters[i].x_pos_exp) +
			' y=' + str(spot_parameters[i].y_pos_meas-spot_parameters[i].y_pos_exp)))

		plots[i].line(source=src_prof_points, x='x', y='y', line_width=2,
			color='black')
		c1 = plots[i].circle(source=src_prof_points, x='x', y='y', color='black',
			fill_alpha=0.5, size=12)
		plots[i].add_tools(PointDrawTool(renderers=[c1], num_objects=2))



	#
	# p_tl.plot_height = round(300)
	# p_tl.plot_width = round(300)
	# p_tl.x_range.start = spot_tl.x_range_start
	# p_tl.x_range.end = spot_tl.x_range_end
	# p_tl.y_range.start = spot_tl.y_range_start
	# p_tl.y_range.end = spot_tl.y_range_end
	# p_tl.image(image=[arr1], x=0, y=0, dw=dw1, dh=dh1, palette="Spectral11", level="image")
	# # Add an 'expected position'
	# p_tl.circle_x([spot_tl.x_pos_exp], [spot_tl.y_pos_exp], size=10,
	# 	color='blue', alpha=0.5)
	# p_tl.circle_x([spot_tl.x_pos_meas], [spot_tl.y_pos_meas], size=10,
	# 	color='white', alpha=0.5)
	# p_tl.add_layout(Arrow(end=OpenHead(size=10, line_color="blue",
	# 	line_width=1.5), x_start=spot_tl.x_pos_exp, y_start=spot_tl.y_pos_exp,
	# 	x_end=spot_tl.x_pos_meas, y_end=spot_tl.y_pos_meas))
	# p_tl.add_layout(Label(x=565, y=762.5, text_color = 'white',
	# 	text = 'x=' + str(spot_tl.x_pos_meas-spot_tl.x_pos_exp) +
	# 	' y=' + str(spot_tl.y_pos_meas-spot_tl.y_pos_exp)))



	# # Thisis still a basic one
	# p3 = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
	# p3.plot_height = round(300)
	# p3.plot_width = round(300)
	# p3.x_range.start, p3.x_range.end = 700, 900
	# p3.y_range.start, p3.y_range.end = 500, 700
	# # p1.xaxis.axis_label = list[3]
	# # p1.yaxis.axis_label = list[4]
	# p3.image(image=[arr1], x=0, y=0, dw=dw1, dh=dh1, palette="Spectral11", level="image")


	row1 = row(p_tl, p_tc, p_tr)
	row2 = row(p_ml, p_mc, p_mr)
	row3 = row(p_bl, p_bc, p_br)
	column1 = column(row1, row2, row3)
	column2 = column(row(p_prof, p_charmander), datatable_prof_points, p_main)
	layout = row(column1, column2)



	# Can probably make this much quicker by making seperate callbacks for each
	# individual image. It will be a lot of code but that way it doesn't have to
	# do a full loop to check if any others have changed.
	#
	# Might be that actually it's the rewritting of the display which is the
	# rate determining step. So by keeping the loop to just rewriting the
	# dictionary this might keep it quick enough?
	def callback_range(attr, old, new):

		for i in index:
			spot_dict['x_'+spot_positions[i]] = [plots[i].x_range.start,
				plots[i].x_range.end, plots[i].x_range.end,
				plots[i].x_range.start, plots[i].x_range.start]
			spot_dict['y_'+spot_positions[i]] = [plots[i].y_range.start,
				plots[i].y_range.start, plots[i].y_range.end,
				plots[i].y_range.end, plots[i].y_range.start]

		df_spot = pd.DataFrame(spot_dict)
		src_spot.data = df_spot.to_dict(orient='list')

		return

	for i in index:
		plots[i].x_range.on_change('start', callback_range)
		plots[i].x_range.on_change('end', callback_range)
		plots[i].y_range.on_change('start', callback_range)
		plots[i].y_range.on_change('end', callback_range)


	def callback_prof (attr, old, new):

		# I think src_prof.data already is a dictionary but just to make sure
		dict_prof_points = src_prof_points.data
		print(dict_prof_points)

		x_prof_start, x_prof_end = dict_prof_points['x']
		y_prof_start, y_prof_end = dict_prof_points['y']
		x_prof_start = float(x_prof_start)
		x_prof_end = float(x_prof_end)
		y_prof_start = float(y_prof_start)
		y_prof_end = float(y_prof_end)

		# Calculate how long the line is
		prof_length = math.sqrt((x_prof_start-x_prof_end)**2
			+ (y_prof_start-y_prof_end)**2)
		# Going to sample every 0.1 pixels which should be plenty
		prof_sample = int(prof_length/0.1)
		# Create a list of the x and y coordinates
		x_prof_sample = np.linspace(x_prof_start, x_prof_end, prof_sample)
		y_prof_sample = np.linspace(y_prof_start, y_prof_end, prof_sample)
		# Map coordinates is like an interpolation thing. Come back to this later?
		z_prof_sample = map_coordinates(arr1, np.vstack((y_prof_sample, x_prof_sample)))
		# Normalise to the max value in the profile
		z_prof_sample = z_prof_sample*(100/(max(z_prof_sample)))
		# Make it into a dictionary
		dict_prof = {'x': list(range(0, len(z_prof_sample))),
						'y': z_prof_sample}
		df_prof = pd.DataFrame(dict_prof)

		src_prof.data = df_prof.to_dict(orient='list')

		return

	src_prof_points.on_change('data', callback_prof)
	datatable_prof_points.on_change('source', callback_prof)



	# Return the panel

	return Panel(child = layout, title = 'ColorMapper')















#
