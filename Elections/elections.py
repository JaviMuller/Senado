from ordered_set import OrderedSet
from functools import reduce



################################################################################
############# Base classes: Classes that give support to the rest ##############
################################################################################


class Candidate:
    """Class that represents a candidate
    
    Attr:
        name (str): name of the candidate
    
    Meth:
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


class Ballot:
    """Class that stores the ballot of a person
    
    Attr:
        type (int): 1 -> Chamber, 2 -> Superior Council
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
    
    Meth:
        __init__
        is_valid
        add_vote
        __str__
    """

    def __init__(self, type = 1, votes = []):
        """This function initializes a new ballot. If the vote is for a chamber, \
            the number of votes should be 4. Otherwise, if it is for the \
                Superior Council, the number of votes should be 8.

        Args:
            type (int, optional): 1 -> Chamber, 2 -> Superior Council. Defaults to 1.
            votes (list<Candidate>, optional): Candidates by preferential order. Defaults to empty 
            
        Raises:
            ValueError: When the type is not 1 or 2
        """
        if (type not in (1, 2)):
            raise ValueError('Ballot.__init__: inexistent type')
        self.type = type
        self.votes = OrderedSet(votes)
    
    def is_valid(self):
        """Checks if a ballot has the correct number of votes

        Returns:
            bool: true if the ballot has the correct number of votes
        """
        if self.type == 1:
            return len(self.votes) <= 4
        if self.type == 2:
            return len(self.votes) <= 8
        
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
        if (self.type, len(self.votes)) in ((1, 4), (2, 8)):
            raise RuntimeError('Ballot.add_vote: max number of votes reached')
        self.votes = self.votes.add(candidate)
    
    def __str__(self):
        """String representation of a vote

        Returns:
            string: Description of type of vote plus each vote, one per line in preferential order.
        """
        ret = 'Voto' + ('C??mara' if self.type == 1 else 'Conselho Superior') + ':\n'
        for i in range(len(self.votes)):
            ret += f' {i+1:>2s}.\t{self.votes[i]}\n'
        return ret


class Tally:
    """Class that stores the tally of votes

    Attr:
        items(dict<Candidate: int>): Dictionary of candidates and their tallies
    
    Meth:
        __init__
        to_ordered_list
        merge
        is_empty
        add_vote_to_candidate
    """
    def __init__(self, items = {}):
        """Initializes a tally
        
        Args:
            items (dict<Candidate: int>, optional): Dictionary of candidates and their tallies
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
    
    Attr:
        votes (int): number of votes considered
        tally (list<list<Candidate, votes>>): Results of the round in an ordered list
        first (list<Candidate>): list of candidates tied for first place
        second (list<Candidate>): list of candidates tied for second place
        percentages: list of percentages corresponding to the votes in tally
        
    Meth:
        __init__
        single_winner
        tie_second
        over_half
        __str__
    """
    res_indentation = '\t\t'
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
        return (RoundResult.res_indentation + f'N??mero de votos contabilizados: {self.votes}.\n' + 
                RoundResult.res_indentation + f'Resultados:\n\n' +
                RoundResult.res_indentation + RoundResult.dash + '\n' +
                RoundResult.res_indentation + RoundResult.result_header + '\n' +
                RoundResult.res_indentation + RoundResult.dash + '\n' + 
                RoundResult.res_indentation + '\n'.join(
                    [f'{RoundResult.res_indentation}\t{x[0]:<30s}{x[1]:^10s}{(x[1]/self.votes*100):^12.1f}' 
                     for x in self.res])) 



################################################################################
################################ Election Rounds ###############################
################################################################################


class Round:
    """Abstract class to represent a round
    
    Attr:
        ballots (list<Ballot>): list of ballots to be tallied
        
    Meth:
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
    
    Attr:
        ballots (list<Ballot>)
    
    Meth:
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
    
    Attr:
        ballots (list<Ballot>): Ballots to be tallied
        excluded (list<Candidate>, optional): List of candidates to be removed from the tally
    
    Meth:
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
    
    Attr:
        ballots (list<Ballot>): ballots to be tallied
        included(list<Candidate>): candidates to be considered
    
    Meth:
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

    Attr:
        ballots (list<Ballot>): ballots to be tallied
    
    Meth:
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
    
    Attr:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
    
    Meth:
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
            _type_: _description_
        """
        return Tally({k:1 for k in ballot.votes & self.included})


class BordaRankedRound(RankedRound):
    """Class to run a preferential vote with borda counting (i.e. arithmetic decreasing progression)
    
    Attr:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
    
    Meth:
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
        return Tally(reduce(lambda d1, d2: 
            d1.update({d2: 8 - len(d1)}) if d2 in self.included else d1, 
            ballot.votes, {}))


class FirstPastThePostRound(Round):
    """Class to run a first-past-the-post round (1st preference)

    Attr:
        ballots (list<Ballot>): ballots to be tallied
        included (list<Candidate>): candidates to be included in the tally
        round (int): which round is being done (look at the nth preference depending on round)
    
    Meth:
        __init__
        result
    """
    def __init__(self, ballots, included, round = 1):
        """Initialize a first-past-the-post round

        Args:
            ballots (list<Ballot>): ballots to be tallied
            included (list<Candidate>): candidates to be included in the tally
            round (int, optional): which round is being done. Defaults to 1.
        """
        super().__init__(ballots)
        self.included = included
        self.round = round - 1
    
    def result(self):
        """Compute the result of the round

        Returns:
            RoundResult: result of the round
        """
        tally = Tally()
        votes = 0
        for ballot in self.ballots:
            if ballot.votes[round] in self.included:
                tally.add_vote_to_candidate(ballot.votes[round])
                votes += 1
        return RoundResult(votes, tally)



################################################################################
################################### Election ###################################
################################################################################


class Election:
    """Class to run an election
    
    Attr:
        type (int): 1 -> Chamber, 2 -> Superior Council
        candidates(list<Candidate>): candidates running for election
        ballots(list<Ballot>): ballots casted
    
    Meth:
        __init__
        run
    """
    def __init__(self, type, candidates, ballots):
        """Initialize a new election

        Args:
            type (int): 1 -> Chamber, 2 -> Superior Council
            candidates(list<Candidate>): candidates running for election
            ballots(list<Ballot>): ballots casted

        Raises:
            ValueError: Type needs to be either 1 or 2
        """
        if (type not in (1, 2)):
            raise ValueError('Ballot.__init__: inexistent type')
        self.type = type
        self.candidates = candidates
        self.ballots = ballots
    
    def run(self, verbose = True, verboser = False):
        """Run an election (## for flow control, # for normal comments)

        Args:
            verbose (bool, optional): Print the output of each round and the next round. Defaults to True.
            verboser (bool, optional): Print the output of each ballot (not implemented, for debugging purposes). Defaults to False.
        """
        elected = []
        if self.type == 1:
            positions = ['I Vogal', 'II Vogal', 'III Vogal']
            
            print('############################   Elei????es Camarais   #############################')
            
        else:
            positions = ['I Conselheiro', 'II Conselheiro', 'III Conselheiro', 
                         'IV Conselheiro', 'V Conselheiro', 'VI Conselheiro', 
                         'VII Conselheiro', 'VIII Conselheiro', 'I Suplente', 
                         'II Suplente', 'III Suplente', 'IV Suplente']
            
            print('########################   Elei????es Conselho Superior   ########################')
        
        print('')

        for i in range(positions):
            if verbose:
                print(f'### Elei????o {positions[i]}:\n')
            
            ## 1st round
            first_round = PreferentialExclusiveRound(self.ballots, elected).result()
            round = first_round
            winners = round.first
            if verbose:
                print(f'\tResultados 1?? ronda:')
                print(round)
                
            ## Winner in 1st round with absolute majority
            if round.over_half(1):
                elected += winners[0]
                if verbose:
                    print('\tVencedor por maioria na primeira ronda.')
                    print(f'\tO cargo de {positions[i]} foi atribu??do a: {winners[0]}.\n')
                continue
            
            ## More than two winners in 1st round (tie breaker round)
            if len(winners) > 2:
                i = 1
                round = PreferentialInclusiveRound(self.ballots, winners).result()
                if verbose:
                    print('\tMais de dois vencedores na primeira ronda. Passa-se ??s rondas de desempate.')
                    print(f'\tResultados da {i}?? ronda de desempate:')
                    print(round)
                while len(round.first) > 2:
                    i += 1
                    ## Persistent tie
                    if winners == round.first:
                        if verbose:
                            print('\tEmpate persistente. Aplicando crit??rios de desempate.')
                        round = Election.persistent_tie_rounds(self.ballots, winners, max=2, verbose=verbose,
                                                               verboser=verboser)
                        winners = round.first
                        break
                    ## Progression (number of winners decreases)
                    else:
                        round = PreferentialInclusiveRound(self.ballots, winners).result()
                        winners = round.first
                        if verbose:
                            print(f'\tResultados da {i}?? volta de desempate:')
                            print(round)
            
            ## One winner after 1st round (+ tie breaker round)
            if len(winners) == 1:
                if verbose:
                    print('\tApenas um vencedor na primeira volta.')
                    
                ## Sum of two most voted is over half
                if first_round.over_half(2):
                    # Store the winner of the first round for the second round
                    finalists = winners
                    if verbose:
                        print('\tSoma dos dois primeiros superior a 50% na primeira volta.')
                    ## No tie for second place
                    if len(round.second) == 1:
                        if verbose:
                            print('\tN??o existe empate entre os segundos lugares. ' +
                                  'Segunda volta com os dois primeiros.')
                        finalists += round.second
                    ## Tie exists for second place
                    else:
                        if verbose:
                            print('\tExiste empate entre os segundos lugares.')
                        winners = round.second
                        round = PreferentialInclusiveRound(self.ballots, round.second)
                        ## More than a winner in intermediate round
                        while len(round.first) > 1:
                            ## Persistent tie
                            if winners == round.first:
                                if verbose:
                                    print('\tEmpate persistente. Aplicando crit??rios de desempate.')
                                round = Election.persistent_tie_rounds(self.ballots, winners, max=1, verbose=verbose,
                                                               verboser=verboser)
                        winners = round.first 
                            

                        
                # Sum of two most voted is less than half
                else:
                    i = 1
                    round = PreferentialExclusiveRound(self.ballots, elected + winners)
                    if verbose:
                        print('\tSoma dos dois primeiros inferior a 50%. ' +
                              'Passa a ser determinado o oponente do vencedor para a segunda ronda')
                        print(f'\tResultado da {i}?? ronda de desempate:')
                        print(round)
                    
            # Two winners after 1st round
            else:
                
                                
            # Second round