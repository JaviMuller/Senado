from constants import TYPE_CS, TYPE_NC
from base import Candidate, ChamberBallot, SuperiorCouncilBallot

class IOInterface():
    def __init__(self):
        pass
    
    def welcome(self):
        pass
    
    def ask_csv_import(self):
        pass
    
    def ask_csv_export(self, election_type, candidates, ballots):
        pass
    
    def ask_log_export(self):
        pass
    
    def get_election_type(self):
        pass
    
    def get_candidates(self):
        pass
    
    def get_ballots(self, election_type):
        pass
    
    def get_chamber_name(self):
        pass
    
    def get_presidential_choices(self, candidates, max_winners):
        pass
    
    def output_results(self, seats, elected):
        pass