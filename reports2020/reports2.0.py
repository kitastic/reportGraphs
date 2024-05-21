# -*- coding: utf-8 -*-
#!/
"""
Created on Wed Oct 14 15:06:59 2020

@author: poh
"""
from reporting import *
import config

'''#######################################################################
                    MAIN FUNCTION
#######################################################################'''

dfIncome = config.dfIncome
table = config.table
promptDate = config.promptDate
check50 = config.check50


# these two variables are specified dates of payroll calculation
startDate = "080921"
endDate = "081521"

startDate = datetime.datetime.strptime(startDate, "%m%d%y")
endDate = datetime.datetime.strptime(endDate, "%m%d%y")


if not promptDate:
    # get hardcoded dates from above
    dates = [startDate, endDate]
else:
    dates = getDates()

employees = []
income = identify(dfIncome, table, employees)
calculateSalary(income, table, employees, dates)

filename = graph(1, table, income, employees)
#sendFtp(filename)

