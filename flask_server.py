from flask import Flask, render_template, request, Response, session
from us_treasury_scrap import web_scrap_treasury
# from numpy import linalg as la
from sim_run import avgco_simopt
import json, datetime, atexit, time
import pandas as pd, pandas.io.sql as psql
import numpy as np
import matplotlib.pyplot as plt
from scraper import Scrape
app = Flask(__name__, template_folder='templates')
app.secret_key = '99qVu2YPjy5ss0Z66Igj'

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
#Get stock data API
from alpha_vantage.timeseries import TimeSeries     #If something goes wrong with stock data stuff, it's here


#Note: On the actual webserver, will need to CREATE USER with full privileges
# After creating the user, then create database
# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="cs411proj",
#     password="Password_123",
#     hostname="cs411proj.mysql.pythonanywhere-services.com",
#     databasename="cs411proj$stock_data"
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://cs411proj:Password_123@localhost/stock_data" #change to mySQL later
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

metadata = db.metadata

users_tracking_stocks = db.Table('users_tracking_stocks',
    db.Column('user', db.String(100), db.ForeignKey('user.user'), primary_key=True),
    db.Column('stock', db.String(5), db.ForeignKey('stock.name'), primary_key=True),
    db.Column('number_of', db.Integer)
)

class User(db.Model):
    user = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))
    tot_money = db.Column(db.Float)
    avail_money = db.Column(db.Float)
    invest_money = db.Column(db.Float)
    tracked_stocks = db.relationship('Stock', secondary=users_tracking_stocks, lazy='subquery',
                    backref=db.backref('users', lazy=True))
    def __repr__(self):
        return '<User %r>' %self.user
class Stock(db.Model):
    name = db.Column(db.String(5), primary_key=True)
    number_of = db.Column(db.Integer)
    def __repr__(self):
        return '<Stock %r>' % self.name
class Time(db.Model):
    datetime = db.Column(db.String(30), primary_key=True)
    open_ = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
    stock_name = db.Column(db.String(5), db.ForeignKey('stock.name'), primary_key=True, nullable=False)
    values_of = db.relationship('Stock', backref=db.backref('times', lazy=True, cascade='all, delete-orphan'))
    def __repr__(self):
        return '<Time id:{0}, stock_name:{1}>'.format(self.datetime, self.stock_name)

class Daily(db.Model):
    day = db.Column(db.String(15), primary_key=True)
    open_ = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
    stock_name = db.Column(db.String(5), db.ForeignKey('stock.name'), primary_key=True, nullable=False)
    values_of = db.relationship('Stock', backref=db.backref('days', lazy=True, cascade='all, delete-orphan'))
    def __repr__(self):
        return '<Daily %r>' % self.datetime

db.create_all() #don't know if this works but let's try?
db.session.commit()
# class User(db.Model):
#     id =

# Begin webscraping
# sss = Scrape()

@app.route('/')
@app.route('/login')
def login():
    return render_template('/login.html')

@app.route('/home')
def home ():
    user = session['user']
    user = user.capitalize()
    return render_template('/home.html', **locals())

@app.route('/register')
def register():
    return render_template('/register.html')

@app.route('/user_info')
def user_info():
    return render_template('/user_info.html', **locals())



@app.route('/insert_user', methods=['POST'])
def insert_user_to_table():
    username = request.form.get('username')
    password = request.form.get('password')
    connection = db.engine.connect()
    user_exist = connection.execute("SELECT * FROM user WHERE user = \"" + username + "\";").first()
    if(user_exist):
         connection.close()
         return json.dumps({'duplicate':True})
    connection.execute("INSERT INTO user(user, password) " + "VALUES ( \"" + username +"\", \""+password+"\");" )
    connection.close()
    session['user'] = username
    return json.dumps({'duplicate':False})

@app.route('/check_user', methods=['POST'])
def check_user():
    username = request.form.get('username')
    password = request.form.get('password')
    engine = db.engine
    user_exist = engine.execute("SELECT * FROM user WHERE user= \""+username+"\" AND password = \""+password+"\";").first()
    if(user_exist):
        return json.dumps({'info':True})
    return json.dumps({'info':False})

@app.route('/user_session', methods=['GET'])
def user_sesssion():
    user = request.args.get('username')
    session['user'] = user
    return Response(None)


#continous web scraping -- update at closing
@app.route('/get_stock', methods=['GET'])
def get_stock():
    #Get stock name and get SQLAlchemy database
    stock = request.args.get('stock')
    stock = stock.upper()
    engine = db.engine
    #Start new session for database
    Session = db.create_session(options={'bind':'dest_db_con'})
    sql_session = Session()
    connection = engine.connect()    #set up connection to engine so you can add stocks
    #Try to get data
    values = engine.execute("SELECT * FROM time WHERE stock_name=\""+stock+"\";").first()
    if(values is not None):
        values = engine.execute("SELECT * FROM daily WHERE stock_name=\""+stock+"\";").fetchall()
        connection.close()
        sql_session.close()
        stock_dict = {}
        for row in values:
            stock_dict[row["day"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
        return json.dumps(stock_dict)

    # If it fails, add the data to the db
    try:
        ts = TimeSeries(key='IK798ICZ6BMU2EZM')
        data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
        day_data, day_meta_data = ts.get_daily(symbol=stock, outputsize='full')
    except:
        connection.close()
        raise Exception("Failed to retrieve data from alpha_vantage")
    #Create a new table
    new_table = Stock(name=stock)

    #if (stock not in sss.stock_list):
    #    sss.stock_list.append(stock)
    #    sss.collect_data(len(sss.stock_list)-1)

    # The only thing we might have to adjust is inserting into the database
    for key in data.keys():
        time = Time(datetime=key, open_=data[key]['1. open'], high=data[key]['2. high'], low=data[key]['3. low'], close=data[key]['4. close'], volume=data[key]['5. volume'])
        new_table.times.append(time)
    for key in day_data.keys():
        day = Daily(day=key, open_=day_data[key]['1. open'], high=day_data[key]['2. high'], low=day_data[key]['3. low'], close=day_data[key]['4. close'], volume=day_data[key]['5. volume'])
        new_table.days.append(day)
    sql_session.add(new_table)
    sql_session.commit()
    #Add to the database
    try:
        values = engine.execute("SELECT * FROM daily WHERE stock_name=\""+stock+"\";")
    finally:
        connection.close()
    sql_session.close()
    # Add the data to the db after grabbing it
    stock_dict = {}
    for row in values:
        stock_dict[row["day"]] = (float(row['open_']), float(row['high']), float(row['low']), float(row['close']), float(row['volume']))
    return json.dumps(stock_dict)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    user = session['user']
    stock = request.form.get('stock')
    number_of = request.form.get('number_of')
    connection = db.engine.connect()
    #check if stock and user are already associated
    values = connection.execute('SELECT * FROM users_tracking_stocks WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";').first()
    if(values is not None):
        result = connection.execute('SELECT number_of FROM users_tracking_stocks WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";')
        tot = int(number_of)
        print(type(tot))
        for row in result:  #guaranteed to be only one result; TRICKESY BAGGINS LOOP @ Golem
            tot = tot + int(row['number_of'])
        if (tot <= 0):
            return Response(None)
        raw_SQL = "UPDATE users_tracking_stocks SET number_of = \'"+str(tot)+'\' WHERE user = \'' + user + '\' AND stock=\"'+stock+'\";'
        result = connection.execute(raw_SQL)
        connection.close()
        return Response(None)
    raw_SQL = "INSERT INTO users_tracking_stocks(user, stock, number_of) VALUES (\""+user+"\", \""+stock+"\", \""+number_of+"\");"
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
        connection.close()
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
        user_dict[row['stock']] = (row['stock'], row['number_of'])
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

@app.route('/update', methods=['POST'])
def update():
    #Get value of today
    now = datetime.datetime.now()
    #Convert today into acceptable datetime string
    date = datetime.date(now.year, now.month, now.day-1).strftime("%Y-%m-%d")
    #Start a session in sqlalchemy so data we write is saved
    Session = db.create_session(options={'bind':'dest_db_con'})
    sql_session = Session()
    # connection variable provides bridge between Python and SQL
    connection = db.engine.connect()
    #For stocks added today, deletes all records where time is today since update will update all stocks with values of today
    result = connection.execute("""
    DELETE FROM time WHERE datetime LIKE '{date}%%'
    """.format(date=date))
    #SQL query returns all stocks not added today
    result = connection.execute("SELECT name FROM stock")
    stocks = []
    for row in result:
        stocks.append(row["name"])
    for stock in stocks:
        print(stock)
        try:
            ts = TimeSeries(key='IK798ICZ6BMU2EZM')
            data, meta_data = ts.get_intraday(symbol=stock, interval='1min', outputsize='full') #get stock prices minute by minute
            day_data, day_meta_data = ts.get_daily(symbol=stock, outputsize='full') #Get daily stock prices of last 100 days
        except:
            # raise Exception("Failed to retrieve data from alpha_vantage")
            print(stock + " failed")
            continue
        for key in data.keys():
            #Create a new Time record then add it to the stock
            temp_key = key[:10]
            time_ = connection.execute('SELECT * FROM time WHERE stock_name=\''+stock+'\' AND datetime=\''+temp_key+'\'').first()
            if(time_ is not None):
                continue
            # if(date not in key):
            #     continue
            connection.execute('INSERT INTO time(datetime, open_, high, low, close, volume, stock_name) VALUES (\''+temp_key+'\', '+data[key]['1. open']+', '+data[key]['2. high']+', '+data[key]['3. low']+', '+data[key]['4. close']+', '+data[key]['5. volume']+', \''+stock+'\');')
        for key in day_data.keys():
            #Create a new Daily record then add it othe stock
            temp_key = key[:10]
            daily_ = connection.execute('SELECT * FROM daily WHERE stock_name=\''+stock+'\' AND day=\''+temp_key+'\'').first()
            if(daily_ is not None):
                continue
            # if(date not in key):
            #     continue
            connection.execute('INSERT INTO daily(day, open_, high, low, close, volume, stock_name) VALUES (\''+temp_key+'\', '+day_data[key]['1. open']+', '+day_data[key]['2. high']+', '+day_data[key]['3. low']+', '+day_data[key]['4. close']+', '+day_data[key]['5. volume']+', \''+stock+'\');')
        time.sleep(30)

    #         day = Daily(day=key, open_=day_data[key]['1. open'], high=day_data[key]['2. high'], low=day_data[key]['3. low'], close=day_data[key]['4. close'], volume=day_data[key]['5. volume'])

    sql_session.commit()    #commit the new info
    connection.close()
    return Response(None)   #Not getting any info for server, so we return it

@app.route('/portfolio_calculator', methods=['GET'])
def portfolio_calculator():
    now = datetime.datetime.now()
    weekday = datetime.date(now.year, now.month, now.day).weekday()
    print(weekday)
    if(weekday == 0 or weekday == 6):
        if(weekday == 6):
            date = datetime.date(now.year, now.month, now.day-2).strftime("%Y-%m-%d")
        else:
            date = datetime.date(now.year, now.month, now.day-3).strftime("%Y-%m-%d")
    else:
        date = datetime.date(now.year, now.month, now.day-1).strftime("%Y-%m-%d")
    print(date)
    year5_ago = datetime.date(now.year-5, now.month, now.day).strftime("%Y-%m-%d")
    year3_ago = datetime.date(now.year-3, now.month, now.day).strftime("%Y-%m-%d")
    year1_ago_weekday = datetime.date(now.year-1, now.month, now.day).weekday()
    print(year1_ago_weekday)
    if(year1_ago_weekday == 5 or year1_ago_weekday == 6):
        if(year1_ago_weekday == 5):
            year1_ago = datetime.date(now.year-1, now.month, now.day-1).strftime("%Y-%m-%d")
        else:
            year1_ago = datetime.date(now.year-1, now.month, now.day-2).strftime("%Y-%m-%d")
    else:
        year1_ago = datetime.date(now.year-1, now.month, now.day).strftime("%Y-%m-%d")
    print(year1_ago)

    user = session.get('user')
    info_dict = {}
    connection = db.engine.connect()
    #First thing is to figure out the average return
    sql_query = """
    SELECT t1.stock_name AS stock, AVG((t1.open_ - t2.open_)/t2.open_) AS average_return
    FROM daily as t1, daily as t2
    WHERE (t1.day BETWEEN '{year1_ago}' AND '{today}') AND
     t1.stock_name = t2.stock_name AND datediff(t1.day, t2.day) = 1 AND
     t1.stock_name IN (
        SELECT stock
        FROM users_tracking_stocks
        WHERE user = '{user}'
        )
    GROUP BY t1.stock_name;
    """.format(user=user, year1_ago=year1_ago, today=date)
    result = connection.execute(sql_query)
    for row in result:
        info_dict[row['stock']] = []
        info_dict[row['stock']].append(row['average_return'])
    #Then calculate the variance and standard deviation over the same period
    variance = """
    SELECT d.stock_name as stock, AVG(d.open_) as average, VARIANCE(d.open_) as variance, STDDEV(d.open_) as deviation
    FROM daily as d
    WHERE (d.day BETWEEN '{year1_ago}' AND '{today}') AND
    d.stock_name IN (
       SELECT stock
       FROM users_tracking_stocks
       WHERE user = '{user}'
       )
    GROUP BY d.stock_name;
     """.format(user=user, year1_ago=year1_ago, today=date)
    var_result = connection.execute(variance)
    for row in var_result:
        info_dict[row['stock']].append(float(row['average']))
        info_dict[row['stock']].append(float(row['variance']))
        info_dict[row['stock']].append(float(row['deviation']))

    #Finding the covariance; SQL sucks to do stats, so converting query into pandas dataframe
    values = """
    SELECT d.day as day, d.stock_name as stock, d.open_ as open
    FROM daily as d
    WHERE (d.day BETWEEN '{year5_ago}' AND '{today}') AND d.stock_name IN (
        SELECT stock
        FROM users_tracking_stocks
        WHERE user = '{user}'
        ) OR d.stock_name='SPY'
    """.format(user=user, year5_ago=year5_ago, today=date)
    df = psql.read_sql(values, con=connection, columns=['day', 'stock', 'open'])
    df['day'] = pd.to_datetime(df['day'])
    df = df.loc[(df['day']>=year3_ago) & (df['day'] <= date)]
    #Gives mean and every stock the user is tracking
    means = df.groupby('stock', sort=False, group_keys=True).agg({'open':np.mean})
    #Pivots table so each stock gets it's own column and then we can get covariance
    stock_pivot = pd.pivot_table(df, index=['day'], columns=['stock'])
    for i in means.index:
        # stock_pivot[i+'_return'] = stock_pivot[('open', i)].apply(lambda x: (x.shift(-1) - x) / x)
        stock_pivot[('return', i)] = (stock_pivot[('open', i)].shift(-1) - stock_pivot[('open', i)]) / stock_pivot[('open', i)]
    covariance = stock_pivot.cov()
    risk_free_return = float(web_scrap_treasury()) / 100
    print(date)
    print(year1_ago)
    market_return = float((stock_pivot.loc[date, ('open', 'SPY')] - stock_pivot.loc[year1_ago, ('open', 'SPY')]) / stock_pivot.loc[year1_ago, ('open', 'SPY')])
    for i in means.index:
        print(i)
        if(i == 'SPY'):
            continue
        info_dict[i].append(covariance[('return', i)][('return', 'SPY')])
        beta = float(info_dict[i][4] / covariance[('return', 'SPY')][('return', 'SPY')])
        info_dict[i].append(beta)
        # calculate alpha
        realized_return = float((stock_pivot.loc[date, ('open', i)] - stock_pivot.loc[year1_ago, ('open', i)]) / stock_pivot.loc[year1_ago, ('open', i)])
        # print(str(realized_return) + " - "+str(risk_free_return)+" - "+str(beta)+" * ("+str(market_return)+" - "+str(risk_free_return)+")")
        alpha = realized_return - risk_free_return - beta*(market_return-risk_free_return)
        # print(alpha)
        info_dict[i].append(alpha)
    number_of = """
    SELECT number_of, stock
    FROM users_tracking_stocks
    WHERE user='{user}'
    """.format(user=user)
    finding_portfolio_distributions = connection.execute(number_of)
    # portfolio_value = 0
    # var = {}
    # # each element in var: [# of shares, total dollar amount, z-score for 95% confidence interval]
    # for row in finding_portfolio_distributions:
    #     var[row['stock']] = []
    #     var[row['stock']].append(row['stock'])
    #     var[row['stock']].append(float(row['number_of']) * float(stock_pivot.loc[date, ('open', row['stock'])]))
    #     # Using a standard normal table, I found the z value for 95% confidence is 1.96, which my stats major friend says is the standard
    #     z_score = info_dict[row['stock']][0] + 1.96*info_dict[row['stock']][1]
    #     var[row['stock']].append(z_score)
    #     portfolio_value += var[row['stock']][1]
    # eigvalues, eigvectors = la.eig(covariance)
    # print(eigvalues)
    # print(portfolio_value)
    for row in finding_portfolio_distributions:
        stock = row['stock']
        number_of = int(row['number_of'])
        print(date)
        price = float(stock_pivot.loc[date, ('open', row['stock'])])
        print(price)
        print(year1_ago)
        last_year_price = float(stock_pivot.loc[year1_ago, ('open', row['stock'])])
        print(last_year_price)
        value = number_of * price
        realized_return = float((stock_pivot.loc[date, ('open', stock)] - stock_pivot.loc[year1_ago, ('open', stock)]) / stock_pivot.loc[year1_ago, ('open', stock)])
        print(realized_return)
        individual_var = abs(((realized_return*price )- (1.96 * info_dict[stock][3])) * number_of)
        print(individual_var)
        info_dict[stock].append(individual_var)
    connection.close()
    return json.dumps(info_dict)

@atexit.register
def clean_up():
    session.clear()

if __name__ == '__main__':
    app.run()


@app.route('/simulation', methods=['GET'])
def simulation():
    stock = request.args.get('stock')
    lavg = request.args.get('lavg')
    savg = request.args.get('savg')
    avgco_simopt(stock, int(lavg), int(savg))
    return Response(None)