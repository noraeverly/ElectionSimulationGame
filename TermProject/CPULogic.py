from candidateClass import *

class CPU(Candidate):
    def __init__(self, party):
        super().__init__(name='CPU', party=party)

        self.winningStates = {}
        self.closeStates = {}
    
    def updateStateInfo(self, stateDict):
        for state in stateDict:
            if stateDict[state].showing:
                if self.party == stateDict[state].winningParty:
                    self.winningStates[state] = stateDict[state]
                elif state in self.winningStates:
                    self.winningStates.pop(state)
                
                if stateDict[state].color == 'purple':
                    self.closeStates[state] = stateDict[state]
                elif state in self.closeStates:
                    self.closeStates.pop(state)

    def chooseMove(self):
        if self.money == 0:
            return FUNDRAISE
        elif len(self.closeStates) > 0:
            if self.money > 1:
                return SPEECH
            else:
                return ADS
        else:
            return POLL
    
    def returnMoveValues(self, app, move):
        if move == FUNDRAISE:
            return self.fundraise()
        elif move == POLL:
            return self.poll(app)
        elif move == ADS:
            return self.runAds()
        elif move == SPEECH:
            return self.makeSpeech()

    def fundraise(self):
        highestMoney = 0
        currentState = None
        for state in self.winningStates:
            if self.winningStates[state].availableMoney > highestMoney:
                currentState = state
                highestMoney = self.winningStates[state].availableMoney
        return (currentState, None)
    
    def poll(self, app):
        while True:
            for state in  app.stateDict:
                if not app.stateDict[state].showing:
                    if random.randint(1, 10) == 9:
                        return (state, None)
    
    def runAds(self):
        closeStates = self.closeStates
        mostVotes = 0
        tempState = None
        tempIssue = None

        for state in closeStates:
            if closeStates[state].electoralVotes > mostVotes:
                for issue in self.issues:
                    if issue in closeStates[state].hotTopics:
                        tempIssue = issue
                if tempIssue!= None and abs(closeStates[state].influence) < 3:
                    mostVotes = closeStates[state].electoralVotes
                    tempState = state

        return (tempState, tempIssue)
    
    def makeSpeech(self):
        closeStates = self.closeStates
        mostVotes = 0
        tempState = None
        tempIssue = None

        for state in closeStates:
            if closeStates[state].electoralVotes > mostVotes:
                for issue in self.issues:
                    if issue in closeStates[state].hotTopics:
                        tempIssue = issue
                if tempIssue!= None and abs(closeStates[state].influence) < 3:
                    mostVotes = closeStates[state].electoralVotes
                    tempState = state

        return (tempState, tempIssue)