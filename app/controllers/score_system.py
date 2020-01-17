from app import app
from flask import request
from app import dbConn
from datetime import datetime
from collections import Counter
from app.utils import *
# =================================================


class ScoreSystem:
    def __init__(self):
        self._collections = dbConn.initialize_collections()

        def calculateIndicatorThreeScore(deputy_id, legislature_number=56):
            """
            calculate the transparent indicator of the deputy final score
            by analysing the public audiences attended.
            :param deputy_id: which deputy
            :param legislature_number: to filter
            :return: score (0-10)
            """

            # recover all the public audiences events that happened in a legislature
            query_all_events = {'legislatura': legislature_number}
            result_all_events = list(self._collections['reuniao_audiencia_publica'].find(query_all_events))
            public_audiences = result_all_events

            # recover the periods in which the deputy was actively working
            query_deputy_availability = {'numLegislatura': str(legislature_number), 'ideCadastro': str(deputy_id)}
            query_field = {'periodosExercicio': 1, '_id': 0}
            result = next(self._collections['deputado'].find(query_deputy_availability, query_field), None)

            if result is not None:
                periods_of_exercise_deputy = result['periodosExercicio']['periodoExercicio']

                if isinstance(periods_of_exercise_deputy, dict):
                    periods_of_exercise_deputy = [periods_of_exercise_deputy]

                dates = [(item['dataInicio'], item['dataFim']) for item in
                         periods_of_exercise_deputy]

                # filter all public audiences by the period of availability of the deputy
                public_audiences_filtered = utils.get_records_by_intervals(public_audiences, dates, 'data')

                # count, for each deputy, how many public audiences attended
                public_audiences_presences = Counter([dep_id for item in public_audiences_filtered
                                                      for dep_id in item['presencas']])
                best_result = public_audiences_presences.most_common(1)[0][1]  # max number of presences
                deputy_result = public_audiences_presences[deputy_id]

                score = (deputy_result / best_result) * 10
                return score

        def calculateIndicatorTwoScore(deputy_id, legislature_number=56):
            """
            this method calculates the score of a deputy in the fiscalizador indicator perspective
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: float - a value between 0 and 10
            """
            pipeline = [{"$match": {"legislatura": legislature_number}},
                        {"$group": {"_id": "$sigla", "count": {"$sum": 1}}}]

            # getting the number of reunions in each cpi
            cpiReunions = list(self._collections['reuniao_comissao_inquerito'].aggregate(pipeline))
            cpiReunionsFormatted = {}
            for cpi in cpiReunions:
                valuesOnly = list(cpi.values())
                cpiReunionsFormatted.update({valuesOnly[0]: valuesOnly[1]})
            pipeline[0]['$match'] = dict(pipeline[0]['$match'], **{'presencas': deputy_id})

            # getting the presences of the deputy in the reunions he attended
            cpiPresences = list(self._collections['reuniao_comissao_inquerito'].aggregate(pipeline))
            cpiPresencesFormatted = {}
            for cpi in cpiPresences:
                valuesOnly = list(cpi.values())
                cpiPresencesFormatted.update({valuesOnly[0]: valuesOnly[1]})

            # for each cpi the deputy attended, we compare his attendances to the total number of meetings
            indicatorScore = 0
            for cpi in cpiPresencesFormatted.items():
                print('cpi formatted', cpiPresencesFormatted)
                print('cpi reunions', cpiReunionsFormatted)
                indicatorScore += (cpi[1] / cpiReunionsFormatted[cpi[0]])

            return str((indicatorScore / len(cpiPresencesFormatted)) * 10)

        def calculateIndicatorOneScore(deputy_id, legislature_number=56):
            """
            this method calculates the score of a deputy in the fiscalizador indicator perspective
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: float - a value between 0 and 10
            """
            # ============ propositions authored
            query_authoring = [{'$match': {'legislatura': legislature_number}},
                               {'$group': {'_id': '$idDeputadoAutor', 'count': {'$sum': 1}}}]

            result = list(self._collections['autoria'].aggregate(query_authoring))

            if len(list) > 0:
                best_result = max(result, key=lambda d: d['count'])['count']
                deputy_result = next((item['count'] for item in result if item['_id'] == deputy_id), None)
                score_authoring = (deputy_result / best_result) * 10
            else:
                print('No authoring data.')
                score_authoring = 0

            # ============ presence in votings
            query_all_events = {'legislatura': legislature_number}
            result_all_events = list(self._collections['votacao'].find(query_all_events))
            votings = result_all_events

            # recover the periods in which the deputy was actively working
            query_deputy_availability = {'numLegislatura': str(legislature_number), 'ideCadastro': str(deputy_id)}
            query_field = {'periodosExercicio': 1, '_id': 0}
            result = next(self._collections['deputado'].find(query_deputy_availability, query_field), None)

            if result is not None:
                periods_of_exercise_deputy = result['periodosExercicio']['periodoExercicio']

                if isinstance(periods_of_exercise_deputy, dict):
                    periods_of_exercise_deputy = [periods_of_exercise_deputy]

                dates = [(item['dataInicio'], item['dataFim']) for item in
                         periods_of_exercise_deputy]

                # filter all public audiences by the period of availability of the deputy
                votings_filtered = utils.get_records_by_intervals(votings, dates, 'data')

                total_votings = len(votings_filtered)
                deputy_presences = [voting for voting in votings if str(deputy_id) in voting['presentes']]
                score_voting = (deputy_presences / total_votings) * 10

            # ============ presence in commissions

            permanent_comissions_initials = getLegislativeBody('Comissão Permanente')

            # recover all commissions that the deputy is member of
            query_deputy_comissions = {'numLegislatura': str(legislature_number), 'ideCadastro': str(deputy_id)}
            query_field = {'comissoes': 1, '_id': 0}
            result_member_comissions = next(self._collections['deputado'].find(query_deputy_comissions, query_field),
                                            None)

            # if result_member_comissions is not None:
            #     # filtering only for permanent commissions
            #     permanent_comissions = [{item['siglaComissao']:} for item in result_member_comissions['comissoes']['comissao']
            #                             if item['siglaComissao'] in permanent_comissions_initials]
            #
            #     #

            # todo finish

        @app.route("/score_indicator_three", methods=['GET', 'POST'])
        def requestIndicatorThreeScore():
            # getting variables from url
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', default=56, type=int)
            return calculateIndicatorThreeScore(deputy_id, legislature_number)

        @app.route("/score_indicator_two", methods=['GET', 'POST'])
        def requestIndicatorTwoScore():
            # getting variables from url
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', default=56, type=int)
            return calculateIndicatorTwoScore(deputy_id, legislature_number)
