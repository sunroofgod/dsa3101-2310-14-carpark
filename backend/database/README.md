# About database folder

This folder contains the code for connecting to the MySQL database and populating the database with cleaned data. 

We provide a dockerised method that does not require setting up MySQL. Alternatively, if you wish to test this initialise the databse locally (targetted to developers), a local MySQL database can also be set up. 

## Notable Functions
`connect_db`: located in `mysql_connector.py`, this function accesses environment variables and returns an engine Connection object to the specified MySQL database. This object is further used to upload and query data from the database

## To initialise databse through Docker

The Docker file will automatically run the `__init__.py` file on build. There is no need to access this directory.

## For local testing
1. Change the MySQL connection string in line 17 of `mysql_connector.py`. 
'db' should be replaced with 'localhost'. This is because the ports used in the docker environment is different from the default ports in the local environment. 

```sh
# CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@db:3306/{DATABASE_NAME}'
CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@localhost:3306/{DATABASE_NAME}'
```

### Setting up local MySQLWorkbench

1. Install MySQLWorkbench [here](https://dev.mysql.com/downloads/workbench/).

2. Setup a new MySQL Connection by clicking on the + icon.
<img src="../.github/public/sql_workbench_setup_step1.png" width="500">

3. Fill in all the compulsory fileds. In the case of our webapp, it is important to remember the fields `Username`, `Password` and `Default Schema` that we set. **ENSURE** that you have set the port to 3306, else it will not run.
<img src="../.github/public/sql_workbench_setup_step2.png" width="700">

4. Press ok. 

### Setting up local environment variables

1. Navigate to the root directory of the repository

2. Set up environment variables. You may do so with your favourite text editor. In this case, we are using vim.

   ```sh
   vim .env # this file must be at the root directory of the cloned repo
   ```
   Make sure you have these three variables declared in .env in accordance to the way you have setup your MySQLWorkbench database.
   ```txt
   DATABASE_NAME=sys 
   MYSQL_USERNAME=<your mysqsl username>
   MYSQL_PASSWORD=<your mysqsl password>
   
   # We use the default database schema name `sys`

   # replace the details within the angle brackets with your details.
   # don't forget to delete the angle brackets as well.
   ```

3. Make sure you have started running a MySQL Connection instance. You may do so by clicking on the MySQL Connection you have previously set up as seen here.
<img src="../.github/public/sql_workbench_setup_step3.png" width="500">

4. Run the file to initialise data in the local database
```sh
python3 backend/database/__init__.py
```