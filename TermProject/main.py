import geopandas as gpd
from cmu_112_graphics import *
from shapely.geometry import Point, Polygon
import random
from moves import *
from constants import *
from endOfRound import *
from screens import *
from mapDrawing import *
import time
import string
from mouseClicking import *
from creatingGame import *

# cmu graphics from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# shapefile geodata from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-1-states-provinces/
# image resizing help from https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
# avatar images from http://www.miicharacters.com


def appStarted(app):
    #geometry info -- Geopandas
    shapefile = './ne_110m_admin_1_states_provinces'
    app.data = gpd.read_file(shapefile)[['name_en', 'iso_3166_2', 'geometry']]
    app.data.columns = ['state', 'state_code', 'geometry']
    app.data.head()

    #images
    flagMap = app.loadImage('flagMap.png')
    flagMap = flagMap.transpose(Image.FLIP_LEFT_RIGHT)
    app.flagMap = flagMap
    app.restartIcon = app.loadImage('restartIcon.png')

    #avatars
    app.avatarList = [app.loadImage('avatar1.jpg'), app.loadImage('avatar6.jpg'), app.loadImage('avatar3.jpg'),
                    app.loadImage('avatar4.jpg'), app.loadImage('avatar5.jpg'), app.loadImage('avatar2.jpg'), app.loadImage('avatar7.jpg')]

    #create all states
    app.stateDict = createStateDict(app)

    #creating player vars
    app.playerName = ''
    app.selectedParty = None
    app.selectedIssues = set()
    app.selectedAvatar = 0

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


def keyPressed(app, event):
    #input name of candidate
    if app.creatingCandidate:
        if event.key == 'Delete':
            app.playerName = app.playerName[0:-1]
        elif event.key == 'Space' or event.key == 'Tab':
            app.playerName += ' '
        elif event.key in list(string.ascii_letters):
            app.playerName += event.key
        elif event.key == '.':
            app.playerName += event.key
        else:
            pass

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
        selectAvatar(app, event)
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

        clickRestartButton(app, event)

def clickRestartButton(app, event):
    x0, y0, x1, y1 = app.width-35, app.height-35, app.width-10, app.width-10
    if x0<event.x<x1 and y0<event.y<y1:
        appStarted(app)


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
        drawRestartButton(app, canvas)

        if app.gameOver:
            canvas.create_text(app.width/2, 50, text=f'Game Over! Winner: {declareWinner(app)}', font='Arial 24 bold')
            canvas.create_text(app.width/2, 75, text=f'{app.player1.votes} - {app.player2.votes}', font='Arial 20')
        elif app.errorMessage != None:
            drawErrorMessage(app, canvas)
        else:
            canvas.create_text(app.width/2, 10, text=f'Round:{app.rounds+1}/{ROUNDS} Turn:{app.turns+1}/{MAX_TURNS}')
            if app.updateMessage != None:
                drawUpdateMessage(app, canvas)


runApp(width=DEFAULT_SCREEN_WIDTH, height=DEFAULT_SCREEN_HEIGHT)