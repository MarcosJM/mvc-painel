from app import app
# from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from app.models.deputy_history import Deputy
import app.utils as utils
from itertools import chain
from collections import Counter
import numpy as np
from datetime import date


class DeputyInfo:

    def __init__(self, id_register):
        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_authors = dbConn.build_collection('autoria')
        self._collection_expenses = dbConn.build_collection('gasto')
        self.deputy = self._set_up_deputy(id_register)

    def _set_up_deputy(self, id_register):
        """ recover all information from the last legislature"""
        all_party_affiliations = []
        last_result = {}
        query = {'ideCadastro': str(id_register)}
        result = list(self._collection_deputy.find(query))

        if len(result) > 0:  # the deputy exists in the DB

            if len(result) > 1:  # more than one register (legislature) for the deputy
                for item in result:
                    if item['filiacoesPartidarias'] is not None:
                        all_party_affiliations.append(item['filiacoesPartidarias']['filiacaoPartidaria'])

                last_result = sorted(result, key=lambda k: int(k['numLegislatura']))[-1]  # most recent info

            elif len(result) == 1:  # just one register (legislature) for the deputy
                last_result = result[0]
                all_party_affiliations = last_result['filiacoesPartidarias']

            all_party_affiliations_dict = {'filiacaoPartidaria': all_party_affiliations}

            deputy_instance = Deputy(last_result['urlFoto'], last_result['ideCadastro'],
                                     last_result['nomeParlamentarAtual'], last_result['nomeCivil'],
                                     last_result['sexo'], last_result['dataNascimento'], last_result['dataFalecimento'],
                                     last_result['nomeProfissao'], last_result['escolaridade'], last_result['email'],
                                     last_result['ufRepresentacaoAtual'], last_result['partidoAtual'],
                                     last_result['situacaoNaLegislaturaAtual'], all_party_affiliations_dict,
                                     last_result['periodosExercicio'])

            return deputy_instance
        else:
            return None

    def getDeputyPersonalInfo(self):
        return self.deputy

    def getDeputyDatesExercise(self, legislature_number=56):
        """ Return an array with tuples of dates corresponding to the deputy's active periods of exercise"""

        query = {'$and': [{'ideCadastro': str(self.deputy.id_register)},
                          {'numLegislatura': str(legislature_number)}]}
        query_field = {'periodosExercicio': 1, '_id': 0}

        result = next(self._collection_deputy.find(query, query_field), None)

        if result is not None:
            period_in_exercise = result['periodosExercicio']['periodoExercicio']

            if isinstance(period_in_exercise, dict):
                period_in_exercise = [period_in_exercise]

            dates_in_exercise = [(item['dataInicio'], item['dataFim']) if item['dataFim'] else (item['dataInicio'], '{}/{}/{}'.format(str(date.today().day),str(date.today().month),str(date.today().year))) for item in period_in_exercise]
            return dates_in_exercise
        else:
            return None

    def getPresenceInEvent(self, event_collection_name, presence_key_name, date_key_name, legislature_number=56):
        """ Given a event collection name and which key is used to identify the presences and the date,
        returns a dictionary w/ the total n of events, the presence of the deputy and the median presence for that
        event (given the deputy's period of exercise)"""
        try:
            # ======= periods of active exercise
            dates_in_exercise = self.getDeputyDatesExercise(legislature_number)

            # ======= recover all events
            query_event = {'legislatura': int(legislature_number)}
            all_events = list(dbConn.build_collection(event_collection_name).find(query_event))

            if (dates_in_exercise is not None) & (len(all_events) > 0):

                # filter all events by the period of availability of the deputy
                filtered_events = utils.get_records_by_intervals(all_events, dates_in_exercise, date_key_name)
                total_num_events = len(filtered_events)

                if total_num_events > 0:
                    presences = list(chain.from_iterable([event[presence_key_name] for event in filtered_events]))
                    presences_by_deputy = Counter(presences)
                    mean_presence = np.mean(list(presences_by_deputy.values()))
                    deputy_presence = presences_by_deputy[self.deputy.id_register]
                    return {'presence': deputy_presence, 'mean-presence': mean_presence, 'all-events': total_num_events}
                else:
                    print('0 events')
                    return None
            else:
                print('Events or period in exercise not found')
                return None
        except Exception as e:
            print(e)

    def getPropositionsAuthored(self, legislature_number=56):
        """ Returns a dictionary w/ the total n of authorings, the authorings of the deputy and the median authorings
         (given the deputy's period of exercise) """
        try:
            # ======= periods of active exercise
            dates_in_exercise = self.getDeputyDatesExercise(legislature_number)

            # ======= recover all authors
            query_authors = {'legislatura': int(legislature_number)}
            all_authors = list(self._collection_authors.find(query_authors))

            if (dates_in_exercise is not None) & (len(all_authors) > 0):

                # filter all events by the period of availability of the deputy
                filtered_events = utils.get_records_by_intervals(all_authors, dates_in_exercise, 'dataApresentacao')
                total_num_events = len(filtered_events)

                if total_num_events > 0:
                    all_propositions_authors = [authoring['idDeputadoAutor'] for authoring in filtered_events]
                    authoring_by_deputy = Counter(all_propositions_authors)
                    median_authoring = np.median(list(authoring_by_deputy.values()))
                    deputy_authoring = authoring_by_deputy[float(str(self.deputy.id_register)+'.0')]

                    return {'authoring': deputy_authoring, 'median-authoring': median_authoring,
                            'all-authorings': total_num_events}
                else:
                    print('0 events')
                    return None
            else:
                print('Events or period in exercise not found')
                return None

        except Exception as e:
            print(e)

    def getExpenses(self, year_number=2018):
        """ Return two arrays, one with the ranges (max, min) for each month given the year and the
         date (1/m/y) as timestamp; the other with all the values spent by the deputy for each month."""
        try:
            pipeline = [{'$group': {'_id': {'legislatura': "$codLegislatura", 'ano': "$numAno", 'mes': "$numMes",
                                            'deputado': "$ideCadastro"}, 'totalGasto': {'$sum': "$vlrLiquido"}}},
                        {'$match': {"_id.ano": year_number}},
                        {'$facet': {
                            "intervalos": [{'$group': {'_id': {'mes': "$_id.mes", 'ano': "$_id.ano"},
                                                       'gastoMaximo': {'$max': "$totalGasto"},
                                                       'gastoMinimo': {'$min': "$totalGasto"}}},
                                           {'$sort': {"_id.mes": 1}}],
                            "gastosDeputado": [{'$match': {"_id.deputado": float(str(self.deputy.id_register)+'.0')}},
                                               {'$group': {'_id': {'mes': "$_id.mes", 'ano': "$_id.ano",
                                                                   'deputado': "$_id.deputado"},
                                                           'valorGasto': {'$push': "$totalGasto"}}},
                                               {'$sort': {"_id.mes": 1}}
                                               ]}}]
            result = next(self._collection_expenses.aggregate(pipeline), None)

            if result is not None:
                ranges = [[utils.date2timestamp('1/'+str(item['_id']['mes'])+'/'+str(item['_id']['ano'])),
                           item['gastoMinimo'], item['gastoMaximo']] for item in result['intervalos']]

                deputy_expenses = [[utils.date2timestamp('1/'+str(item['_id']['mes'])+'/'+str(item['_id']['ano'])),
                                    item['valorGasto'][0]] for item in result['gastosDeputado']]

                if (len(ranges) > 0) & (len(deputy_expenses) > 0):
                    return {'ranges': ranges, 'deputy_expenses': deputy_expenses}
                else:
                    print('No ranges or no deputy expenses.')
                    return None
            else:
                print('No result found in the DB.')
                return None

        except Exception as e:
            print(e)

    def getExpensesCategory(self, year_number=2018):
        """ Return the expense category and its value spent by the deputy in a year """
        try:
            pipeline = [{'$match': {'$and': [{"ideCadastro": float(str(self.deputy.id_register))}, {"numAno": year_number}]}},
                        {'$group': {'_id': {'legislatura': "$codLegislatura", 'ano': "$numAno", 'deputado': "$ideCadastro",
                                            'categoria': "$txtDescricao"}, 'totalGasto': {'$sum': "$vlrLiquido"}}},
                        {'$sort': {"_id.ano": 1}}]

            result = list(self._collection_expenses.aggregate(pipeline))

            if len(result) > 0:
                categories = [{'name': item["_id"]["categoria"], 'value': item["totalGasto"]} for item in result]
                return categories
            else:
                return None
        except Exception as e:
            print(e)
