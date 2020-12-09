import random
from constants import *

class Candidate():
    def __init__(self, name, party):
        self.party = party
        self.issues = set()
        self.money = 0

        self.name = name

        self.votes = 0

        self.avatar = None
    
    def __repr__(self):
        return f'{self.name} ({self.party})'
    
    def getMoney(self, money):
        self.money += money
    
    def chooseIssues(self):
        if self.party == DEM:
            while len(self.issues) < 4:
                randIndex = random.randint(0, len(DEM_ISSUES)-1)
                self.issues.add(DEM_ISSUES[randIndex])
        else:
            while len(self.issues) < 4:
                randIndex = random.randint(0, len(REP_ISSUES)-1)
                self.issues.add(REP_ISSUES[randIndex])
