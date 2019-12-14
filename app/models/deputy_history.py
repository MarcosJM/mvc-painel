from app import dbConn
from app.models.deputy import *


class DeputyHistory:

    def __init__(self, id_register):
        self.id_register = id_register
        self._collection = 'deputado'
        self.history = self._history()

    def _history(self):
        query = {'ideCadastro': self.id_register}
        result = list(dbConn.build_collection(self._collection).find(query))

        history = {element['numLegislatura']: Deputy(element['ideCadastro'], element['nomeParlamentarAtual'],
                                                     element['nomeCivil'], element['sexo'],
                                                     element['dataNascimento'], element['dataFalecimento'],
                                                     element['nomeProfissao'],
                                                     element['escolaridade'], element['email'],
                                                     element['ufRepresentacaoAtual'], element['partidoAtual'],
                                                     element['situacaoNaLegislaturaAtual'],
                                                     element['filiacoesPartidarias'],
                                                     element['periodosExercicio']) for element in result}

        return history

    # returns deputy data from a particular legislatura
    def getLegislatureData(self, legislature_number):
        return self.history[legislature_number]

