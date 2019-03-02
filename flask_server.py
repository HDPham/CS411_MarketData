from flask import Flask, flash, redirect, render_template, request, session, abort
import random

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home ():
    return render_template('/home.html')
