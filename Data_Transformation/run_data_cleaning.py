import os
from data_helper import *

# Check if the 'Data' folder exists, and create it if not.
# Note that Data folder is untracked by git, hence data files can be added here
data_folder = '../Data'
if not os.path.exists(data_folder):
    os.mkdir(data_folder)

## Add csv files into the Data folder for the below steps to work

data_folder = '../Data/Cleaned'
if not os.path.exists(data_folder):
    os.mkdir(data_folder)

## Clean three raw data files that were provided to us
carpark_data = {'Cp5': '../Data/raw_Cp5_a.csv',
                'Cp_grouped': '../Data/raw_Cp33a45b6b_a.csv',
                'Cp10': '../Data/Sample raw data format - duration_cp10_Apr2023_a.csv'}

for carpark in carpark_data:
    file_path = carpark_data[carpark]
    df_clean = clean_carpark_data(file_path)
    df_clean_final = generate_duration(df_clean)

    ## Hard Code additional column for Cp10 raw data
    if carpark == 'Cp10':
        df_clean_final['exit_id'] = 'Cp10'

    # Save the cleaned data to a csv file
    df_clean_final.to_csv(os.path.join('../',data_folder, carpark + '_cleaned' + '.csv'), index=False)