import os
import shutil
import re
import datetime
import pandas as pd
import json
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource,CustomJS,Slider,FactorRange,HoverTool,Dropdown,LinearAxis,Range1d
from bokeh.plotting import figure, show
from bokeh.transform import factor_cmap

import config


directory = config.jsonDirectory
files = config.get_db_files()
salesDb = {}
salons = ['upscale', 'nails']

for salon, list in files.items():
    salesDb[salon] = {}
    for file in list:
        year = re.search('\d{4}', file).group(0)
        with open(file) as f:
            data = json.load(f)
            salesDb[salon][year] = data

daily = pd.DataFrame({'date': pd.date_range(start='2000-01-01', end='2000-12-31', freq='D', )})
monthDayLeap = []
dailyDatetime = []
# remove year, only keep month and day
for key, value in daily.items():
    for item in value:
        monthDayLeap.append(item.strftime('%m/%d'))
        dailyDatetime.append(item)

days = []
dayTotals = []
salonTotals = {}
yearsList = []
# adds daily and yearly totals
for salon, years in salesDb.items():
    salonTotals[salon] = {}
    for year, dates in years.items():
        yearly_total = 0
        yearsList.append(year)
        salonTotals[salon][int(year)] = [[], []]    # left list for day, right for total
        for day, employees in dates.items():
            dailytotal = 0
            for employee in employees.items():
                dailytotal += employee[1][0]
                yearly_total += employee[1][0]
            salesDb[salon][year][day]['total'] = dailytotal
            days.append(day)
            dayTotals.append(dailytotal)
            salonTotals[salon][int(year)][0].append(datetime.datetime.strptime(day, '%m/%d/%Y'))
            salonTotals[salon][int(year)][1].append(float(dailytotal))
        salesDb[salon][year]['total'] = yearly_total

hoverTool = HoverTool(
    tooltips=[
        ( 'date',   '@x{%F}'            ),
        ( 'total',  '$@{y}{%0.2f}' ), # use @{ } for field names with spaces
    ],

    formatters={
        '@x'        : 'datetime', # use 'datetime' formatter for '@date' field
        '@{y}' : 'printf',   # use 'printf' formatter for '@{adj close}' field
                                     # use default 'numeral' formatter for other fields
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
)

figsDaily = []
figsYearly = []
xMultiYear = {}
yMultiYear = {}
source = ColumnDataSource(data=dict(
    x = dailyDatetime
))
for salon, years in salonTotals.items():
    year = 0
    xMultiYear[salon] = []
    yMultiYear[salon] = []
    for year, values in years.items():
        notNormX = values[0]
        notNormY = values[1]
        x, y = config.normalizeData(notNormX, notNormY, year)
        xMultiYear[salon].append(x)
        yMultiYear[salon].append(y)
        source.data[str(year)] = y
        # construct a Figure obj and pass x-data wrapped in a factorrange obj
        p = figure(
            title=f'{salon} {year}',
            x_axis_label='day',
            y_axis_label='total',
            x_axis_type='datetime',
            width=800,
        )
        p.add_tools(hoverTool)
        p.line(x, y,line_width=2)
        figsDaily.append(p)

# p = figure(
#             title=f'{salon} years',
#             x_axis_type='datetime',
#             width=800,
#             x_range=(xMultiYear['upscale'][0][0], xMultiYear['upscale'][0][-1])
#         )
# p.add_tools(hoverTool)
# p.line(x, y,line_width=2)
# p.extra_x_ranges = {'2021': Range1d(start=xMultiYear['upscale'][1][0], end=xMultiYear['upscale'][1][-1])}
# p.line(xMultiYear['upscale'][1], yMultiYear['upscale'][1], x_range_name='2021')
# p.add_layout(LinearAxis(x_range_name='2021'))
# show(p)



menu = [('daily', 'daily'), ('weekly', 'weekly'), ('monthly', 'monthly'), ('yearly', 'yearly')]
# dropDown = Dropdown(label='Frequency', button_type='primary', menu=menu)
# dropDown.js_on_event('freq_change', CustomJS(code="console.log('dropDown: ' + this.item, this.toString())"))

dropdown = Dropdown(label="Frequency", button_type="primary", menu=menu)
dropdown.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown: ' + this.item, this.toString())"))

# show(row(p, column(dropdown)))
show(column([fig for fig in figsDaily]))





