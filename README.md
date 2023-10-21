# dsa3101-2310-14-carpark

## On local terminal:
1. Run `data_preprocessing/run_data_cleaning.py`: this generates a local data/ and data/cleaned folder if not already present
2. Add raw csv files and EXIT_ID_MAPPING.json to local folder
3. Re-run `data_preprocessing/run_data_cleaning.py`

Cleaned data tables contain headers: IU,carpark,exit_id,enter_dt,exit_dt,type,parked_min,parked_hrs,parked_days