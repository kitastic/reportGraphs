# -*- coding: utf-8 -*-
#!/
"""
Created on Wed Oct 14 15:06:59 2020

@author: poh
"""
from reporting import *
import config
import pandas as pd
from openpyxl import load_workbook

dfIncome = config.dfIncome
table = config.table
df1099 = config.df1099

dfTemp = pd.DataFrame({"date":["01/22/21"],
                       "date2":["01/23/21"],
                       "name":["kelly"],
                       "actual":[234],
                       "paid":[235],
                       "check #":[1234]})

with pd.ExcelWriter(config.report1099, mode="a") as writer:
    dfTemp.to_excel(writer, sheet_name="all")





