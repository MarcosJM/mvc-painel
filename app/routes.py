from app import app
from app.controllers.main import Main
from app.controllers.general_analysis import GeneralAnalysis


class Route():
    def __init__(self):
        Main()
        GeneralAnalysis()
