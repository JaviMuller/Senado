from functools import reduce
from constants import *
from utils import *


################################################################################
################################# Base classes #################################
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
        
    def get_name(self):
        return self.name

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
        id (int): id of the ballot
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
        max_votes (int): Maximum number of votes of the ballot
    
    Methods:
        __init__
        is_valid
        add_vote
        __str__
    """

    def __init__(self, id, votes = []):
        """This function initializes a new ballot.

        Args:
            id (int): id of the ballot
            votes (optional(list<Candidate>)): Candidates by preferential order. Defaults to []
        """
        self.id = id
        self.votes = votes.copy()
        self.max_votes = -1
    
    def get_id(self):
        """Gets the id of the ballot

        Returns:
            int: ballot id
        """
        return self.id

    def get_max_votes(self):
        """Gets the maximum number of votes of a ballot

        Returns:
            int: maximum number of votes
        """
        return self.max_votes

    def get_votes(self):
        """Get the votes of a ballot

        Returns:
            list(Candidate): votes
        """
        return self.votes

    def is_valid(self):
        """Checks if a ballot has a correct number of votes and each vote is a candidate

        Returns:
            bool: true if the ballot has a correct number of votes and each vote is a candidate
        """
        return len(self.votes) <= self.max_votes and reduce(
            lambda x, y: x and y, [isinstance(x, Candidate) for x in self.votes])

    def add_vote(self, candidate):
        """Adds a vote to a ballot

        Args:
            candidate (Candidate): Candidate to be added to the ballot

        Raises:
            TypeError: If candidate is not of type Candidate
            RuntimeError: If ballot doesn't have more capacity
        """
        if not isinstance(candidate, Candidate):
            raise TypeError(f'{self.__class__.__name__}.add_vote: candidate is not of type Candidate')
        if len(self.votes) >= self.max_votes:
            raise RuntimeError(f'{self.__class__.__name__}.add_vote: ballot is full')
        self.votes.append(candidate)

    def __str__(self):
        """String representation of a vote

        Returns:
            string: Description of type of vote plus each vote, one per line in preferential order.
        """
        ret = f'Boletim de voto ({self.id}):\n'
        for i in range(len(self.votes)):
            ret += indent(f'{str(i+1):>2s}. {str(self.votes[i])}\n', 1)
        return ret


class ChamberBallot(Ballot):
    """Class that stores the ballot of a person for the Chamber elections
    
    Attributes:
        id (int): id of the ballot
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
        max_votes (int): Maximum number of votes of the ballot
    
    Methods:
        __init__  (inherits from Ballot)
        is_valid  (extends Ballot.is_valid)
        add_vote  (extends Ballot.add_vote)
        __str__   (overrides Ballot.__str__)
    """
    type = TYPE_NC
    
    def __init__(self, id, votes=[]):
        super().__init__(id, votes)
        self.max_votes = 4


class SuperiorCouncilBallot(Ballot):
    """Class that stores the ballot of a person for the Superior Council elections
    
    Attributes:
        id (int): id of the ballot
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
        max_votes (int): Maximum number of votes of the ballot
    
    Methods:
        __init__  (inherits from Ballot)
        is_valid  (extends Ballot.is_valid)
        add_vote  (extends Ballot.add_vote)
        __str__   (overrides Ballot.__str__)
    """
    type = TYPE_CS

    def __init__(self, id, votes=[]):
        super().__init__(id, votes)
        self.max_votes = 8


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
        self.items = items.copy()

    def to_ordered_list(self):
        """Transforms the tally into an ordered list with decreasing order of votes

        Returns:
            list<list[2]<Candidate, int>>: List of candidates and their votes ordered by \
                decreasing number of votes
        """
        output = [[key, value] for key, value in self.items.items()]
        return sorted(output, key = lambda x: x[1], reverse=True)

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
        """Checks if the tally is empty

        Returns:
            bool: True if the tally is empty
        """
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
    result_header = f'{" NOME":<30s}{"VOTOS":^10s}{"PERCENTAGEM":^12s}'

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

    def sum_percentages(self, n):
        """Function to sum the percentages of the top n candidates

        Args:
            n (int): number of top candidates to consider

        Returns:
            float: sum of the percentages of the top n candidates
        """
        return sum(self.percentages[0:n])
    
    def __str__(self):
        """String representation of a tally

        Returns:
            str: representation of tally
        """
        return ('\n'.join([f'Número de votos contabilizados: {self.votes}.',
                         '', 
                         f'Resultados:',
                         '',
                         RoundResult.dash,
                         RoundResult.result_header,
                         RoundResult.dash,
                         #         Nome       Votos           Percentagem
                         '\n'.join(
                             [f'{str(x[0]):<30}{str(x[1]):^10}{(x[1]/self.votes*100):^12.1f}' for x in self.res]),
                         ' '
                         ])
        )


################################################################################
############################## Auxiliary functions #############################
################################################################################

def parse_csv(path):
    """Parses the data from the import file

    Args:
        path (str): path to the import file
    
    Returns:
        tuple(election_type (int), candidates (list(Candidate)), ballots (list(Ballot))): election type, list of candidates and list of ballots
    """
    data = import_csv(path)
    candidates = [Candidate(name) for name in data['candidates']]
    if data['type'] == TYPE_CS:
        ballots = [SuperiorCouncilBallot(id, votes) for id, votes in data['ballots']]
    elif data['type'] == TYPE_NC:
        ballots = [ChamberBallot(id, votes) for id, votes in data['ballots']]    
    return data['type'], candidates, ballots