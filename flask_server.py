from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__, template_folder='templates')

@app.route('/')
@app.route('/home')
def home ():
    return render_template('/home.html')
