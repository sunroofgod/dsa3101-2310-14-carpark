import pandas as pd
import numpy as np

# create two functions due to difference in column headers
def clean_carpark_data(path):
    ''' 
    Input path is for
    - .csv format
    - contains columns 'hourly_du', 'staff_du', 'student_du', 'esp_du'
    - enter_dt and exit_dt are all non-null
    '''
    df = pd.read_csv(path)

    # For cp5 and Cp33a45b6b_a and other carpark data in similar format:
    if all(df.columns == ['ExitId', 'IU', 'enter', 'Exit', 'hourly_du', 'staff_du', 'student_du','esp_du']):
        df.rename(columns={'enter':'enter_dt', 'Exit': 'exit_dt'}, inplace=True)
        df['enter_dt'] = pd.to_datetime(df['enter_dt'], format='%d/%m/%Y %H:%M')
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%d/%m/%Y %H:%M')
    
    # For cp10 and other carpark data in similar format:
    elif all(df.columns == ['report time', 'IU', 'Enter Time', 'Exit time', 'hourly_du', 'staff_du', 'student_du', 'esp_du']):
        df.drop(columns='report time', inplace=True)
        df.rename(columns={'Enter Time':'enter_dt', 'Exit time': 'exit_dt'}, inplace=True)
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%Y-%m-%d %H:%M:%S')
        df['enter_dt'] = pd.to_datetime(df['enter_dt'], format='%Y-%m-%d %H:%M:%S')

    # remove NA values
    df = df.replace(to_replace='\\N', value = np.nan) # for Cp5 and Cp33a45b6b_a
    df = df.fillna(np.nan, inplace=False) # for Cp10

    # convert X_du into one column specifying the type of parking, since there are invalid duration values
    df.loc[df['hourly_du'].notnull(), 'type'] = 'non_season'
    df.loc[df['staff_du'].notnull(), 'type'] = 'staff'
    df.loc[df['student_du'].notnull(), 'type'] = 'student'
    df.loc[df['esp_du'].notnull(), 'type'] = 'esp'
    # drop the X_du columns
    df.drop(columns=['hourly_du', 'staff_du', 'student_du', 'esp_du'], inplace=True)

    # based on observation, we change year value of enter_dt:
    df["enter_dt"] = df["enter_dt"].apply(lambda x: x.replace(year = 2023) if x.year == 2037 else x)
    df["enter_dt"] = df["enter_dt"].apply(lambda x: x.replace(year = 2022) if x.year == 2026 else x)

    return df

def generate_duration(df):
    # gets minute, hours and days spent in carpark between Enter and Exit Time
    df[['parked_min', 'parked_hrs', 'parked_days', 'parked_valid']] = list(map(lambda dt: \
        # total_seconds() gives +ve and -ve values # use int() to round negative numbers to 0 instead of -1                                                                      
        (dt.total_seconds()//60, round(dt.total_seconds()/(60*60), 2), int(dt.total_seconds()/(60*60*24)), dt.total_seconds() >= 0) , df['exit_dt'] - df['enter_dt']))
    
    return df