import random


class State():

    repIssues = ['Lower Taxes', 'Large Military', 'Protect Borders', 'R', 'R1', 'R2']

    demIssues = ['Women''s Health', 'Racial Inequality', 'LGBTQ Rights', 'D', 'D1', 'D2']

    def __init__(self, name):
        self.name = name
        self.polygon = None
        self.demSupport = random.randint(30, 70)
        self.repSupport = 100 - self.demSupport
        self.issues = set()
        self.color = None
        self.electoralVotes = None
    
    def __repl__(self):
        return f'{self.name}'
    
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
            while len(self.issues) < 2:
                randIndex = random.randint(0, len(State.demIssues)-1)
                self.issues.add(State.demIssues[randIndex])
            randIndex = random.randint(0, len(State.repIssues)-1)
            self.issues.add(State.repIssues[randIndex])
        else:
            while len(self.issues) < 2:
                randIndex = random.randint(0, len(State.repIssues)-1)
                self.issues.add(State.repIssues[randIndex])
            randIndex = random.randint(0, len(State.demIssues)-1)
            self.issues.add(State.demIssues[randIndex])