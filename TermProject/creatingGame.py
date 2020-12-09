from constants import *
from stateList import *
from stateClass import *
from candidateClass import *
from CPULogic import *

#create randomized map for start of game
def createStateDict(app):
    stateDict = {}

    bigStateDemCount = 0
    bigStateRepCount = 0
    #state info
    for line in stateList.splitlines():
        abbrev, pop, votes = line.split("\t", 3)
        pop = pop.replace(',','')
        stateDict[abbrev] = State(abbrev, pop, votes)
        stateDict[abbrev].whoIsWinning()
        stateDict[abbrev].generateWealth()

        #balance big states
        if stateDict[abbrev].wealth == 3:
            if stateDict[abbrev].winningParty == DEM:
                bigStateDemCount += 1
            elif stateDict[abbrev].winningParty == REP:
                bigStateRepCount += 1
            
            if bigStateDemCount >= 3 :
                stateDict[abbrev].repSupport = random.randint(50, 70)
                stateDict[abbrev].demSupport = 100 - stateDict[abbrev].repSupport
                bigStateDemCount -= 1
                bigStateRepCount += 1
            
            elif bigStateRepCount >= 3:
                stateDict[abbrev].demSupport = random.randint(50, 70)
                stateDict[abbrev].repSupport = 100 - stateDict[abbrev].demSupport
                bigStateDemCount += 1
                bigStateRepCount -= 1
            stateDict[abbrev].whoIsWinning()
        
        stateDict[abbrev].generateIssues()
        stateDict[abbrev].findColor()
    
    #geography
    for _, row in app.data.iterrows():
        code = row['state_code'][3:]
        statePolygon = (row['geometry'])
        stateDict[code].polygon = statePolygon

    stateDict = randomizeShowing(app, stateDict)
    
    return stateDict


def randomizeShowing(app, stateDict):
    dCounter = 0
    rCounter = 0
    #only some states are shown at start
    while dCounter < STARTING_STATES or rCounter < STARTING_STATES:
        for state in stateDict:
            if random.randint(1, 6) == 1:
                if stateDict[state].winningParty == DEM and dCounter < STARTING_STATES:
                    dCounter += 1
                    stateDict[state].showing = True
                elif stateDict[state].winningParty == REP and rCounter < STARTING_STATES:
                    rCounter += 1
                    stateDict[state].showing = True
    return stateDict
    

def createCandidate(app, name, party):
    #uses player inputs
    candidate = Candidate(name, party)
    candidate.issues = app.selectedIssues
    candidate.avatar = app.avatarList[app.selectedAvatar]
    return candidate

#creates CPU player
def createCPU(app, party):
    candidate = CPU(party)
    candidate.chooseIssues()
    candidate.updateStateInfo(app.stateDict)
    randIndex = random.randint(0, len(app.avatarList)-1)
    candidate.avatar = app.avatarList[randIndex]
    return candidate