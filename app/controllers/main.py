from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app.models.deputy_history import DeputyHistory

class Main():
    def __init__(self):
        @app.route("/")
        def homepage():
            deputy = DeputyHistory('74847').getLegislatureData('53')
            return render_template("index.html", deputy=deputy)
