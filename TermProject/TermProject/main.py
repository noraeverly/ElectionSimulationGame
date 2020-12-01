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
        #choose move --> for speeding up testing, will remove for final project
        if event.key == '1':
            app.move = 'fundraise'
        elif event.key == '2':
            app.move = 'poll'
        elif event.key == '3':
            app.move = 'runAds'
        elif event.key == '4':
            app.move = 'speech'
        #if not valid key, player not doing a move
        else:
            app.doingMove = False
    #press a key to stop doing move
    else:
        app.doingMove = False
        app.move = None


def timerFired(app):
    return 42

def findPlayerTurn(app):
    #even turns are player1, odds are player2
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
        #click on state to complete move
        state = clickedState(app, point)
        if state != None:
            #do move and then reset move vars
            doMove(app, state, player)
            app.doingMove = False
            app.move = None
            return
    else:
        #if not doing move, give info about state
        state = clickedState(app, point)
        if state != None and app.stateDict[state].showing:
            #give state info panel
            print(app.stateDict[state])

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
                    app.move = 'fundraise'
                elif i == 3:
                    app.move = 'poll'
                elif i == 5:
                    app.move = 'runAds'
                elif i == 7:
                    app.move = 'speech'

        if app.move == None:
            app.doingMove = False


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
    #turn counter goes down by one if the move cannot be completed
    if app.stateDict[state].showing:
        if app.move == 'fundraise':
            fundraise(app, state, player)
        elif app.move == 'runAds':
            runAds(app, state, player)
        elif app.move == 'speech':
            makeSpeech(app, state, player)
        else:
            app.turns -= 1
    else:
        if app.move == 'poll':
            poll(app, state, player)
            print('polling new state')
        else:
            app.turns -= 1

    #keep track of turns and go to next round at end of 3 turns each
    app.turns += 1
    if app.turns == MAX_TURNS:
        endRound(app)
    
    # print('Turn:', app.turns, app.rounds)


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

#centered in state
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

def drawButton(app, canvas, move, spacing):
    size= int(app.width/9)
    x0 = spacing * size
    y0 = app.height - 100
    x1 = (spacing+1)*size
    y1 = app.height - 50
    canvas.create_rectangle(x0, y0, x1, y1, fill='white')
    xText = (x0+x1)/2
    yText = (y0+y1)/2
    canvas.create_text(xText, yText, text=f'{move}')


def redrawAll(app, canvas):
    drawMap(app, canvas)
    player = findPlayerTurn(app)
    canvas.create_text(app.width/2, 10, text=f'Current Turn: {player} - You have {player.money}$ to spend.')
    if app.gameOver:
        canvas.create_text(app.width/2, 50, text=f'Game Over! Winner: {declareWinner(app)}')
        canvas.create_text(app.width/2, 75, text=f'{app.player1.votes} - {app.player2.votes}')
    drawButton(app, canvas, 'Fundraise', 1)
    drawButton(app, canvas, 'Poll', 3)
    drawButton(app, canvas, 'Run Ads', 5)
    drawButton(app, canvas, 'Make Speech', 7)

runApp(width=1000, height=1000)