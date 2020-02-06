from app import app
from flask import render_template, request, redirect, url_for, session, flash, json
from app import dbConn

# =================================================


class DeputyListing:
    def __init__(self):
        self._collection_deputy = dbConn.build_collection('deputado')
        self._query_fields = {'_id':0, 'ideCadastro': 1, 'nomeParlamentarAtual': 1, 'ufRepresentacaoAtual':1, 'partidoAtual':1, 'urlFoto':1}

        @app.route("/deputy_listing", methods=['POST'])
        def getDeputyListing():
            allDeputiesId = self.getDeputyIdList()
            allDeputies = []
            for depId in allDeputiesId:
                result = list(
                    self._collection_deputy.find({'ideCadastro': depId}, self._query_fields).sort('numLegislatura', -1))
                allDeputies.append(result[0])
            return {'allDeputies': allDeputies}

        @app.route("/deputy_listing_legislature", methods=['POST'])
        def getDeputyListingLegislature():
            legislature_number = request.form['legislature']
            allDeputiesId = self.getDeputyIdList()
            allDeputies= []
            for depId in allDeputiesId:
                result = list(self._collection_deputy.find({'ideCadastro': depId, 'numLegislatura':str(legislature_number)}))
                allDeputies.append(result[0])
            return {'allDeputies': allDeputies}
    def getDeputyIdList(self):
        result = self._collection_deputy.find().distinct("ideCadastro")
        return result
