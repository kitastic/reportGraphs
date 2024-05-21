"""
	This file contains most of the constant global variables that can be accessed
	with other programs.
"""
import datetime

import pandas as pd
import os
from math import nan
import shutil
import calendar


'''
    After importing and skewing unwanted data,
    rows are dailies
    columns are date, subtotal, ticket discount, and gift sale
'''

jsonDirectory = '..\\..\\payrollAutomation\\db'


def get_db_files():
    """
    finds all sales json in folder and saves them according to salon name
    Returns
    -------
    files : dataframe
        keys are salons and values are filepaths
    """
    files = {'upscale': [], 'nails': []}
    for filename in os.listdir(jsonDirectory):
        file = os.path.join(jsonDirectory, filename)
        if os.path.isfile(file):
            if 'nails' in filename:
                files['nails'].append(file)
            elif 'upscale' in filename:
                files['upscale'].append(file)
    return files


def is_leap(year):
    """Return True for leap years, False for non-leap years."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def normalizeData(notX, notY, year):
    """
    This function is supposed make all the x and y lists equal to ideal's list size
    Parameters. it will add days to notX and add 'nan' to notY if there are no sales for any day
    ----------
    notX    : [datetime] days of transactions. may be missing some months and days from ideal list
    notY    : [float] total daily sales list
    ideal   : [datetime] leap year days, size of 366 based on year 2000

    Returns
    -------
    list, list : two lists that are normalized that is the same size as ideal list
    """
    daily = pd.DataFrame({'date': pd.date_range(start=str(year)+'-01-01', end=str(year)+'-12-31', freq='D', )})
    ideal = []
    for key,value in daily.items():
        for item in value:
            ideal.append(item)
    # first create a solid template of days by so that data does not get out of order
    x = []
    y = []
    leapYear = is_leap(year)
    for day in ideal:
        idealDay = day.day
        idealMonth = day.month
        foundFlag = False
        index = 0
        for i, d in enumerate(notX):
            notXday = d.day
            notXMonth = d.month
            if notXMonth > idealMonth and notXday > idealDay:
                break
            if idealDay == notXday and idealMonth == notXMonth:
                foundFlag = True
                index = i
                break
            if not leapYear:
                if (notXday and idealMonth) == 28 and (notXMonth and idealDay) == 2:
                    x.append(nan)
                    y.append(float('nan'))
        if foundFlag:
            x.append(day)
            y.append(notY[index])
        else:
            try:
                x.append(day)
                y.append(float('nan'))
            except ValueError:
                continue
    if year == '2021':
        print()

    return x, y


# hardcoded file paths for each year summary
files = []
files.append("totalSalesSummary2020.xlsx")
files.append("totalSalesSummary2021.xlsx")
files.append("totalSalesSummary2022.xlsx")
files.append("2023totalSales031523.xlsx")


# table is an array of an arrray; 
# yearly array of dates ranging from 1/1/2020 - 1/1/2030
table = []

for i in range(2020,2031):
    start = "1/1/" + str(i)
    end = "12/31/" + str(i)
    t = pd.date_range(start=start, end=end)
    table.append(t)

# this table is used for sharing data from multiple years
# xtable is days of the leap year without actual year. 
# used during plotting to plot multiple years

def createDailyTable():
    xDailyTables = []
    
    oddMonths = ["January", "March", "May", "July", "August", "October", "December"]
    evenMonths = ["April", "June", "September", "November"]
    
    year = 2020
    dailies = []
    for i in range(len(files)):
        for month in calendar.month_name[1:]:
            if month in oddMonths:
                for days in range(1,32):
                   dailies.append(month + " " + str(days))
            elif month in evenMonths:
                for days in range(1,31):
                    dailies.append(month + " " + str(days))
            else:
                # if leap year feb will have 29
                if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:            
                    for days in range(1,30):
                        dailies.append(month + " " + str(days))
                else:
                    for days in range(1,29):
                        dailies.append(month + " " + str(days))
            
            if month == "December":
                year = year + 1
                xDailyTables.append(dailies.copy())
                dailies.clear()
            
    return xDailyTables
    
                  