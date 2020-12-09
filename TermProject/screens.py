from mapDrawing import *
from constants import *
from cmu_112_graphics import *


def drawStateCard(app, canvas):
    #extract important attributes
    state = app.currentState
    stateGeo = app.stateDict[state].polygon
    color = app.stateDict[state].color

    #state name and electoral votes
    canvas.create_text(app.width/2, 50, text=f'{state} - {app.stateDict[state].electoralVotes}', font=('Arial 30 bold'))

    #state's important topics 
    x0 = app.width/2 - 80
    y0 = app.height/2
    canvas.create_text(x0, y0, text=f'Hot Topics:', font=('Arial 22 bold'), anchor='w')
    for topic in app.stateDict[state].hotTopics:
        y0 += 30
        canvas.create_text(x0, y0, text=f'{topic}', font=('Arial 22 bold'), anchor='w')
    

    money = '$' * app.stateDict[state].availableMoney
    if app.stateDict[state].availableMoney == 0:
        money = 'Out of money right now.'
    #available money
    canvas.create_text(app.width/2, 100, text=f'Possible Fundraising Money: {money}', font=('Arial 25 bold'))

    #current influence
    influence = abs(app.stateDict[state].influence)
    if influence == 0:
        infColor = 'black'
    elif influence == app.stateDict[state].influence:
        infColor = 'blue'
    else:
        infColor = 'red'
    canvas.create_text((app.width/2) - 60, 250, text=f'Current Influence:', font=('Arial 25 bold'))
    canvas.create_text((app.width/2) + 60, 250, text=f'{influence}', font=('Arial 25 bold'), fill=infColor)

    #polling info
    canvas.create_text(app.width/2 - 65, 150, text=f'Latest Polls:', font=('Arial 25 bold'))
    canvas.create_text(app.width/2 + 35, 150, text=f'{app.stateDict[state].demSupport}', font=('Arial 25 bold'), fill='blue')
    canvas.create_text(app.width/2 + 65, 150, text=f'-', font=('Arial 25 bold'))
    canvas.create_text(app.width/2 + 95, 150, text=f'{app.stateDict[state].repSupport}', font=('Arial 25 bold'), fill='red')

        
    #polygon shapes
    if stateGeo.geom_type == 'Polygon':
        points = list(stateGeo.exterior.coords)
        center = list(stateGeo.centroid.coords)[0]
        drawStateOnCard(app, canvas, points, center, color)
    
    #multipolygon shapes
    else:
        polygons = list(stateGeo)
        for item in polygons:
            points = list(item.exterior.coords)
            center = list(stateGeo.centroid.coords)[0]
            drawStateOnCard(app, canvas, points, center, color)


def drawStateOnCard(app, canvas, points, center, color):
    for i in range(len(points)):
        long, lat = points[i]
        # nextLong, nextLat = points[i+1]
        x = convertLongToX(app, long)
        y = convertLatToY(app, lat)
        
        #shift state into upper left corner
        if i == 0:
            dx = convertLongToX(app, center[0]) - app.width/8
            dy = convertLatToY(app, center[1]) - app.height/8
        
        x = x - dx
        y = y - dy
        points[i] = (x, y)

    canvas.create_polygon(points, fill=color)


def drawIssueChoiceScreen(app, canvas):
    canvas.create_text(app.width/2, 50, text=f'Choose an issue to campaign about in {app.currentState}:')
    size= int(app.height/8)
    x0 = app.width - 200
    y0 = app.height / 5
    x1 = 200
    y1 = app.height / 4

    #draw box for each issue
    for issue in app.currentPlayer.issues:
        xText = (x0+x1)/2
        yText = (y0+y1)/2
        canvas.create_rectangle(x0, y0, x1, y1, fill='white')
        canvas.create_text(xText, yText, text=f'{issue}')
        y0 += size
        y1 += size

#display if user clicks on wrong state
def drawErrorMessage(app, canvas):
    error = app.errorMessage
    canvas.create_text(app.width/2, 250, text=error, fill='firebrick1', font='Arial 28 bold')

#updates user on what just happened
def drawUpdateMessage(app, canvas):
    update = app.updateMessage
    canvas.create_text(app.width/2, 250, text=update, font='Arial 28 bold')


def drawTitleScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill='blue')
    canvas.create_image(app.width/2, app.height-175, image=ImageTk.PhotoImage(app.flagMap))
    canvas.create_text(app.width/2, (app.height/2)-200, text='Welcome to Election Simulator!', font='Arial 60 bold', fill='white')
    canvas.create_text(app.width/2, (app.height/2)-50, text='Time to see if you have what it takes to win the presidency!', font='Arial 30', fill='white')

    canvas.create_rectangle((app.width/3)-50, (app.height/2)+50, (app.width/3)+50, (app.height/2)+100, fill='white', width=3)
    canvas.create_text((app.width/3), (app.height/2)+75, text='Single Player')

    canvas.create_rectangle(2*(app.width/3)-50, (app.height/2)+50, 2*(app.width/3)+50, (app.height/2)+100, fill='white', width=3)
    canvas.create_text(2*(app.width/3), (app.height/2)+75, text='Multiplayer')


def drawCreateCandidateScreen(app, canvas):
    if app.localMultiplayer:
        if app.player1 == None:
            canvas.create_text((app.width/2), 50, text=f'Create Player 1', font='Arial 30 bold')
        else:
            canvas.create_text((app.width/2), 50, text=f'Create Player 2', font='Arial 30 bold')
    else:
        canvas.create_text((app.width/2), 50, text=f'Create your Candidate', font='Arial 30 bold')

    drawAvatarChoice(app, canvas)

    center = app.width/2
    #name
    canvas.create_text((app.width/4)-25, 125, text=f'Name your character: {app.playerName}|', font='Arial 30 bold', anchor='w')

    #party
    canvas.create_text(center-150, 200, text='Choose your party:', font='Arial 26 bold')

    color = 'light grey' if app.selectedParty == DEM else 'grey'
    canvas.create_rectangle(center, 175, center+50, 225, fill=color)
    canvas.create_text(center+25, 200, text=DEM, fill='blue', font='Arial 26 bold')

    color = 'light grey' if app.selectedParty == REP else 'grey'
    canvas.create_rectangle(center+100, 175, center+150, 225, fill=color)
    canvas.create_text(center+125, 200, text=REP, fill='red', font='Arial 26 bold')

    #issues
    if app.selectedParty == DEM:
        drawPartyIssues(app, canvas, DEM_ISSUES)
    elif app.selectedParty == REP:
        drawPartyIssues(app, canvas, REP_ISSUES)
    
    #start button
    x0, y0, x1, y1 = app.width-150, app.height-60, app.width-25, app.height-25
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text((x0+x1)/2, (y0+y1)/2, text='Begin Campaign')
    
def drawPartyIssues(app, canvas, partyIssues):
    size= int(app.height/(2*len(partyIssues)))
    x0 = app.width - 200
    y0 = app.height/3 + 50
    x1 = 200
    y1 = y0 + 50
    xText = (x0+x1)/2
    canvas.create_text(xText, y0-20, text='Choose 4 issues to support:', anchor='s', font='Arial 26 bold')

    for issue in partyIssues:
        color = 'white'
        yText = (y0+y1)/2
        if issue in app.selectedIssues:
            color = 'LightSkyBlue1'
        canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        canvas.create_text(xText, yText, text=f'{issue}')
        y0 += size
        y1 += size

def drawAvatarChoice(app, canvas):
    image = app.avatarList[app.selectedAvatar]

    #image resizing help from https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
    basewidth = 100
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((basewidth,hsize), Image.ANTIALIAS)
    canvas.create_rectangle(48, 48, 151, 151, width=2)
    canvas.create_image(100, 100, image=ImageTk.PhotoImage(image))

    canvas.create_text(75, 165, text='<', font='Arial 16 bold')
    canvas.create_text(125, 165, text='>', font='Arial 16 bold')