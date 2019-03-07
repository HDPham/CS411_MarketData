from flask import Flask, render_template, request
app = Flask(__name__, template_folder='templates')

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
from pandas.io import sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# Build database as you GO!!!!!
class Stock(db.Model):
    id = db.Column(db.Integer)
    name = db.Column(db.String(5), primary_key=True)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    close = db.Column(db.Numeric)
    volume = db.Column(db.Integer)
    def __repr__(self):
        return '<Stock %r>' % self.name

@app.route('/')
@app.route('/home')
def home ():
    return render_template('/home.html')

#continous web scraping -- update at closing
from alpha_vantage.timeseries import TimeSeries
import json
@app.route('/get_stock', methods=['GET', 'POST'])
def get_stock():
    # try to get the data
    try:
        stock = request.args.get('stock')
    # Add the data to the db
    except:
        return json.dumps(stock)
    ts = TimeSeries(key='IK798ICZ6BMU2EZM', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
    #Add to the database
    Session = db.create_session(options={'bind':'dest_db_con'})
    session = Session()
    engine = db.engine
    connection = engine.raw_connection()
    try:
        data.to_sql(name=stock, con=connection)
    finally:
        connection.close()
    stocks = session.query()
    session.close()

    for stock in stocks:
        print(stock)
    # Add the data to the db after grabbing it
    json_data= data.to_json(orient='split')
    return json_data

# @app.route('/update', methods=['GET'])
# def update_stock_table():
#     return
if __name__ == '__main__':
    db.create_all() #don't know if this works but let's try?
    app.run()
