import random
from constants import *


class State():
    def __init__(self, name, pop, votes):
        self.name = name
        self.polygon = None
        self.electoralVotes = int(votes)
        self.population = pop

        self.demSupport = random.randint(30, 70)
        self.repSupport = 100 - self.demSupport
        self.hotTopics = set()
        self.color = None

        self.wealth = None
        self.availableMoney = self.wealth

        self.influence = 0 #positive is democrat, negative is republican

        self.showing = False

        self.outline = 'black'
    
    def __repr__(self):
        return f"{self.name}:{self.hotTopics}, {self.demSupport}-{self.repSupport}, {self.influence}"
    
    def __hash__(self):
        return hash(self.name)

    def findColor(self):
        if abs(self.demSupport - self.repSupport) <= 5:
            self.color = 'purple'
        elif self.demSupport > self.repSupport :
            self.color = 'blue'
        else:
            self.color = 'red'
    
    def generateIssues(self):
        if self.demSupport > self.repSupport:
            while len(self.hotTopics) < 2:
                randIndex = random.randint(0, len(DEM_ISSUES)-1)
                self.hotTopics.add(DEM_ISSUES[randIndex])
            randIndex = random.randint(0, len(REP_ISSUES)-1)
            self.hotTopics.add(REP_ISSUES[randIndex])
        else:
            while len(self.hotTopics) < 2:
                randIndex = random.randint(0, len(REP_ISSUES)-1)
                self.hotTopics.add(REP_ISSUES[randIndex])
            randIndex = random.randint(0, len(DEM_ISSUES)-1)
            self.hotTopics.add(DEM_ISSUES[randIndex])
    
    def generateWealth(self):
        if int(self.population) >= 15000000:
            self.wealth = 3
        elif int(self.population) >= 7000000:
            self.wealth = 2
        else:
            self.wealth = 1
        self.availableMoney = self.wealth
    
    def updateMoney(self):
        if self.availableMoney < self.wealth:
            self.availableMoney += 1