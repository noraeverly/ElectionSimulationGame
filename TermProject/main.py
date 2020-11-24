import geopandas as gpd
from cmu_112_graphics import *
import pandas as pd
from shapely.geometry import Point, Polygon
import random
from stateList import *
from stateClass import *

# cmu graphics from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# shapefile geodata from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-1-states-provinces/

def appStarted(app):
    shapefile = '/Users/noraeverly/Desktop/TermProject/ne_110m_admin_1_states_provinces'
    app.data = gpd.read_file(shapefile)[['name_en', 'iso_3166_2', 'geometry']]
    app.data.columns = ['state', 'state_code', 'geometry']
    app.data.head()
    app.stateDict = createStateDict(app)

#create randomized map for start of game
def createStateDict(app):
    stateDict = {}
    for line in stateList.splitlines():
        abbrev, long, lat, name = line.split("\t", 3)
        stateDict[abbrev] = State(abbrev)
        stateDict[abbrev].findColor()
        stateDict[abbrev].generateIssues()
        # print(stateDict[abbrev].color, stateDict[abbrev].issues)
    
    #unfinished adding electoral votes to dict
    # for line in stateElectoralVotes.splitlines():
    #     state, votes = line.split(' - ')
    #     votes = votes.split()[0]
    #     stateDict[abbrev].electoralVotes = votes
    
    for index, row in app.data.iterrows():
        code = row['state_code'][3:]
        print(index)
        statePolygon = (row['geometry'])
        stateDict[code].polygon = statePolygon
    return stateDict

def keyPressed(app, event):
    return 42

def timerFired(app):
    return 42

def mousePressed(app, event):
    long = convertXToLong(app, event.x)
    lat = convertYToLat(app, event.y)
    point = Point(long, lat)

    #check if state is clicked on
    for state in app.stateDict:
        stateGeo = app.stateDict[state].polygon
        stateColor = app.stateDict[state].color
        if pointInState(point, stateGeo):
            print(state, ':', app.stateDict[state].issues)

            #uncomment to change the color of each state (tech demo)

            # if stateColor == 'red':
            #     app.stateDict[state].color = 'blue'
            # else:
            #     app.stateDict[state].color = 'red'

            return

#Is clicked-point in state?
def pointInState(point, poly):
    return poly.contains(point) #or point.within(poly)


#need to find good ratios to orient map well
def drawMap(app, canvas):
    #do each state at a time
    for state in app.stateDict:
        stateGeo = app.stateDict[state].polygon
        #polygon shapes
        if stateGeo.geom_type == 'Polygon':
            points = list(stateGeo.exterior.coords)
            for i in range(len(points)):
                long, lat = points[i]
                x = convertLongToX(app, long)
                y = convertLatToY(app, lat)
                points[i] = (x, y)
            canvas.create_polygon(points, fill=app.stateDict[state].color)
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
                canvas.create_polygon(points, fill=app.stateDict[state].color)   
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

runApp(width=1000, height=1000)