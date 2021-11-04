'''
Scripts for plotting from the PBT Isocentre Table

'''


# pandas and numpy for data manipulation
import sys
import pandas as pd
import numpy as np
from easygui import buttonbox, msgbox, ynbox
import tkinter as tk
import datetime
from datetime import date, timedelta
import keyboard


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
from bokeh.models.callbacks import CustomJS

from scripts.Universal import (	Create_Select_Axis, Create_Select_Legend,
                                Create_Range_Sliders, Update_Range_Sliders,
                                Update_Range_Sliders_2,
                                Create_Checkbox_Legend, Define_Plot_Parameters,
                                Update_HoverTool, Create_Legend, Make_Dataset,
                                Make_Dataset_Tolerance,
                                Create_Checkbox_HoverTool)


def create_df(sql, conn):
    '''
    Takes a connection to an MS Access database and pulls information from a
    table in that database into a dataframe using an SQL Query
    '''

    # Read from database into dataframe
    df = pd.read_sql(sql, conn)

    # Delete empty rows where the data is very important to have
    df = df.dropna(subset=['adate'], how='any')
    df = df.dropna(subset=['machinename'], how='any')

    # Set data types correctly
    df.loc[:, 'adate'] = pd.to_datetime(df.loc[:, 'adate'], dayfirst=True)
    df['energy'] = df['energy'].apply(str)

    # Drop any columns where there is no data
    df = df.dropna(axis='columns', how='all')

    # Add an offset column
    df['offset'] = np.sqrt(df['x-offset']**2 + df['y-offset']**2)
    print(df)

    return df


def PBT_Isocentre_Graph(conn, Config):
    '''
    Create a graph for the PBT Isocentre table from the Proton database
    '''

    # Decide what the default viewing option is going to be.
    x_data1 = 'adate'
    y_data1 = 'average_offset'
    plot_title1 = 'PBT Isocentre Results'
    x_axis_title1 = x_data1
    y_axis_title1 = y_data1
    plot_size_height1 = 500
    plot_size_width1 = 800
    legend_location = 'bottom_left'
    hover_tool_fields = ['ga', 'energy']
    # Create a list of the plot parameters
    list_plot_parameters = [x_data1, y_data1, plot_title1, x_axis_title1,
                            y_axis_title1, plot_size_height1, plot_size_width1,
                            legend_location]

    # Define the fields that the legend will be based off.
    color_column = 'energy'
    custom_color_boolean = False
    custom_color_palette = []
    marker_column = 'machinename'
    custom_marker_boolean = False
    custom_marker_palette = []

    # From the legend defined above give the values that will be pre-ticked
    # when the plot is opened.
    color_to_plot = ['245']
    marker_to_plot = ['Gantry 1', 'Gantry 2', 'Gantry 3', 'Gantry 4']

    # Create a dataframe containing the data from the table
    sql = 'SELECT [GA], [Energy], [x-offset], [y-offset], [Diameter], ' \
          '[MachineName], [ADate] FROM [xrv124results] '
    df = create_df(sql, conn)

    # Create a list of the fields using the dataframe.
    AxisFields = ['ga', 'energy', 'x-offset', 'y-offset', 'Diameter',
                  'MachineName']
    TableFields = (list(df.columns))

    # If you want to add/remove tolerances change the boolean to True/False
    tolerance_boolean = False
    # Create toleance dataframes.
    # NB: df_tol1 is of 'normal' format. df_tol1_qi is a special format that will
    # interact with a custom function made in this file.
    if tolerance_boolean is True:
        exit()
        # df_tol1 = pd.DataFrame({'adate': [df['adate'].max(), df['adate'].max()],
        #                 'output': [98, 102],
        #                 'graph % diff in output': [-2, 2]})
        #
        # df_tol1_qi = pd.DataFrame({	'adate': [df['adate'].max(), df['adate'].max()],
        #                     'qi_6MV': [0.64, 0.68],
        #                     'qi_6XFFF': [0.61, 0.65],
        #                     'qi_10MV': [0.71, 0.75],
        #                     'qi_10XFFF': [0.68, 0.72]})

    # Create columns for the legend
    (color_list, color_palette, marker_list, marker_palette, df, add_legend_to_df) = Create_Legend(df, color_column,
                                                                                                   custom_color_boolean, custom_color_palette, marker_column, custom_marker_boolean, custom_marker_palette)

    # Make a sub dataframe that will be plotted and convert to ColumnDataSource
    Sub_df1 = Make_Dataset(df, color_column, color_to_plot, marker_column,
                           marker_to_plot, x_data1, y_data1)
    src1 = ColumnDataSource(Sub_df1.to_dict(orient='list'))

    # Create a plot
    p1 = figure()
    p1.scatter(source=src1, x='x', y='y', fill_alpha=0.4, size=12,
               legend_field='legend',
               marker=factor_mark('marker1', marker_palette, marker_list),
               color=factor_cmap('color1', color_palette, color_list))

    # Set the plot parameters
    Define_Plot_Parameters(p1, list_plot_parameters)

    # Add tolerances if requested
    if tolerance_boolean is True:
        pass
        # # Normal tolerances for outputs
        # Sub_df1_tol1 = Make_Dataset_Tolerance(x_data1, y_data1, Sub_df1, df_tol1)
        # src1_tol = ColumnDataSource(Sub_df1_tol1.to_dict(orient='list'))
        # # Add to plot
        # p1.line(source=src1_tol, x='x', y='y_low', color='firebrick')
        # p1.line(source=src1_tol, x='x', y='y_high', color='firebrick')

    # Create a hovertool
    hover1 = HoverTool()
    # Check to make sure not too many fields are added to the field.
    if len(hover_tool_fields) < 11:
        kwargs = {}
        i = 0
        for x in hover_tool_fields:
            i = i+1
            kwargs['Field'+str(i)] = x
    else:
        kwargs = {}
        msgbox('Too many fields selected to display on HoverTool '
               '(Max = 10). Please reduce number of fields selected')

    # Set hovertool parameters and add to the plot
    Update_HoverTool(hover1, x_data1, y_data1, **kwargs)
    p1.add_tools(hover1)

    # ####### Add widgets
    # Dropdown lists to change the x/y-axis.
    select_xaxis, select_yaxis = Create_Select_Axis(
        AxisFields, x_axis_title1, y_axis_title1)

    # Dropdown list to change the legend position.
    select_legend = Create_Select_Legend(legend_location)
    # Checkbox widgets used to create a tool to select the 'color' and 'marker'
    # that are being plotted.
    checkbox_color, checkbox_marker = Create_Checkbox_Legend(
        df, color_column, color_to_plot, marker_column, marker_to_plot)

    # Checkbox widget used to select hovertool fields
    checkbox_hovertool = Create_Checkbox_HoverTool(
        TableFields, hover_tool_fields)
    # Button to requery the database and get up to date data.
    update_button = Button(
        label='Update', button_type='success', width=int(plot_size_width1/2))
    # Button to set to a pre defined range instead of all data
    range_button = Button(label='Range', button_type='primary',
                          width=int(plot_size_width1/2))
    # Button to quit
    quit_button = Button(label='Quit', button_type='danger',
                         width=int(plot_size_width1/2))
    # Button to export raw data
    export_button = Button(label='Export to CSV',
                           button_type='warning',
                           width=int(plot_size_width1/2))
    # Titles for the checkboxes
    color_title = Div(text='<b>Energy Choice</b>')
    marker_title = Div(text='<b>Machine Choice</b>')
    hover_title = Div(text='<b>Hovertool Fields</b>')

    # Create a layout
    if color_column == marker_column:
        layout_checkbox = column([color_title, checkbox_color])
    else:
        layout_checkbox = column([color_title, checkbox_color, marker_title,
                                  checkbox_marker])
    button_row1 = row([update_button, range_button])
    button_row2 = row([quit_button, export_button])
    layout_plots = column([button_row1, button_row2, select_xaxis,
                           select_yaxis, select_legend, p1])
    tab_layout = row([layout_plots, layout_checkbox])

    # ##################### CREATE CALLBACK FUNCTIONS #########################

    # Big callback that does most stuff
    def callback(attr, old, new):
        # Acquire the current values of all of the widgets
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

        # Create new version of the sub dataframe.
        Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
                                marker_to_plot, plot1_xdata_to_plot,
                                plot1_ydata_to_plot)

        # Update the plot.
        Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
                                    plot_title1, x_axis_title1, y_axis_title1,
                                    plot_size_height1, plot_size_width1,
                                    legend_location])

        # Update the hovertool
        if len(hovertool_to_plot) < 11:
            kwargs = {}
            i = 0
            for x in hovertool_to_plot:
                i = i+1
                kwargs['Field'+str(i)] = x
        else:
            kwargs = {}
            msgbox('Too many fields selected to display on HoverTool '
                   '(Max = 10). Please reduce number of fields selected')
        Update_HoverTool(hover1, plot1_xdata_to_plot, plot1_ydata_to_plot,
                         **kwargs)

        # Update the tolerances.
        if tolerance_boolean is True:
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
        # Make a new version of the dataframe going back to the database
        df = create_df(sql, conn)
        df = add_legend_to_df(df, color_column, marker_column)

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
                                marker_to_plot, plot1_xdata_to_plot,
                                plot1_ydata_to_plot)

        Define_Plot_Parameters(p1, [plot1_xdata_to_plot, plot1_ydata_to_plot,
                                    plot_title1, x_axis_title1, y_axis_title1,
                                    plot_size_height1, plot_size_width1,
                                    legend_location])

        if len(hovertool_to_plot) < 11:
            kwargs = {}
            i = 0
            for x in hovertool_to_plot:
                i = i+1
                kwargs['Field'+str(i)] = x
        else:
            kwargs = {}
            msgbox('Too many fields selected to display on HoverTool '
                   '(Max = 10). Please reduce number of fields selected')

        Update_HoverTool(hover1, plot1_xdata_to_plot, plot1_ydata_to_plot,
                         **kwargs)

        if tolerance_boolean is True:
            Sub_df1_tol1 = Make_Dataset_Tolerance(plot1_xdata_to_plot,
                                                  plot1_ydata_to_plot, Sub_df1,
                                                  df_tol1)

        src1.data = Sub_df1.to_dict(orient='list')
        if tolerance_boolean is True:
            src1_tol.data = Sub_df1_tol1.to_dict(orient='list')

        return

    update_button.on_click(callback_update)

    # Callback for the Range Button
    # Sets reasonable range if certain fields are selected
    def callback_range():

        color_to_plot = [checkbox_color.labels[i] for i in
                         checkbox_color.active]
        if color_column != marker_column:
            marker_to_plot = [checkbox_marker.labels[i] for i in
                              checkbox_marker.active]
        else:
            marker_to_plot = color_to_plot
        plot1_xdata_to_plot = select_xaxis.value
        plot1_ydata_to_plot = select_yaxis.value

        # Create new version of the sub-df
        Sub_df1 = Make_Dataset(	df, color_column, color_to_plot, marker_column,
                                marker_to_plot, plot1_xdata_to_plot,
                                plot1_ydata_to_plot)

        if (plot1_xdata_to_plot == 'adate') and ((plot1_ydata_to_plot == 'offset')
                                                 or (plot1_ydata_to_plot == 'x-offset')
                                                 or (plot1_ydata_to_plot == 'y-offset')
                                                 or (plot1_ydata_to_plot == 'diameter')):

            p1.x_range.start = Sub_df1['x'].max() - timedelta(weeks=53)
            p1.x_range.end = Sub_df1['x'].max() + timedelta(weeks=2)

            if plot1_ydata_to_plot == 'output':
                p1.y_range.start = 97
                p1.y_range.end = 103
            elif plot1_ydata_to_plot == 'graph % diff in output':
                p1.y_range.start = -3
                p1.y_range.end = 3
            elif plot1_ydata_to_plot == 'qi':
                p1.y_range.start = 0.55
                p1.y_range.end = 0.8

        return

    range_button.on_click(callback_range)

    def callback_quit():

        # Close the open browser tab and shut down the bokeh server
        keyboard.press_and_release('ctrl+w')
        sys.exit()

        return

    quit_button.on_click(callback_quit)

    def callback_export():

        x_data1 = select_xaxis.value
        y_data1 = select_yaxis.value

        Sub_df2 = Sub_df1.copy()
        Sub_df2[x_data1] = Sub_df2['x']
        Sub_df2[y_data1] = Sub_df2['y']
        # Find a file name and location to save the export

        if ynbox(msg='Do you want to export the visible range or all data?',
                 choices=('Visible Range', 'All Data')):

            if x_data1 == 'adate' and (isinstance(p1.x_range.start, float) or isinstance(p1.x_range.start, int)):
                x_range_start = datetime.datetime.fromtimestamp(
                    p1.x_range.start/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
                x_range_end = datetime.datetime.fromtimestamp(
                    p1.x_range.end/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
                Sub_df2.drop(
                    Sub_df2[Sub_df2['x'] < x_range_start].index, inplace=True)
                Sub_df2.drop(
                    Sub_df2[Sub_df2['x'] > x_range_end].index, inplace=True)
            else:
                Sub_df2.drop(
                    Sub_df2[Sub_df2['x'] < p1.x_range.start].index, inplace=True)
                Sub_df2.drop(
                    Sub_df2[Sub_df2['x'] > p1.x_range.end].index, inplace=True)

            if y_data1 == 'adate' and (isinstance(p1.y_range.start, float) or isinstance(p1.y_range.start, int)):
                y_range_start = datetime.datetime.fromtimestamp(
                    p1.y_range.start/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
                y_range_end = datetime.datetime.fromtimestamp(
                    p1.y_range.end/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
                Sub_df2.drop(
                    Sub_df2[Sub_df2['y'] < y_range_start].index, inplace=True)
                Sub_df2.drop(
                    Sub_df2[Sub_df2['y'] > y_range_end].index, inplace=True)
            else:
                Sub_df2.drop(
                    Sub_df2[Sub_df2['y'] < p1.y_range.start].index, inplace=True)
                Sub_df2.drop(
                    Sub_df2[Sub_df2['y'] > p1.y_range.end].index, inplace=True)

        root = tk.Tk()
        root.withdraw()
        filepath = tk.filedialog.asksaveasfilename(filetypes=[("csv files", '*.csv')],
                                                   initialfile='graphing_export.csv', defaultextension='.csv', initialdir='O:\\')
        if filepath:
            # If the filepath has been selected
            Sub_df2.to_csv(filepath, index=False)
            msgbox('Data saved to: ' + filepath)

        return

        export_button.on_click(callback_export)

    # Return the panel to the main script
    return Panel(child=tab_layout, title='Photon Output')


#