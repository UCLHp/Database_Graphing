import tkinter as tk
from tkinter.filedialog import asksaveasfilename

root = tk.Tk()
root.withdraw()
filepath = tk.filedialog.asksaveasfilename(filetypes=[("csv files", '*.csv')],
    initialfile='graphing_export.csv', defaultextension = '.csv', initialdir = 'O:\\')
print(filepath)
if not filepath:  # asksaveasfile return `None` if dialog closed with "cancel".
    print('hi')
# defaultextension = '.csv'
