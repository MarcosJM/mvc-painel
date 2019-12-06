from app import app
from flask import render_template, request, redirect, url_for, session, flash, json

class Main:
    def __init__(self):
        @app.route("/")
        def homepage():
            return render_template("index.html")
