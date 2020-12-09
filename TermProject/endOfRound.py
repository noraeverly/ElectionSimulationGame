import random
from constants import *

def endRound(app):
    app.turns = 0
    app.rounds += 1

    updateMap(app)

    if app.rounds == ROUNDS:
        app.gameOver = True
        countElectoralVotes(app)
        app.winner = declareWinner(app)

#update state vars
def updateMap(app):
    for state in app.stateDict:
        if app.stateDict[state].showing:
            supportChange = app.stateDict[state].influence * 2
            app.stateDict[state].demSupport += supportChange
            app.stateDict[state].repSupport -= supportChange
            app.stateDict[state].whoIsWinning()
            app.stateDict[state].findColor()
            app.stateDict[state].updateMoney()
            app.stateDict[state].diminishInfluence()

#tally up votes at end of game
def countElectoralVotes(app):
    for state in app.stateDict:
        app.stateDict[state].showing = True
        votes = app.stateDict[state].electoralVotes

        if app.stateDict[state].winningParty == None:
            if random.randint(1,2) == 1:
                app.stateDict[state].winningParty = DEM
            else:
                app.stateDict[state].winningParty = REP
        
        if app.stateDict[state].winningParty == app.player1.party:
            app.player1.votes += votes
        
        elif app.stateDict[state].winningParty == app.player2.party:
            app.player2.votes += votes
        
#majority of votes = winner
def declareWinner(app):
    if app.player1.votes >= 270:
        return app.player1
    elif app.player2.votes >= 270:
        return app.player2
    else:
        return 'Tie!'