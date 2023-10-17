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
        df.rename(columns={'enter':'enter_dt', 'Exit': 'exit_dt'})
        df['enter_dt'] = pd.to_datetime(df['enter_dt'], format='%d/%m/%Y %H:%M')
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%d/%m/%Y %H:%M')
    
    # For cp10 and other carpark data in similar format:
    elif all(df.columns == ['report time', 'IU', 'Enter Time', 'Exit time', 'hourly_du', 'staff_du', 'student_du', 'esp_du']):
        df.drop(columns='report time', inplace=True)
        df.rename(columns={'Enter Time':'enter_dt', 'Exit time': 'exit_dt'})
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%Y-%m-%d %H:%M:%S')

    df = df.replace(to_replace='\\N', value = np.nan)
    df = df.fillna(np.nan, inplace=False) 

    df.loc[df['hourly_du'].notnull(), 'type'] = 'non_season'
    df.loc[df['staff_du'].notnull(), 'type'] = 'staff'
    df.loc[df['student_du'].notnull(), 'type'] = 'student'
    df.loc[df['esp_du'].notnull(), 'type'] = 'esp'
    
    df.drop(columns=['hourly_du', 'staff_du', 'student_du', 'esp_du'], inplace=True)

def generate_duration(df):
    # gets minute, hours and days spent in carpark between Enter and Exit Time
    df[['parked_min', 'parked_hrs', 'parked_days', 'parked_valid']] = list(map(lambda dt: \
        (dt.seconds//60, round(dt.seconds/(60*60), 2), dt.seconds//(60*60*24), dt.total_seconds() >= 0) , df['exit_dt'] - df['enter_dt']))
    
    return df