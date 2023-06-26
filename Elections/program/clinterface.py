__author__ = "Javier de Muller"
__copyright__ = "Copyright (C) 2023 Javier de Muller"
__license__ = "MIT License"
__version__ = "0.9"

from io_interface import *
from utils import *

class CLInterface(IOInterface):
    def election_type_selection_str(self):
        return '\n'.join([
            indent('Selecione o tipo de eleição:', 0),
            indent(f'{TYPE_CS}. Conselho Superior', 1),
            indent(f'{TYPE_NC}. Direção de Câmara', 1),
            '',
            indent('Escolha: ', 0)
        ])
    
    def get_choice(self, max, empty=False):
        while True:
            print(f'Escolha (1-{max}): ', end='')
            try:
                opt_choice = input()
                
                if empty:
                    if opt_choice == '':
                        return None
                choice = int(opt_choice)
                assert choice in range(1, max+1)
                return choice
            except:
                print(f'Escolha inválida (O valor deve ser entre 1 e {max})')
    
    def get_confirmation(self, text):
        while True:
                print(f'{text} (S/N) ', end='')
                try:
                    choice = input()
                    assert choice in ('S', 's', 'N', 'n')
                    if choice in ('S', 's'):
                        return True
                    if choice in ('N', 'n'):
                        return False
                except:
                    print('Escolha inválida (O valor deve ser S ou N)')
    
    def get_election_type(self):
        while True:
            try:
                print(self.election_type_selection_str(), end='')
                choice = int(input())
                assert choice in (TYPE_CS, TYPE_NC)
                return choice
            except:
                print(f'Escolha inválida (O valor deve ser {TYPE_CS} ou {TYPE_NC})')
    
    def get_candidates(self, initial = []):
        while True:
            candidates = [candidate for candidate in initial]
            print(title_str('Candidatos'))
            while True:
                print('Candidatos:')
                for i in range(len(candidates)):
                    print(indent(f'{i+1}. {candidates[i]}', 1))
                print('')
                print('Introduza o nome de um novo candidato (ou deixe vazio para terminar): ', end='')
                name = input()
                if name == '':
                    break
                candidates.append(Candidate(name))
            print('Os candidatos são:')
            for i in range(len(candidates)):
                print(indent(f'{i+1}. {candidates[i]}', 1))
            if self.get_confirmation('Confirmar?'):
                return candidates
    
    def get_id(self, inserted_ids = []):
        while True:
            try:
                print('Introduza o id do boletim: ', end='')
                id = int(input())
                assert id not in inserted_ids
                return id
            except ValueError:
                print('O id tem de ser um número.')
            except AssertionError:
                print(f'O boletim com id {id} já foi inserido.')
    
    def get_ballot(self, election_type, candidates, inserted_ids = []):
        id = self.get_id(inserted_ids)
        while True:
            if election_type == TYPE_CS:
                ballot = SuperiorCouncilBallot(id)
            elif election_type == TYPE_NC:
                ballot = ChamberBallot(id)
            for i in range(ballot.get_max_votes()):
                remaining_candidates = [candidate for candidate in candidates if candidate not in ballot.get_votes()]
                print(f'Introduza a {i+1}ª escolha (ou deixe vazio para terminar).')
                print('Candidatos restantes:')
                for i in range(len(remaining_candidates)):
                    print(indent(f'{i+1}. {remaining_candidates[i]}', 1))
                choice = self.get_choice(len(remaining_candidates), empty=True)
                if choice == None:
                    break
                ballot.add_vote(candidates[choice-1])
                print('Votos inseridos:')
                votes = ballot.get_votes()
                for i in range(len(votes)):
                    print(indent(f'{i+1}. {votes[i]}', 1))
            print(f'O boletim inserido é:')
            print(indent(ballot, 1))
            if self.get_confirmation('Confirmar?'):
                return ballot

    def get_ballots(self, election_type, candidates, initial=[]):
        while True:
            print(title_str('Boletins de voto'))
            ballots = [ballot for ballot in initial]
            while True:
                print(f'Foram inseridos {len(ballots)} boletins de voto.')
                if not self.get_confirmation('Quer inserir mais um boletim?'):
                    break
                ballots.append(self.get_ballot(election_type, candidates, inserted_ids=[ballot.get_id() for ballot in ballots]))
            ballots.sort(key=lambda x: x.get_id())
            print('Os boletins são:')
            for ballot in ballots:
                print(indent(ballot, 1))
            if self.get_confirmation('Confirmar?'):
                return ballots
    
    def get_presidential_choice(self, candidates):
        print('Voto presidencial:')
        for i in range(len(candidates)):
            print(indent(f'{i+1}. {candidates[i]}', 1))
        choice = self.get_choice(len(candidates))
        return candidates[choice-1]
    
    def output_results(self, seats, elected):
        print(title_str('Resultados'))
        for i in range(len(seats)):
            print(f'{seats[i]}: {str(elected[i])}')