from constants import *

################################################################################
############################ Mathematical functions ############################
################################################################################

def zero_div(num, denom):
    """Function to divide two numbers, returning 0 if the denominator is 0

    Arguments:
        num (int): numerator
        denom (int): denominator

    Returns:
        int: result of the division
    """
    return 0 if denom == 0 else num / denom


################################################################################
############################## String manipulation #############################
################################################################################

def indent(text, lvl):
    """Function to indent a text for a given number of levels

    Arguments:
        text (string): text to be indented
        lvl (int): number of levels to indent

    Returns:
        string: indented text
    """
    spacer = 4 * ' ' * lvl
    return '\n'.join([(spacer + line) for line in str(text).splitlines()])

def title_str(title):
    """Function to create a title string
    
    Arguments:
        title (string): title to be used
    
    Returns:
        string: title string
    """
    return '\n'.join(['',
                      '',
                      80*'#',
                      ('  ' + title + '  ').center(80, '#'),
                      80*'#',
                      '']) 

def subtitle_str(subtitle):
    """Function to create a subtitle string

    Arguments:
        subtitle (string): subtitle to be used

    Returns:
        string: subtitle string
    """
    return '\n'.join(['',
                      '',
                      ('  ' + subtitle + '  ').center(80, '-'),
                      ''])


################################################################################
################################## CSV parsing #################################
################################################################################

import pandas as pd

def csv_to_df(path):
    """Function to parse a csv file into a dataframe

    Arguments:
        path (string): path to the csv file

    Returns:
        pandas.DataFrame: dataframe with the csv file data
    """
    df = pd.read_csv(path, index_col=0, encoding='utf-8')
    return df.astype('Int64')

def get_election_type(df):
    """Function to get the election type from a dataframe
    
    Arguments:
        df (pandas.DataFrame): dataframe with the csv file data
    
    Returns:
        int: election type
    """
    if df.index.name == 'CS':
        return TYPE_CS
    elif df.index.name == 'NC':
        return TYPE_NC

def get_candidates(df):
    """Function to get the candidates from a dataframe

    Arguments:
        df (pandas.DataFrame): dataframe with the csv file data

    Returns:
        list: list of candidates
    """
    return [name for name in df.index.array]

def get_ballots(df, candidates):
    """Function to get the ballots from a dataframe

    Arguments:
        df (pandas.DataFrame): dataframe with the csv file data

    Returns:
        list: list of ballots
    """
    ballots = []
    df_transposed = df.T
    for id, row in df_transposed.iterrows():
        votes = 8 * ['']
        for i in range(len(row.array)):
            if not pd.isna(row[i]):
                votes[row.array[i] - 1] = candidates[i]
        votes = list(filter(None, votes))
        ballots.append((int(id), votes))
    return ballots

def csv_vote(ballot, candidate):
    """Converts a ballot vote to a csv entry

    Arguments:
        ballot (Ballot): ballot
        candidate (Candidate): candidate 

    Returns:
        pd.NA or int: 
    """
    try:
        return ballot.get_votes().index(candidate) + 1
    except ValueError:
        return pd.NA

def export_csv(path, election_type, candidates, ballots):
    """Function to export a csv file to given path
    
    Arguments:
        path (string): path to the csv file
        election_type (int): election type
        candidates (list(Candidate)): list of candidates
        ballots (list(Ballot)): list of ballots
    """
    if election_type == TYPE_CS:
        id = 'CS'
    elif election_type == TYPE_NC:
        id = 'NC'
    data = {id: [candidate.get_name() for candidate in candidates]}
    for ballot in ballots:
        data[ballot.get_id()] = [csv_vote(ballot, candidate) for candidate in candidates]
    
    df = pd.DataFrame(data)
    df.to_csv(path, encoding='utf-8')
    
def import_csv(path):
    """Imports a csv file from a given path
    
    Arguments:
        path (string): path to the csv file
    
    Returns:
        dict: dictionary with the election data (type, candidates, ballots)
    """
    ret = {}
    df = csv_to_df(path)
    ret['type'] = get_election_type(df)
    ret['candidates'] = get_candidates(df)
    ret['ballots'] = get_ballots(df, ret['candidates'])
    return ret



################################################################################
#################################### Getchar ###################################
################################################################################

class _Getchar:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetcharWindows()
        except ImportError:
            self.impl = _GetcharUnix()

    def __call__(self): return self.impl()


class _GetcharUnix:
    """Getchar implementation for Unix"""
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetcharWindows:
    """Getchar implementation for Windows"""
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getchar = _Getchar()