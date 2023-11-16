# About data_preprocessing

This folder contains one file `run_data_cleaning.py` that preprocess raw data in csv format for them to be uploaded into the MySQL database (see `backend/database/` for further details).

Cleaned data files can also be manually generated in local environment for viewing/verification purpose.

## Notable Functions
- `load_and_clean_data`: takes a dictionary of raw file paths and uses the below functions to generate the final aggregated and cleaned Dataframe.
- `clean_carpark_data`: returns cleaned data in pd.Dataframe format.
- `generate_duration`: add columns related to duration of stay in carpark to cleaned Dataframe. 

## Getting Started
To view and save the cleaned dataframes in your local environment, follow the steps below:

1. Create a `data/` folder in the root of this repository. This folder is untracked.

2. Add raw csv files provided by UCI staff and `EXIT_ID_MAPPING.json` into the `data/` folder.

3. Navigate to the `backend/data_preprocessing` directory in your terminal
```sh
cd backend/data_preprocessing
```

4. Run the file 
```sh
python3 run_data_cleaning.py
```

5. View the cleaned files in `data/cleaned/` folder
