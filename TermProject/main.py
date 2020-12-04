import geopandas as gpd
from cmu_112_graphics import *
import pandas as pd
from shapely.geometry import Point, Polygon
import random
from stateList import *
from stateClass import *
from candidateClass import *
from moves import *
from constants import *
from endOfRound import *
from screens import *
from mapDrawing import *
import time

# cmu graphics from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# shapefile geodata from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-1-states-provinces/

def appStarted(app):
    #geometry info -- Geopandas
    shapefile = '/Users/noraeverly/Desktop/TermProject/ne_110m_admin_1_states_provinces'
    app.data = gpd.read_file(shapefile)[['name_en', 'iso_3166_2', 'geometry']]
    app.data.columns = ['state', 'state_code', 'geometry']
    app.data.head()

    #create all states
    app.stateDict = createStateDict(app)

    app.player1 = createCandidate('Juan', 'D')
    app.player2 = createCandidate('Jerry', 'R')

    app.turns = 0
    app.rounds = 0

    #whose turn is it?
    # app.playerTurn = app.turns%2 #0 = player1, 1 = player2

    app.gameOver = False
    app.winner = None

    #keeping track of which screen is up
    app.titleScreen = True

    app.creatingCandidate = False

    app.mapScreen = False

    app.stateCard = False

    app.selectingIssue = False

    #keeping track of current move
    app.doingMove = False
    app.move = None
    app.currentIssue = None
    app.currentState = None
    app.currentPlayer = None

    app.previousState = 'AK'
    app.mapOverlay = 'Name'
    app.overlays = ['Name', 'Votes', 'Wealth', 'Status']

    app.errorMessage = None
    app.updateMessage = None


#create randomized map for start of game
def createStateDict(app):
    stateDict = {}

    #state info
    for line in stateList.splitlines():
        abbrev, pop, votes = line.split("\t", 3)
        pop = pop.replace(',','')
        stateDict[abbrev] = State(abbrev, pop, votes)
        stateDict[abbrev].findColor()
        stateDict[abbrev].generateIssues()
        stateDict[abbrev].generateWealth()
    
    #geography
    for _, row in app.data.iterrows():
        code = row['state_code'][3:]
        statePolygon = (row['geometry'])
        stateDict[code].polygon = statePolygon
    
    dCounter = 0
    rCounter = 0
    #only some states are known at start -- maybe change this later
    while dCounter < STARTING_STATES or rCounter < STARTING_STATES:
        for state in stateDict:
            if random.randint(1, 6) == 1:
                if stateDict[state].color == 'blue' and dCounter < STARTING_STATES:
                    dCounter += 1
                    stateDict[state].showing = True
                elif stateDict[state].color == 'red' and rCounter < STARTING_STATES:
                    rCounter += 1
                    stateDict[state].showing = True
    
    return stateDict


def createCandidate(name, party):
    candidate = Candidate(name, party)
    candidate.chooseIssues(party)
    return candidate


def keyPressed(app, event):
    pass


def timerFired(app):
    if (app.currentState != None and 
        (app.currentIssue != None or app.move == POLL or app.move == FUNDRAISE)):
        #do move and then reset move vars
        doMove(app, app.currentState, app.currentPlayer, app.currentIssue)
        cancelMove(app)
        return
    
    if app.errorMessage != None:
        time.sleep(1.2)
        app.errorMessage = None
    
    elif app.updateMessage != None:
        time.sleep(1.3)
        app.updateMessage = None

def cancelMove(app):
    app.doingMove = False
    app.move = None
    app.currentState = None
    app.currentIssue = None
    app.selectingIssue = False

def findPlayerTurn(app):
    #even turns are player1, odds are player2
    if app.turns%2 == 0:
        return app.player1
    else:
        return app.player2

def mouseMoved(app, event):
    prevState = app.previousState
    app.stateDict[prevState].outline = 'black'
    long = convertXToLong(app, event.x)
    lat = convertYToLat(app, event.y)
    point = Point(long, lat)
    state = clickedState(app, point)
    if state != None:
        app.stateDict[state].outline = 'yellow'
        app.previousState = state
    

def mousePressed(app, event):
    #convert click to geometric point
    long = convertXToLong(app, event.x)
    lat = convertYToLat(app, event.y)
    point = Point(long, lat)

    app.currentPlayer = findPlayerTurn(app)

    if app.stateCard:
        app.stateCard = False
        app.currentState = None

    elif app.selectingIssue and app.currentState != None:
        app.currentIssue = clickedIssue(app, event)

    elif app.doingMove:
        #click on state
        state = clickedState(app, point)
        if ((app.move == ADS and app.currentPlayer.money >= 1) 
            or (app.move == SPEECH and app.currentPlayer.money >= 2)):
            app.selectingIssue = True
        if state == None:
            cancelMove(app)
        else:
            app.currentState = state

    else:
        #if not doing move, give info about state
        state = clickedState(app, point)
        if state != None and app.stateDict[state].showing:
            #show state info panel
            app.stateCard = True
            app.currentState = state

        isMoveClicked(app, event, app.currentPlayer)

        changeMapOverlay(app, event)

#checks if overlay is clicked and changes to it
def changeMapOverlay(app, event):
    if not app.stateCard and not app.selectingIssue:
        x0 = 10
        x1 = 60
        y0 = app.height/2 - 80
        y1 = app.height/2 - 50
        for overlay in app.overlays:
            if y0<event.y<y1 and x0<event.x<x1:
                app.mapOverlay = overlay
            y0 += 40
            y1 += 40

#returns selected issue
def clickedIssue(app, event):
    size= int(app.height/8)
    x0 = 200
    y0 = app.height / 5
    x1 = app.width - 200
    y1 = app.height / 4

    for issue in app.currentPlayer.issues:
        if y0 < event.y < y1 and x0 < event.x < x1:
            app.selectingIssue = False
            return issue
        y0 += size
        y1 += size
    
    return None

def clickedState(app, point):
    for state in app.stateDict:
        stateGeo = app.stateDict[state].polygon
        # stateColor = app.stateDict[state].color
        if pointInState(point, stateGeo):
            return state
    return None

#Is clicked-point in state?
def pointInState(point, poly):
    return poly.contains(point) #or point.within(poly)

def isMoveClicked(app, event, player):
    for i in range(1, 8, 2):
        size= int(app.width/9)
        x0 = i * size
        y0 = app.height - 100
        x1 = (i+1)*size
        y1 = app.height - 50
        #check which move is clicked on
        if x0<event.x<x1 and y0<event.y<y1:
            app.doingMove = True
            if i == 1:
                app.move = FUNDRAISE
            elif i == 3 and player.money>=1:
                app.move = POLL
            elif i == 5 and player.money>=1:
                app.move = ADS
            elif i == 7 and player.money>=2:
                app.move = SPEECH
            return
    app.doingMove = False


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

    #keep track of turns and go to next round at end of 3 turns each
    app.turns += 1
    if app.turns == MAX_TURNS:
        endRound(app)
    


def drawButton(app, canvas, move, spacing):
    size= int(app.width/9)
    x0 = spacing * size
    y0 = app.height - 100
    x1 = (spacing+1)*size
    y1 = app.height - 50
    outline = 'yellow' if move == app.move else 'black'
    canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline=outline)
    xText = (x0+x1)/2
    yText = (y0+y1)/2
    canvas.create_text(xText, yText, text=f'{move}')


def drawPlayerStats(app, canvas, player, allign):
    dem = 'blue'
    rep = 'red'
    boxWidth = app.width/4
    boxHeight = app.height/10
    if allign == 'left':
        x0 = 5
        x1 = boxWidth
    else:
        x0 = app.width-boxWidth
        x1 = app.width-5
    y0 = 5
    y1 = boxHeight - 10
    marg = 5
    canvas.create_rectangle(x0, y0, x1, y1+15)
    canvas.create_text(x0+marg, y0, text=f'{player.name}  {"*" if player==findPlayerTurn(app) else ""}', anchor='nw', font='Arial 16 bold')
    canvas.create_text(x1-marg, y0+marg, text=f'{player.party}', anchor='ne', 
                        font='Arial 16 bold', fill=(dem if player.party=='D' else rep))
    canvas.create_text(x0+marg, y0+boxHeight/4-marg, text='Candidate Issues:', anchor='nw', font='Arial 14 italic')
    count = 1
    for issue in player.issues:
        count += 1
        canvas.create_text(x0+marg, y0+(count * boxHeight/7)+marg, text=f'{issue}', anchor='nw', font='Arial 13')
    canvas.create_text(x1, y1, text=f'{"$" * player.money}', anchor='e', fill='green', font=('Comic Sans MS', 15))


def redrawAll(app, canvas):
    if app.selectingIssue:
        drawIssueChoiceScreen(app, canvas)
    elif app.stateCard:
        drawStateCard(app, canvas)
    else:
        drawMap(app, canvas)
        drawMapOverlayButtons(app, canvas)
        drawButton(app, canvas, FUNDRAISE, 1)
        drawButton(app, canvas, POLL, 3)
        drawButton(app, canvas, ADS, 5)
        drawButton(app, canvas, SPEECH, 7)
        drawPlayerStats(app, canvas, app.player1, 'left')
        drawPlayerStats(app, canvas, app.player2, 'right')

    if app.errorMessage != None:
        drawErrorMessage(app, canvas)
    elif app.updateMessage != None:
        drawUpdateMessage(app, canvas)

    if app.gameOver:
        canvas.create_text(app.width/2, 50, text=f'Game Over! Winner: {declareWinner(app)}')
        canvas.create_text(app.width/2, 75, text=f'{app.player1.votes} - {app.player2.votes}')
    else:
        canvas.create_text(app.width/2, 10, text=f'Round:{app.rounds+1}/{ROUNDS} Turn:{app.turns+1}/{MAX_TURNS}')

runApp(width=1000, height=800)