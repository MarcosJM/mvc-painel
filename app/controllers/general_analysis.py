from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from collections import Counter
from itertools import chain
from app.utils import LEGISLATURES
import math
# =================================================


# function for formatting big numbers
def format_number(number, units=['', 'K', 'M', 'G', 'T', 'P']):
    k = 1000.0
    magnitude = int(math.log10(number) // 3)
    return '%.2f%s' % (number / k**magnitude, units[magnitude])


class GeneralAnalysis:
    def __init__(self):

        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_uf = dbConn.build_collection('uf')
        self._collection_expense = dbConn.build_collection('gasto')

        @app.route("/professions", methods=['POST'])
        def getProfessionsChartData(legislature_number='56'):  # TODO: create a constant for legs numbers
            query_search = {'numLegislatura': legislature_number}
            query_field = {'nomeProfissao': 1, '_id': 0}
            result = list(self._collection_deputy.find(query_search, query_field))

            result_values = [list(map(str.strip, item['nomeProfissao'].split(','))) if item['nomeProfissao'] is not None
                             else ["Não informada"] for item in result]
            result_values_merged = list(chain.from_iterable(result_values))
            result_counter = dict(Counter(result_values_merged))
            result_counter_fmt = {'data': [{'name': key, 'value': value} for key, value in result_counter.items()]}
            return result_counter_fmt

        @app.route("/schooling", methods=['POST'])
        def getSchoolingChartData(legislature_number='56'):  # TODO: create a constant for legs numbers
            query_search = {'numLegislatura': legislature_number}
            query_field = {'escolaridade': 1, '_id': 0}
            result = list(self._collection_deputy.find(query_search, query_field))

            result_values = [item['escolaridade'] if item['escolaridade'] is not None else "Não informado" for
                             item in result]
            result_counter = dict(Counter(result_values))
            result_counter_sorted = {key: value for key, value in sorted(result_counter.items(),
                                                                         key=lambda item: item[1], reverse=True)}
            result_counter_fmt = {'data': [[key, value] for key, value in result_counter_sorted.items()]}
            return result_counter_fmt

        @app.route("/total_spent", methods=['POST'])
        def getTotalSpentChartData():
            allSpent = {}
            for legislature in LEGISLATURES:
                query = [{'$match': {'codLegislatura': legislature}},
                         {'$group': {'_id': 0, 'sum': {'$sum': '$vlrLiquido'}}}]
                result = list(self._collection_expense.aggregate(query))
                if result:
                    result = result[0]['sum']
                    allSpent.update({legislature: format_number(result)})
            return {'allSpent': allSpent}

        @app.route("/values_by_state", methods=['POST'])
        def getValuesByState():
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(self._collection_uf.find({}, query))
            result_fmt = [['br-'+item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': {'55': result_fmt}}

        @app.route("/deputies_quantity", methods=['POST'])
        def getDeputiesQuantity():
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(self._collection_uf.find({}, query))
            result_fmt = [['br-' + item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': result_fmt}
