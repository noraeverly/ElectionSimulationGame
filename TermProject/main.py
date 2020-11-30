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

    app.player1 = createCandidate('D')
    app.player2 = createCandidate('R')

    app.doingMove = False
    app.move = None

    app.turns = 0
    app.rounds = 0

    #whose turn is it?
    # app.playerTurn = app.player1

    app.gameOver = False
    app.winner = None

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
    for index, row in app.data.iterrows():
        code = row['state_code'][3:]
        statePolygon = (row['geometry'])
        stateDict[code].polygon = statePolygon
    
    #only some states are known at start -- maybe change this later
    for state in stateDict:
        if random.randint(1, 6) == 1:
            stateDict[state].showing = True
    
    return stateDict


def createCandidate(party):
    candidate = Candidate(party)
    candidate.chooseIssues(party)
    return candidate


def keyPressed(app, event):
    #only select move if not currently doing move
    if not app.doingMove:
        app.doingMove = True
        #choose move --> will change to buttons later
        if event.key == 'p':
            app.move = 'poll'
        elif event.key == 'f':
            app.move = 'fundraise'
        elif event.key == 'r':
            app.move = 'runAds'
        elif event.key == 's':
            app.move = 'speech'
        #if not valid move, player not doing a move
        else:
            app.doingMove = False
    #press another key to stop doing move
    else:
        app.doingMove = False
        app.move = None


def timerFired(app):
    return 42

def findPlayerTurn(app):
    if app.turns%2 == 0:
        return app.player1
    else:
        return app.player2

def mousePressed(app, event):
    #convert click to geometric point
    long = convertXToLong(app, event.x)
    lat = convertYToLat(app, event.y)
    point = Point(long, lat)

    player = findPlayerTurn(app)

    if app.doingMove:
        state = clickedState(app, point)
        if state != None:
            #do move and then reset move vars
            doMove(app, state, player)
            app.doingMove = False
            app.move = None
            return
    else:
        state = clickedState(app, point)
        if state != None and app.stateDict[state].showing:
            #give state info panel
            print(app.stateDict[state])

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

def doMove(app, state, player):
    #do selected move
    if app.stateDict[state].showing:
        if app.move == 'fundraise':
            fundraise(app, state, player)
            print(app.player1.money)
        elif app.move == 'runAds':
            runAds(app, state, player)
    else:
        if app.move == 'poll':
            poll(app, state, player)

    #keep track of  turns and go to next round at end of 3 turns each
    app.turns += 1
    if app.turns == MAX_TURNS:
        endRound(app)

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


def countElectoralVotes(app):
    for state in app.stateDict:
        votes = app.stateDict[state].electoralVotes

        if app.stateDict[state].demSupport > app.stateDict[state].repSupport:
            app.player1.votes += votes
        
        elif app.stateDict[state].demSupport < app.stateDict[state].repSupport:
            app.player2 += votes
        
        else:
            if random.randint(1,2) == 1:
                app.player1.votes += votes
            else:
                app.player2 += votes
    
def declareWinner(app):
    if app.player1.votes >= 270:
        return app.player1
    else:
        return app.player2

#need to find good ratios to orient map well
def drawMap(app, canvas):
    #do each state at a time
    for state in app.stateDict:
        stateGeo = app.stateDict[state].polygon

        #state color
        if not app.stateDict[state].showing:
            color = 'grey'
        else:
            color = app.stateDict[state].color
        
        #polygon shapes
        if stateGeo.geom_type == 'Polygon':
            points = list(stateGeo.exterior.coords)
            for i in range(len(points)):
                long, lat = points[i]
                x = convertLongToX(app, long)
                y = convertLatToY(app, lat)
                points[i] = (x, y)
            canvas.create_polygon(points, fill=color)
            #state name
            drawStateName(app, canvas, state, stateGeo)
      
        #multipolygon shapes
        else:
            polygons = list(stateGeo)
            for item in polygons:
                points = list(item.exterior.coords)
                for i in range(len(points)):
                    long, lat = points[i]
                    x = convertLongToX(app, long)
                    y = convertLatToY(app, lat)
                    points[i] = (x, y)
                canvas.create_polygon(points, fill=color)   

            drawStateName(app, canvas, state, stateGeo) 

def drawStateName(app, canvas, name, stateGeo):
    center = list(stateGeo.centroid.coords)[0]
    cx = convertLongToX(app, center[0])
    cy = convertLatToY(app, center[1])
    canvas.create_text(cx, cy, text=name, font='Arial 8 bold')


#these 4 functions convert between canvas points and longitude/latitude points
def convertLongToX(app, long):
    return int(long*9 + (app.width*1.55))

def convertLatToY(app, lat):
    return int(-lat*11 + (app.height*1.05))

def convertXToLong(app, x):
    return (x - (app.width*1.55))/9

def convertYToLat(app, y):
    return -(y - (app.height*1.05))/11



def redrawAll(app, canvas):
    drawMap(app, canvas)
    canvas.create_text(app.width/2, 10, text=f'Current Turn: {findPlayerTurn(app)}')

runApp(width=1000, height=1000)