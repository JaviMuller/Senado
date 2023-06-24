__author__ = "Javier de Muller"
__copyright__ = "Copyright (C) 2023 Javier de Muller"
__license__ = "MIT License"
__version__ = "0.9"

from ordered_set import OrderedSet
from functools import reduce
import logging

log = logging.getLogger(__name__)


################################################################################
################################### Auxiliary ##################################
################################################################################


TYPE_CS = 1
TYPE_NC = 2

def indent(text, lvl):
    """Function to indent a text for a given number of levels

    Args:
        text (string): text to be indented
        lvl (int): number of levels to indent

    Returns:
        string: indented text
    """
    spacer = 4 * ' ' * lvl
    return '\n'.join((spacer + line) for line in text.splitlines())



################################################################################
############# Base classes: Classes that give support to the rest ##############
################################################################################


class Candidate:
    """Class that represents a candidate
    
    Attributes:
        name (str): name of the candidate
    
    Methods:
        __init__
        __str__
    """

    def __init__(self, name):
        """Initialize a new candidate

        Args:
            name (string): name of the candidate
        """
        self.name = name

    def __str__(self):
        """String representation of a candidate

        Returns:
            string: the candidate's name
        """
        return self.name

    def initals(self):
        return ''.join([x[0].upper() for x in self.name.split(' ')])


class Ballot:
    """Class that stores the ballot of a person
    
    Attributes:
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
    
    Methods:
        __init__
        is_valid
        add_vote
        __str__
    """

    def __init__(self, votes = []):
        """This function initializes a new ballot.

        Args:
            votes (optional(list<Candidate>)): Candidates by preferential order. Defaults to []
        """
        self.votes = OrderedSet(votes)

    def is_valid(self):
        """Checks if a ballot has a correct number of votes and each vote is a candidate

        Returns:
            bool: true if the ballot has a correct number of votes and each vote is a candidate
        """
        return reduce(lambda x, y: x and y, [isinstance(x, Candidate) for x in self.votes])

    def add_vote(self, candidate):
        """Adds a vote to a ballot

        Args:
            candidate (Candidate): Candidate to be added to the ballot

        Raises:
            TypeError: If candidate is not of type Candidate
            RuntimeError: If ballot doesn't have more capacity
        """
        if not isinstance(candidate, Candidate):
            raise TypeError('Ballot.add_vote: candidate is not of type Candidate')
        self.votes = self.votes.add(candidate)

    def __str__(self):
        """String representation of a vote

        Returns:
            string: Description of type of vote plus each vote, one per line in preferential order.
        """
        raise NotImplementedError('Ballot.__str__ not implemented')


class Tally:
    """Class that stores the tally of votes

    Attributes:
        items(dict<Candidate: int>): Dictionary of candidates and their tallies
    
    Methods:
        __init__
        to_ordered_list
        merge
        is_empty
        add_vote_to_candidate
    """

    def __init__(self, items = {}):
        """Initializes a tally
        
        Args:
            items (optional(dict<Candidate: int>)): Dictionary of candidates and their tallies. Defaults to {}.
        """
        self.items = items

    def to_ordered_list(self):
        """Transforms the tally into an ordered list with decreasing order of votes

        Returns:
            list<list[2]<Candidate, int>>: List of candidates and their votes ordered by \
                decreasing number of votes
        """
        return sorted(self.items(), key = lambda item: item[1])

    def merge(self, tally):
        """Merges two tallies into a single one

        Args:
            tally (Tally): second tally to be added

        Returns:
            Tally: the merged tally 
        """
        for candidate in tally.items.keys():
            self.items[candidate] = self.items.get(candidate, 0) + tally.items[candidate]

    def is_empty(self):
        return len(self.items) == 0

    def add_vote_to_candidate(self, candidate):
        self.items[candidate] = self.items.get(candidate, 0) + 1


class RoundResult:
    """Class that stores the result of a round

    Attributes:
        votes (int): number of votes considered
        tally (list<list<Candidate, votes>>): Results of the round in an ordered list
        first (list<Candidate>): list of candidates tied for first place
        second (list<Candidate>): list of candidates tied for second place
        percentages: list of percentages corresponding to the votes in tally

    Methods:
        __init__
        single_winner
        tie_second
        over_half
        __str__
    """

    dash = 52 * '-'
    result_header = f'{"NOME":^30s}{"VOTOS":^10s}{"PERCENTAGEM":^12s}'

    def __init__(self, votes, tally):
        """Initialize a round result

        Args:
            votes (int): number of votes considered
            tally (Tally): Results of the round
        """
        self.votes = votes
        self.res = tally.to_ordered_list()
        self.first = [x[0] for x in self.res if x[1] == self.res[0][1]]
        self.second = [x[0] for x in self.res[len(self.first):] if x[1] == self.res[len(self.first)][1]]
        self.percentages = [x[1]/self.votes for x in self.res]

    def single_winner(self):
        """Function to check if a round has had a single winner

        Returns:
            bool: True if the round has had a single winner, False otherwise
        """
        return len(self.first) == 1

    def tie_second(self):
        """Function to check if there has been a tie for secon place

        Returns:
            bool: True if there is a tie for second place, False otherwise
        """
        return len(self.second) != 1

    def over_half(self, n):
        """Function to check if the top n candidates have over half the votes

        Args:
            n (int): number of top candidates to consider

        Returns:
            bool: True if the top n candidates have over half the votes, False otherwise
        """
        return sum(self.percentages[0:n]) > 0.5

    def __str__(self):
        """String representation of a tally

        Returns:
            str: representation of tally
        """
        return ('\n'.join(f'Número de votos contabilizados: {self.votes}.',
                         '', 
                         f'Resultados:',
                         '',
                         RoundResult.dash,
                         RoundResult.result_header,
                         RoundResult.dash,
                         #         Nome       Votos           Percentagem
                         '\n'.join(
                             [f'{x[0]:<30s}{x[1]:^10s}{(x[1]/self.votes*100):^12.1f}' 
                             for x in self.res]) 
                         )
        )



################################################################################
################################ Concrete Ballots ##############################
################################################################################


class ChamberBallot(Ballot):
    """Class that stores the ballot of a person for the Chamber elections
    
    Attributes:
        votes (OrderedSet<Candidate>): Votes of the person by preferential order  (inherits from Ballot)
    
    Methods:
        __init__  (inherits from Ballot)
        is_valid  (extends Ballot.is_valid)
        add_vote  (extends Ballot.add_vote)
        __str__   (overrides Ballot.__str__)
    """

    def is_valid(self):
        return self.votes.size <= 4 and super().is_valid()

    def add_vote(self, candidate):
        if self.votes.size >= 4:
            raise RuntimeError('ChamberBallot.add_vote: ballot is full')
        super().add_vote(candidate)

    def __str__(self):
        ret = 'Voto Câmara:\n'
        for i in range(len(self.votes)):
            ret += f' {i+1:>2s}.    {self.votes[i]}\n'
        return ret


class SuperiorCouncilBallot(Ballot):
    """Class that stores the ballot of a person for the Superior Council elections
    
    Attributes:
        votes (OrderedSet<Candidate>): Votes of the person by preferential order  (inherits from Ballot)
    
    Methods:
        __init__  (inherits from Ballot)
        is_valid  (extends Ballot.is_valid)
        add_vote  (extends Ballot.add_vote)
        __str__   (overrides Ballot.__str__)
    """

    def is_valid(self):
        return self.votes.size() <= 8 and super().is_valid()

    def add_vote(self, candidate):
        if self.votes.size >= 8:
            raise RuntimeError('SuperiorCouncilBallot.add_vote: ballot is full')
        super().add_vote(candidate)

    def __str__(self):
        ret = 'Voto Conselho Superior:\n'
        for i in range(len(self.votes)):
            ret += f' {i+1:>2s}.    {self.votes[i]}\n'
        return ret



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
    """

    def __init__(self, ballots):
        """Initializes a round by attaching the ballots to it

        Args:
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

        Args:
            ballots (list<Ballot>): list of ballots to be tallied
        """
        super().__init__(ballots)

    def preferred(self, ballot):
        """Abstract method to select the preferred candidate of a ballot

        Args:
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
    """

    def __init__(self, ballots, excluded = []):
        """Initializes a new preferential exclusive round
        
        Args:
            ballots (list<Ballot>): Ballots to be tallied
            excluded (list<Candidate>): Exclude candidates from tally. Defaults to []
        """
        super().__init__(ballots)
        self.excluded = excluded

    def preferred(self, ballot):
        """Selects the preferred candidate in a ballot, exculding the candidates that need to be excluded

        Args:
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
    """

    def __init__(self, ballots, included):
        """Initializes a new preferential inclusive round

        Args:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included

    def preferred(self, ballot):
        """Selects the preferred candidate in a ballot, from the list of included candidates

        Args:
            ballot (Ballot): ballot to be tallied

        Returns:
            Candidate: the preferred candidate from the included
        """
        for vote in ballot.votes:
            if vote in self.included:
                return vote
        return None


##### Persistent tie breaker rounds

class RankedRound(Round):
    """Abstract class to run a ranked round

    Attributes:
        ballots (list<Ballot>): ballots to be tallied

    Methods:
        __init__
        ballot_tally
        result
    """

    def __init__(self, ballots):
        """Initialize a new ranked round. This types of rounds have more than 1 votes per ballot

        Args:
            ballots (list<Ballot>): list of ballots to be tallied
        """
        super().__init__(ballots)

    def ballot_tally(self, ballot):
        """Tally for an individual ballot

        Args:
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
        tally = Tally()
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
    """

    def __init__(self, ballots, included):
        """Initialize a new approval voting round

        Args:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included
    
    def ballot_tally(self, ballot):
        """Add 1 vote for each candidate named in the ballot and included in the tally

        Args:
            ballot (Ballot): ballot to be tallied

        Returns:
            Tally: tally of the ballot
        """
        return Tally({k:1 for k in (ballot.votes & self.included)})


class BordaRankedRound(RankedRound):
    """Class to run a preferential vote with borda counting (i.e. arithmetic decreasing progression)
    
    Attributes:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
    
    Methods:
        __init__
        ballot_tally
    """

    def __init__(self, ballots, included):
        """Initialize a new borda ranked round

        Args:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
        """
        super().__init__(ballots)
        self.included = included

    def ballot_tally(self, ballot):
        """Add 8 votes for 1st candidate, 7 for second, ...

        Args:
            ballot (Ballot): ballot to be tallied

        Returns:
            Tally: tally of the ballot
        """
        dict = {}
        for i in range(len(ballot.votes)):
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
        result
    """

    def __init__(self, ballots, included, round = 1):
        """Initialize a first-past-the-post round

        Args:
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
        round (int): which round is being done (look at the nth preference depending on round)
    
    Methods:
        __init__
        result
    """

    def __init__(self, ballots, included):
        """Initialize a presidential round

        Args:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
            round (optional(int)): which round is being done. Defaults to 1.
        """
        super().__init__(ballots)
        self.included = included

    def result(self, interface):
        """Compute the result of the round

        Args:
            interface (IOInterface): Class used to input the presidential election
        
        Returns:
            RoundResult: result of the round
        """
        tally = Tally()
        votes = 1
        tally.add_vote_to_candidate(interface.get_presidential_choice(self.included))

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

        Args:
            candidates(list<Candidate>): candidates running for election
            ballots(list<Ballot>): ballots casted
            interface (IOInterface): Class used to input the presidential election
        """
        self.candidates = candidates
        self.ballots = ballots
        self.interface = interface

    def tiebreaker(self, candidates, lvl, max_winners = 1):
        """Tiebreaker for an inclusive round

        Args:
            candidates (list<Candidate>): candidates to be considered
            lvl (int): indentation of logs
            max_winners (int): maximum number of winners to be considered

        Returns:
            RoundResult: result of the last round of the tiebreaker
        """
        assert len(candidates) > max_winners
        
        log.info(indent("Aplicando rondas de desempate intermédias (4.4).", lvl))
        i = 1
        log.info(indent(f'Resultados da {i}ª ronda de desempate:', lvl))
        round = PreferentialInclusiveRound(self.ballots, candidates).result()
        log.info(indent(round, lvl+1))
        
        ## Successive preferential rounds
        while len(round.first) > max_winners:
            i += 1
            ## Persistent tie
            if candidates == round.first:
                round = Election.persistent_tie_rounds(self, candidates, lvl, 2)
                break
            ## Progression (number of winners decreases)
            else:
                round = PreferentialInclusiveRound(self.ballots, candidates).result()
                candidates = round.first
                log.info(indent(f'Resultados da {i}ª ronda de desempate:', lvl))
                log.info(indent(round, lvl+1))

        return round

    def persistent_tie_rounds(self, candidates, lvl, presidential_round = True, max_winners = 1):
        """Run persistent tie rounds

        Args:
            candidates (list<Candidate>): candidates to be considered
            lvl (int): indentation of logs
            max_winners (int): maximum number of winners to be considered

        Returns:
            RoundResult: result of the last round of the tiebreaker
        """
        log.info(indent('Empate persistente (5). Aplicando critérios de desempate.', lvl))
        ## Candidate with most votes wins @5.1
        log.info(indent('Vence o nome que está em mais boletins (5.1):', lvl))
        round = ConstantRankedRound(self.ballots, candidates).result()
        log.info(indent(round, lvl+1))
        if len(round.first) < max_winners:
            return round
        ## Tiebreaker with Borda system @5.2
        log.info(indent('Pontuação com sistema de Borda (5.2):', lvl))
        round = BordaRankedRound(self.ballots, candidates).result()
        if round.first < max_winners:
            return round
        
        ## Successive FPTP rounds @5.3 & @5.4
        for i in range(1, self.ballot_size+1):
            log.info(indent('Vence quem surja mais vezes em {i}ª preferência (5.3 & 5.4):', lvl))
            round = FirstPastThePostRound(self.ballots, round.first, i).result()
            log.info(indent(round, lvl+1))
            if len(round.first) < max_winners:
                return round
        
        ## Presidential round @5.5
        if presidential_round:
            log.info(indent('Empate absoluto, a decisão pertence ao Presidente (5.5)', lvl))
            round = PresidentialRound(self.ballots, round.first).result(self.interface)
            log.info(indent(round, lvl+1))
        
        return round

    def run(self):
        """Run an election (## for flow control, # for normal comments, @ for references to statutes)"""
        elected = []
        lvl = 0        
        
        for i in range(self.seats):
            log.info('')
            log.info(f'### Eleição {self.seats[i]}:\n')
            ## 1st round
            first_round = PreferentialExclusiveRound(self.ballots, elected).result()
            round = first_round
            # This variable stores the winners of the first round (+1st round tiebreakers)
            winners = round.first
            log.info(indent('1ª ronda:', lvl))
            log.info(indent(round, lvl+1))
            
            ## Winner in 1st round with absolute majority @3
            if round.over_half(1):
                elected += winners[0]
                log.info(indent('Vencedor por maioria na primeira ronda (3).', lvl))
                log.info(indent(f'O cargo de {self.seats[i]} foi atribuído a: {winners[0]}.', lvl))
                continue
            
            log.info(indent("Não houve vencedor por maioria na primeira ronda (4).", lvl))
            lvl += 1
            
            ## More than two winners in 1st round (tie breaker round) @4.1
            if len(winners) > 2:
                log.info(indent('Mais de dois vencedores na primeira ronda (4.1).'), lvl)
                round = self.tiebreaker(winners, lvl+1, 2)
                winners = round.first
            
            ## One winner after 1st round (+ tie breaker rounds) @4.2
            if len(winners) == 1:
                log.info(indent('Apenas um vencedor na primeira volta (4.2).', lvl))
                # Save the winner of the first round for the second round
                finalists = winners
                    
                ## Sum of two most voted is over half @4.2.a)
                if first_round.over_half(2):
                    log.info(indent('Soma dos dois primeiros superior a 50% na primeira volta (4.2.a).', lvl))
                    ## Tie for second place @4.2.a).i)
                    if len(round.second) > 1:
                        log.info(indent('Existe empate para segundo lugar (4.2.a.i).', lvl))
                        round = self.tiebreaker(round.second, lvl+1)
                    ## No tie for second place @4.2.a).ii)
                    else:
                        log.info(indent('Não existe empate para segundo lugar (4.2.a.ii). ', lvl))
                        log.info(indent('Segunda volta com os dois primeiros.', lvl))
                        finalists += round.second
                        
                ## Sum of two most voted is less than half @4.2.b)
                else:
                    i = 1
                    log.info(indent('Soma dos dois primeiros inferior a 50% (4.2.b).', lvl)) 
                    log.info(indent('Passa a ser determinado o oponente do vencedor para a segunda ronda.', lvl))
                    round = PreferentialExclusiveRound(self.ballots, elected + winners).result()
                    if len(round.first) > 1:
                        log.info(indent('Existe empate na volta intermédia.', lvl))
                        round = self.tiebreaker(round.first, lvl+1)
                    finalists += round.first
                    
            ## Two winners after 1st round (+ tie breaker rounds) @4.3
            else:
                ## Sum of two most voted is over half @4.3.c)
                if first_round.over_half(2):
                    log.info(indent('Soma dos dois primeiros superior a 50% na primeira volta (4.3.c).', lvl))
                    finalists = winners
                ## Sum of two most voted is less than half
                else:
                    ## Sum of three most voted is less than half @4.3.d)
                    if not first_round.over_half(3):
                        log.info(indent('Soma dos três primeiros inferior a 50% na primeira volta (4.3.d).', lvl))
                        log.info(indent('Passa a ser determinado o primeiro candidato de entre os dois vencedores da primeira ronda.', lvl))
                        # Intermediate round to determine first candidate
                        round = PreferentialInclusiveRound(self.ballots, winners)
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl+1)
                        finalists = winners
                        # Second intermediate round without the first candidate
                        round = PreferentialExclusiveRound(self.ballots, elected + finalists).result()
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl+1)
                        finalists += round.first
                    ## Sum of three most voted is over half @4.3.e)
                    else:
                        log.info(indent('Soma dos três primeiros superior a 50% na primeira volta (4.3.e).', lvl))
                        log.info(indent('Passa a ser determinado o terceiro candidato sem os dois vencedores da primeira ronda.', lvl))
                        round = PreferentialExclusiveRound(self.ballots, elected + winners).result()
                        if len(round.first) > 1:
                            log.info(indent('Existe empate na volta intermédia.', lvl))
                            round = self.tiebreaker(round.first, lvl+1)
                        finalists = winners + round.first
                        # Special second round (no presidential election if absolute tie, normal second round with the first two)
                        round = PreferentialInclusiveRound(self.ballots, finalists).result()
                        # Single winner
                        if len(round.first) == 1:
                            elected += round.first[0]
                            continue
                        # Tie
                        log.info(indent('Existe empate na segunda volta especial.', lvl))
                        round = self.persistent_tie_rounds(round.first, lvl+1, False)
                        # Successful tie breaker
                        if len(round.first) == 1:
                            elected += round.first[0]
                            continue
                        # Absolute tie
                        else:
                            log.info(indent('Existe empate absoluto na segunda volta especial.', lvl))
                            finalists = winners
                            
            ## Second round
            lvl = 0
            log.info(indent('1ª ronda:', lvl))
            round = PreferentialInclusiveRound(self.ballots, finalists).result()
            if (len(round.first) > 1):
                log.info(indent('Existe empate na segunda volta.', lvl))
                round = self.persistent_tie_rounds(round.first, lvl+1)
            elected += round.first

        ## End of election, output results
        self.interface.output_results(elected, self.seats)


class ChamberElection(Election):
    """Class to run a Chamber election

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
    ballot_size = 4
    seats = ['I Vogal', 'II Vogal', 'III Vogal', 'I Suplente']
    
    def run(self):
        log.info('############################   Eleições Camarais   #############################')
        super().run()
        log.info('#####################################  FIM  ####################################')

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
    ballot_size = 8
    seats = ['I Conselheiro', 'II Conselheiro', 'III Conselheiro', 
             'IV Conselheiro', 'V Conselheiro', 'VI Conselheiro', 
             'VII Conselheiro', 'VIII Conselheiro', 'I Suplente', 
             'II Suplente', 'III Suplente', 'IV Suplente']
    
    def run(self):
        log.info('########################   Eleições Conselho Superior   ########################')
        super().run()
        log.info('#####################################  FIM  ####################################')
        


################################################################################
###################### IOInterfaces - Allow interactivity ######################
################################################################################

class IOInterface():
    def __init__(self):
        pass
    
    def get_election_type():
        pass
    
    def get_candidates():
        pass
    
    def get_ballots():
        pass
    
    def output_results():
        pass
    
    def get_presidential_choice(candidates):
        pass

class CLInterface():
    pass

class GUInterface():
    pass

class WebInterface():
    pass

################################################################################
#####################################  App  ####################################
################################################################################

class App():
    def __init__(self, interface=CLInterface()):
        self.interface = interface
    
    def run(self):
        election_type = self.interface.get_election_type()
        candidates = self.interface.get_candidates()
        ballots = self.interface.get_ballots(election_type)
        if election_type == TYPE_CS:
            election = SuperiorCouncilElection(candidates, ballots, self.interface)
        elif election_type == TYPE_NC:
            election = ChamberElection(candidates, ballots, self.interface)
        else:
            raise ValueError('App.run: Invalid Election Type.')
        election.run()



################################################################################
####################################  Main  ####################################
################################################################################


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Program to run Senate\'s elections.',
        epilog=__copyright__,
        add_help=False)
    
    parser.add_argument('-h', '--help', action='help', help='Mostra esta mensagem de ajuda e sai.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-cli', '--command-line', action='store_true', help='Executes the program in command line mode. This is the behaviour by default.')
    group.add_argument('-gui', '--graphical-user-interface', action='store_true', help='Executes the program in graphical user interface mode.')
    group.add_argument('-web', '--web-interface', action='store_true', help='Executes the program in web interface mode.')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port to run the web interface. (default: 8080)')
    
    args = parser.parse_args()
    if args.command_line:
        interface = CLInterface()
    elif args.graphical_user_interface:
        interface = GUInterface()
    elif args.web_interface:
        interface = WebInterface(args.port)
    else:
        interface = CLInterface() # Default
    
    app = App(interface)
    app.run()