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

def updateMap(app):
    for state in app.stateDict:
        if app.stateDict[state].showing:
            supportChange = app.stateDict[state].influence * 2
            app.stateDict[state].demSupport += supportChange
            app.stateDict[state].repSupport -= supportChange
            app.stateDict[state].findColor()
            app.stateDict[state].updateMoney()


def countElectoralVotes(app):
    for state in app.stateDict:
        votes = app.stateDict[state].electoralVotes

        if app.stateDict[state].demSupport > app.stateDict[state].repSupport:
            app.player1.votes += votes
        
        elif app.stateDict[state].demSupport < app.stateDict[state].repSupport:
            app.player2.votes += votes
        
        else:
            if random.randint(1,2) == 1:
                app.player1.votes += votes
            else:
                app.player2.votes += votes
        
        app.stateDict[state].showing = True
    
def declareWinner(app):
    if app.player1.votes >= 270:
        return app.player1
    else:
        return app.player2