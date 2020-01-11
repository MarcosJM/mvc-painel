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
        self.deputy = self._set_up_deputy(id_register)

    def _set_up_deputy(self, id_register):
        """ recover all information from the last legislature"""
        query = {'ideCadastro': str(id_register)}
        result = list(self._collection_deputy.find(query).limit(1).sort({"$natural": -1}))

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

    def getPresenceInEvent(self, event_collection_name, presence_key_name, date_key_name, legislature_number=56):
        """ Given a event collection name and which key is used to identify the presences and the date,
        returns a dictionary w/ the total n of events, the presence of the deputy and the mean presence for that
        event (given the deputy's period of exercise)"""

        # ======= periods of active exercise
        query = {'$and': [{'ideCadastro': str(self.deputy.id_register)},
                          {'numLegislatura': str(legislature_number)}]}, {'periodosExercicio': 1, '_id': 0}

        result = list(self._collection_deputy.find(query))

        period_in_exercise = result[0]['periodosExercicio']['periodoExercicio']

        if isinstance(period_in_exercise, dict):
            periods_of_exercise_deputy = [period_in_exercise]

        dates_in_exercise = [(item['dataInicio'], item['dataFim']) for item in periods_of_exercise_deputy]

        # ======= recover all events
        query_event = {'legislatura': legislature_number}
        result_event = list(dbConn.build_collection(event_collection_name).find(query_event))
        all_events = result_event

        # filter all public audiences by the period of availability of the deputy
        filtered_events = utils.get_records_by_intervals(all_events, dates_in_exercise, date_key_name)
        total_events = len(filtered_events)  # number of votings happened in the period observed

        presences = list(chain.from_iterable([voting[presence_key_name] for voting in total_events]))
        presences_by_deputy = Counter(presences)
        mean_presence = np.mean(list(presences_by_deputy.values()))
        deputy_presence = presences_by_deputy[self.deputy.id_register]

        return {'presence': deputy_presence, 'mean-presence': mean_presence, 'all-events': total_events}











