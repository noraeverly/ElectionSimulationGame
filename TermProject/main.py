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
from CPULogic import *

# cmu graphics from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# shapefile geodata from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-1-states-provinces/

def appStarted(app):
    #geometry info -- Geopandas
    shapefile = '/Users/noraeverly/Desktop/TermProject/ne_110m_admin_1_states_provinces'
    app.data = gpd.read_file(shapefile)[['name_en', 'iso_3166_2', 'geometry']]
    app.data.columns = ['state', 'state_code', 'geometry']
    app.data.head()

    #images
    url = 'https://i.pinimg.com/originals/88/46/8a/88468a8c331004db26b00b31e642b090.png'
    app.flagImage = app.loadImage(url)

    #create all states
    app.stateDict = createStateDict(app)

    #creating player vars
    app.playerName = ''
    app.selectedParty = None
    app.selectedIssues = set()

    #two players
    app.player1 = None
    app.player2 = None

    #keep track of turns and rounds
    app.turns = 0
    app.rounds = 0

    #game over vars
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

    #map overlay and hovering vars
    app.previousState = 'AK'
    app.mapOverlay = 'Name'
    app.overlays = ['Name', 'Votes', 'Wealth', 'Status']

    #displaying updates or errors
    app.errorMessage = None
    app.updateMessage = None

    #keep track of state of previous move
    app.previousMove = None

    #multiplayer mode
    app.localMultiplayer = False


#create randomized map for start of game
def createStateDict(app):
    stateDict = {}

    #state info
    for line in stateList.splitlines():
        abbrev, pop, votes = line.split("\t", 3)
        pop = pop.replace(',','')
        stateDict[abbrev] = State(abbrev, pop, votes)
        stateDict[abbrev].whoIsWinning()
        stateDict[abbrev].generateIssues()
        stateDict[abbrev].generateWealth()
        stateDict[abbrev].findColor()
    
    #geography
    for _, row in app.data.iterrows():
        code = row['state_code'][3:]
        statePolygon = (row['geometry'])
        stateDict[code].polygon = statePolygon
    
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
    return candidate

#creates CPU player
def createCPU(app, party):
    candidate = CPU(party)
    candidate.chooseIssues()
    candidate.updateStateInfo(app.stateDict)
    return candidate


def keyPressed(app, event):
    if event.key == 'Enter' and app.titleScreen:
        app.titleScreen = False
        app.creatingCandidate = True
    #input name of candidate
    elif app.creatingCandidate:
        if event.key == 'Delete':
            app.playerName = app.playerName[0:-1]
        elif event.key == 'Space' or event.key == 'Tab':
            app.playerName += ' '
        else:
            app.playerName += event.key

def timerFired(app):
    #only shows error message briefly
    if app.errorMessage != None:
        time.sleep(1.2)
        app.errorMessage = None

    app.currentPlayer = findPlayerTurn(app)

    #finds CPU's move vars
    if isinstance(app.currentPlayer, CPU):
        app.currentPlayer.updateStateInfo(app.stateDict)
        app.move = app.currentPlayer.chooseMove()
        CPUMoveVals = app.currentPlayer.returnMoveValues(app, app.move)
        app.currentState = CPUMoveVals[0]
        app.currentIssue = CPUMoveVals[1]
        #CPU "thinking"
        time.sleep(1.2)
    
    #perform move if all vars are ready
    if (app.currentState != None and 
        (app.currentIssue != None or app.move == POLL or app.move == FUNDRAISE)):
        #do move and then reset move vars
        doMove(app, app.currentState, app.currentPlayer, app.currentIssue)
        cancelMove(app)
        return


def findPlayerTurn(app):
    #even turns are player1, odds are player2
    if app.turns%2 == 0:
        return app.player1
    else:
        return app.player2

def mouseMoved(app, event):
    #hovered over state is outlined in yellow
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

    #clicks check different things depending on game state
    if app.titleScreen:
        x0, y0, x1, y1 = (app.width/3)-50, (app.height/2)+50, (app.width/3)+50, (app.height/2)+100,
        if x0<event.x<x1 and y0<event.y<y1:
            app.titleScreen = False
            app.creatingCandidate = True
        x0, y0, x1, y1 = 2*(app.width/3)-50, (app.height/2)+50, 2*(app.width/3)+50, (app.height/2)+100
        if x0<event.x<x1 and y0<event.y<y1:
            app.titleScreen = False
            app.creatingCandidate = True
            app.localMultiplayer = True

    elif app.creatingCandidate:
        selectParty(app, event)
        selectIssues(app, event)
        startGame(app, event)

    #click to exit out of state info panel
    elif app.stateCard:
        app.stateCard = False
        app.currentState = None

    elif app.selectingIssue and app.currentState != None:
        app.currentIssue = clickedIssue(app, event)

    elif app.doingMove:
        #click on state
        state = clickedState(app, point)
        #if move is ads or speech, check for money then change game state to selecting issue
        if ((app.move == ADS and app.currentPlayer.money >= 1) 
            or (app.move == SPEECH and app.currentPlayer.money >= 2)):
            app.selectingIssue = True
        if state == None:
            #if no state was clicked on, cancel the move
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

        #check what move is clicked, make it active move
        isMoveClicked(app, event, app.currentPlayer)

        #check which map overlay is clicked, apply it
        clickMapOverlay(app, event)


#checks if overlay is clicked and changes to it
def clickMapOverlay(app, event):
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
        if pointInState(point, stateGeo):
            return state
    return None

#Is clicked-point in state?
def pointInState(point, poly):
    return poly.contains(point) #or point.within(poly)

def selectParty(app, event):
    if app.localMultiplayer and app.player1 != None:
        return

    center = app.width/2
    if center<event.x<center+50 and 175<event.y<225:
        app.selectedParty = DEM
        app.selectedIssues = set()
    elif center+100<event.x<center+150 and 175<event.y<225:
        app.selectedParty = REP
        app.selectedIssues = set()

def selectIssues(app, event):
    x0 = 200
    y0 = app.height/3 + 50
    x1 = app.width - 200
    y1 = y0 + 50
    if app.selectedParty == DEM:
        issues = DEM_ISSUES
    elif app.selectedParty == REP:
        issues = REP_ISSUES
    else:
        return
    size= int(app.height/(2*len(issues)))

    for issue in issues:
        if x0<event.x<x1 and y0<event.y<y1:
            if issue in app.selectedIssues:
                app.selectedIssues.remove(issue)
            elif len(app.selectedIssues) < 4:
                app.selectedIssues.add(issue)
            return
        y0 += size
        y1 += size

def startGame(app, event):
    x0, y0, x1, y1 = app.width-150, app.height-60, app.width-25, app.height-25
    if x0<event.x<x1 and y0<event.y<y1:
        if len(app.selectedIssues)==4 and app.playerName!='' and not app.localMultiplayer:
            #create both candidates if game is ready to start
            app.player1 = createCandidate(app, app.playerName, app.selectedParty)
            cpuParty = DEM if app.selectedParty==REP else REP
            app.player2 = createCPU(app, cpuParty)
            app.creatingCandidate = False
        elif app.player1==None and len(app.selectedIssues)==4 and app.playerName!='' and app.localMultiplayer:
            app.player1 = createCandidate(app, app.playerName, app.selectedParty)
            app.playerName = ''
            app.selectedParty = DEM if app.selectedParty==REP else REP
            app.selectedIssues = set()
        elif app.player1 != None and len(app.selectedIssues)==4 and app.playerName!='' and app.localMultiplayer:
            app.player2 = createCandidate(app, app.playerName, app.selectedParty)
            app.creatingCandidate = False
        else:
            #game doesn't start until player completes character
            app.errorMessage = 'Finish creating your character first!'

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

#score bar at bottom
def drawScore(app, canvas):
    x0 = 200
    x1 = app.width-200
    y0 = app.height-190
    y1 = app.height-170

    middle = (x0+x1)/2

    demVoteCount = 0
    repVoteCount = 0
    unknownVoteCount = 0

    for state in app.stateDict:
        if app.stateDict[state].winningParty == DEM and app.stateDict[state].showing:
            demVoteCount += app.stateDict[state].electoralVotes
        elif app.stateDict[state].winningParty == REP and app.stateDict[state].showing:
            repVoteCount += app.stateDict[state].electoralVotes
        else:
            unknownVoteCount += app.stateDict[state].electoralVotes

    length = x1 - x0
    voteSize = int(length/538)

    canvas.create_rectangle(x0, y0, x0+(voteSize*demVoteCount), y1, fill='blue')
    canvas.create_text(x0+5, (y0+y1)/2, text=f'{demVoteCount}', anchor=W, fill='white')
    x0 += (voteSize*demVoteCount)
    canvas.create_rectangle(x0, y0, x0+(voteSize*unknownVoteCount), y1, fill='grey')
    x0 += (voteSize*unknownVoteCount)
    canvas.create_rectangle(x0, y0, x1, y1, fill='red')
    canvas.create_text(x1-5, (y0+y1)/2, text=f'{repVoteCount}', anchor=E, fill='white')

    canvas.create_line(middle, y0-3, middle, y1+3, width=2)

#move buttons
def drawButton(app, canvas, move, spacing):
    size= int(app.width/9)
    x0 = spacing * size
    y0 = app.height - 100
    x1 = (spacing+1)*size
    y1 = app.height - 50
    outline = 'light gray' if move == app.move else 'white'
    canvas.create_rectangle(x0, y0, x1, y1, fill=outline, outline='black', width=2)
    xText = (x0+x1)/2
    yText = (y0+y1)/2
    canvas.create_text(xText, yText, text=f'{move}')

#player stat boxes
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
    if app.titleScreen:
        drawTitleScreen(app, canvas)
    elif app.creatingCandidate:
        drawCreateCandidateScreen(app, canvas)
        if app.errorMessage != None:
            drawErrorMessage(app, canvas)
    elif app.selectingIssue:
        drawIssueChoiceScreen(app, canvas)
    elif app.stateCard:
        drawStateCard(app, canvas)
    else:
        drawMap(app, canvas)
        drawMapOverlayButtons(app, canvas)
        drawScore(app, canvas)
        drawButton(app, canvas, FUNDRAISE, 1)
        drawButton(app, canvas, POLL, 3)
        drawButton(app, canvas, ADS, 5)
        drawButton(app, canvas, SPEECH, 7)
        drawPlayerStats(app, canvas, app.player1, 'left')
        drawPlayerStats(app, canvas, app.player2, 'right')

        if app.gameOver:
            canvas.create_text(app.width/2, 50, text=f'Game Over! Winner: {declareWinner(app)}', font='Arial 25 bold')
            canvas.create_text(app.width/2, 75, text=f'{app.player1.votes} - {app.player2.votes}', font='Arial 20')
        elif app.errorMessage != None:
            drawErrorMessage(app, canvas)
        else:
            canvas.create_text(app.width/2, 10, text=f'Round:{app.rounds+1}/{ROUNDS} Turn:{app.turns+1}/{MAX_TURNS}')
            if app.updateMessage != None:
                drawUpdateMessage(app, canvas)


runApp(width=DEFAULT_SCREEN_WIDTH, height=DEFAULT_SCREEN_HEIGHT)