from ordered_set import OrderedSet
from functools import reduce


class Candidate:
    """Class that represents a candidate
    
    Attr:
        name (str): name of the candidate
    """
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name


class Ballot:
    """Class that stores the ballot of a person
    
    Attr:
        type (int): 1 -> Chamber, 2 -> Superior Council
        votes (OrderedSet<Candidate>): Votes of the person by preferential order
    """

    def __init__(self, type = 1):
        """This function initializes a new ballot. If the vote is for a chamber, \
            the number of votes should be 4. Otherwise, if it is for the \
                Superior Council, the number of votes should be 8.

        Args:
            type (int, optional): 1 -> Chamber, 2 -> Superior Council. Defaults to 1.
        """
        if (type not in (1, 2)):
            raise ValueError('Ballot.__init__: inexistent type')
        self.type = type
        self.votes = OrderedSet([])
    
    def is_valid(self):
        """Checks if a ballot has the correct number of votes

        Return:
            bool: true if the ballot has the correct number of votes
        """
        if self.type == 1:
            return len(self.votes) <= 4
        if self.type == 2:
            return len(self.votes) <= 8
        
    def add_vote(self, candidate):
        if not isinstance(candidate, Candidate):
            raise TypeError('Ballot.add_vote: candidate is not of type Candidate')
        if (self.type, len(self.votes)) in ((1, 4), (2, 8)):
            raise RuntimeError('Ballot.add_vote: max number of votes reached')
        self.votes = self.votes.add(candidate)
    
    def __str__(self):
        ret = 'Voto' + ('Câmara' if self.type == 1 else 'Conselho Superior') + ':\n'
        for i in range(len(self.votes)):
            ret += f' {i+1}.\t{self.votes[i]}\n'
        return ret


class RoundResult:
    def __init__(self, votes, tally):
        self.votes = votes
        self.tally = sorted(tally.items(), key = lambda item: item[1])
        self.first = [x[0] for x in self.tally if x[1] == self.tally[0][1]]
        self.second = [x[0] for x in self.tally[len(self.first):] if x[1] == self.tally[len(self.first)][1]]
        self.percentages = [x[1]/self.votes for x in self.tally]
    
    def tie_second_third(self):
        return self.tally[1][1] == self.tally[2][1]
    
    def over_half(self, n):
        return sum(self.percentages[0:n]) > 0.5
    

        
        



class Round:
    def __init__(self, ballots):
        self.ballots = ballots
    
    def result(self):
        raise NotImplementedError('Round.result: This method is not implemented')
    
    @staticmethod
    def res_str(result):
        raise NotImplementedError('Round.res_str: This method is not implemented')
    
    def __str__(self):
        return self.res_str(self.result())


class PreferentialRound(Round): 
    """Abstract class for a preferential type vote
    
    Attr:
        ballots (list <Ballot>)
    """
    def __init__(self, ballots):
        super().__init__(ballots)
    
    def preferred(self, ballot):
        raise NotImplementedError('PreferentialRound.preferred: This method is not implemented')
    
    def result(self):
        tally = {}
        votes = len(self.ballots)
        for ballot in self.ballots:
            preferred = self.preferred(ballot)
            if preferred is None:
                votes -= 1
            else:
                tally[preferred] = tally.get(preferred, 0) + 1
        return RoundResult(votes, tally)
    
    #TODO: Implement the written result string
    @staticmethod
    def res_str(result):
        return ''


class PreferentialExclusiveRound(PreferentialRound):
    """Class to run a preferential exclusive vote on a ballot list
    
    Attr:
        ballots (list<Ballot>): Ballots to be tallied
        excluded (list<Candidate>, optional): List of candidates to be removed from the tally
    """
    def __init__(self, ballots, excluded = []):
        """This function initializes a new preferential vote.
        
        Args:
            ballots (list<Ballot>): Ballots to be tallied
            excluded (list<Candidate>): Exclude candidates from tally. Defaults to []
        """
        super().__init__(ballots)
        self.excluded = excluded
    
    def preferred(self, ballot):
        for vote in ballot:
            if vote not in self.excluded:
                return vote
        return None


class PreferentialInclusiveRound(PreferentialRound):
    """Class to run a preferential inclusive vote on a ballot list
    
    Attr:
        ballots (list<Ballot>): Ballots to be tallied
        included(list<Candidate>): List of candidates to be considered
    """
    def __init__(self, ballots, included=[]):
        super().__init__(ballots)
        self.included = included
    
    def preferred(self, ballot):
        for vote in ballot:
            if vote in self.included:
                return vote
        return None
    

class RankedRound(Round):
    def __init__(self, ballots):
        super().__init__(ballots)
        
    def ballot_tally(self, ballot):
        raise NotImplementedError('RankedRound.ballot_tally: This method is not implemented')
    
    def result(self):
        tally = {}
        votes = 0
        for ballot in self.ballots:
            ballot_tally = self.ballot_tally(ballot)
            if ballot_tally != {}:
                for vote in ballot_tally:
                    tally[vote] = tally.get(vote, 0) + ballot_tally[vote]
                votes += ballot_tally[vote]
        return RoundResult(votes, tally)
    
    #TODO: Implement the written result string
    @staticmethod
    def res_str(result):
        return ''
        
        

class ConstantRankedRound(RankedRound):
    """Class to run an approval voting (i.e.in which all preferences are considered equal)"""
    def __init__(self, ballots, included):
        super().__init__(ballots)
        self.included = included
    
    def ballot_tally(self, ballot):
        return {k:1 for k in ballot & self.included}


class BordaRankedRound(RankedRound):
    """Class to run a preferential vote with borda counting (i.e. arithmetic decreasing progression)"""
    def __init__(self, ballots, included):
        super().__init__(ballots)
        self.included = included
    
    def ballot_tally(self, ballot):
        return reduce(lambda d1, d2: 
            d1.update({d2: 8 - len(d1)}) if d2 in self.included else d1, 
            ballot, {})


class FirstPastThePostRound(Round):
    def __init__(self, ballots, included, round = 1):
        super().__init__(ballots)
        self.included = included
        self.round = round - 1
    
    def result(self):
        tally = {}
        votes = 0
        for ballot in self.ballots:
            if ballot[round] in self.included:
                tally[ballot[round]] = tally.get(ballot[round], 0) + 1
                votes += 1
        return RoundResult(votes, tally)


class Election:
    def __init__(self, type, candidates, ballots):
        if (type not in (1, 2)):
            raise ValueError('Ballot.__init__: inexistent type')
        self.type = type
        self.candidates = candidates
        self.ballots = ballots
    
    def run(self, verbose = True, verboser = False):
        elected = []
        if self.type == 1:
            positions = ['I Vogal', 'II Vogal', 'III Vogal']
            
            print('############################   Eleições Câmarais   #############################')
            
        else:
            positions = ['Presidente do CS', 'I Conselheiro', 'II Conselheiro', 
                         'III Conselheiro', 'IV Conselheiro', 'V Conselheiro',
                         'VI Conselheiro', 'VII Conselheiro', 'VIII Conselheiro',
                         'IX Conselheiro', 'I Suplente', 'II Suplente', 
                         'III Suplente', 'IV Suplente']
            
            print('########################   Eleições Conselho Superior   ########################')
        
        print('')

        for i in range(positions):
            if verbose:
                print(f'### Eleição {positions[i]}:')
            
            # 1st round
            first_round = PreferentialExclusiveRound(self.ballots, elected).result()
            if verbose:
                print(f'\tResultados 1ª ronda:')
                print(PreferentialExclusiveRound.res_str(first_round))
                
            # Winner in 1st round (absolute majority)
            if first_round.tally[0][1] / first_round.votes > 0.5:
                elected += first_round.tally[0][0]
                if verbose:
                    print(f'\tO cargo de {positions[i]} foi atribuído a: {first_round.tally[0][0]}.\n')
                continue
                
            # Not a tie for second place in first round and sum of two first > 50%
            if first_round.tally[1][1] != first_round.tally[2][1] and (
                sum(first_round.tally[0][1], first_round.tally[1][1]) / first_round.votes > 0.5):
                # 2nd round
                included = [first_round.tally[0][0], first_round.tally[1][0]]
                second_round = PreferentialInclusiveRound(self.ballots, included).result()
                if verbose:
                    print(f'Resultados 2ª ronda:')
                    print(PreferentialInclusiveRound.res_str(second_round))
            
                # Winner in 2nd round
                if second_round.tally[0][1] != second_round.tally[1][1]:
                    elected += second_round.tally[0][0]
                    if verbose:
                        print(f'\tO cargo de {positions[i]} foi atribuído a: {first_round.tally[0][0]}.\n')
                    continue
            
                # Persistent tie (2nd round)
                included = [second_round.tally[0][0], second_round.tally[1][0]]
                tie_breaker = PersistentTieRound
                 
                
                    
                
                
                
            