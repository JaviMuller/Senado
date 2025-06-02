__author__ = "Javier de Muller"
__copyright__ = "Copyright (C) 2023 Javier de Muller"
__license__ = "MIT License"
__version__ = "2.0"

from utils import *
from base import *
from clinterface import CLInterface
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


################################################################################
################################ Election Rounds ###############################
################################################################################


class Round:
    """Abstract class to represent a round

    Attributes:
        ballots (list<Ballot>): list of ballots to be tallied
        
    Methods:
        __init__
        result
        __str__
    """

    def __init__(self, ballots):
        """Initializes a round by attaching the ballots to it

        Arguments:
            ballots (list<Ballot>): list of ballots to be tallied
        """
        self.ballots = ballots

    def result(self):
        """Abstract method to compute the result of a round
        
        Returns:
            RoundResult: the result of a round

        Raises:
            NotImplementedError: Needs to be implemented by children
        """
        raise NotImplementedError('Round.result: This method is not implemented')

    def __str__(self):
        """String representation of a round

        Raises:
            NotImplementedError: Needs to be implemented by children
        """
        raise NotImplementedError('Round.__str__: This method is not implemented')


### Preferential rounds (main ones)

class PreferentialRound(Round): 
    """Abstract class for a preferential type round

    Attributes:
        ballots (list<Ballot>)

    Methods:
        __init__
        preferred
        result
    """

    def __init__(self, ballots):
        """Initialize a new preferential round

        Arguments:
            ballots (list<Ballot>): list of ballots to be tallied
        """
        super().__init__(ballots)

    def preferred(self, ballot):
        """Abstract method to select the preferred candidate of a ballot

        Arguments:
            ballot (Ballot): ballot to select the preferred candidate from

        Raises:
            NotImplementedError: Needs to be implemented by children
        """
        raise NotImplementedError('PreferentialRound.preferred: This method is not implemented')

    def result(self):
        """Computes the result of a preferential round

        Returns:
            RoundResult: The result of the preferential round
        """
        tally = Tally()
        votes = len(self.ballots)
        for ballot in self.ballots:
            preferred = self.preferred(ballot)
            if preferred is None:
                votes -= 1
            else:
                tally.add_vote_to_candidate(preferred)
        return RoundResult(votes, tally)


class PreferentialExclusiveRound(PreferentialRound):
    """Class to run a preferential exclusive round on a ballot list

    Attributes:
        ballots (list<Ballot>): Ballots to be tallied
        excluded (optional(list<Candidate>)): List of candidates to be removed from the tally. Defaults to []

    Methods:
        __init__
        preferred
        result
    """

    def __init__(self, ballots, excluded = []):
        """Initializes a new preferential exclusive round
        
        Arguments:
            ballots (list<Ballot>): Ballots to be tallied
            excluded (list<Candidate>): Exclude candidates from tally. Defaults to []
        """
        super().__init__(ballots)
        self.excluded = excluded.copy()

    def preferred(self, ballot):
        """Selects the preferred candidate in a ballot, exculding the candidates that need to be excluded

        Arguments:
            ballot (Ballot): ballot to be tallied

        Returns:
            Candidate: the preferred candidate after exclusions
        """
        for vote in ballot.votes:
            if vote not in self.excluded:
                return vote
        return None


class PreferentialInclusiveRound(PreferentialRound):
    """Class to run a preferential inclusive round on a ballot list
    
    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included(list<Candidate>): candidates to be considered

    Methods:
        __init__
        preferred
        result
    """

    def __init__(self, ballots, included):
        """Initializes a new preferential inclusive round

        Arguments:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included

    def preferred(self, ballot):
        """Selects the preferred candidate in a ballot, from the list of included candidates

        Arguments:
            ballot (Ballot): ballot to be tallied

        Returns:
            Candidate: the preferred candidate from the included
        """
        for vote in ballot.votes:
            if vote in self.included:
                return vote
        return None
    
    def result(self):
        """Computes the result of a preferential round

        Returns:
            RoundResult: The result of the preferential round
        """
        initial = {candidate: 0 for candidate in self.included}
        tally = Tally(initial)
        votes = len(self.ballots)
        for ballot in self.ballots:
            preferred = self.preferred(ballot)
            if preferred is None:
                votes -= 1
            else:
                tally.add_vote_to_candidate(preferred)
        return RoundResult(votes, tally)


##### Persistent tie breaker rounds

class RankedRound(Round):
    """Abstract class to run a ranked round

    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (optional(list<Candidate>)): candidates to be included in the tally. Defaults to None  

    Methods:
        __init__
        ballot_tally
        result
    """

    def __init__(self, ballots):
        """Initialize a new ranked round. This types of rounds have more than 1 votes per ballot

        Arguments:
            ballots (list<Ballot>): list of ballots to be tallied
        """
        super().__init__(ballots)
        self.included = None

    def ballot_tally(self, ballot):
        """Tally for an individual ballot

        Arguments:
            ballot (Ballot): ballot to be tallied

        Raises:
            NotImplementedError: Needs to be implemented by children
        """
        raise NotImplementedError('RankedRound.ballot_tally: This method is not implemented')

    def result(self):
        """Computes the result of a ranked round

        Returns:
            RoundResult: The result of a ranked round
        """
        if self.included is None:
            tally = Tally()
        else:
            tally = Tally({candidate: 0 for candidate in self.included})
        votes = 0
        for ballot in self.ballots:
            ballot_tally = self.ballot_tally(ballot)
            if not ballot_tally.is_empty():
                tally.merge(ballot_tally)
                votes += sum(ballot_tally.items.values())
        return RoundResult(votes, tally)        


class ConstantRankedRound(RankedRound):
    """Class to run an approval voting round (i.e.in which all preferences are considered equal)
    
    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
    
    Methods:
        __init__
        ballot_tally
        result
    """

    def __init__(self, ballots, included):
        """Initialize a new approval voting round

        Arguments:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included
    
    def ballot_tally(self, ballot):
        """Add 1 vote for each candidate named in the ballot and included in the tally

        Arguments:
            ballot (Ballot): ballot to be tallied

        Returns:
            Tally: tally of the ballot
        """
        return Tally({k:1 for k in (set(ballot.votes) & set(self.included))})


class BordaRankedRound(RankedRound):
    """Class to run a preferential vote with borda counting (i.e. arithmetic decreasing progression)
    
    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
    
    Methods:
        __init__
        ballot_tally
        result
    """

    def __init__(self, ballots, included):
        """Initialize a new borda ranked round

        Arguments:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included

    def ballot_tally(self, ballot):
        """Add 8 votes for 1st candidate, 7 for second, ...

        Arguments:
            ballot (Ballot): ballot to be tallied

        Returns:
            Tally: tally of the ballot
        """
        dict = {}
        for i in range(len(ballot.votes)):
            if ballot.votes[i] in self.included:
                dict[ballot.votes[i]] = 8 - i
        return Tally(dict)


class FirstPastThePostRound(RankedRound):
    """Class to run a first-past-the-post round (1st preference)

    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
        round (int): which round is being done (look at the nth preference depending on round)

    Methods:
        __init__
        ballot_tally
        result
    """

    def __init__(self, ballots, included, round = 1):
        """Initialize a first-past-the-post round

        Arguments:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
            round (optional(int)): which round is being done. Defaults to 1.
        """
        super().__init__(ballots)
        self.included = included
        self.round = round - 1

    def ballot_tally(self, ballot):
        if (len(ballot.votes) > self.round+1) and (ballot.votes[self.round] in self.included):
            return Tally({ballot.votes[self.round]: 1})
        return Tally()


class PresidentialRound(Round):
    """Class to run a presidential round (1st preference)

    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
        max_w (int): maximum number of winning candidates (1 by default)
    
    Methods:
        __init__
        result
    """

    def __init__(self, ballots, included, max_w = 1):
        """Initialize a presidential round

        Arguments:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
            max_winners (optional(int)): maximum number of winning candidates.
        """
        super().__init__(ballots)
        self.included = included
        self.max_w = max_w

    def result(self, interface):
        """Compute the result of the round

        Arguments:
            interface (IOInterface): Class used to input the presidential election
        
        Returns:
            RoundResult: result of the round
        """
        choice = interface.get_presidential_choices(self.included, self.max_w)
        tally = Tally({candidate: 0 for candidate in self.included})
        votes = len(choice)
        for candidate in choice:
            tally.add_vote_to_candidate(candidate)

        return RoundResult(votes, tally)



################################################################################
################################### Election ###################################
################################################################################


class Election:
    """Class to run an election

    Attributes:
        ballot_size(int): number of candidates to be elected
        seats(list<str>): names of the seats to be filled
        candidates(list<Candidate>): candidates running for election
        ballots(list<Ballot>): ballots casted

    Methods:
        __init__
        tiebreaker
        persistent_tie_rounds
        run
    """

    def __init__(self, candidates, ballots, interface):
        """Initialize a new election

        Arguments:
            candidates(list<Candidate>): candidates running for election
            ballots(list<Ballot>): ballots casted
            interface (IOInterface): Class used to input the presidential election
        """
        self.candidates = candidates
        self.ballots = ballots
        self.interface = interface

    def tiebreaker(self, candidates, lvl, max_winners = 1):
        """Tiebreaker for an inclusive round

        Arguments:
            candidates (list<Candidate>): candidates to be considered
            lvl (int): indentation of logs
            max_winners (int): maximum number of winners to be considered

        Returns:
            RoundResult: result of the last round of the tiebreaker
        """
        assert len(candidates) > max_winners
        
        log.info(indent("Aplicando voltas de desempate intermédias (4.4).", lvl))
        i = 1
        log.info('')
        log.info(indent(f'Resultados da {i}ª volta de desempate:', lvl))
        round = PreferentialInclusiveRound(self.ballots, candidates).result()
        log.info(indent(round, lvl+1))
        
        ## Successive preferential rounds
        while len(round.first) > max_winners:
            i += 1
            ## Persistent tie
            if candidates == round.first:
                round = Election.persistent_tie_rounds(self, candidates, lvl, max_winners)
                break
            ## Progression (number of winners decreases)
            else:
                candidates = round.first
                round = PreferentialInclusiveRound(self.ballots, candidates).result()
                log.info('')
                log.info(indent(f'Resultados da {i}ª volta de desempate:', lvl))
                log.info(indent(round, lvl+1))

        return round

    def persistent_tie_rounds(self, candidates, lvl, max_winners = 1, presidential_round = True):
        """Run persistent tie rounds

        Arguments:
            candidates (list<Candidate>): candidates to be considered
            lvl (int): indentation of logs
            presidential_round (bool) = in case of absolute tie, should a presidential round be run? (default: True) 
            max_winners (int): maximum number of winners to be considered

        Returns:
            RoundResult: result of the last round of the tiebreaker
        """
        log.info(indent('Empate persistente (5). Aplicando critérios de desempate.', lvl))
        ## Candidate with most votes wins @5.1
        log.info('')
        log.info(indent('Vence o nome que está em mais boletins (5.1):', lvl))
        round = ConstantRankedRound(self.ballots, candidates).result()
        log.info(indent(round, lvl+1))
        if len(round.first) <= max_winners:
            return round
        ## Tiebreaker with Borda system @5.2
        log.info('')
        log.info(indent('Pontuação com sistema de Borda (5.2):', lvl))
        round = BordaRankedRound(self.ballots, candidates).result()
        log.info(indent(round, lvl+1))
        if len(round.first) <= max_winners:
            return round
        
        ## Presidential round @5.5
        if presidential_round:
            log.info('')
            log.info(indent('Empate absoluto, a decisão pertence ao Presidente (5.3)', lvl))
            round = PresidentialRound(self.ballots, round.first, max_winners).result(self.interface)
            log.info(indent(round, lvl+1))
        
        return round

    def run(self):
        """Run an election (## for flow control, # for normal comments, @ for references to statutes)"""
        # Log candidates and ballots
        lvl = 0
        elected = []
        log.info(subtitle_str('Dados iniciais'))
        log.info('Candidatos:')
        for i in range(len(self.candidates)):
            log.info(indent(f'{i+1}. {self.candidates[i]}', lvl+1))
        log.info('')
        log.info('Boletins:')
        for ballot in self.ballots:
            log.info(indent(ballot, lvl+1))       
        
        # Run election for each seat
        for seat in self.seats:
            log.info('')
            log.info(subtitle_str(f'Eleição {seat}'))
            ## 1st round
            first_round = PreferentialExclusiveRound(self.ballots, elected).result()
            round = first_round
            # This variable stores the winners of the first round (+1st round tiebreakers)
            winners = round.first
            log.info(indent('1ª volta:', lvl))
            log.info(indent(round, lvl+1))
            
            # No more ballots left to count, the substitute is elected by the president
            if len(winners) == 0:
                log.info('Não há mais boletins para contar, o candidato é eleito pelo Presidente (5.3).')
                round = PresidentialRound(self.ballots, list(set(self.candidates) - set(elected))).result(self.interface)
                log.info(indent(round, lvl+1))
                elected += round.first
                log.info(indent(f'O cargo de {seat} foi atribuído a: {str(round.first[0])}.', lvl))
                continue
    
            ## Winner in 1st round with absolute majority @3
            if round.over_half(1):
                elected += winners
                log.info(indent(f'{str(winners[0])} vencedor por maioria na 1ª volta (3).', lvl))
                log.info(indent(f'O cargo de {seat} foi atribuído a: {str(winners[0])}.', lvl))
                continue
            
            ## No winner by majority in 1st round @4
            log.info(indent("Não houve vencedor por maioria na 1ª volta (4).", lvl))
            
            ## More than two winners in 1st round (tie breaker round) @4.1
            if len(winners) > 2:
                log.info(indent('Mais de dois vencedores na 1ª volta (4.1).', lvl))
                round = self.tiebreaker(winners, lvl, 2)
                winners = round.first
            
            ## One winner after 1st round (+ tie breaker rounds) @4.2
            if len(winners) == 1:
                log.info(indent(f'Apenas um vencedor ({winners[0]}) na 1ª volta (4.2).', lvl))
                # Save the winner of the first round for the second round
                finalists = winners
                    
                ## Sum of two most voted is over half @4.2.a)
                if first_round.over_half(2):
                    log.info(indent(f'Soma dos dois primeiros superior a 50% ({first_round.sum_percentages(2)*100:.1f}%) na 1ª volta (4.2.1).', lvl))
                    ## Tie for second place @4.2.a).i)
                    if len(round.second) > 1:
                        log.info(indent('Existe empate para segundo lugar (4.2.1.1).', lvl))
                        round = self.tiebreaker(round.second, lvl)
                        finalists += round.first
                    ## No tie for second place @4.2.a).ii)
                    else:
                        log.info(indent('Não existe empate para segundo lugar (4.2.1.2). ', lvl))
                        log.info(indent(f'2ª volta com os dois primeiros ({str(winners[0])} e {str(round.second[0])}).', lvl))
                        finalists += round.second
                        
                ## Sum of two most voted is less than half @4.2.b)
                else:
                    log.info(indent(f'Soma dos dois primeiros igual ou inferior a 50% ({first_round.sum_percentages(2)*100:.1f}%) na 1ª volta (4.2.2).', lvl)) 
                    log.info(indent(f'Passa a ser determinado o oponente do vencedor ({str(winners[0])}) para a 2ª volta.', lvl))
                    round = PreferentialExclusiveRound(self.ballots, elected + winners).result()
                    log.info('')
                    log.info(indent('Volta intermédia:', lvl))
                    log.info(indent(round, lvl+1))
                    if len(round.first) > 1:
                        log.info(indent('Existe empate na volta intermédia.', lvl))
                        round = self.tiebreaker(round.first, lvl)
                    finalists += round.first
                    
            ## Two winners after 1st round (+ tie breaker rounds) @4.3
            else:
                log.info(indent(f'Empate na 1ª volta ({str(winners[0])} e {str(winners[1])}) (4.3).', lvl))
                ## Sum of two most voted is over half @4.3.c)
                if first_round.over_half(2):
                    log.info(indent(f'Soma dos dois primeiros ({str(winners[0])} e {str(winners[1])}) superior a 50% ({first_round.sum_percentages(2)*100:.1f}%) na 1ª volta (4.3.1).', lvl))
                    finalists = winners
                ## Sum of two most voted is less than half
                else:
                    ## Sum of three most voted is less than half @4.3.d)
                    if not first_round.over_half(3):
                        log.info(indent(f'Soma dos três primeiros igual ou inferior a 50% ({first_round.sum_percentages(3)*100:.1f}%) na 1ª volta (4.3.2).', lvl))
                        log.info(indent('Passa a ser determinado o primeiro candidato de entre os dois vencedores da 1ª volta.', lvl))
                        # Intermediate round to determine first candidate
                        round = PreferentialInclusiveRound(self.ballots, winners).result()
                        log.info('')
                        log.info(indent('1ª volta intermédia:', lvl))
                        log.info(indent(round, lvl+1))
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na 1ª volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl)
                        finalists = round.first
                        # Second intermediate round without the first candidate
                        round = PreferentialExclusiveRound(self.ballots, elected + finalists).result()
                        log.info('')
                        log.info(indent('2ª volta intermédia:', lvl))
                        log.info(indent(round, lvl+1))
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na 2ª volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl)
                        finalists += round.first
                    ## Sum of three most voted is over half @4.3.e)
                    else:
                        log.info(indent(f'Soma dos três primeiros superior a 50% ({first_round.sum_percentages(3)*100:.1f}%) na 1ª volta (4.3.3).', lvl))
                        log.info(indent('Passa a ser determinado o terceiro candidato sem os dois vencedores da 1ª volta.', lvl))
                        round = PreferentialExclusiveRound(self.ballots, elected + winners).result()
                        log.info('')
                        log.info(indent('Volta intermédia:', lvl))
                        log.info(indent(round, lvl+1))
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl)
                        finalists = winners + round.first
                        # Special second round (no presidential election if absolute tie, normal second round with the first two)
                        round = PreferentialInclusiveRound(self.ballots, finalists).result()
                        log.info('')
                        log.info(indent('2ª volta especial:', lvl))
                        log.info(indent(round, lvl+1))
                        # Single winner
                        if len(round.first) == 1:
                            elected += round.first
                            log.info(indent(f'O cargo de {seat} foi atribuído a: {str(round.first[0])}.', lvl))
                            continue
                        # Tie
                        log.info(indent('Existe empate na 2ª volta especial.', lvl))
                        round = self.persistent_tie_rounds(round.first, lvl, 1, False)
                        # Successful tie breaker
                        if len(round.first) == 1:
                            elected += round.first
                            log.info(indent(f'O cargo de {seat} foi atribuído a: {str(round.first[0])}.', lvl))
                            continue
                        # Absolute tie
                        else:
                            log.info(indent('Existe empate absoluto na 2ª volta especial.', lvl))
                            finalists = winners
                            
            ## Second round
            lvl = 0
            log.info('')
            log.info(indent('2ª volta:', lvl))
            round = PreferentialInclusiveRound(self.ballots, finalists).result()
            log.info(indent(round, lvl+1))
            if (len(round.first) > 1):
                log.info(indent('Existe empate na segunda volta.', lvl))
                round = self.persistent_tie_rounds(round.first, lvl)
            elected += round.first
            log.info(indent(f'O cargo de {seat} foi atribuído a: {str(round.first[0])}.', lvl))

        ## End of election, log and output results
        log.info(subtitle_str('Resultados'))
        for i in range(len(self.seats)):
            log.info(indent(f'{self.seats[i]}: {str(elected[i])}', 1))

        self.interface.output_results(self.seats, elected)


class ChamberElection(Election):
    """Class to run a Chamber election

    Attributes:
        ballot_size(int): number of candidates to be elected
        seats(list<str>): names of the seats to be filled
        candidates(list<Candidate>): candidates running for election
        ballots(list<Ballot>): ballots casted
        chamber(str): name of the chamber

    Methods:
        __init__
        tiebreaker
        persistent_tie_rounds
        set_chamber
        run
    """
    type = TYPE_NC
    ballot_size = 4
    seats = ['I Vogal', 'II Vogal', 'III Vogal']
    
    def set_chamber(self, name):
        """Sets the chamber name

        Arguments:
            name(str): name of the chamber
        """
        self.chamber = name
    
    def run(self):
        log.info(title_str(f'Eleições {self.chamber} Câmara'))
        super().run()
        log.info(title_str('FIM'))

class SuperiorCouncilElection(Election):
    """Class to run a Superior Council election

    Attributes:
        ballot_size(int): number of candidates to be elected
        seats(list<str>): names of the seats to be filled
        candidates(list<Candidate>): candidates running for election
        ballots(list<Ballot>): ballots casted

    Methods:
        __init__
        tiebreaker
        persistent_tie_rounds
        run
    """
    type = TYPE_CS
    ballot_size = 8
    seats = ['I Conselheiro', 'II Conselheiro', 'III Conselheiro', 
             'IV Conselheiro', 'V Conselheiro', 'VI Conselheiro', 
             'VII Conselheiro', 'VIII Conselheiro', 'I Suplente', 
             'II Suplente', 'III Suplente', 'IV Suplente']
    
    def run(self):
        log.info(title_str('Eleições Conselho Superior'))
        super().run()
        log.info(title_str('FIM'))


################################################################################
#####################################  App  ####################################
################################################################################

class App():
    """Main application class"""
    
    def __init__(self, election_type = -1, candidates = [], ballots = [], interface=CLInterface()):
        self.election_type = election_type
        self.candidates = candidates.copy()
        self.ballots = ballots.copy()
        self.interface = interface
        
    def is_set(self):
        return self.election_type != -1 and len(self.candidates) > 0 and len(self.ballots) > 0
    
    def run(self, export_path = ''):
        self.interface.welcome()
        if (len(log.handlers) == 1): # Only console handler
            path = self.interface.ask_log_export()
            if path != '':
                file_handler = logging.FileHandler(path, mode='w', encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(FORMATTER)
                log.addHandler(file_handler)
        if not self.is_set():
            path = self.interface.ask_csv_import()
            if path != '':
                self.election_type, self.candidates, self.ballots = parse_csv(path)
            else:
                self.election_type = self.interface.get_election_type()
                self.candidates = self.interface.get_candidates(self.candidates)
                self.ballots = self.interface.get_ballots(self.election_type, self.candidates, self.ballots)
                self.interface.ask_csv_export(self.election_type, self.candidates,self.ballots)
        if export_path != '':
            export_csv(export_path, self.election_type, self.candidates, self.ballots)
        if self.election_type == TYPE_CS:
            election = SuperiorCouncilElection(self.candidates, self.ballots, self.interface)
        elif self.election_type == TYPE_NC:
            election = ChamberElection(self.candidates, self.ballots, self.interface)
            election.set_chamber(self.interface.get_chamber_name())
        else:
            raise ValueError('App.run: Invalid Election Type.')
        election.run()
        print("Pressione qualquer tecla para saír...")
        getchar()



################################################################################
####################################  Main  ####################################
################################################################################

if __name__ == '__main__':
    import argparse
    from datetime import datetime
    import sys
    import os

    LOG_DIR = os.path.join(os.path.normpath(__file__ + 2*(os.sep + os.pardir)), 'logs')
    OUT_DIR = os.path.join(os.path.normpath(__file__ + 2*(os.sep + os.pardir)), 'out')
    LOG_FILENAME = os.path.join(LOG_DIR, datetime.today().strftime("%Y-%m-%d_%H-%M-%S") + '.log')
    OUT_FILENAME = os.path.join(OUT_DIR, datetime.today().strftime("%Y-%m-%d_%H-%M-%S") + '.csv')
    
    ## Argument parsing
    
    parser = argparse.ArgumentParser(
        description='Program to run Senate\'s elections.',
        epilog=__copyright__,
        add_help=False)
    
    parser.add_argument('-h', '--help', action='help', help='Display this message and exit.')
    group_csv = parser.add_mutually_exclusive_group()
    group_csv.add_argument('-icsv', '--input-csv', type=str, help='CSV file with the ballots.')
    group_csv.add_argument('-ocsv', '--output-csv', action='store_true', help='Save ballots to csv file.')
    group_ui = parser.add_mutually_exclusive_group()
    group_ui.add_argument('-cli', '--command-line', action='store_true', help='Executes the program in command line mode. This is the behaviour by default.')
    # group.add_argument('-gui', '--graphical-user-interface', action='store_true', help='Executes the program in graphical user interface mode.')
    # group.add_argument('-web', '--web-interface', action='store_true', help='Executes the program in web interface mode.')
    # parser.add_argument('-p', '--port', type=int, default=8080, help='Port to run the web interface. (default: 8080)')
    parser.add_argument('-l', '--log', action='store_true', help='Save log to file.')
    
    args = parser.parse_args()
    if args.command_line:
        interface = CLInterface()
    # elif Arguments.graphical_user_interface:
    #     raise NotImplementedError('Graphical User Interface not implemented.')
    # elif Arguments.web_interface:
    #     raise NotImplementedError('Web Interface not implemented.')
    else:
        interface = CLInterface() # Default
    
    ## Add log handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(FORMATTER)
    log.addHandler(console_handler)
    if (args.log):
        root_log = logging.getLogger()
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        file_handler = logging.FileHandler(LOG_FILENAME, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(FORMATTER)
        root_log.addHandler(file_handler)
    
    
    ## Import election_type, candidates and ballots from CSV
    if (args.input_csv):
        election_type, candidates, ballots = parse_csv(args.input_csv)
        app = App(election_type, candidates, ballots, interface)
    else:
        app = App(interface=interface)
    
    if (args.output_csv):
        if not os.path.exists(OUT_DIR):
            os.makedirs(OUT_DIR)
        app.run(OUT_FILENAME)
    else:
        app.run()