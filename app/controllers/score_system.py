from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn
from datetime import datetime
from collections import Counter
# =================================================

COLLECTIONS_NAMES = ['deputado', 'gasto', 'reuniao_audiencia_publica', 'reuniao_comissao_inquerito',
                     'reuniao_comissao_permanente', 'autoria', 'votacao']


def initialize_collections(collections=COLLECTIONS_NAMES):
    """ Function to initialize mongodb collections. Return a dictionary w/ each collection. """
    try:
        collections_dict = {}
        for collection in collections:
            collections_dict[collection] = dbConn.build_collection(collection)
        return collections_dict
    except Exception as e:
        print(e)

def dateformats():
    """ Possible date formats. Both of them are used by the Camara dos Deputados data API. """
    return ['%Y-%m-%d', '%d/%m/%Y']


def str2date(string):
    """Parse a string into a datetime object."""
    for fmt in dateformats():
        try:
            return datetime.strptime(string, fmt)
        except ValueError:
            pass
    raise ValueError("'%s' is not a recognized date/time" % string)


def get_records_by_intervals(records, dates, data_key):
    """ Given a records with date (accessed by data_key) and dates, recover the events within the dates ranges. """
    if len(dates) == 1:
        date_start = str2date(dates[0][0])
        date_finish = str2date(dates[0][1])
        result = [item for item in records if date_start <= str2date(item[data_key]) <= date_finish]

    elif len(dates) > 1:  # more than one date to compare
        result = []
        for date in dates:
            date_start = str2date(date[0])
            date_finish = str2date(date[1])
            result += [item for item in records if date_start <= str2date(item[data_key])
                       <= date_finish]
    return result


class ScoreSystem:
    def __init__(self):
        self._collections = initialize_collections()

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
                public_audiences_filtered = get_records_by_intervals(public_audiences, dates, 'data')

                # count, for each deputy, how many public audiences attended
                public_audiences_presences = Counter([dep_id for item in public_audiences_filtered
                                                      for dep_id in item['presencas']])
                best_result = public_audiences_presences.most_common(1)[0][1]  # max number of presences
                deputy_result = public_audiences_presences[deputy_id]

                score = (deputy_result / best_result) * 10
                return score

        @app.route("/score_indicator_three", methods=['GET', 'POST'])
        def requestIndicatorThreeScore():
            # getting variables from url
            deputy_id = request.args.get('deputy_id', type=int)
            legislature_number = request.args.get('legislature_number', default=56, type=int)
            return calculateIndicatorThreeScore(deputy_id, legislature_number)

        # @app.route("/score_indicator_one", methods=['GET', 'POST'])

