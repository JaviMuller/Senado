from constants import TYPE_CS, TYPE_NC
from base import Candidate, ChamberBallot, SuperiorCouncilBallot

class IOInterface():
    def __init__(self):
        pass
    
    def get_election_type():
        pass
    
    def get_candidates():
        pass
    
    def get_ballots(election_type):
        pass
    
    def get_presidential_choice(candidates):
        pass
    
    def output_results(seats, elected):
        pass