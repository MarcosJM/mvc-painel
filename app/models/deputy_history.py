from app import dbConn
from app.models.deputy import *


class DeputyHistory:

    def __init__(self, id_register):
        self.id_register = id_register
        self._collection = dbConn.build_collection('deputado')
        self.history = self._history()

    def _history(self):
        query = {'ideCadastro': self.id_register}
        result = list(self._collection.find(query))

        history = {element['numLegislatura']: Deputy(element['ideCadastro'], element['nomeParlamentarAtual'],
                                                     element['nomeCivil'], element['sexo'],
                                                     element['dataNascimento'], element['dataFalecimento'],
                                                     element['nomeProfissao'],
                                                     element['escolaridade'], element['email'],
                                                     element['ufRepresentacaoAtual'], element['partidoAtual'],
                                                     element['situacaoNaLegislaturaAtual'],
                                                     element['filiacoesPartidarias'],
                                                     element['periodosExercicio'],
                                                     element['tempoDeCamara']) for element in result}

        return history

    def getLegislatureData(self, legislature_number):
        """ returns deputy data from a particular legislature """
        return self.history[legislature_number]

