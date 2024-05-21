import pandas as pd
import datetime
import calendar
import math     # truncate decimals for checks reporting
import copy
#import PySimpleGUI as sg
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots

import config
check50 = config.check50


##############################################################################
# Hardcoded employee status update functions
##############################################################################

def definePayTier(employees):
    '''
    Hardcode each employees' paygrade by name. This function needs 
    to be updated each time there is a new employee.

    Args:
        employees (dict): list of employees

    Returns: 
        payGrade (dict): each employee is assigned a pay tier and rent amount
    '''
    payGrade = dict()
    # 850/wk
    tier1 = ["Vu", "Nick", "Cindy", "Tu", "Thi"]
    # 900/wk
    tier2 = ["Hong","Lyna", "Rose", "Bin","Tai"]
    # 1000/wk
    tier3 = ["De","Quang","Van","Vivian","Kelly","Anna","Andrew","Linh", "Tung", "Tianna", "Joey", "Kim", "Tam", "Tien","Ngoc"]
    # 1100/wk
    tier4 = ["Cici"]
    # weekly rent deductions
    rent60 = ["Hong", "Rose", "De", "Cindy", "Tam", "Joey", "Ngoc", "Tai"]
    rent70 = ["Vu", "Quang", "Tung", "Nick", "Tianna", "Kim"]
    rent35 = ["Van", "Vivian"]
    
    for person in employees:
        if person in tier1:
            if person in rent60:
                payGrade[person] = [850,60]
            elif person in rent70:
                payGrade[person] = [850,70]
            elif person in rent35:
                payGrade[person] = [850,35]
            else:
                payGrade[person] = [850,0]            
        elif person in tier2:
            if person in rent60:
                payGrade[person] = [900,60]
            elif person in rent70:
                payGrade[person] = [900,70]
            elif person in rent35:
                payGrade[person] = [900,35]
            else:
                payGrade[person] = [900,0]
        elif person in tier3:
            if person in rent60:
                payGrade[person] = [1000,60]
            elif person in rent70:
                payGrade[person] = [1000,70]
            elif person in rent35:
                payGrade[person] = [1000,35]
            else:
                payGrade[person] = [1000,0]
        elif person in tier4:
            if person in rent60:
                payGrade[person] = [1100,60]
            elif person in rent70:
                payGrade[person] = [1100,70]
            elif person in rent35:
                payGrade[person] = [1100,35]
            else:
                payGrade[person] = [1100,0]
        else:
            payGrade[person] = [0,0]
            
    return payGrade

def currentStatus(employees):
    '''
    Manually set employee status so that reports show their income

    Args:
        employees(dict): list of employees

    Returns:
        stats(dict): status of employees currently working; True if yes else False
    '''
    stats = dict()
    active = ["Kelly", "Anna", "Andrew", "Van", "Vivian", "Manager", "Bin", "Joey", "Cindy", "Tai", "Ngoc"]
    for person in employees:
        if person in active:
            stats[person] = True
        else:
            stats[person] = False
    return stats

#################################################################################



def identify(dfIncome, table, employees):
    '''
    Extracts first column of report excel sheet to determine date/employee.
    Also populates full list of all employees

    Args: 
        dfIncome (data frame): imported from excel file using pandas
        table (array): [10][366] 10 year column with 366 day rows
        employees (dict): dictionary of employees with names as keys

    Returns: 
        dict: income dictionary with employees as keys and values are 3d arrays
             income[employee][year][day][various incomes]
    '''
    income = dict()
    dayIndex = 0
    
    # to avoid assigning a value in array and it shows up multiple places,
    # you should declare array size first, then go through each element and
    # assign values
    yearly = [0] * 11
    daily = [0] * 377
    for year in range(11):
        for day in range(377):
            daily[day] = [0] * 5
        yearly[year] = copy.deepcopy(daily)
    
    year = 0
    for i in range(len(dfIncome)):
        if i == 13:
            pass
        if i <= 2:
            continue
        value = dfIncome.iloc[i,0]
        # now figure out what datatype "value" is in order to parse correctly
        if isinstance(value, pd.Timestamp):
            date_obj = value.to_pydatetime()
            # any year after modded will be indexed 0-10
            year = date_obj.timetuple()[0] % 2020
            if date_obj.date() in table[year]:
                dayIndex = date_obj.date().timetuple()[7]
        elif isinstance(value, str):
            # add employee name if not yet in list
            # get just first name out of whole name string of "first last (nick)"
            name = ""
            for letter in value:
                if letter != " ":
                    name = name + letter
                else:
                    break
            value = name   
            if value not in employees:
                if value == "Grand":
                    break
                employees.append(value)
                # for each employee add blank template for whole year
                income[value] = copy.deepcopy(yearly) 
            
            # "S"=services, "G"=Gift card sales which can be ignored
            if dfIncome.iloc[i,1] == "S":
                income[value][year][dayIndex][0] = dfIncome.iloc[i,4]     # price
                income[value][year][dayIndex][1] = dfIncome.iloc[i,7]    # discount
                income[value][year][dayIndex][2] = dfIncome.iloc[i,10]    # tips
                income[value][year][dayIndex][3] = dfIncome.iloc[i,11]    # commission
                # row 5 will be for paid salary
        else:
            # this will be when value is nan datatype is float
            continue
       
    return income

def calculateSalary(income, table, employees, dates):
    '''-------------------------------------------------------------
    Calculates weekly salary from selected date range and prints
    results week by week
    
    Args:
        income (dict): employees are keys, and values are 3d arrays of daily values
        table (array): [10][366] array for daily indices
        employees (array): list of all employees
        dates (array) : [startDate, endDate] variables are datetime format

    Returns:
        n/a
    '''
    # dates = getDates()    # now passed as an argument
    stats = currentStatus(employees)
    # retrieves day of the year starting at one, 
    # but in "table" variable index starts at 0, not 1
    start = dates[0].timetuple()[7] - 1
    end = dates[1].timetuple()[7] - 1
    
    yearStart = dates[0].timetuple()[0] % 2020
    yearEnd = dates[1].timetuple()[0] % 2020
    
    payGrade = definePayTier(employees)
    ## this portion finds employee weekly sales
    # will have 8 elements: keys are employees and value is total payment
    weeklyPay = dict()
    weeklyDiscount = dict()
    # each person has a list [commission, tips, discount] * 7 for each day of week
    dailySalary = dict()
    for person in employees: 
        weeklyPay[person] = []
        dailySalary[person] = []
        weeklyDiscount[person] = []
        
    print("*******************************************************************")
    print("                              Salary                               ")
    print("*******************************************************************")
    print("           Commission   |   Pay   |   Tip   |   Check   |   Cash   ")
    
    year = yearStart
    
    # if consists of december and january, indices will be messed up because
    # end will be smaller than start variable. Therefore, special counter 
    # must be implemented in for loop
    if yearStart != yearEnd:
        end = len(table[yearStart]) + end
    actualDayIndex = start
    for i in range(start, end+1):
        day = table[year][actualDayIndex]        
        dayIndex = day.timetuple()[7]
        dayName = calendar.day_name[day.weekday()]
        for j,person in enumerate(employees):
            dayCommission = income[person][year][dayIndex][3]
            dayTip = income[person][year][dayIndex][2]
            discount = income[person][year][dayIndex][1]
            dailySalary[person].append([dayCommission,dayTip,discount])
    
        if dayName == "Sunday":        
            for person in employees:
                minimumPay = payGrade[person][0]
                rent = payGrade[person][1]
                # find out how many days they worked that week
                days = 0                
                commission = 0
                tips = 0
                discounts = 0
                for items in dailySalary[person]:
                    # if commission for that day is greater than zero
                    if items[0] > 0:
                        days = days + 1
                    commission = commission + items[0]
                    tips = tips + items[1]
                    discounts = discounts + items[2]
                # if 6 days
                if days < 6:
                    minimumPay = 0
                elif days > 6:
                    # if 1000 an extra day would be 1100 
                    minimumPay = minimumPay + 100
                    
                pay = commission   
                if commission < minimumPay:
                    pay = minimumPay
                    
                if person == "Nick":
                    payCheck = (pay * 0.5) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.5) - rent
                else:
                    payCheck = (pay * 0.6) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.4) - rent #(cash minus rent)
                
                
                weeklyPay[person].append([commission, pay, tips, payCheck, payCash])
                weeklyDiscount[person].append(discounts)
                # clear out daily values for new week
                dailySalary[person].clear()
    
            print(f"============       Week: {table[year][actualDayIndex-6]:%m/%d/%Y} - {table[year][actualDayIndex]:%m/%d/%Y}       ============")
            employees.sort()
            for person in employees:
                # if person has active status
                if stats[person]:
                    print(f"{person:10}: {weeklyPay[person][0][0]:10.1f}  |  {weeklyPay[person][0][1]:6.1f} |  {weeklyPay[person][0][2]:7.1f}  | {weeklyPay[person][0][3]:7.1f}  |  {weeklyPay[person][0][4]:7.1f}")
                    print("-------------------------------------------------------------------")
                weeklyPay[person].clear()
            
        
        actualDayIndex = actualDayIndex + 1
        d = day.timetuple()[2]
        m = day.timetuple()[1]
        # if it is december 31, update year index
        if d == 31 and m == 12:
            year = yearEnd
            actualDayIndex = 0


def export1099(income, table, employees):
    '''-------------------------------------------------------------
    Calculates weekly salary from selected date range and prints
    results
    
    Args:
        income (dict): employees are keys, and values are 3d arrays of daily values
        table (array): [10][366] array for daily indices
        employees (array): list of all employees

    Returns:
        checksPaid (dict): for each employee (keys), an array of strings set to be written to file (values)
    '''
    dates = getDates()
    stats = allActiveStatus(employees)
    # retrieves day of the year starting at one, 
    # but in "table" variable index starts at 0, not 1
    start = dates[0].timetuple()[7] - 1
    end = dates[1].timetuple()[7] - 1
    
    yearStart = dates[0].timetuple()[0] % 2020
    yearEnd = dates[1].timetuple()[0] % 2020
    
    payGrade = definePayTier(employees)
    ## this portion finds employee weekly sales
    # will have 8 elements: keys are employees and value is total payment
    weeklyPay = dict()
    weeklyDiscount = dict()
    # each person has a list [commission, tips, discount] * 7 for each day of week
    dailySalary = dict()
    # record weekly checks for tax purposes
    checksPaid = dict()
    for person in employees: 
        weeklyPay[person] = []
        dailySalary[person] = []
        weeklyDiscount[person] = []
        checksPaid[person] = []

    year = yearStart    
    # if consists of december and january, indices will be messed up because
    # end will be smaller than start variable. Therefore, special counter 
    # must be implemented in for loop
    if yearStart != yearEnd:
        # len of table can arbitrarily be larger because at the end of the loop,
        # there will be a catch for december 31 and then index will be adjusted
        end = len(table[yearStart]) + end
    actualDayIndex = start
    for i in range(start, end+1):
        day = table[year][actualDayIndex]        
        dayIndex = day.timetuple()[7]
        dayName = calendar.day_name[day.weekday()]
        for j,person in enumerate(employees):
            dayCommission = income[person][year][dayIndex][3]
            dayTip = income[person][year][dayIndex][2]
            discount = income[person][year][dayIndex][1]
            dailySalary[person].append([dayCommission,dayTip,discount])
    
        if dayName == "Sunday":        
            for person in employees:
                minimumPay = payGrade[person][0]
                rent = payGrade[person][1]
                # find out how many days they worked that week
                days = 0                
                commission = 0
                tips = 0
                discounts = 0
                for items in dailySalary[person]:
                    # if commission for that day is greater than zero
                    if items[0] > 0:
                        days = days + 1
                    commission = commission + items[0]
                    tips = tips + items[1]
                    discounts = discounts + items[2]
                # if 6 days
                if days < 6:
                    minimumPay = 0
                elif days > 6:
                    # if 1000 an extra day would be 1100 
                    minimumPay = minimumPay + 100
                    
                pay = commission   
                if commission < minimumPay:
                    pay = minimumPay
                    
                if person in check50:
                    payCheck = (pay * 0.5) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.5) - rent
                else:
                    payCheck = (pay * 0.6) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.4) - rent #(cash minus rent)
                    
                weeklyPay[person].append([commission, pay, tips, payCheck, payCash])
                weeklyDiscount[person].append(discounts)
                # clear out daily values for new week
                dailySalary[person].clear()
    
            for person in employees:
                # if person has active status
                if stats[person]:
                    checksPaid[person].append([f"{table[year][actualDayIndex-6]:%m/%d/%Y}", f"{table[year][actualDayIndex]:%m/%d/%Y}", weeklyPay[person][0][3]])
                weeklyPay[person].clear()
            
        
        actualDayIndex = actualDayIndex + 1
        d = day.timetuple()[2]
        m = day.timetuple()[1]
        # if it is december 31, update year index
        if d == 31 and m == 12:
            year = yearEnd
            actualDayIndex = 0

    return checksPaid


def graph(yearIndex, table, income, employees):
    '''-------------------------------------------------------------
    Graphs reports of incomes and saves it into Upscale{yearIndex}.html. Html is then opened in file browser automatically.
    
    Args: 
        yearIndex(int): the year is modded by 2020 resulting in 0-10
        table (array): [10][366] array for daily indices
        income (dict): employees are keys, and values are 3d arrays of daily values
        employees (dict): list of all employees

    Returns:
        string: name of html file
    '''
    # find weekly income
    #---------------------------------------
    dailyIncome = []    # y-axis labels, income of salon
    weeklyIncome = []   # y-axis labels; income of salon
    weekDates = []      # x-axis labels
    weeklyTotal = 0
    weekNumber = 0
    for day in table[yearIndex]:
        d = calendar.day_name[day.weekday()]
        dayIndex = day.timetuple()[7]
        dailyTotal = 0
        for person in employees:
            # everyone's daily total minus their discounts
            dailyTotal = dailyTotal + income[person][yearIndex][dayIndex][0] - income[person][yearIndex][dayIndex][1]
            # everyone's weekly total minus their discounts
            weeklyTotal = weeklyTotal + income[person][yearIndex][dayIndex][0] - income[person][yearIndex][dayIndex][1]
        if d == "Sunday":
            weeklyIncome.append(weeklyTotal)
            weeklyTotal = 0
            startWeek = datetime.datetime.strftime(table[yearIndex][dayIndex-7], "%m/%d")
            endWeek = datetime.datetime.strftime(day, "%m/%d")
            weekDates.append(f"{startWeek}-{endWeek}")
            weekNumber = weekNumber + 1
        dailyIncome.append(dailyTotal)
    
    if weeklyTotal > 0:
        weeklyIncome.append(weeklyTotal)
        
    # find weekly payout for each employee
    #--------------------------------------    
    payGrade = definePayTier(employees)
    ## this portion finds employee weekly sales
    # contains weekly payout, cash & check, for each employee
    weeklyPay = dict()
    weeklyDiscount = dict()
    # each person has a list [commission, tips, discount] * 7 for each day of week
    dailySalary = dict()
    for person in employees: 
        weeklyPay[person] = []
        dailySalary[person] = []
        weeklyDiscount[person] = []
        
    for day in table[yearIndex]:
        dayIndex = day.timetuple()[7]
        d = calendar.day_name[day.weekday()]
        
        # for each day, this loop gathers commission, tip, discount for each person
        for person in employees:
            dayCommission = income[person][yearIndex][dayIndex][3]
            dayTip = income[person][yearIndex][dayIndex][2]
            dayDiscount = income[person][yearIndex][dayIndex][1]
            dailySalary[person].append([dayCommission,dayTip,dayDiscount])
        
        # if it is Sunday, calculate weekly totals and determine if paying 
        # commission or salary
        if d == "Sunday":
            for person in employees:
                minimumPay = payGrade[person][0]
                rent = payGrade[person][1]
                # find out how many days they worked that week
                days = 0                
                commission = 0
                tips = 0
                discounts = 0
                
                # for employee, each items are daily [commission, tip, discount]
                for items in dailySalary[person]:
                    # if commission for that day is greater than zero
                    # count how many days that person worked in that week
                    if items[0] > 0:
                        days = days + 1
                    commission = commission + items[0]
                    tips = tips + items[1]
                    discounts = discounts + items[2]
                    
                # if 6 days
                if days < 6:
                    minimumPay = 0
                elif days > 6:
                    # if worked everyday, add $100 to pay
                    minimumPay = minimumPay + 100
                pay = commission   
                if commission < minimumPay:
                    pay = minimumPay
                    
                if person in check50:
                    payCheck = (pay * 0.5) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.5) - rent
                else:
                    payCheck = (pay * 0.6) + tips
                    # if person did not work during week (or quit) then no rent 
                    if payCheck == 0:
                        rent = 0
                    payCash = (pay * 0.4) - rent #(cash minus rent)
                
                weeklyPay[person].append(payCheck + payCash)
                weeklyDiscount[person].append(discounts)
                # clear out daily values for new week
                dailySalary[person].clear()
    
    # find out net income for each week after payroll
    #------------------------------------------------------        
    weeklyNet = []
    for i, week in enumerate(weeklyIncome):
        if i == len(weeklyIncome)-1:
            break
        weekOut = 0
        if week > 0:
            # sum up everyone's outgoing money: check, cash, discounts
            for person in employees:
                weekOut = weekOut + weeklyPay[person][i] + weeklyDiscount[person][i]
            # weekNet appends weekly income minus 
            weeklyNet.append(week - weekOut)
        else:
            weeklyNet.append(0)
        
    # find out net income after payroll and bills
    # bills = 8800/month
    # 2200 (2 duplex rent)
    # 1000 (1 house rent)
    # update later
    # estimated total will be 10k for one month which is 2500 each week
    #---------------------------------------------------------
    weeklyNetAfterBills = []
    for i, items in enumerate(weeklyIncome):
        if i == len(weeklyIncome)-1:
            break
        if items == 0:
            weeklyNetAfterBills.append(0)
        else:
            weeklyNetAfterBills.append(weeklyNet[i] - 2500)
    
    cumulativeNetAfterBills = []
    for i, items in enumerate(weeklyNetAfterBills):
        if items == 0 or i == 0:
            cumulativeNetAfterBills.append(0)
        else:
            cumulativeNetAfterBills.append(weeklyNetAfterBills[i] + cumulativeNetAfterBills[i-1])
        
    # plotting of figures in html
    #---------------------------------------------------------
    # create figure  
    fig = make_subplots(rows=4, cols=1,
            shared_xaxes=True,
            subplot_titles=("Daily Income", "Weekly Income", "Weekly Net",
                            "Cumulative Net")                    
    )
    
    # add traces
    fig.append_trace(
            go.Scatter(
            x=table[yearIndex],
            y=dailyIncome,
            name="Daily Income",
            line = dict(color = "#e36bbb"),
            opacity = 0.8
            ),
            row=1,
            col=1
    )
    
    fig.append_trace(
            go.Scatter(
                x=weekDates,
                y=weeklyIncome,
                name="Weekly Income",
                line = dict(color="#17BECF")
            ),
            row=2,
            col=1
    )
    
    fig.append_trace(
        go.Scatter(
            x=weekDates,
            y=weeklyNet,
            name="Weekly Net",
            line=dict(color="#90fc92")
        ),
        row=2,
        col=1
    )
    
    fig.append_trace(
        go.Scatter(
            x=weekDates,
            y=weeklyNetAfterBills,
            name="After salary and bills",
            line=dict(color="#7baced")
        ),
        row=3,
        col=1
    )
    
    fig.append_trace(
        go.Scatter(
            x=weekDates,
            y=cumulativeNetAfterBills,
            name="Cumulative Net",
            line=dict(color="#1ba153")
        ),
        row=4,
        col=1
    )
     # style all traces
    fig.update_traces(
        hoverinfo="x+y",
        mode="lines+markers"    
    )
    pio.write_html(fig, file=f"upscale{yearIndex}.html", auto_open=True)
    return f"upscale{yearIndex}.html"

def sendFtp(filename):
    '''
    Sends html of graphs to ftp server into a folder named "web"

    Args: 
        filename(str): name of html file to be uploaded

    Returns: n/a
    '''
    # send upscale.html file to webserver
    import pysftp
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    
    # connect
    with pysftp.Connection("kitpham.i234.me", username="kit", password="Yugen334", cnopts=cnopts) as sftp:
        with sftp.cd("/web"):
            sftp.put(filename)



def allActiveStatus(employees):
    '''
    This function sets everyone's status to active for full year reporting 

    Args:
        employees(dict): list of employees

    Returns:
        stats(dict): status of employees currently working; everyone is set True
    '''
    stats = dict()
    for person in employees:
        stats[person] = True
    return stats


   
# =============================================================================
# def getDates():
#     '''-----------------------------------------------------------------
#     Popup dialog asking for date range
# 
#     Args: n/a
# 
#     Returns: 
#         [datetime,datetime]: datetime objects
#     '''  
#     month = datetime.datetime.today().month
#     day = datetime.datetime.today().day
#     year = datetime.datetime.today().year
#     layout = [[sg.Text('Date Chooser Test Harness', key='-TXT-')],
#            [sg.Input(key='-IN0-', size=(20,1)), sg.CalendarButton('Start',  target='-IN0-', format='%Y-%m-%d', default_date_m_d_y=(month,day,year))],
#            [sg.Input(key='-IN1-', size=(20,1)), sg.CalendarButton('End',  target='-IN1-', format='%Y-%m-%d', default_date_m_d_y=(month,day,year))],
#       [sg.Button('OK'), sg.Exit()]]
# 
#     window = sg.Window('window', layout)
# 
#     while True:
#         event, values = window.read()
#         if event in (sg.WIN_CLOSED, 'Exit'):
#             window.close()
#             break
#         elif event == 'OK':
#             window.close()
#             start = datetime.datetime.strptime(values["-IN0-"], "%Y-%m-%d")
#             end = datetime.datetime.strptime(values["-IN1-"], "%Y-%m-%d")
#             return [start,end]
# =============================================================================
def getDates():
    '''-----------------------------------------------------------------
    Popup dialog asking for date range

    Args: n/a

    Returns: 
        [datetime,datetime]: datetime objects
    '''  
    # date input is separated by a dash
    date = input("Input date (monthdayyear-monthdayyear): ")
    start,end = date.split("-")
    start = datetime.datetime.strptime(start, "%m%d%y")
    end = datetime.datetime.strptime(end, "%m%d%y")
    return [start,end]
          
def writeChecksReport(checksPaid, employees):
    '''------------------------------------------------------------
    This function writes out every check written and saves them
    into files named after employee

    Args:
        checksPaid(dict): each employee has an array of texts to be written line by line

    Returns: n/a
    ''' 
    for person in employees:
        subtotal = 0
        # create a file with each person's name to write data into
        with open(f"{person}.txt", "w") as fp:
            for week in checksPaid[person]:
                subtotal = subtotal + week[2]
                line = week[0] + ", " + week[1] + ", " + str(math.ceil(week[2])) + ", " + str(math.ceil(subtotal)) + "\n"
                fp.write(line)   