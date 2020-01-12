from app import app
# from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from app.models.deputy_history import Deputy
import app.utils as utils
from itertools import chain
from collections import Counter
import numpy as np


class DeputyInfo:

    def __init__(self, id_register):
        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_authors = dbConn.build_collection('autoria')
        self.deputy = self._set_up_deputy(id_register)

    def _set_up_deputy(self, id_register):
        """ recover all information from the last legislature"""
        query = {'ideCadastro': str(id_register)}
        result = list(self._collection_deputy.find(query).limit(1).sort({"$natural": -1}))[0]

        deputy_instance = Deputy(result['ideCadastro'], result['nomeParlamentarAtual'], result['nomeCivil'],
                                 result['sexo'], result['dataNascimento'], result['dataFalecimento'],
                                 result['nomeProfissao'], result['escolaridade'], result['email'],
                                 result['ufRepresentacaoAtual'], result['partidoAtual'],
                                 result['situacaoNaLegislaturaAtual'], result['filiacoesPartidarias'],
                                 result['periodosExercicio'])

        return deputy_instance

    @app.route("/deputy_personal_info", methods=['GET', 'POST'])
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
                periods_of_exercise_deputy = [period_in_exercise]

            dates_in_exercise = [(item['dataInicio'], item['dataFim']) for item in periods_of_exercise_deputy]
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
            all_events = next(dbConn.build_collection(event_collection_name).find(query_event), None)

            if (dates_in_exercise is not None) & (all_events is not None):

                # filter all events by the period of availability of the deputy
                filtered_events = utils.get_records_by_intervals(all_events, dates_in_exercise, date_key_name)
                total_num_events = len(filtered_events)

                if total_num_events > 0:
                    presences = list(chain.from_iterable([voting[presence_key_name] for voting in filtered_events]))
                    presences_by_deputy = Counter(presences)
                    median_presence = np.median(list(presences_by_deputy.values()))
                    deputy_presence = presences_by_deputy[self.deputy.id_register]
                    return {'presence': deputy_presence, 'median-presence': median_presence, 'all-events': total_num_events}
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
            all_authors = next(self._collection_authors.find(query_authors), None)

            if (dates_in_exercise is not None) & (all_authors is not None):

                # filter all events by the period of availability of the deputy
                filtered_events = utils.get_records_by_intervals(all_authors, dates_in_exercise, 'dataApresentacao')
                total_num_events = len(filtered_events)

                if total_num_events > 0:
                    all_propositions_authors = [authoring['idDeputadoAutor'] for authoring in filtered_events]
                    authoring_by_deputy = Counter(all_propositions_authors)
                    median_authoring = np.median(list(authoring_by_deputy.values()))
                    deputy_authoring = authoring_by_deputy[self.deputy.id_register]

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














