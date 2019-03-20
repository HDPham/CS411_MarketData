from flask import Flask, render_template, request
import json
app = Flask(__name__, template_folder='templates')

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
from pandas.io import sql
#Note: On the actual webserver, will need to CREATE USER with full privileges
# After creating the user, then create database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://thomas:Password_123@localhost/stock_data" #change to mySQL later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

metadata = db.metadata

class Stock(db.Model):
    name = db.Column(db.String(5), primary_key=True)
    def __repr__(self):
        return '<Stock %r>' % self.name
class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(30))
    open_ = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
    stock_name = db.Column(db.String(5), db.ForeignKey('stock.name'), nullable=False)
    stocks = db.relationship('Stock', backref=db.backref('times', lazy=True))
    def __repr__(self):
        return '<Time %r>' % self.datetime
# class User(db.Model):
#     id =

@app.route('/')
@app.route('/home')
def home ():
    db.create_all() #don't know if this works but let's try?
    return render_template('/home.html')

#continous web scraping -- update at closing
from alpha_vantage.timeseries import TimeSeries
@app.route('/get_stock', methods=['GET', 'POST'])
def get_stock():
    #Get stock name and get SQLAlchemy database
    stock = request.args.get('stock')
    engine = db.engine
    #Start new session for database
    Session = db.create_session(options={'bind':'dest_db_con'})
    session = Session()
    connection = engine.connect()    #set up connection to engine so you can add stocks
    #Try to get data
    values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";").first()
    if(values is not None):
        values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";").fetchall()
        connection.close()
        session.close()
        stock_dict = {}
        for row in values:
            stock_dict[row["datetime"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
        return json.dumps(stock_dict)

    # If it fails, add the data to the db
    try:
        ts = TimeSeries(key='IK798ICZ6BMU2EZM')
        data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
        print(data)
    except:
        raise Exception("Failed to retrieve data from alpha_vantage")
    #Create a new table
    new_table = Stock(name=stock)
    # The only thing we might have to adjust is inserting into the database
    for key in data.keys():
        time = Time(datetime=key, open_=data[key]['1. open'], high=data[key]['2. high'], low=data[key]['3. low'], close=data[key]['4. close'], volume=data[key]['5. volume'])
        new_table.times.append(time)
    session.add(new_table)
    session.commit()
    #Add to the database
    try:
        values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";")
    finally:
        connection.close()
    session.close()
    # Add the data to the db after grabbing it
    stock_dict = {}
    for row in values:
        stock_dict[row["datetime"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
    return json.dumps(stock_dict)

# This will be the automated webscrapper that updates stock info daily (during low use hours (2 AM?))
@app.route('/update', methods=['GET'])
def update_stock_table():
    return
if __name__ == '__main__':
    app.run()
