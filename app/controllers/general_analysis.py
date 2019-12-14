from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from collections import Counter
from itertools import chain


class GeneralAnalysis:
    def __init__(self):

        self._collection_deputy = 'deputado'  # collection to connect
        self._collection_uf = 'uf'

        @app.route("/professions", methods=['POST'])
        def getProfessionsChartData(legislature_number='56'):  # TODO: create a constant for legs numbers
            query_search = {'numLegislatura': legislature_number}
            query_field = {'nomeProfissao': 1, '_id': 0}
            result = list(dbConn.build_collection(self._collection_deputy).find(query_search, query_field))

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
            result = list(dbConn.build_collection(self._collection_deputy).find(query_search, query_field))

            result_values = [item['escolaridade'] if item['escolaridade'] is not None else "Não informado" for
                             item in result]
            result_counter = dict(Counter(result_values))
            result_counter_sorted = {key: value for key, value in sorted(result_counter.items(),
                                                                         key=lambda item: item[1], reverse=True)}
            result_counter_fmt = {'data': [[key, value] for key, value in result_counter_sorted.items()]}
            return result_counter_fmt

        @app.route("/values_by_state", methods=['POST'])
        def getValuesByState():
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(dbConn.build_collection(self._collection_uf).find({}, query))
            result_fmt = [['br-'+item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': result_fmt}

        @app.route("/deputies_quantity", methods=['POST'])
        def getDeputiesQuantity(legislature_number='56'):
            query = {'sigla': 1, 'cotaParlamentar': 1, '_id': 0}
            result = list(dbConn.build_collection(self._collection_uf).find({}, query))
            result_fmt = [['br-' + item['sigla'].lower(), item['cotaParlamentar']] for item in result]
            return {'data': result_fmt}
