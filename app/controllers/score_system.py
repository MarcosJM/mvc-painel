from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
# =================================================


class ScoreSystem:
    def __init__(self):

        self._collection_deputy = dbConn.build_collection('deputado')
        self._collection_expense = dbConn.build_collection('gasto')
        self._collection_public_audience = dbConn.build_collection('reuniao_audiencia_publica')
        self._collection_cpi = dbConn.build_collection('reuniao_comissao_inquerito')

        @app.route("/score_indicator_three", methods=['POST'])
        def calculateIndicatorThreeScore(deputy_id, legislature_number=56):
            """
            calculate the transparent indicator of the deputy final score
            by analysing the public audiences attended.
            :param deputy_id: which deputy
            :param legislature_number: to filter
            :return: score (0-10)
            """
            # getting variables from url
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', default=56, type=int)

            query = {'legislatura': legislature_number}
            result = self._collection_public_audience.count_documents(query)
            total_number_of_public_audience = result

            query2 = dict(query, **{'presencas': deputy_id})
            result2 = self._collection_public_audience.count_documents(query2)
            total_number_of_public_audience_deputy = result2

            score = (total_number_of_public_audience_deputy/total_number_of_public_audience)*10
            return score

        @app.route("/score_indicator_two", methods=['GET','POST'])
        def calculateIndicatorTwoScore():
            """
            this method calculates the score of a deputy in the fiscalizador indicator perspective
            :param deputy_id: String - the deputy's identifier
            :param legislature_number: String - the legislature to be considered
            :return: float - a value between 0 and 10
            """
            # getting variables from url
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', default=56, type=int)

            pipeline = [{"$match": {"legislatura":legislature_number}},
                        {"$group": {"_id": "$sigla", "count": {"$sum": 1}}}]
            # getting the number of reunions in each cpi
            cpiReunions = list(self._collection_cpi.aggregate(pipeline))
            cpiReunionsFormatted = {}
            for cpi in cpiReunions:
                valuesOnly = list(cpi.values())
                cpiReunionsFormatted.update({valuesOnly[0]: valuesOnly[1]})

            pipeline[0]['$match'] = dict(pipeline[0]['$match'], **{'presencas':deputy_id})
            # getting the presences of the deputy in the reunions he attended
            cpiPresences = list(self._collection_cpi.aggregate(pipeline))
            cpiPresencesFormatted = {}
            for cpi in cpiPresences:
                valuesOnly = list(cpi.values())
                cpiPresencesFormatted.update({valuesOnly[0]: valuesOnly[1]})

            # for each cpi the deputy attended, we compare his attendances to the total number of meetings
            indicatorScore = 0
            for cpi in cpiPresencesFormatted.items():
                print('cpi formatted', cpiPresencesFormatted)
                print('cpi reunions', cpiReunionsFormatted)
                indicatorScore += (cpi[1]/cpiReunionsFormatted[cpi[0]])

            return str((indicatorScore/len(cpiPresencesFormatted)) * 10)
