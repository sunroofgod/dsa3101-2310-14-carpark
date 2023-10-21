import numpy as np
import pandas as pd
from datetime import datetime

COL_NAMES = ['exit_id', 'iu', 'enter', 'enter_formatted', 'exit', 'exit_formatted',
             'hourly_du', 'staff_du', 'student_du', 'esp_du']

COL_TYPES = {
    'exit_id' : int, 
    'iu' : str, 
    'enter' : 'datetime64[ns]', 
    'enter_formatted' : bool, 
    'exit' : 'datetime64[ns]',
    'exit_formatted' : bool,
    'hourly_du' : float, 
    'staff_du' : float, 
    'student_du' : float,
    'esp_du' : float
}

NA_VALUES = ['\\N']

def parse_xlsx(path):
    """
    Rename data columns, convert to correct datatypes and tidy table format

    Parameters:
    path : xlsx file path

    Returns:
    pandas DataFrame
    """
    
    ## Read excel file
    df = pd.read_excel(path, names=COL_NAMES, dtype=COL_TYPES,
                   index_col=False, na_values=NA_VALUES)
    df = df.drop(['enter_formatted', 'exit_formatted'], axis=1)

    ## Reformat table
    df = pd.melt(df, id_vars=['exit_id', 'iu', 'enter', 'exit'], 
                 var_name='type', value_name='duration')
    df = df.dropna(axis=0)

    ## Split datetime to date and time
    df['enter_date'] = df['enter'].dt.date
    df['enter_time'] = df['enter'].dt.time
    df['exit_date'] = df['exit'].dt.date
    df['exit_time'] = df['exit'].dt.time    
    
    ## Drop redundant columns
    df = df.drop(['enter', 'exit'], axis=1)

    return df

