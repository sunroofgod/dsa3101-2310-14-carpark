import os
import pandas as pd
import numpy as np

def load_and_clean_data(carpark_data : dict):
    """
    Function takes in a dictionary of file paths and returns an aggregated dataframe 
    To save the cleaned datasets and final aggregated dataset as a csv file, run this file in this folder directory (backend/data_preprocessing)

    Args:
        carpark_data (dict): dictionary of carpark name and file path

    Returns:
        pd.DataFrame: aggregated dataframe of all carpark data
    """
    aggregate_df = pd.DataFrame()
    for carpark in carpark_data:
        file_path = carpark_data[carpark]
        df_clean = clean_carpark_data(file_path)
        df_clean_duration = generate_duration(df_clean)

        # Hard code additional column for Cp10 raw data
        if carpark == 'Cp10':
            df_clean_duration['carpark'] = 'CP10'
            df_clean_duration['exit_id'] = 'CP10' # for consistency with other datasets

        # Drop invalid rows with non-positive durations as they do not make sense
        df_clean_final = df_clean_duration.loc[df_clean_duration['parked_min']>0]
        print(f"Number of non-positive durations dropped for {carpark}: {df_clean_duration.shape[0] - df_clean_final.shape[0]}")
        
        aggregate_df = pd.concat([aggregate_df, df_clean_final], ignore_index=True)
        # Save the cleaned data to a csv file if main
        if __name__ == '__main__':
            df_clean_final.to_csv(os.path.join('../../data/cleaned', carpark + '_cleaned' + '.csv'), index=False)
    
    aggregate_df.drop_duplicates(inplace=True, ignore_index=True)
    # Select max parked duration for any duplicated IU, carpark and enter_dt
    find_max_series = aggregate_df.groupby(['IU', 'carpark', 'enter_dt']).parked_min.transform('max')
    filterd_df = aggregate_df[aggregate_df['parked_min'] == find_max_series]
    if __name__ == '__main__':
        filterd_df.to_csv(os.path.join('../../data/cleaned', 'all_carparks_cleaned' + '.csv'), index=False)
    return filterd_df

def clean_carpark_data(path : str):
    """
    Function takes in path to raw data file and returns a cleaned dataframe

    Args:
        csv file path, assumes that csv
            - contains columns 'hourly_du', 'staff_du', 'student_du', 'esp_du'
            - and columns enter_dt and exit_dt are all non-null

    Returns:
    cleaned dataframe with columns 'IU', 'carpark', 'exit_id', 'enter_dt', 'exit_dt', 'type'
    """
    df = pd.read_csv(path)
    print(f"loaded {path} with shape {df.shape}")

    # For cp5 and Cp33a45b6b_a and other carpark data in similar format:
    if all(df.columns == ['ExitId', 'IU', 'enter', 'Exit', 'hourly_du', 'staff_du', 'student_du','esp_du']):
        df.rename(columns={'enter':'enter_dt', 'Exit': 'exit_dt', 'ExitId': 'exit_id'}, inplace=True)
        df['enter_dt'] = pd.to_datetime(df['enter_dt'], format='%d/%m/%Y %H:%M')
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%d/%m/%Y %H:%M')
    
    # For cp10 and other carpark data in similar format:
    elif all(df.columns == ['report time', 'IU', 'Enter Time', 'Exit time', 'hourly_du', 'staff_du', 'student_du', 'esp_du']):
        df.drop(columns='report time', inplace=True)
        df.rename(columns={'Enter Time':'enter_dt', 'Exit time': 'exit_dt', 'ExitId': 'exit_id'}, inplace=True)
        df['exit_dt'] = pd.to_datetime(df['exit_dt'], format='%Y-%m-%d %H:%M:%S')
        df['enter_dt'] = pd.to_datetime(df['enter_dt'], format='%Y-%m-%d %H:%M:%S')

    # remove NA values
    df = df.replace(to_replace='\\N', value = np.nan) # for Cp5 and Cp33a45b6b_a raw csv
    df = df.fillna(np.nan, inplace=False) # for Cp10 raw csv

    # convert X_du into one column specifying the type of parking, since there are invalid duration values
    df.loc[df['hourly_du'].notnull(), 'type'] = 'visitor'
    df.loc[df['staff_du'].notnull(), 'type'] = 'staff'
    df.loc[df['student_du'].notnull(), 'type'] = 'student'
    df.loc[df['esp_du'].notnull(), 'type'] = 'esp'

    # drop the X_du columns
    df.drop(columns=['hourly_du', 'staff_du', 'student_du', 'esp_du'], inplace=True)

    # drop rows with invalid IU
    df = df[df['IU']!='5228257a']
    
    # add exit_id values if needed, mainly for Cp10
    if 'exit_id' not in df.columns:
        df['exit_id'] = np.nan
    else:
        df['exit_id'] = df['exit_id'].astype(int).astype(str)
    
    # map exit_id to carpark name using json file stored locally in data folder
    import json
    if __name__ == '__main__':
        relative_path = '../../data' 
    else: # assume running from root directory
        relative_path = 'data'
    with open(relative_path + '/exit_id_mapping.json') as f:
        EXIT_ID_MAPPING = json.load(f)

    df['carpark'] = df['exit_id'].apply(lambda key: EXIT_ID_MAPPING[key] if key in EXIT_ID_MAPPING else np.nan)

    # reorder columns
    df = df[['IU', 'carpark', 'exit_id', 'enter_dt', 'exit_dt', 'type']]

    return df 

def generate_duration(df : pd.DataFrame):
    """
    Function to generate duration between exit and enter datetime
    adds columns 'parked_min', 'parked_hrs', 'parked_days' to df

    Args:
        df (pd.DataFrame): dataframe with columns 'enter_dt' and 'exit_dt'

    Returns:
        df (pd.DataFrame): dataframe with columns 'parked_min', 'parked_hrs', 'parked_days'
    """
    # gets minute, hours and days spent in carpark between Enter and Exit Time
    df[['parked_min', 'parked_hrs', 'parked_days']] = list(map(lambda dt: \
        # total_seconds() gives +ve and -ve values # use int() to round negative numbers to 0 instead of -1                                                                      
        (dt.total_seconds()//60, round(dt.total_seconds()/(60*60), 2), int(dt.total_seconds()/(60*60*24))) , df['exit_dt'] - df['enter_dt']))
    
    return df


if __name__ == '__main__':
    # Ensure to run this file from the backend/data_preprocessing folder directory
    # Check if the 'Data' folder exists, and create it if not.
    # Note that Data folder is untracked by git, hence data files can be added here
    data_folder = '../../data'
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)

    ## Add raw csv files and EXIT_ID_MAPPING.json into the Data folder for the below steps to work

    data_folder_cleaned = '../../data/cleaned'
    if not os.path.exists(data_folder_cleaned):
        os.mkdir(data_folder_cleaned)

    ## Clean three raw data files that were provided to us
    carpark_data = {'Cp5': '../../data/raw_Cp5_a.csv',
                'Cp_multiple': '../../data/raw_Cp33a45b6b_a.csv',
                'Cp10': '../../data/Sample raw data format - duration_cp10_Apr2023_a.csv'}
    
    clean_data = load_and_clean_data(carpark_data)