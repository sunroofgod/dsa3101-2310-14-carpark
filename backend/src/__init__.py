from flask import Flask, request
from flask_cors import CORS
from database import db, setup_database

app = Flask(__name__)
CORS(app)

# init and connect to database
if (db == None):
    app.logger.error("Not able to connect to database.")
    raise Exception("No Database detected")
setup_database(db)
app.logger.info("Database created and populated")

# routings
@app.route('/')
def home():
    return '/ GET'

@app.route('/app>', methods=['GET', 'POST'])
def get_app():
    if request.method == 'POST':
        date = request.form.get('date') or '2024/12/25 09:00'
        # TO ADD: passing date into des/model functions
        return '/app POST'
    else:
        return '/app GET'

@app.route('/app/<int:carpark_id', methods=['GET', 'POST'])
def get_carparks(carpark_id):
    # TO ADD: either an sql query from a carparks table for info or query from a class
    # e.g. 
    # carpark_details = db.execute(text(f'SELECT * FROM carparks WHERE id = {carpark_id};')).fetchall()
    # db.commit()
    if request.method == 'POST':
        closed = request.form.get('closed') or 0
        red_lots = request.form.get('red_lots') or 0
        white_lots = request.form.get('white_lots') or 0
        # TO ADD: passing these three values into des/model functions
        return '/app/<int:carpark_id> POST'
    else:
        return '/app/<int:carpark_id> GET'

# init app
if __name__ == "__main__":
    app.run()
