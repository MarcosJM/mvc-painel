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

        @app.route("/explore/")
        def exploreSelect():
            return render_template("selectionPage.html")

        @app.route("/explore/camara")
        def exploreGeneral():
            return render_template("camara.html")

        @app.route("/explore/deputados")
        def exploreDeputados():
            return render_template("deputados.html")

        @app.route("/explore/deputados/deputado", methods=['GET', 'POST'])
        def deputadoPersonalInfo():
            depId = request.args['depId']
            deputy = DeputyInfo(depId)
            personalInfo = deputy.getDeputyPersonalInfo()
            if personalInfo.party_affiliations:
                if isinstance(personalInfo.party_affiliations['filiacaoPartidaria'], dict):
                    personalInfo.party_affiliations = personalInfo.party_affiliations['filiacaoPartidaria']['siglaPartidoAnterior']
                else:
                    affiliations = ''
                    for affiliation in personalInfo.party_affiliations['filiacaoPartidaria']:
                        affiliations += affiliation['siglaPartidoAnterior'] + ','
                    personalInfo.party_affiliations = affiliations[: -1]
            return render_template("deputado.html", personalInfo=personalInfo)




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
                if (votingPresenceInLegislature is not None) or (audiencePresenceInLegislature is not None) or (cpiPresenceInLegislature is not None) or (cpPresenceInLegislature is not None):
                    eventPresences.update({legislature:
                                            {'votacoes': votingPresenceInLegislature,
                                            'audiencias': audiencePresenceInLegislature,
                                            'comissao_inquerito': cpiPresenceInLegislature,
                                            'comissao_permanente': cpPresenceInLegislature}
                                            })

            return {'eventPresences': eventPresences}

        @app.route('/deputy_expenses_history', methods=['POST'])
        def getDeputyExpenses():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            expensesHistory = {}
            for year in YEARS:
                expenses = deputy.getExpenses(year)
                if expenses is not None:
                    expensesHistory.update({year: expenses})
            return {'expensesHistory': expensesHistory}

        @app.route('/deputy_authorships', methods=['POST'])
        def getDeputyAuthorships():
            depId = request.form['depId']
            deputy = DeputyInfo(depId)
            allAuthorships = {}
            for legislature in LEGISLATURES:
                authorships = deputy.getPropositionsAuthored(legislature)
                if authorships is not None:
                    allAuthorships.update({legislature: authorships})
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
