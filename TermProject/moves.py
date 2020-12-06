import random
from constants import *
from endOfRound import endRound


def doMove(app, state, player, issue):
    #do selected move
    #turn counter goes down by one if the move cannot be completed
    if app.stateDict[state].showing:
        if app.move == FUNDRAISE:
            fundraise(app, state, player)
        elif app.move == ADS:
            runAds(app, state, player, issue)
        elif app.move == SPEECH:
            makeSpeech(app, state, player, issue)
        elif app.move == POLL:
            app.errorMessage = f'This state is already polled.'
            app.turns -= 1
    else:
        if app.move == POLL:
            poll(app, state, player)
        else:
            app.turns -= 1

    #keep track of previous move for CPU
    app.previousMove = app.stateDict[state]
    #keep track of turns and go to next round at end of 3 turns each
    app.turns += 1
    if app.turns == MAX_TURNS:
        endRound(app)

def fundraise(app, state, candidate):
    money = app.stateDict[state].availableMoney
    #check that state has money
    if money == 0:
        app.errorMessage = f'{state} has no more money! Try something else.'
        app.turns -= 1
    #can only gain money from states you are leading in
    elif app.stateDict[state].winningParty == DEM:
        if candidate.party == DEM:
            candidate.getMoney(money)
            app.stateDict[state].availableMoney = 0
            app.updateMessage = f'{candidate.name} earned {money}$'
        else:
            app.errorMessage = f'Not your state! Try another one.'
            app.turns -= 1
    elif app.stateDict[state].winningParty == REP:
        if candidate.party == REP:
            candidate.getMoney(money)
            app.stateDict[state].availableMoney = 0
            app.updateMessage = f'{candidate.name} earned {money}$'
        else:
            app.errorMessage = f'Not your state! Try another one.'
            app.turns -= 1
    #no one can fundraise in tied states
    else:
        app.errorMessage = f'Not your state yet! Try something else.'
        app.turns -= 1

def poll(app, state, candidate):
    candidate.money -= 1
    #polled state is now visible
    app.stateDict[state].showing = True
    #message
    app.updateMessage = f'{candidate.name} polled {state}'

def runAds(app, state, candidate, issue):
    candidate.money -= 1
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == DEM:
            app.stateDict[state].influence += 1
        else:
            app.stateDict[state].influence -= 1
        app.updateMessage = f'Successful ad campaign in {state} by {candidate.name}!'
    else:
        app.updateMessage = f'The people of {state} did not like {candidate.name}\'s ad campaign.'

def makeSpeech(app, state, candidate, issue):
    candidate.money -= 2
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == DEM:
            app.stateDict[state].influence += 2
        else:
            app.stateDict[state].influence -= 2
        app.updateMessage = f'{candidate.name}\'s speech in {state} was a massive success!'
    else:
        app.updateMessage = f'The people of {state} did not like {candidate.name}\'s speech.'

#reset move vars
def cancelMove(app):
    app.doingMove = False
    app.move = None
    app.currentState = None
    app.currentIssue = None
    app.selectingIssue = False