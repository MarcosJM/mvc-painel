from app import app
from flask import request, render_template
from app import dbConn
from datetime import datetime
from collections import Counter
import app.utils as utils
import numbers
from app.controllers.deputy_listing import DeputyListing


# =================================================


class ScoreSystem:
    def __init__(self):
        self._collections = dbConn.initialize_collections()

        def calculateIndicatorThreeScore(deputy_id, legislature_number=None):
            """
            calculate the transparent indicator of the deputy final score
            by analysing the public audiences attended.
            :param deputy_id: which deputy
            :param legislature_number: to filter
            :return: score (0-10)
            """
            indicator_three_score = 0

            # recover all the public audiences events that happened in a legislature
            if legislature_number is None:
                query_all_events = {}
            else:
                query_all_events = {'legislatura': {"$in": legislature_number}}

            result_all_events = list(self._collections['reuniao_audiencia_publica'].find(query_all_events))
            public_audiences = result_all_events

            # recover the periods in which the deputy was actively working
            if legislature_number is None:
                query_deputy_availability = {'ideCadastro': str(deputy_id)}
            else:
                query_deputy_availability = {'numLegislatura': {"$in": list(map(str, legislature_number))},
                                             'ideCadastro': str(deputy_id)}

            query_field = {'periodosExercicio': 1, '_id': 0}
            result = next(self._collections['deputado'].find(query_deputy_availability, query_field), None)

            if result is not None and result['periodosExercicio'] is not None:
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
                if len(public_audiences_presences) > 0:
                    best_result = public_audiences_presences.most_common(1)[0][1]  # max number of presences
                    deputy_result = public_audiences_presences[deputy_id]

                    indicator_three_score = (deputy_result / best_result) * 10
                    return indicator_three_score
                else:
                    return indicator_three_score
            else:
                return indicator_three_score

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

            # recover all commissions that the deputy is member of
            query_deputy_comissions = {'numLegislatura': str(legislature_number), 'ideCadastro': str(deputy_id)}
            query_field = {'comissoes': 1, '_id': 0}
            result_member_comissions = next(self._collections['deputado'].find(query_deputy_comissions, query_field),
                                            None)
            if result_member_comissions is not None and result_member_comissions['comissoes'] is not None:
                if isinstance(result_member_comissions['comissoes']['comissao'], dict):
                    siglas = result_member_comissions['comissoes']['comissao']['siglaComissao']
                else:
                    siglas = [result['siglaComissao'] for result in result_member_comissions['comissoes']['comissao']]

                # get presence in those commissions
                query_commissions_presence = {'legislatura': int(legislature_number)}
                result_comissions_presence = list(
                    self._collections['reuniao_comissao_inquerito'].find(query_commissions_presence))

                deputy_presences = [item for item in result_comissions_presence if item['sigla'] in siglas]
                if deputy_presences is not None:

                    presencesGroup = {}

                    for presence in deputy_presences:
                        if presence['sigla'] in presencesGroup:
                            presencesGroup[presence['sigla']] += presence['presencas']
                        else:
                            presencesGroup.update({presence['sigla']: presence['presencas']})

                    deputyPresences = {}

                    for sigla in presencesGroup.keys():
                        deputyPresences.update({sigla: presencesGroup[sigla].count(deputy_id)})

                    # correction factor
                    cf = max(list(cpiReunionsFormatted.values()))

                    # for each cpi the deputy attended, we compare his attendances to the total number of meetings

                    indicatorScore = 0
                    for cpi in deputyPresences.items():
                        indicatorScore += (cpi[1] / cpiReunionsFormatted[cpi[0]]) * (cpi[1] / cf)
                    if len(presencesGroup) > 0:
                        return str((indicatorScore / len(presencesGroup)) * 10)
                    else:
                        return 0
                else:
                    return None
            else:
                return None

        def calculateAuthoringCriteria(deputy_id, legislature_number=None):
            """
            calculates the criteria of the number of propositions authored
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: score of the criteria (between 0 and 10)
            """
            score_authoring = 0

            if legislature_number is None:
                query_authoring = [{'$group': {'_id': '$idDeputadoAutor', 'count': {'$sum': 1}}}]
            else:
                query_authoring = [{'$match': {'legislatura': {"$in": legislature_number}}},
                                   {'$group': {'_id': '$idDeputadoAutor', 'count': {'$sum': 1}}}]

            result = list(self._collections['autoria'].aggregate(query_authoring))

            if len(result) > 0:
                best_result = max(result, key=lambda d: d['count'])['count']
                deputy_result = [item['count'] for item in result if item['_id'] == deputy_id]
                print("[INDICATOR ONE - AUTHORING SCORE] Results found. Deputy has {} "
                      "propositions authored".format(len(deputy_result)))
                if len(deputy_result) > 0:
                    deputy_result = deputy_result[0]
                    score_authoring = (deputy_result / best_result) * 10
                    return score_authoring
                else:
                    return score_authoring
            else:
                print('No authoring data.')
                return score_authoring

        def calculateVotingCriteria(deputy_id, legislature_number=None):
            """
            calculates the criteria of the presence in votings
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: score of the criteria (between 0 and 10)
            """
            score_voting = 0

            if legislature_number is None:
                query_all_events = {}
            else:
                query_all_events = {'legislatura': {"$in": legislature_number}}

            result_all_events = list(self._collections['votacao'].find(query_all_events))

            if len(result_all_events) > 0:
                deputy_presences = [voting for voting in result_all_events if str(deputy_id) in voting['presentes']]
                print("[INDICATOR ONE - VOTING SCORE] Results found. Deputy attended {} votings".format(len(deputy_presences)))
                score_voting = (len(deputy_presences) / len(result_all_events)) * 10
                return score_voting
            else:
                return score_voting  # there were no votings in the period

        def calculatePermanentCommissionCriteria(deputy_id, legislature_number=None):
            """
            calculates the criteria of the presence in permanent commissions
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: score of the criteria (between 0 and 10)
            """
            score_cp = 0

            if legislature_number is None:
                query_commissions = {}
                query_field = {'data': 1, 'sigla': 1, 'presencas': 1, '_id': 0}
            else:
                query_commissions = {'legislatura': {"$in": legislature_number}}
                query_field = {'legislatura': 1, 'data': 1, 'sigla': 1, 'presencas': 1, '_id': 0}

            # getting cp reunions
            cpReunions = list(self._collections['reuniao_comissao_permanente'].find(query_commissions, query_field))

            if len(cpReunions) > 0:  # there are at least 1 reunion in the period

                number_of_reunions_by_cp = dict(Counter([reunion['sigla'] for reunion in cpReunions]))
                max_number_of_reunions = max(number_of_reunions_by_cp.values())

                # recover all commissions that the deputy is member of
                if legislature_number is None:
                    query_deputy_comissions = {'ideCadastro': str(deputy_id)}
                else:
                    query_deputy_comissions = {'numLegislatura': {"$in": list(map(str,legislature_number))},
                                               'ideCadastro': str(deputy_id)}

                query_field = {'comissoes': 1, '_id': 0}
                result_member_comissions = next(
                    self._collections['deputado'].find(query_deputy_comissions, query_field),
                    None)

                if result_member_comissions is not None and result_member_comissions['comissoes'] is not None:

                    if isinstance(result_member_comissions['comissoes']['comissao'], dict):
                        deputy_commissions = [{result_member_comissions['comissoes']['comissao']['siglaComissao']:
                                                   (result_member_comissions['comissoes']['comissao']['dataEntrada'],
                                                    result_member_comissions['comissoes']['comissao']['dataSaida'])}]
                    else:
                        deputy_commissions = [{result['siglaComissao']: (result['dataEntrada'], result['dataSaida'])}
                                              for result in result_member_comissions['comissoes']['comissao']]

                    # get just the permanent commissions
                    deputy_commissions = [commission for commission in deputy_commissions
                                          if list(commission.keys())[0] in
                                          utils.getLegislativeBody("Comissão Permanente")]

                    all_deputy_commissions_presences = []
                    if len(deputy_commissions) > 0:
                        for commission in deputy_commissions:
                            initials, periodsOfPresence = list(commission.items())[0]
                            if periodsOfPresence[0] is not None:

                                date_start = utils.str2date(periodsOfPresence[0])

                                if periodsOfPresence[1] is None:
                                    periodsOfPresence = list(periodsOfPresence)
                                    periodsOfPresence[1] = datetime.today()  # assign today's date if no end
                                    date_end = periodsOfPresence[1]
                                else:
                                    date_end = utils.str2date(periodsOfPresence[1])

                                reunions = [reunion for reunion in cpReunions
                                            if reunion['sigla'] == initials and
                                            (date_start <= utils.str2date(reunion['data']) <= date_end)]

                                cp_frequency = len(reunions)
                                if cp_frequency > 0:  # there were reunions from this CP when deputy was member
                                    print(str(int(deputy_id)))
                                    deputy_presence_in_cp = len([reunion for reunion in reunions
                                                                 if int(float(deputy_id)) in reunion['presencas']])
                                    all_deputy_commissions_presences.append({'comission': initials,
                                                                             'frequency': cp_frequency,
                                                                             'deputy_presence': deputy_presence_in_cp})
                        sum_of_cp_score = 0
                        print("[INDICATOR ONE - C.P. SCORE] Results found. Deputy has {} comissions"
                              "and attended {}".format(len(deputy_commissions), all_deputy_commissions_presences))

                        if len(all_deputy_commissions_presences) > 0:
                            for cp in all_deputy_commissions_presences:
                                adjustment_factor = cp['frequency'] / max_number_of_reunions
                                score = ((cp['deputy_presence'] / cp['frequency']) * adjustment_factor) * 10
                                sum_of_cp_score += score

                            score_cp = sum_of_cp_score / len(all_deputy_commissions_presences)
                            return score_cp
                    else:
                        return score_cp  # deputy has no cp comissions
                else:
                    return score_cp  # deputy has no comissions at all
            else:
                return score_cp  # there are no cp reunions

        def calculateIndicatorOneScore(deputy_id, legislature_number=None):
            """
            this method calculates the score of a deputy in the fiscalizador indicator perspective
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: float - a value between 0 and 10
            """
            if legislature_number is None:  # when no legislature number provided, calculate for all dep's legislatures

                # recover which legislatures the deputy participated
                query_all_periods_of_activity = {'ideCadastro': str(deputy_id)}
                query_fields = {"numLegislatura": 1, "_id": 0}

                deputy_all_periods_of_activity = \
                    list(self._collections['deputado'].find(query_all_periods_of_activity,
                                                            query_fields).sort("numLegislatura", 1))

                deputy_legislatures = [int(leg['numLegislatura']) for leg in deputy_all_periods_of_activity]
                print("=============== Deputy's all legislatures:", deputy_legislatures)

                authoring_score = calculateAuthoringCriteria(deputy_id, deputy_legislatures)
                voting_score = calculateVotingCriteria(deputy_id, deputy_legislatures)
                cp_score = calculatePermanentCommissionCriteria(deputy_id, deputy_legislatures)
            else:
                if isinstance(legislature_number, numbers.Number):
                    legislature_number = [int(legislature_number)]  # if it's a number, convert to list (pattern)
                authoring_score = calculateAuthoringCriteria(deputy_id, legislature_number)
                voting_score = calculateVotingCriteria(deputy_id, legislature_number)
                cp_score = calculatePermanentCommissionCriteria(deputy_id, legislature_number)

            print("[INDICATOR ONE] ==== Partial scores:", [authoring_score, voting_score, cp_score])
            partial_scores = [0 if score is None else score for score in [authoring_score, voting_score, cp_score]]

            indicator_one_score = sum(partial_scores)/3
            return {'indicator_one_score': indicator_one_score, 'authoring_criteria': partial_scores[0],
                    'voting_criteria': partial_scores[1], 'cp_criteria': partial_scores[2]}

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

        @app.route("/score_indicator_one", methods=['GET', 'POST'])
        def requestIndicatorOneScore():
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', type=int)
            return calculateIndicatorOneScore(deputy_id, legislature_number)

        @app.route("/ranking")
        def requestRanking():
            allScores = {}

            allDeputiesIds = utils.getAllDeputiesIds()

            for _, deputy_id in enumerate(allDeputiesIds):
                print("*******D E P U T Y     I D", deputy_id, " - ", _, " O F", len(allDeputiesIds), '*******')
                indicator_one_score = calculateIndicatorOneScore(deputy_id)
                # indicator_two_score = calculateIndicatorTwoScore(deputy_id)
                indicator_three_score = calculateIndicatorThreeScore(deputy_id)

                scores = {'scores': {'indicator_one': indicator_one_score,
                                     'indicator_two': '',
                                     'indicator_three': indicator_three_score}}

                allScores[deputy_id] = scores

            # write data into a JSON file
            # utils.dict_to_json_file(allScores, '/home/mariana/Documents', 'indicador_one_and_three')

            allScoresFMT = {k: v['scores'] for k, v in allScores.items()}
            allScoresFMT = {k: {'indicator_one': v['indicator_one']['indicator_one_score'],
                                'I1_authoring': v['indicator_one']['authoring_criteria'],
                                'I1_voting': v['indicator_one']['voting_criteria'],
                                'I1_cp': v['indicator_one']['cp_criteria'],
                            'indicator_three': v['indicator_three']} for k, v in allScoresFMT.items()}

            with open('/home/mariana/Documents/indicador_one_and_threev3.json', 'w') as fp:
                json.dump(allScoresFMT, fp)

            return allScores

        # @app.route("/ranking")
        # def requestRanking():
        #     query_fields = {'_id': 0, 'ideCadastro': 1, 'nomeParlamentarAtual': 1, 'ufRepresentacaoAtual': 1,
        #                     'partidoAtual': 1, 'urlFoto': 1}
        #     collections = dbConn.initialize_collections()
        #     allIds = collections['deputado'].find().distinct("ideCadastro")
        #     allDeputies = []
        #     for depId in allIds:
        #         result = list(
        #             collections['deputado'].find({'ideCadastro': depId}, query_fields).sort('numLegislatura', -1))
        #         allDeputies.append(result[0])
        #     ranking = {}
        #     for legislature in utils.LEGISLATURES:
        #         ranking.update({legislature: []})
        #
        #     for iterator in range(100):
        #         for legislature in utils.LEGISLATURES:
        #             # indicatorOneScore = calculateIndicatorOneScore(allDeputies[iterator], 56)
        #             indicatorTwoScore = calculateIndicatorTwoScore(int(allDeputies[iterator]['ideCadastro']),
        #                                                            legislature)
        #             indicatorThreeScore = calculateIndicatorThreeScore(int(allDeputies[iterator]['ideCadastro']),
        #                                                                legislature)
        #             if indicatorTwoScore is None:
        #                 finalScoreComponentOne = 0
        #             else:
        #                 finalScoreComponentOne = float(indicatorTwoScore)
        #             if indicatorThreeScore is None:
        #                 finalScoreComponentTwo = 0
        #             else:
        #                 finalScoreComponentTwo = float(indicatorThreeScore)
        #             finalScore = (finalScoreComponentOne + finalScoreComponentTwo) / 2
        #             if (indicatorThreeScore is not None or indicatorTwoScore is not None):
        #                 ranking[legislature].append({'id': allDeputies[iterator]['ideCadastro'],
        #                                              'nome': allDeputies[iterator]['nomeParlamentarAtual'],
        #                                              'partido': allDeputies[iterator]['partidoAtual']['idPartido'],
        #                                              'uf': allDeputies[iterator]['ufRepresentacaoAtual'],
        #                                              'urlFoto': allDeputies[iterator]['urlFoto'],
        #                                              'fiscalizador': indicatorTwoScore,
        #                                              'transparente': indicatorThreeScore, 'finalScore': finalScore})
        #         for legislature in utils.LEGISLATURES:
        #             ranking[legislature] = sorted(ranking[legislature], key=lambda x: x['finalScore'], reverse=True)
        #     return render_template("ranking.html", ranking=ranking, lenDeputies=len(ranking[53]))
