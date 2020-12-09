from constants import DEM, REP, DEFAULT_SCREEN_HEIGHT, DEFAULT_SCREEN_WIDTH
from cmu_112_graphics import ImageTk
from PIL import Image

#need to find good ratios to orient map well
def drawMap(app, canvas):
    #do each state at a time
    for state in app.stateDict:
        stateGeo = app.stateDict[state].polygon

        #state color
        if not app.stateDict[state].showing:
            color = 'grey'
        elif app.gameOver:
            color = 'blue' if app.stateDict[state].winningParty == DEM else 'red'
        else:
            color = app.stateDict[state].color
        
        outline = app.stateDict[state].outline
        
        #polygon shapes
        if stateGeo.geom_type == 'Polygon':
            points = list(stateGeo.exterior.coords)
            #draw state
            drawState(app, canvas, points, color, outline)
            #state name
            drawMapOverlay(app, canvas, state, stateGeo)
      
        #multipolygon shapes
        else:
            polygons = list(stateGeo)
            for item in polygons:
                points = list(item.exterior.coords)
                drawState(app, canvas, points, color, outline)  

            drawMapOverlay(app, canvas, state, stateGeo)

def drawState(app, canvas, points, color, outline):
    for i in range(len(points)):
        long, lat = points[i]
        x = convertLongToX(app, long)
        y = convertLatToY(app, lat)
        points[i] = (x, y)
    width = 2 if outline=='yellow' else 1
    canvas.create_polygon(points, fill=color, outline=outline, width=width)


#map overlay logic
def drawStateName(app, canvas, name, cx, cy):
    canvas.create_text(cx, cy, text=name, font='Arial 8 bold')

def drawStateVotes(app, canvas, state, cx, cy):
    canvas.create_text(cx, cy, text=f'{app.stateDict[state].electoralVotes}', font='Arial 9 bold')

def drawStateWealth(app, canvas, state, cx, cy):
    canvas.create_text(cx, cy, text=f'{"$"*app.stateDict[state].availableMoney}', font='Arial 10 bold', fill='lime green')

def drawStateStatus(app, canvas, state, cx, cy):
    canvas.create_text(cx-7, cy, text=f'{app.stateDict[state].demSupport}', font='Arial 9 bold', fill='SteelBlue1')
    canvas.create_text(cx, cy, text=f'-', font='Arial 9 bold', fill='white')
    canvas.create_text(cx+7, cy, text=f'{app.stateDict[state].repSupport}', font='Arial 9 bold', fill='light coral')

def drawMapOverlay(app, canvas, state, stateGeo):
    center = list(stateGeo.centroid.coords)[0]
    cx = convertLongToX(app, center[0])
    cy = convertLatToY(app, center[1])
    if app.mapOverlay == 'Name':
        drawStateName(app, canvas, state, cx, cy)
    elif app.mapOverlay == 'Votes':
        drawStateVotes(app, canvas, state, cx, cy)
    elif app.mapOverlay == 'Wealth':
        drawStateWealth(app, canvas, state, cx, cy)
    elif app.mapOverlay == 'Status' and app.stateDict[state].showing:
        drawStateStatus(app, canvas, state, cx, cy)
    

#these 4 functions convert between canvas points and longitude/latitude points
def convertLongToX(app, long):
    return int(long*9 + (1000*1.55)) * (app.width/DEFAULT_SCREEN_WIDTH)

def convertLatToY(app, lat):
    return int(-lat*11 + (800*1.05)) * (app.height/DEFAULT_SCREEN_HEIGHT)

def convertXToLong(app, x):
    return ((x - (app.width*1.55))/9) * (DEFAULT_SCREEN_WIDTH/app.width)

def convertYToLat(app, y):
    return (-(y - (app.height*1.05))/11) * (DEFAULT_SCREEN_HEIGHT/app.height)

#buttons for map overlays
def drawMapOverlayButtons(app, canvas):
    x0 = 10
    x1 = 60
    y0 = app.height/2 - 80
    y1 = app.height/2 - 50
    for overlay in app.overlays:
        canvas.create_rectangle(x0, y0, x1, y1)
        canvas.create_text((x0+x1)/2, (y0+y1)/2, text=overlay)
        y0 += 40
        y1 += 40

def drawRestartButton(app, canvas):
    basewidth = 25
    image = app.restartIcon
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((basewidth,hsize), Image.ANTIALIAS)
    canvas.create_image(app.width-10, app.height-10, image=ImageTk.PhotoImage(image), anchor='se')