import pandas as pd
import datetime
import calendar
import copy
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots

#local import
import config
table = config.table

def createDf(files):
    # declare empty for yearly dataframes
    df = []
    
    for path in files:    
        # retrieves dataframe using pandas
        dfIncome = pd.read_excel(path, sheet_name=0)
        # deletes unwanted header rows and replace is set to true
        dfIncome.drop(
            labels=[0,1],
            axis=0,
            inplace=True
        )
        # deletes unwanted columns (use iloc if column names have duplicates)
        dfIncome.drop(
            columns=["Unnamed: 2","Unnamed: 4","Unnamed: 6","Unnamed: 7","Unnamed: 8",
                     "Unnamed: 9"],
            inplace=True
        )
        # removes header rows that are not actual column labels and also removes last
        # row labeled grand total
        newHeader = dfIncome.iloc[0]
        dfIncome = dfIncome[1:len(dfIncome)-1]
        dfIncome.columns = newHeader
        
        df.append(dfIncome)
    return df

def convertWeekly(df):
    """
    takes an array of yearly income and converts from daily to weekly with
    Monday as the starting week

    Parameters
    ----------
    df : array of dataframes
        each dataframe contains total daily sales.
        columns are ["Date","Subtotal","Ticket Discount","Gift Sale"]

    Returns
    -------
    weekly : array of dataframes
        Sum of weekly income starting on Mondays

    """
    weekly = []
    
    for data in df:
        weeklyIncome = data.set_index("Date", inplace=False).resample("W-SUN", label="left", closed="left").sum()
        # reset index so we can use it as a y axis for graphing
        weeklyIncome.reset_index(inplace=True)
        weekly.append(weeklyIncome)
    
    return weekly
            
def graph(df):
    weeklyDf = convertWeekly(df)
    
    # create figure
    fig = make_subplots(rows=4, cols=1, shared_xaxes=False,
                        subplot_titles=("Daily 2021", "Daily 2020",
                                        "Weekly 2021: Dates are beginning of week", "Weekly 2020")
    )
    
    # add traces
    colors = ["#17BECF","#90fc92"]
    fig.append_trace(
        go.Scatter(
            x=df[1]["Date"].tolist(),
            y=df[1]["Sub Total"].tolist(),
            name="Daily 2021",
            line= dict(color=colors[0]),
            opacity=0.8
            ),
        row=1,
        col=1
    )
    
    fig.append_trace(
        go.Scatter(
            x=df[0]["Date"].tolist(),
            y=df[0]["Sub Total"].tolist(),
            name="Daily 2020",
            line= dict(color=colors[1]),
            opacity=0.8
            ),
        row=2,
        col=1
    )    
    
    fig.append_trace(
        go.Scatter(
            x=weeklyDf[1]["Date"].tolist(),
            y=weeklyDf[1]["Sub Total"].tolist(),
            name="Weekly 2021",
            line= dict(color=colors[0]),
            opacity=0.8
            ),
        
        row=3,
        col=1
    )
    
    fig.append_trace(
        go.Scatter(
            x=weeklyDf[0]["Date"].tolist(),
            y=weeklyDf[0]["Sub Total"].tolist(),
            name="Weekly 2020",
            line= dict(color=colors[1]),
            opacity=0.8
            ),
        row=4,
        col=1
    ) 
    
    # style all traces
    fig.update_traces(
        hoverinfo="x+y",
        mode="lines+markers"
    )
    
    pio.write_html(fig, file="upscale.html", auto_open=True)
        
            
        
        