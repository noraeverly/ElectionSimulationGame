import random
from constants import *

class Candidate():
    def __init__(self, party):
        self.party = party
        self.issues = set()
        self.money = 0

        self.votes = 0
    
    def __repr__(self):
        return f'{self.party}'
    
    def getMoney(self, money):
        self.money += money
    
    def chooseIssues(self, party):
        if party == 'D':
            while len(self.issues) < 5:
                randIndex = random.randint(0, len(DEM_ISSUES)-1)
                self.issues.add(DEM_ISSUES[randIndex])
        else:
            while len(self.issues) < 5:
                randIndex = random.randint(0, len(REP_ISSUES)-1)
                self.issues.add(REP_ISSUES[randIndex])
