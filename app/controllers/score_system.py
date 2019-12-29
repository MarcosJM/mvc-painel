from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
# =================================================


class ScoreSystem:
    def __init__(self):

        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_expense = dbConn.build_collection('gasto')
        self._collection_public_audience = dbConn.build_collection('reuniao_audiencia_publica')

        @app.route("/score_indicator_three", methods=['POST'])
        def calculateIndicatorThreeScore(deputy_id, legislature_number=56):
            """
            calculate the transparent indicator of the deputy final score
            by analysing the public audiences attended.
            :param deputy_id: which deputy
            :param legislature_number: to filter
            :return: score (0-10)
            """
            query = {'legislatura': legislature_number}
            result = self._collection_public_audience.count_documents(query)
            total_number_of_public_audience = result

            query2 = dict(query, **{'presencas': deputy_id})
            result2 = self._collection_public_audience.count_documents(query2)
            total_number_of_public_audience_deputy = result2

            score = (total_number_of_public_audience_deputy/total_number_of_public_audience)*10
            return score
