# CS411_MarketData


# Notes
Welcome to Stock Squirrel! We're interested in developing real time analytics of stocks utilizing MySQL, all run on a nice Flask server.

# Dependencies
Since we're mid development, in order to run this, please install the following:
1) Flask
2) flask_sqlalchemy
3) Flask-Session
4) MySQL
5) alpha_vantage
6) pandas
7) numpy
8) matplotlib
9) git

All these have official documentation for installation, according to your operating system. I'd double check if you have them before going through the hassle since these are all fairly common.

# Setting Up MySQL
Since we will all be using the same code, please adjust your MySQL server with the following instructions and it should work/be compatible with the DBMS as currently implement:

1) In terminal, run "mysql -u root -p" and enter your password
2) Then we will create a new user called "cs411proj" with the password "Password_123"; to do so, follow the instructions at https://www.a2hosting.com/kb/developer-corner/mysql/managing-mysql-databases-and-users-from-the-command-line
3) After you have created the user, you should create a database within that user called 'stock_data'

For debugging purposes, use the command line to run mysql and see if you have actually affected the Users (use SELECT User FROM mysql.Users;) and the databases.
# Using Flask
Once you have Flask installed, to run it, do the following from terminal:
1) Type 'export FLASK_APP=flask_server.py'
2) Then 'export FLASK_ENV=development'
3) Then 'flask run'
4) After that, lots of information should appear. The only thing relevant here is the 'Running on ...' which should be followed by something like 'http://127.0.0.1:5000/'. If for some reason that port is taken, go to Flask docs to figure out how to manually change the associated port.
5) Finally, use the server address above and type it into your browser of choice (I'd recommend Chrome or Firefox personally).
