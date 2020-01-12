from app import app
from app.controllers.main import Main
from app.controllers.main import MainReqs
from app.controllers.general_analysis import GeneralAnalysis
from app.controllers.score_system import ScoreSystem
from app.controllers.deputy_listing import DeputyListing

class Route():
    def __init__(self):
        Main()
        MainReqs()
        GeneralAnalysis()
        ScoreSystem()
        DeputyListing()
