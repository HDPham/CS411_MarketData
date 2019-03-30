from flask import Flask, render_template, request, Response, session
import json, datetime
app = Flask(__name__, template_folder='templates')
app.secret_key = '99qVu2YPjy5ss0Z66Igj'

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
#Get stock data API
from alpha_vantage.timeseries import TimeSeries     #If something goes wrong with stock data stuff, it's here


#Note: On the actual webserver, will need to CREATE USER with full privileges
# After creating the user, then create database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://cs411proj:Password_123@localhost/stock_data" #change to mySQL later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

metadata = db.metadata

users_tracking_stocks = db.Table('users_tracking_stocks',
    db.Column('user', db.String(100), db.ForeignKey('user.user'), primary_key=True),
    db.Column('stock', db.String(5), db.ForeignKey('stock.name'), primary_key=True)
    )

class User(db.Model):
    user = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))
    tracked_stocks = db.relationship('Stock', secondary=users_tracking_stocks, lazy='subquery',
                    backref=db.backref('users', lazy=True))
    def __repr__(self):
        return '<User %r' %self.user
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
    values_of = db.relationship('Stock', backref=db.backref('times', lazy=True))
    def __repr__(self):
        return '<Time %r>' % self.datetime

db.create_all() #don't know if this works but let's try?
db.session.commit()
# class User(db.Model):
#     id =
@app.route('/')
@app.route('/login')
def login():
    return render_template('/login.html')

@app.route('/home')
def home ():
    user = session['user']
    user = user.capitalize()
    return render_template('/home.html', **locals())

@app.route('/create_user')
def create_user():
    return render_template('/create_user.html')

@app.route('/user_info')
def user_info():
    return render_template('/user_info.html', **locals())

@app.route('/insert_user', methods=['POST'])
def insert_user_to_table():
    user = request.form.get('user')
    password = request.form.get('password')
    connection = db.engine.connect()
    result = connection.execute("INSERT INTO user(user, password) " + "VALUES ( \"" + user +"\", \""+password+"\");" )
    connection.close()
    session['user'] = user
    return Response(None)


@app.route('/check_user', methods=['GET'])
def check_user():
    user = request.args.get('user')
    password = request.args.get('password')
    engine = db.engine
    user_exist = engine.execute("SELECT * FROM user WHERE user= \""+user+"\" AND password = \""+password+"\";").first()
    if(user_exist is None):
        invalid_user = {}
        invalid_user['exists'] = False
        return json.dumps(invalid_user)
    valid_user = {}
    valid_user['exists'] = True
    valid_user['user'] = user
    session['user'] = user
    return json.dumps(valid_user)


#continous web scraping -- update at closing
@app.route('/get_stock', methods=['GET', 'POST'])
def get_stock():
    #Get stock name and get SQLAlchemy database
    stock = request.args.get('stock')
    engine = db.engine
    #Start new session for database
    Session = db.create_session(options={'bind':'dest_db_con'})
    sql_session = Session()
    connection = engine.connect()    #set up connection to engine so you can add stocks
    #Try to get data
    values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";").first()
    if(values is not None):
        values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";").fetchall()
        connection.close()
        sql_session.close()
        stock_dict = {}
        for row in values:
            stock_dict[row["datetime"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
        return json.dumps(stock_dict)

    # If it fails, add the data to the db
    try:
        ts = TimeSeries(key='IK798ICZ6BMU2EZM')
        data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
    except:
        raise Exception("Failed to retrieve data from alpha_vantage")
    #Create a new table
    new_table = Stock(name=stock)
    # The only thing we might have to adjust is inserting into the database
    for key in data.keys():
        time = Time(datetime=key, open_=data[key]['1. open'], high=data[key]['2. high'], low=data[key]['3. low'], close=data[key]['4. close'], volume=data[key]['5. volume'])
        new_table.times.append(time)
    sql_session.add(new_table)
    sql_session.commit()
    #Add to the database
    try:
        values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";")
    finally:
        connection.close()
    sql_session.close()
    # Add the data to the db after grabbing it
    stock_dict = {}
    for row in values:
        stock_dict[row["datetime"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
    return json.dumps(stock_dict)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    user = session['user']
    stock = request.form.get('stock')
    connection = db.engine.connect()
    #check if stock and user are already associated
    values = connection.execute('SELECT * FROM users_tracking_stocks WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";').first()
    if(values is not None):
        return Response(None)
    raw_SQL = "INSERT INTO users_tracking_stocks(user, stock) VALUES (\""+user+"\", \""+stock+"\");"
    result = connection.execute(raw_SQL)
    connection.close()
    return Response(None)

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    user = session['user']
    stock = request.form.get('stock')
    connection = db.engine.connect()
    #check if stock and user are already associated
    print('reached 2')
    values = connection.execute('SELECT * FROM users_tracking_stocks WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";').first()
    if(values is None):
        return Response(None)
    print('reached')
    raw_SQL = 'DELETE FROM users_tracking_stocks WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";'
    result = connection.execute(raw_SQL)
    connection.close()
    return Response(None)

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    user = session.get('user')
    connection = db.engine.connect()
    query = 'SELECT * FROM user WHERE user = \''+user+'\';'
    result = connection.execute(query)
    user_dict = {}
    for row in result:      #guaranteed to only be one since users are unique
        user_dict['user'] = row['user']
        user_dict['password'] = row['password']
    return json.dumps(user_dict)

@app.route('/get_user_stocks', methods=['GET'])
def get_user_stocks():
    user = session.get('user')
    connection = db.engine.connect()
    query = 'SELECT * FROM users_tracking_stocks WHERE user = \''+user+'\';'
    result = connection.execute(query)
    user_dict = {}
    for row in result:
        user_dict[row['stock']] = row['stock']
        user_dict[row['stock']] = row['stock']
    return json.dumps(user_dict)

@app.route('/update_user_info', methods=['POST'])
def update_user_info():
    user = session.get('user')
    password = request.form.get('password')
    connection = db.engine.connect()
    query = 'UPDATE user SET password = \''+password+'\' WHERE user = \''+user+'\';'
    result = connection.execute(query)
    return Response(None)

@app.route('/find_volatility', methods=['GET', 'POST'])
def find_volatility():
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    year = int(request.args.get('year'))
    user = session.get('user')

    date = datetime.date(year, month, day).strftime("%Y-%m-%d") 
    print(date)
    connection = db.engine.connect()
    advanced_SQL = """
    SELECT stock AS stock, AVG(close) AS average
    FROM time
    JOIN users_tracking_stocks ON time.stock_name = users_tracking_stocks.stock
    WHERE datetime LIKE '{date}%%' AND user = '{user}'
    GROUP BY time.stock_name;""".format(date=date, user=user)

    result = connection.execute(advanced_SQL)
    avg_price = {}
    for row in result:
        print(row)
        avg_price[row['stock']] = row['average']
    return json.dumps(avg_price)
# This will be the automated webscrapper that updates stock info daily (during low use hours (2 AM?))
@app.route('/most_popular', methods=['GET'])
def most_popular():
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    year = int(request.args.get('year'))
    user = session.get('user')

    date = datetime.date(year, month, day)
    date_str = date.strftime("%Y-%m-%d")
    connection = db.engine.connect()
    
    advanced_SQL = """
    SELECT stock, count, close FROM 
    (SELECT stock, count(*) AS count FROM users_tracking_stocks
    GROUP BY stock) AS s1
    JOIN
    (SELECT stock_name, close FROM time
    WHERE datetime = %s) AS s2
    ON s1.stock = s2.stock_name;
    """
    result = connection.execute(advanced_SQL, '{date} 16:00:00'.format(date=date_str))
    most_popular = {}
    for row in result:
        
        most_popular[row['stock']] = (row['count'], row['close'])
    return json.dumps(most_popular)

@app.route('/update', methods=['GET'])
def update_stock_table():
    return
if __name__ == '__main__':
    app.run()
