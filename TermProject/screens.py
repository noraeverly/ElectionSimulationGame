from mapDrawing import *

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
        y0 += 20
        canvas.create_text(x0, y0, text=f'{topic}', font=('Arial 22 bold'), anchor='w')
    
    #available money
    canvas.create_text(app.width/2, 100, text=f'Possible Fundraising Money: {"$ " * app.stateDict[state].availableMoney}', font=('Arial 26 bold'))

    #current influence
    canvas.create_text(app.width/2, 150, text=f'Current Influence: {app.stateDict[state].influence}', font=('Arial 26 bold'))

    #polling info
    canvas.create_text(app.width/2 - 65, 300, text=f'Latest Polls:', font=('Arial 26 bold'))
    canvas.create_text(app.width/2 + 35, 300, text=f'{app.stateDict[state].demSupport}', font=('Arial 26 bold'), fill='blue')
    canvas.create_text(app.width/2 + 65, 300, text=f'-', font=('Arial 26 bold'))
    canvas.create_text(app.width/2 + 95, 300, text=f'{app.stateDict[state].repSupport}', font=('Arial 26 bold'), fill='red')

        
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


def drawTitleScreen(app, canvas):
    return 42

def drawCreateCandidateScreen(app, canvas):
    return 42

#display if user clicks on wrong state
def drawErrorMessage(app, canvas):
    error = app.errorMessage
    canvas.create_text(app.width/2, 250, text=error, fill='firebrick1', font='Arial 28 bold')

#updates user on what just happened
def drawUpdateMessage(app, canvas):
    update = app.updateMessage
    canvas.create_text(app.width/2, 250, text=update, font='Arial 28 bold')