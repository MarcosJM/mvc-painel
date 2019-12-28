from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
# =================================================


class ScoreSystem:
    def __init__(self):

        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_expense = dbConn.build_collection('gasto')

        # @app.route("/professions", methods=['POST'])
        # def calculateIndicatorThreeScore(legislature_number='56'):


