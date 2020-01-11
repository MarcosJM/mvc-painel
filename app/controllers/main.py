from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app.models.deputy_history import DeputyHistory
from app import dbConn
from app.controllers.deputy_info import DeputyInfo

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
            print('depId', depId)
            deputy = DeputyInfo(depId)
            print('deputy ', deputy.getDeputyPersonalInfo)
            return render_template("deputado.html", personalInfo=deputy.getDeputyPersonalInfo)




class MainReqs:
    def __init__(self):
        @app.route("/gender_count", methods=['POST'])
        def returnGenterCount():
            return get_count_deputies_by_gender()


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
