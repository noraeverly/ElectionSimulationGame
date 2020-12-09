from constants import *
from creatingGame import *

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

def selectAvatar(app, event):
    x0, y0, x1, y1 = 70, 160, 80, 170
    if x0<event.x<x1 and y0<event.y<y1:
        if app.selectedAvatar == 0:
            app.selectedAvatar = len(app.avatarList)-1
        else:
            app.selectedAvatar -= 1
    x0, y0, x1, y1 = 120, 160, 130, 170
    if x0<event.x<x1 and y0<event.y<y1:
        if app.selectedAvatar == len(app.avatarList)-1:
            app.selectedAvatar = 0
        else:
            app.selectedAvatar += 1

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