from flask import Flask, render_template, request
import json
app = Flask(__name__, template_folder='templates')

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
from pandas.io import sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db' #change to mySQL later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

metadata = db.metadata
# stock = db.Table('stock', metadata,
#         db.Column('id', db.Integer, db.ForeignKey('id')),
#         db.Column('name', db.String(5), primary_key=True, db.ForeignKey('name')),
#         db.Column('high', db.Numeric, db.ForeignKey('high')),
#         db.Column('low', db.Numeric, db.ForeignKey('low')),
#         db.Column('close', db.Numeric, db.ForeignKey('close'))
#         db.Column('volume', db.Integer, db.ForeignKey('volume'))
#         )
# class Stock(db.Model):
#     id = db.Column(db.Integer)
#     name = db.Column(db.String(5), primary_key=True)
#     high = db.Column(db.Numeric)
#     low = db.Column(db.Numeric)
#     close = db.Column(db.Numeric)
#     volume = db.Column(db.Integer)
#     def __repr__(self):
#         return '<Stock %r>' % self.name
# class User(db.Model):
#     id =

@app.route('/')
@app.route('/home')
def home ():
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
    try:
        keys = engine.execute("SELECT * FROM "+stock).keys()
        values = engine.execute("SELECT * FROM "+stock).fetchall()
        connection.close()
        session.close()
        stock_table = {keys[i] : values[i] for i in range(0, len(keys))}
        return json.dumps(stock_table)
    except:
        pass
    # If it fails, add the data to the db
    ts = TimeSeries(key='IK798ICZ6BMU2EZM')
    data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')

    #Add to the database
    try:
        data.to_sql(stock, con=engine, schema=Stock(), if_exists='replace')
        keys = engine.execute("SELECT * FROM "+stock).keys()
        values = engine.execute("SELECT * FROM "+stock).fetchall()
        session.commit()
    finally:
        connection.close()
    session.close()
    # Add the data to the db after grabbing it
    stock_table = {keys[i] : values[i] for i in range(0, len(keys))}
    return json.dumps(stock_table)

# This will be the automated webscrapper that updates stock info daily (during low use hours (2 AM?))
# @app.route('/update', methods=['GET'])
# def update_stock_table():
#     return
if __name__ == '__main__':
    db.create_all() #don't know if this works but let's try?
    app.run()
