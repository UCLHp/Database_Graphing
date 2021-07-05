import easygui as eg
import datetime
import tkinter as tk
import pandas as pd

def callback_export():

	x_data1 = select_xaxis.value
	y_data1 = select_yaxis.value

	Sub_df2 = Sub_df1.copy()
	Sub_df2[x_data1] = Sub_df2['x']
	Sub_df2[y_data1] = Sub_df2['y']
	# Find a file name and location to save the export

	if eg.ynbox(msg = 'Do you want to export the visible range or all data?', choices=('Visible Range', 'All Data')):
		if x_data1 == 'adate':
			x_range_start = datetime.datetime.fromtimestamp(p1.x_range.start/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
			x_range_end = datetime.datetime.fromtimestamp(p1.x_range.end/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
			Sub_df2.drop(Sub_df2[Sub_df2['x'] < x_range_start].index, inplace=True)
			Sub_df2.drop(Sub_df2[Sub_df2['x'] > x_range_end].index, inplace=True)
		else:
			Sub_df2.drop(Sub_df2[Sub_df2['x'] < p1.x_range.start].index, inplace=True)
			Sub_df2.drop(Sub_df2[Sub_df2['x'] > p1.x_range.end].index, inplace=True)
		if y_data1 == 'adate':
			y_range_start = datetime.datetime.fromtimestamp(p1.y_range.start/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
			y_range_end = datetime.datetime.fromtimestamp(p1.y_range.end/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
			Sub_df2.drop(Sub_df2[Sub_df2['y'] < y_range_start].index, inplace=True)
			Sub_df2.drop(Sub_df2[Sub_df2['y'] > y_range_start].index, inplace=True)
		else:
			Sub_df2.drop(Sub_df2[Sub_df2['y'] < p1.y_range.start].index, inplace=True)
			Sub_df2.drop(Sub_df2[Sub_df2['y'] > p1.y_range.end].index, inplace=True)

	root = tk.Tk()
	root.withdraw()
	filepath = tk.filedialog.asksaveasfilename(filetypes=[("csv files", '*.csv')],
	    initialfile='graphing_export.csv', defaultextension = '.csv', initialdir = 'O:\\')
	if filepath:
		# If the filepath has been selected
		Sub_df2.to_csv(filepath, index=False)
		eg.msgbox('Data saved to: ' + filepath)
