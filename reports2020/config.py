"""
	This file contains most of the constant global variables that can be accessed
	with other programs.
"""

import pandas as pd

# check pay 50/50
check50 = ["Vivian", "Van"]

# this variable signals for a date that requests input or hardcoded
# 0 = hardcoded, 1 = prompt
promptDate = False

# location of report file
pathIncome = "Report.xlsx"


# retrieves dataframe using pandas
dfIncome = pd.read_excel(pathIncome, sheet_name=0)

# table is an array of an arrray; 
# yearly array of dates ranging from 1/1/2020 - 1/1/2030
table = []
for i in range(2020,2031):
    start = "1/1/" + str(i)
    end = "1/1/" + str(i + 1)
    t = pd.date_range(start=start, end=end)
    table.append(t)