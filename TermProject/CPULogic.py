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
            return self.influenceMove(app)
        elif move == SPEECH:
            return self.influenceMove(app)

    def fundraise(self):
        #optimized fundraising strategy
        highestMoney = 0
        currentState = None
        for state in self.winningStates:
            if self.winningStates[state].availableMoney > highestMoney:
                currentState = state
                highestMoney = self.winningStates[state].availableMoney
        return (currentState, None)
    
    def poll(self, app):
        #random polling
        while True:
            for state in app.stateDict:
                if not app.stateDict[state].showing:
                    if random.randint(1, 10) == 9:
                        return (state, None)
    
    #logic for choosing state for ads and speeches
    def influenceMove(self, app):
        closeStates = self.closeStates
        mostVotes = 0
        tempState = None
        tempIssue = None

        #first looks at close states and targets best close state
        for state in closeStates:
            if closeStates[state].electoralVotes > mostVotes:
                for issue in closeStates[state].hotTopics:
                    if issue in self.issues:
                        tempIssue = issue
                        if abs(closeStates[state].influence) < 4:
                            mostVotes = closeStates[state].electoralVotes
                            tempState = state
        
        #if no close states, finds best state from opponent's states
        if tempState == None:
            for state in app.stateDict:
                if (app.stateDict[state].electoralVotes > mostVotes
                    and app.stateDict[state].winningParty != self.party):
                    for issue in app.stateDict[state].hotTopics:
                        if issue in self.issues:
                            tempIssue = issue
                            if abs(closeStates[state].influence) < 4:
                                mostVotes = closeStates[state].electoralVotes
                                tempState = state

        #if opponent attacked one of CPU's states, CPU will try to defend that state
        if app.previousMove.winningParty == self.party and abs(app.previousMove.influence)>0:
            if app.previousMove.electoralVotes > mostVotes:
                for issue in app.previousMove.hotTopics:
                    if issue in self.issues:
                        if abs(closeStates[state].influence) < 4:
                            mostVotes = app.previousMove.electoralVotes
                            tempState = app.previousMove.name
                            tempIssue = issue

        return (tempState, tempIssue)
        