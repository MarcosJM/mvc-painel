from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app.models.deputy_history import DeputyHistory
from app import dbConn
from app.controllers.deputy_info import DeputyInfo
from app.utils import LEGISLATURES, YEARS


class Main:
    def __init__(self):
        @app.route("/")
        def homepage():
            return render_template("home.html")

        @app.route("/explorar/")
        def exploreSelect():
            return render_template("selectionPage.html")

        @app.route("/explorar/camara")
        def exploreGeneral():
            return render_template("camara.html")

        @app.route("/explorar/deputados")
        def exploreDeputados():
            return render_template("deputados.html")

        @app.route("/explorar/avaliacao")
        def exploreAvaliation():
            return render_template("avaliacao.html")

        @app.route("/explorar/avaliacao/ranking")
        def exploreRanking():
            return render_template("ranking.html")

        @app.route("/explorar/deputados/deputado", methods=['GET', 'POST'])
        def deputadoPersonalInfo():
            depId = request.args['depId']
            deputy = DeputyInfo(depId)
            personalInfo = deputy.getDeputyPersonalInfo()

            temp = personalInfo.party_affiliations
            temp = temp['filiacaoPartidaria']
            if len(temp) > 0:
                temp = [item['siglaPartidoAnterior'] for item in temp]

            personalInfo.setPartyAffiliations(temp)

            return render_template("deputado.html", personalInfo=personalInfo)

        @app.route('/evaluation')
        def evaluationBuild():
            return render_template("avaliacao.html")


class MainReqs:
    def __init__(self):
        @app.route("/gender_count", methods=['POST'])
        def returnGenterCount():
            return get_count_deputies_by_gender()

        @app.route("/deputy_event_presence", methods=['POST'])
        def getPresenceInEvents():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            eventPresences = {}
            for legislature in LEGISLATURES:
                votingPresenceInLegislature = deputy.getPresenceInEvent('votacao', 'presentes', 'data', legislature)
                audiencePresenceInLegislature = deputy.getPresenceInEvent('reuniao_audiencia_publica', 'presencas',
                                                                          'data', legislature)
                cpiPresenceInLegislature = deputy.getPresenceInEvent('reuniao_comissao_inquerito', 'presencas', 'data',
                                                                     legislature)
                cpPresenceInLegislature = deputy.getPresenceInEvent('reuniao_comissao_permanente', 'presencas', 'data',
                                                                    legislature)

                if votingPresenceInLegislature is None:
                    votingPresenceInLegislature = {'all-events': -1, 'mean-presence': -1, 'presence': -1}

                if audiencePresenceInLegislature is None:
                    audiencePresenceInLegislature = {'all-events': -1, 'mean-presence': -1, 'presence': -1}

                if cpiPresenceInLegislature is None:
                    cpiPresenceInLegislature = {'all-events': -1, 'mean-presence': -1, 'presence': -1}

                if cpPresenceInLegislature is None:
                    cpPresenceInLegislature = {'all-events': -1, 'mean-presence': -1, 'presence': -1}

                if (votingPresenceInLegislature is not None) or (audiencePresenceInLegislature is not None) or (cpiPresenceInLegislature is not None) or (cpPresenceInLegislature is not None):
                    eventPresences.update({legislature:
                                            {'votacoes': votingPresenceInLegislature,
                                            'audiencias': audiencePresenceInLegislature,
                                            'comissao_inquerito': cpiPresenceInLegislature,
                                            'comissao_permanente': cpPresenceInLegislature}
                                            })

            return {'eventPresences': eventPresences}

        @app.route('/deputy_expenses_history', methods=['POST'])
        def getDeputyExpensesgetDeputyExpenses():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            expensesHistory = {}
            for year in YEARS:
                expenses = deputy.getExpenses(year)
                if expenses is not None:
                    expensesHistory.update({year: expenses})
            return {'expensesHistory': expensesHistory}

        @app.route('/deputy_expenses_category', methods=['POST'])
        def getDeputyExpensesCategory():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            expensesCategory = {}
            for year in YEARS:
                categories = deputy.getExpensesCategory(year)
                if categories is not None:
                    sorted_categories = sorted(categories, key=lambda x: x['value'], reverse=True)

                    totalSpent = sum(item['value'] for item in categories)
                    others_threshold = totalSpent*0.15  # if category is below 15% of total spent, goes to "Others"
                    inner_circle_name = 'Gastos'  # the name inside white middle part of the sunburst

                    has_other = False  # a flag to indicate if creates or not the "Others" category
                    others_ids = []  # the category indices that goes to "Others"
                    for i, category in enumerate(sorted_categories):
                        if category['value'] > others_threshold:
                            category.update({'id': '1.'+str(i+1), 'parent': '0.0'})  # needed to plot
                        else:
                            has_other = True
                            others_ids.append(i)
                            category.update({'id': '2.'+str(i-others_ids[0]+1), 'parent': '1.'+str(others_ids[0]+1)})

                    sorted_categories.append({'id': '0.0', 'parent': '', 'name': inner_circle_name})
                    if has_other:
                        sorted_categories.append({'id': '1.'+str(others_ids[0]+1), 'parent': '0.0',
                                                  'name': 'Outros'})

                    expensesCategory.update({year: sorted_categories})
                else:
                    print('No categories.')
            return {'expensesCategory': expensesCategory}

        @app.route('/deputy_authorships', methods=['POST'])
        def getDeputyAuthorships():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            allAuthorships = {}
            for legislature in LEGISLATURES:
                authorships = deputy.getPropositionsAuthored(legislature)
                if authorships is not None:
                    authorshipData = deputy.getPropositionsAuthoredDetails(legislature)
                    allAuthorships.update({legislature: {'authorshipQuantity': authorships, 'authorshipData': authorshipData['authorshipMetadata']}})
            return {'authorships': allAuthorships}


def get_count_deputies_by_gender():
    genderCount = {}
    result = list(dbConn.build_collection('deputado').aggregate(
        [{"$group": {"_id": {"legislatura": "$numLegislatura", "sexo": "$sexo", "deputado": "$ideCadastro"}}}]))

    for item in result:
        if item['_id']['legislatura'] in genderCount:
            if item['_id']['sexo'] in genderCount[item['_id']['legislatura']]:
                genderCount[item['_id']['legislatura']][item['_id']['sexo']] += 1
            else:
                genderCount[item['_id']['legislatura']][item['_id']['sexo']] = 1
        else:
            genderCount[item['_id']['legislatura']] = { item['_id']['sexo']: 1}
    return genderCount
