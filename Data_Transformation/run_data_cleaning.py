import os
import csv

# Check if the 'Data' folder exists, and create it if not.
# Note that Data folder is untracked by git, hence data files can be added here
data_folder = 'Data'
if not os.path.exists(data_folder):
    os.mkdir(data_folder)

