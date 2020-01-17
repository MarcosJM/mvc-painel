from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from collections import Counter
from itertools import chain
from app.utils import LEGISLATURES
import math
from app.utils import *
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
        def getProfessionsChartData():  # TODO: create a constant for legs numbers
            allProfessionData= {}
            for legislature in LEGISLATURES:
                query_search = {'numLegislatura': str(legislature)}
                query_field = {'nomeProfissao': 1, '_id': 0}
                result = list(self._collection_deputy.find(query_search, query_field))
                if result:
                    result_values = [list(map(str.strip, item['nomeProfissao'].split(','))) if item['nomeProfissao'] is not None
                                     else ["Não informada"] for item in result]
                    result_values_merged = list(chain.from_iterable(result_values))
                    result_counter = dict(Counter(result_values_merged))
                    result_counter_fmt = {'data': [{'name': key, 'value': value} for key, value in result_counter.items()]}
                    allProfessionData.update({str(legislature): result_counter_fmt['data']})
            return {'professionData': allProfessionData}

        @app.route("/schooling", methods=['POST'])
        def getSchoolingChartData():  # TODO: create a constant for legs numbers
            allSchoolingData = {}
            for legislature in LEGISLATURES:
                query_search = {'numLegislatura': str(legislature)}
                query_field = {'escolaridade': 1, '_id': 0}
                result = list(self._collection_deputy.find(query_search, query_field))
                if result:
                    result_values = [item['escolaridade'] if item['escolaridade'] is not None else "Não informado" for
                                     item in result]
                    result_counter = dict(Counter(result_values))
                    result_counter_sorted = {key: value for key, value in sorted(result_counter.items(),
                                                                                 key=lambda item: item[1], reverse=True)}
                    result_counter_fmt = {'data': [[key, value] for key, value in result_counter_sorted.items()]}
                    allSchoolingData.update({str(legislature): result_counter_fmt['data']})
            return {'schoolingData': allSchoolingData}
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
            return {'data': {'56': result_fmt}}

        @app.route("/deputies_quantity", methods=['POST'])
        def getDeputiesQuantity():
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(self._collection_uf.find({}, query))
            result_fmt = [['br-' + item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': result_fmt}

        @app.route("/party_representation", methods=['POST'])
        def getPartiesRepresentation(legislature_number=55):
            query = [{'$match': {'numLegislatura': str(legislature_number)}},
                     {'$group': {'_id': '$partidoAtual.sigla', 'count': {'$sum': 1}}}]
            result = list(self._collection_deputy.aggregate(query))
            if len(result) > 0:
                result_fmt = {'data': [[item['_id'], item['count'], item['_id'], color_party(item['_id'])]
                                       for item in result]}
                return result_fmt
            else:
                print('No query results.')
                return None
