from app import app
from flask import request, render_template
from app import dbConn
from datetime import datetime
from collections import Counter
import app.utils as utils
from app.controllers.deputy_listing import DeputyListing
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

                    score = (deputy_result / best_result) * 10
                    return score
                else:
                    return 0

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
                    result_comissions_presence = list(self._collections['reuniao_comissao_inquerito'].find(query_commissions_presence))

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


                        #correction factor
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

            if len(result) > 0:
                best_result = max(result, key=lambda d: d['count'])['count']
                deputy_result = [item['count'] for item in result if item['_id'] == deputy_id]
                if deputy_result:
                    deputy_result = deputy_result[0]
                    score_authoring = (deputy_result / best_result) * 10
                else:
                    print('No authoring data.')
                    score_authoring = 0
            else:
                print('No authoring data.')
                score_authoring = 0

            # ============ presence in votings
            query_all_events = {'legislatura': legislature_number}
            result_all_events = list(self._collections['votacao'].find(query_all_events))

            if len(result_all_events) > 0:
                deputy_presences = [voting for voting in result_all_events if str(deputy_id) in voting['presentes']]
                score_voting = (len(deputy_presences) / len(result_all_events)) * 10
            else:
                return None  # there were no votings in the period

            # ============ presence in permanent commissions

            pipeline = [{"$match": {"legislatura": legislature_number}},
                        {"$group": {"_id": "$sigla", "count": {"$sum": 1}}}]

            # getting the number of reunions in each cpi
            cpReunions = list(self._collections['reuniao_comissao_permanente'].aggregate(pipeline))
            cpReunionsFormatted = {}
            for cp in cpReunions:
                valuesOnly = list(cp.values())
                cpReunionsFormatted.update({valuesOnly[0]: valuesOnly[1]})


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
                    self._collections['reuniao_comissao_permanente'].find(query_commissions_presence))

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
                    cf = max(list(cpReunionsFormatted.values()))

                    # for each cp the deputy attended, we compare his attendances to the total number of meetings
                    score_commission = 0
                    for cp in deputyPresences.items():
                        score_commission += (cp[1] / cpReunionsFormatted[cp[0]]) * (cp[1] / cf)

                    score_commission = score_commission / len(deputyPresences)


                return {'indicatorOne':{'scoreAuthoring': score_authoring, 'score_voting': score_voting, 'scoreCommission':score_commission, 'totalScore': (score_authoring +score_voting+score_commission)/3 }}

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
            legislature_number = request.args.get('legislature_number', default=56, type=int)
            return calculateIndicatorOneScore(deputy_id, legislature_number)

        @app.route("/ranking")
        def requestRanking():
            query_fields = {'_id': 0, 'ideCadastro': 1, 'nomeParlamentarAtual': 1, 'ufRepresentacaoAtual': 1,
                            'partidoAtual': 1, 'urlFoto': 1}
            collections = dbConn.initialize_collections()
            allIds = collections['deputado'].find().distinct("ideCadastro")
            allDeputies = []
            for depId in allIds:
                result = list(
                    collections['deputado'].find({'ideCadastro': depId}, query_fields).sort('numLegislatura', -1))
                allDeputies.append(result[0])
            ranking = {}
            for legislature in utils.LEGISLATURES:
                ranking.update({legislature: []})

            for iterator in range(100):
                for legislature in utils.LEGISLATURES:
                    # indicatorOneScore = calculateIndicatorOneScore(allDeputies[iterator], 56)
                    indicatorTwoScore = calculateIndicatorTwoScore(int(allDeputies[iterator]['ideCadastro']), legislature)
                    indicatorThreeScore = calculateIndicatorThreeScore(int(allDeputies[iterator]['ideCadastro']), legislature)
                    if indicatorTwoScore is None:
                        finalScoreComponentOne = 0
                    else:
                        finalScoreComponentOne = float(indicatorTwoScore)
                    if indicatorThreeScore is None:
                        finalScoreComponentTwo = 0
                    else:
                        finalScoreComponentTwo = float(indicatorThreeScore)
                    finalScore = (finalScoreComponentOne + finalScoreComponentTwo)/2
                    if (indicatorThreeScore is not None or indicatorTwoScore is not None):

                        ranking[legislature].append({'id': allDeputies[iterator]['ideCadastro'], 'nome':allDeputies[iterator]['nomeParlamentarAtual'],
                                                     'partido': allDeputies[iterator]['partidoAtual']['idPartido'], 'uf':allDeputies[iterator]['ufRepresentacaoAtual'],
                                                     'urlFoto':allDeputies[iterator]['urlFoto'], 'fiscalizador': indicatorTwoScore,
                                                     'transparente': indicatorThreeScore, 'finalScore':finalScore})
                for legislature in utils.LEGISLATURES:
                    ranking[legislature] = sorted(ranking[legislature], key = lambda x: x['finalScore'], reverse=True)
            return render_template("ranking.html", ranking=ranking, lenDeputies=len(ranking[53]))
