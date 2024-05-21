"""
	This file contains most of the constant global variables that can be accessed
	with other programs.
"""

import pandas as pd

'''
    After importing and skewing unwanted data,
    rows are dailies
    columns are date, subtotal, ticket discount, and gift sale
'''

# hardcoded file paths for each year summary
files = []
files.append("../reports2020/totalSalesSummary2020.xlsx")
files.append("totalSalesSummary2021.xlsx")

# table is an array of an arrray; 
# yearly array of dates ranging from 1/1/2020 - 1/1/2030
table = []
for i in range(2020,2031):
    start = "1/1/" + str(i)
    end = "1/1/" + str(i + 1)
    t = pd.date_range(start=start, end=end)
    table.append(t)
