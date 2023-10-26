import os
from data_helper import *

def load_and_clean_data(file_paths: dict):
    '''
    function takes in a dictionary of file paths and returns an aggregated dataframe 
    if __name__ == "__main__": individual carpark datasets and final dataframe will also be saved to a csv file
    '''
    aggregate_df = pd.DataFrame()
    for carpark in carpark_data:
        file_path = carpark_data[carpark]
        df_clean = clean_carpark_data(file_path)
        df_clean_duration = generate_duration(df_clean)

        # Hard code additional column for Cp10 raw data
        if carpark == 'Cp10':
            df_clean_duration['carpark'] = 'CP10'

        # Drop invalid rows with non-positive durations as they do not make sense
        df_clean_final = df_clean_duration.loc[df_clean_duration['parked_min']>0]
        print(f"Number of rows dropped for {carpark}: {df_clean_duration.shape[0] - df_clean_final.shape[0]}")
        
        aggregate_df = pd.concat([aggregate_df, df_clean_final], ignore_index=True)
        # Save the cleaned data to a csv file if main
        if __name__ == '__main__':
            df_clean_final.to_csv(os.path.join(data_folder, carpark + '_cleaned' + '.csv'), index=False)
    
    aggregate_df.drop_duplicates(inplace=True, ignore_index=True)
    aggregate_df.to_csv(os.path.join(data_folder, 'all_carparks_cleaned' + '.csv'), index=False)
    return aggregate_df

if __name__ == '__main__':
    # Check if the 'Data' folder exists, and create it if not.
    # Note that Data folder is untracked by git, hence data files can be added here
    data_folder = '../../data'
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)

    ## Add raw csv files and EXIT_ID_MAPPING.json into the Data folder for the below steps to work

    data_folder = '../../data/cleaned'
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
    ## Clean three raw data files that were provided to us
    carpark_data = {'Cp5': '../../data/raw_Cp5_a.csv',
                'Cp_multiple': '../../data/raw_Cp33a45b6b_a.csv',
                'Cp10': '../../data/Sample raw data format - duration_cp10_Apr2023_a.csv'}
    
    load_and_clean_data(carpark_data)