from constants import *
from cmu_112_graphics import ImageTk
from PIL import Image
from moves import findPlayerTurn

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
    return int(-lat*11 + (800*1.08)) * (app.height/DEFAULT_SCREEN_HEIGHT)

def convertXToLong(app, x):
    return ((x - (app.width*1.55))/9) * (DEFAULT_SCREEN_WIDTH/app.width)

def convertYToLat(app, y):
    return (-(y - (app.height*1.08))/11) * (DEFAULT_SCREEN_HEIGHT/app.height)

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
    #image resizing help from https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
    basewidth = 25
    image = app.restartIcon
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((basewidth,hsize), Image.ANTIALIAS)

    canvas.create_image(app.width-10, app.height-10, image=ImageTk.PhotoImage(image), anchor='se')

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
    voteSize = length/538 #538 electoral votes

    canvas.create_rectangle(x0, y0, x0+(voteSize*demVoteCount), y1, fill='blue')
    canvas.create_text(x0+5, (y0+y1)/2, text=f'{demVoteCount}', anchor='w', fill='white')
    x0 += (voteSize*demVoteCount)
    canvas.create_rectangle(x0, y0, x0+(voteSize*unknownVoteCount), y1, fill='grey')
    x0 += (voteSize*unknownVoteCount)
    canvas.create_rectangle(x0, y0, x1, y1, fill='red')
    canvas.create_text(x1-5, (y0+y1)/2, text=f'{repVoteCount}', anchor='e', fill='white')

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
    canvas.create_text(xText, yText-7, text=f'{move}')
    cost = '0$'
    if move == POLL or move == ADS:
        cost = '1$'
    elif move == SPEECH:
        cost = '2$'
    canvas.create_text(xText, yText+7, text=f'Cost: {cost}', fill='green')

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

    image = player.avatar
    basewidth = 80
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((basewidth,hsize), Image.ANTIALIAS)

    if allign == 'left':
        canvas.create_image(x0+40, y0+40, image=ImageTk.PhotoImage(image))
        x0 += 80
        x1 += 80
    else:
        canvas.create_image(x1-40, y0+40, image=ImageTk.PhotoImage(image))
        x0 -= 80
        x1 -= 80
    canvas.create_rectangle(x0, y0, x1, y1+15)
    canvas.create_text(x0+marg, y0, text=f'{player.name}  {"*" if player==findPlayerTurn(app) else ""}', anchor='nw', font='Arial 16 bold')
    canvas.create_text(x1-marg, y0+marg, text=f'{player.party}', anchor='ne', 
                        font='Arial 16 bold', fill=(dem if player.party=='D' else rep))
    
    #draw player issues
    canvas.create_text(x0+marg, y0+boxHeight/4-marg, text='Candidate Issues:', anchor='nw', font='Arial 14 italic')
    count = 1
    for issue in player.issues:
        count += 1
        canvas.create_text(x0+marg, y0+(count * boxHeight/7)+marg, text=f'{issue}', anchor='nw', font='Arial 13')
    
    #draw player money
    money = '0 '
    if 0<player.money<=5:
        money = '$' * player.money
    elif player.money > 5:
        money = f'$x{player.money}'
    canvas.create_text(x1, y1, text=f'{money}', anchor='e', fill='green', font=('Comic Sans MS', 15))
