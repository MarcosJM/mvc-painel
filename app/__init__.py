from flask import Flask, render_template, request, redirect, url_for
from server import Db
from app.routes import Route

app = Flask(__name__, static_folder="static")

dbConn = Db('127.0.0.1', 27017, 'dep_db')

# load routes
Route()

