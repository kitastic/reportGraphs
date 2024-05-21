# -*- coding: utf-8 -*-
#!/
"""
Created on Wed Oct 14 15:06:59 2020

@author: poh
"""
from reporting import *
import config

'''#####################################################
                    MAIN FUNCTION
####################################################'''
# initialize global data from config
dfIncome = config.dfIncome
table = config.table

employees = []
income = identify(dfIncome, table, employees)

checksPaid = export1099(income, table, employees)
writeChecksReport(checksPaid, employees)




