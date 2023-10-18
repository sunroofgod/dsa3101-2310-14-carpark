import os
import csv
from data_helper import *

# Check if the 'Data' folder exists, and create it if not.
# Note that Data folder is untracked by git, hence data files can be added here
data_folder = 'Data'
if not os.path.exists(data_folder):
    os.mkdir(data_folder)

## Add csv files into the Data folder for the below steps to work

data_folder = 'Data/Cleaned'
if not os.path.exists(data_folder):
    os.mkdir(data_folder)


file_paths = ['../Data/raw_Cp5_a.csv',
              '../Data/raw_Cp33a45b6b_a.csv',
              '../Data/Sample raw data format - duration_cp10_Apr2023_a.csv']

for file_path in file_paths:
    df_clean = clean_carpark_data(file_path)
    df_clean_final = generate_duration(generate_dow(df_clean))

    # Save the cleaned data to a csv file
    file_name = file_path.split('/')[-1].split('.')[0]
    df_clean_final.to_csv(os.path.join('../',data_folder, file_name + '_cleaned' + '.csv'), index=False)