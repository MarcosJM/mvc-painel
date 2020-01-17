from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from collections import Counter
from itertools import chain
from app.utils import *
# =================================================


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
        def getTotalSpentChartData(legislature_number=55):
            query = [{'$match': {'codLegislatura': legislature_number}},
                     {'$group': {'_id': 0, 'sum': {'$sum': '$vlrLiquido'}}}]
            result = list(self._collection_expense.aggregate(query))
            if len(result) > 0:
                result = result[0]['sum']
                result_fmt = {'data': format_number(result)}
                return result_fmt
            else:
                return None

        @app.route("/values_by_state", methods=['POST'])
        def getValuesByState():
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(self._collection_uf.find({}, query))
            result_fmt = [['br-'+item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': result_fmt}

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
